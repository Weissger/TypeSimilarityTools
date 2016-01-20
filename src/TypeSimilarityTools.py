from SparqlInterface.src import ClientFactory
from Utilities.Logger import log
from ProcessManager.ProcessManager import ProcessManager, OccupiedError
from SQLiteStore.SimilarityStore import SimilarityStore
from SimilarityCalculator.SimilarityCalculator import SimilarityCalculator
import time
from multiprocessing import Process


class TypeSimilarityTools(object):
    def __init__(self, server, user, password, n_processes, log_level, similarity_store=None,
                 instance_count_store=None):
        log.setLevel(log_level)
        if n_processes:
            self.processManager = ProcessManager(n_processes)
        self.__calculator = SimilarityCalculator(server=ClientFactory.make_client(server=server, user=user, password=password), instance_count_store=instance_count_store)
        if similarity_store:
            self.__similarity_store = SimilarityStore(similarity_store)

    def get_type_similarity(self, type_a, type_b, force_calc=False):
        # look in store
        if not force_calc and hasattr(self, '__similarity_store'):
            similarity = self.__similarity_store.get_similarity(type_a, type_b)
            if similarity:
                return similarity
        # calc similarity
        similarity = self.__calculator.get_similarity(type_a, type_b)
        if hasattr(self, '__similarity_store'):
            self.__similarity_store.store_similarity(type_a, type_b, similarity)
        return similarity
        #     self.__spawn_daemon(get_similarity, dict(type_a=type_a, type_b=type_b, server=self.__server))
        #
        # def __spawn_daemon(self, target, kwargs):
        #     # Todo Event based?
        #     # Check every 0.1 seconds if we can continue
        #     if hasattr(self, "processManager"):
        #         while not self.processManager.has_free_process_slot():
        #             time.sleep(0.1)
        #
        #     p = Process(target=target, kwargs=kwargs)
        #     p.daemon = True
        #     if hasattr(self, "processManager"):
        #         try:
        #             self.processManager.add(p)
        #         except OccupiedError as e:
        #             log.critical(e)
        #             return 2
        #         else:
        #             p.start()
        #     else:
        #         p.start()
