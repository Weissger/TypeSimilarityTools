import sqlite3


class InstanceCountStore(object):
    def __init__(self, sqlite_path):
        self.__connection = sqlite3.connect(sqlite_path)
        self.__connection.execute("""
            CREATE TABLE IF NOT EXISTS instance_counts (type, instance_count INT, PRIMARY KEY(type))
            """)

    def store_instance_count(self, in_type, count):
        pass

    def get_instance_count(self, in_type):
        pass