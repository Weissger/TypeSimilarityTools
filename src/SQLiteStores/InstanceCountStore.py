import sqlite3
import collections
import functools

CACHE_SIZE = 2000


# Class to memorize last lookups (reduction of needed sqlite access)
class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
       If called later with the same arguments, the cached value is returned
       (not reevaluated).
       '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)

        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            # drop random values if cache is too big Todo intelligent dropping
            if len(self.cache) > CACHE_SIZE:
                self.cache = dict(self.cache.items()[len(self.cache)/2:])
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


class InstanceCountStore(object):
    def __init__(self, sqlite_path):
        self.__connection = sqlite3.connect(sqlite_path)
        self.__connection.execute("""
            CREATE TABLE IF NOT EXISTS instance_counts (type, instance_count INT, PRIMARY KEY(type))
            """)
        self.__connection.commit()

    def store_instance_count(self, in_type, count):
        self.__connection.execute("""
            INSERT INTO instance_counts VALUES (?, ?)
          """, (in_type, count))
        return self.__connection.commit()

    @memoized
    def get_instance_count(self, in_type):
        self.__connection.execute("""
            SELECT ?instance_count FROM instance_counts WHERE type=?
          """, in_type)
        return self.__connection.fetchone()
