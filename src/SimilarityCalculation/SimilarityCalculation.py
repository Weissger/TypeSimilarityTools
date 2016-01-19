from SparqlInterface.src.Interfaces.AbstractClient import AbstractClient
from SQLiteStore.InstanceCountStore import InstanceCountStore
import gevent


def get_similarity(type_a, type_b, server, instance_count_store):
    threads = [
        gevent.spawn(get_instance_cooccurrence(type_a, type_b, server, instance_count_store)),
        gevent.spawn(get_best_parent_concept_value(type_a, type_b, server, instance_count_store))
    ]
    gevent.joinall(threads)
    instance_cooccurrence = threads[0].value
    parent_concept_value = threads[1].value
    return (instance_cooccurrence + parent_concept_value) / 2


def get_instance_cooccurrence(type_a, type_b, server, instance_count_store):
    """
    :param type_a:
    :param type_b:
    :type server: AbstractClient
    :param server:
    :type instance_count_store: InstanceCountStore
    :return:
    """
    shared_instances_count = float(server.count_shared_instances(type_a, type_b))
    if shared_instances_count == 0:
        return 0
    if instance_count_store:
        instance_count_a = float(instance_count_store.get_instance_count(type_a))
        instance_count_b = float(instance_count_store.get_instance_count(type_b))
    else:
        instance_count_a = float(server.count_instances(type_a))
        instance_count_b = float(server.count_instances(type_b))
    return shared_instances_count / (instance_count_a + instance_count_b - shared_instances_count)


def get_best_parent_concept_value(type_a, type_b, server, instance_count_store):
    """
    :param type_a:
    :param type_b:
    :type server: AbstractClient
    :param server:
    :return:
    """
    best = ("", 0)
    for value in get_all_parent_concept_values(type_a, type_b, server, instance_count_store):
        if value[1] > best[1]:
            best = value
    return best


def get_all_parent_concept_values(type_a, type_b, server, instance_count_store):
    """
    :param type_a:
    :param type_b:
    :type server: AbstractClient
    :param server:
    :return:
    """

    def get_types_fn(in_type):
        def get_types():
            return server.get_class_parents(in_type)

        return get_types

    threads = [
        gevent.spawn(get_types_fn(type_a)),
        gevent.spawn(get_types_fn(type_b))
    ]
    gevent.joinall(threads)

    out_values = []
    for t in threads[0].value.intersection(threads[1].value):
        if instance_count_store:
            instance_count_parent = float(instance_count_store.get_instance_count(t))
        else:
            instance_count_parent = float(server.count_instances(t))
        if instance_count_parent == 0:
            continue
        if instance_count_store:
            instance_count_a = float(instance_count_store.get_instance_count(type_a))
            instance_count_b = float(instance_count_store.get_instance_count(type_b))
        else:
            instance_count_a = float(server.count_instances(type_a))
            instance_count_b = float(server.count_instances(type_b))
        value = ((instance_count_a / instance_count_parent) + (instance_count_b / instance_count_parent)) / 2
        out_values.append((t, value))
    return out_values
