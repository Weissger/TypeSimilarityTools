import sqlite3


class SimilarityStore(object):
    def __init__(self, sqlite_path):
        self.__connection = sqlite3.connect(sqlite_path)
        self.__connection.execute("""
            CREATE TABLE IF NOT EXISTS type_similarity (type_a, type_b, similarity FLOAT, PRIMARY KEY(type_a, type_b))
            """)

    def store_similarity(self, type_a, type_b, similarity):
        tmp = [type_a, type_b]
        tmp.sort()
        self.__connection.execute("""
            INSERT INTO type_similarity VALUES (?, ?, ?)
          """, tmp.append(similarity))
        return self.__connection.commit()

    def get_similarity(self, type_a, type_b,):
        tmp = [type_a, type_b]
        tmp.sort()
        self.__connection.execute("""
            SELECT ?instance_count FROM type_similarity WHERE type_a=? AND type_b=?
          """, tmp)
        return self.__connection.fetchone()