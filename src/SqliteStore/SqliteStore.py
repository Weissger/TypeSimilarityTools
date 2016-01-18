import sqlite3


class SQLiteStore(object):
    def __init__(self, sqlite_path):
        self.__connection = sqlite3.connect(sqlite_path)
        self.__connection.execute("""
            CREATE TABLE IF NOT EXISTS type_similarity (type_a, type_b, similarity FLOAT, PRIMARY KEY(type_a, type_b))
            """)

    def store_similarity(self, type_a, type_b, similarity):
        pass

    def get_similarity(self, type_a, type_b,):
        pass

    def has_similarity(self, type_a, type_b):
        pass