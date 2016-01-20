from SparqlInterface.src.Interfaces.AbstractClient import AbstractClient
from SQLiteStores.InstanceCountStore import InstanceCountStore
from SQLiteStores.SimilarityStore import SimilarityStore
import gevent


class SimilarityCalculator(object):
    def __init__(self, server, instance_count_store=None):
        self.__server = server
        self.__instance_count_store = instance_count_store

    def get_similarity(self, type_a, type_b):
        """
        :param instance_count_store:
        :type instance_count_store: InstanceCountStore
        :param type_a:
        :param type_b:
        :param server:
        :param similarity_store: SimilarityStore
        :type similarity_store: SimilarityStore
        """
        threads = [
            gevent.spawn(self.get_instance_cooccurrence, type_a, type_b),
            gevent.spawn(self.get_best_parent_concept_value, type_a, type_b)
        ]
        gevent.joinall(threads)
        instance_cooccurrence = threads[0].value
        parent_concept_value = threads[1].value[1]
        return (instance_cooccurrence + parent_concept_value) / 2


    def get_instance_cooccurrence(self, type_a, type_b):
        """
        :param type_a:
        :param type_b:
        :type server: AbstractClient
        :param server:
        :type instance_count_store: InstanceCountStore
        :return:
        """
        shared_instances_count = float(self.__server.count_shared_instances(type_a, type_b))
        if shared_instances_count == 0:
            return 0
        if hasattr(self, 'instance_count_store'):
            instance_count_a = float(self.__instance_count_store.get_instance_count(type_a))
            instance_count_b = float(self.__instance_count_store.get_instance_count(type_b))
        else:
            instance_count_a = float(self.__server.count_instances(type_a))
            instance_count_b = float(self.__server.count_instances(type_b))
        return shared_instances_count / (instance_count_a + instance_count_b - shared_instances_count)


    def get_best_parent_concept_value(self, type_a, type_b):
        """
        :param instance_count_store:
        :param type_a:
        :param type_b:
        :type server: AbstractClient
        :param server:
        :return:
        """
        best = ("", 0)
        for value in self.get_all_parent_concept_values(type_a, type_b):
            if value[1] > best[1]:
                best = value
        return best


    def get_all_parent_concept_values(self, type_a, type_b):
        """
        :param instance_count_store:
        :param type_a:
        :param type_b:
        :type server: AbstractClient
        :param server:
        :return:
        """

        def get_types_fn(in_type):
            def get_types():
                return self.__server.get_class_parents(in_type)

            return get_types

        threads = [
            gevent.spawn(get_types_fn(type_a)),
            gevent.spawn(get_types_fn(type_b))
        ]
        gevent.joinall(threads)

        types_a = threads[0].value
        types_b = threads[1].value
        types_a.add(type_a)
        types_b.add(type_b)

        all_parents = threads[0].value.intersection(threads[1].value)

        out_values = [("", 0)]
        for t in all_parents:
            if hasattr(self, 'instance_count_store'):
                instance_count_parent = float(self.__instance_count_store.get_instance_count(t))
            else:
                instance_count_parent = float(self.__server.count_instances(t))
            if instance_count_parent == 0:
                continue
            if hasattr(self, 'instance_count_store'):
                instance_count_a = float(self.__instance_count_store.get_instance_count(type_a))
                instance_count_b = float(self.__instance_count_store.get_instance_count(type_b))
            else:
                instance_count_a = float(self.__server.count_instances(type_a))
                instance_count_b = float(self.__server.count_instances(type_b))
            value = ((instance_count_a / instance_count_parent) + (instance_count_b / instance_count_parent)) / 2
            out_values.append((t, value))
        return out_values
