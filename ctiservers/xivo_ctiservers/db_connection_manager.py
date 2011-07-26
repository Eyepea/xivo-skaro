# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011 Proformatique'
__author__    = 'Pascal Cadotte-Michaud'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Queue

from xivo import anysql
from xivo.BackSQL import backmysql
from xivo.BackSQL import backsqlite
from xivo.BackSQL import backsqlite3
from xivo.BackSQL import backpostgresql

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
        return self.get()

    def __exit__(self, type, value, traceback):
        self.put()
    
    def get(self):
        self._connection = DbConnectionPool._pool[self._db_uri].get()
        return self._connection
    
    def put(self):
        DbConnectionPool._pool[self._db_uri].put(self._connection)
