# from ..SparqlInterface.src.Interfaces.AbstractClient import AbstractClient
# from ..SQLiteStores.InstanceCountStore import InstanceCountStore
# from ..SQLiteStores.SimilarityStore import SimilarityStore
from ..Utilities.Logger import log
from datetime import datetime
import gevent


class SimilarityCalculator(object):
    def __init__(self, server, instance_count_store=None):
        self.__server = server
        self.__instance_count_store = instance_count_store

    def get_similarity(self, type_a, type_b):
        """
        :param type_a:
        :param type_b:
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
        :return:
        """
        cur_time = datetime.now()
        shared_instances_count = float(self.__server.count_shared_instances(type_a, type_b))
        if shared_instances_count == 0:
            return 0
        if hasattr(self, 'instance_count_store'):
            instance_count_a = float(self.__instance_count_store.get_instance_count(type_a))
            instance_count_b = float(self.__instance_count_store.get_instance_count(type_b))
        else:
            instance_count_a = float(self.__server.count_instances(type_a))
            instance_count_b = float(self.__server.count_instances(type_b))
        log.info("Found instance cooccurrence in : {}".format(datetime.now() - cur_time))
        return shared_instances_count / (instance_count_a + instance_count_b - shared_instances_count)


    def get_best_parent_concept_value(self, type_a, type_b):
        """
        :param type_a:
        :param type_b:
        :return:
        """
        best = ("", 0)
        cur_time = datetime.now()
        for value in self.get_all_parent_concept_values(type_a, type_b):
            if value[1] > best[1]:
                best = value
        log.info("Found best parent in : {}".format(datetime.now() - cur_time))
        return best

    def get_all_parent_concept_values(self, type_a, type_b):
        """
        :param type_a:
        :param type_b:
        :return:
        """

        def get_types_fn(in_type):
            return self.__server.get_class_parents(in_type)

        cur_time = datetime.now()
        threads = [
            gevent.spawn(get_types_fn, type_a),
            gevent.spawn(get_types_fn, type_b)
        ]
        gevent.joinall(threads)
        log.info("Got parents for best parent search in : {}".format(datetime.now() - cur_time))

        types_a = threads[0].value
        types_b = threads[1].value
        types_a.add(type_a)
        types_b.add(type_b)

        all_parents = threads[0].value.intersection(threads[1].value)

        out_values = [("", 0)]
        cur_time = datetime.now()
        threads = [gevent.spawn(self.__get_parent_concept_value, t, type_a, type_b) for t in all_parents]
        gevent.joinall(threads)
        log.info("Got parent values in: {}".format(datetime.now() - cur_time))
        for t in threads:
            out_values.append(t.value)
        return out_values

    def __get_parent_concept_value(self, t, type_a, type_b):
        if hasattr(self, 'instance_count_store'):
            instance_count_parent = float(self.__instance_count_store.get_instance_count(t))
        else:
            instance_count_parent = float(self.__server.count_instances(t))
        if instance_count_parent == 0:
            return t, 0
        if hasattr(self, 'instance_count_store'):
            instance_count_a = float(self.__instance_count_store.get_instance_count(type_a))
            instance_count_b = float(self.__instance_count_store.get_instance_count(type_b))
        else:
            instance_count_a = float(self.__server.count_instances(type_a))
            instance_count_b = float(self.__server.count_instances(type_b))
        value = ((instance_count_a / instance_count_parent) + (instance_count_b / instance_count_parent)) / 2
        return t, value
