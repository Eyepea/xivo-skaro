import Queue

from xivo import anysql
from xivo.BackSQL import backmysql
from xivo.BackSQL import backsqlite3

class DbConnectionPool:
    '''Connection manager for DB connections.

    A single connection will be established for any given URI and a connection
    will not be shared by two processes at the same time. The with statement
    will be blocked if the connection is already in use.

    Usage:
        with DbConnectionPool(uri) as connection:
            connection['cur'].query(query)
            connection['conn'].commit()
    '''

    _pool = {}

    def __init__(self, db_uri):
        self._db_uri = db_uri
        if not DbConnectionPool._pool.has_key(db_uri):
            DbConnectionPool._pool[db_uri] = Queue.Queue()
            connection = {}
            connection['conn'] = anysql.connect_by_uri(db_uri)
            connection['cur'] = connection['conn'].cursor()
            DbConnectionPool._pool[db_uri].put(connection)

    def __enter__(self):
        self._connection = DbConnectionPool._pool[self._db_uri].get()
        return self._connection

    def __exit__(self, type, value, traceback):
        DbConnectionPool._pool[self._db_uri].put(self._connection)

