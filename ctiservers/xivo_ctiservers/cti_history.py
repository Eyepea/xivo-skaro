# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011 Proformatique'
__author__    = 'Corentin Le Gall'

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

from xivo_ctiservers import db_connection_manager

class History:
    selectbase = 'SELECT ${columns} FROM cdr'
    orderstring = 'ORDER BY calldate'
    columns = ('calldate', 'clid', 'src', 'dst', 'dcontext', 'channel', 'dstchannel',
               'lastapp', 'lastdata', 'duration', 'billsec', 'disposition', 'amaflags',
               'accountcode', 'uniqueid', 'userfield')

    def __init__(self, uri):
        self.uri = uri.replace('\/', '/')
        return

    def fetch(self, request):
        with db_connection_manager.DbConnectionPool(self.uri) as connection:
            connection['cur'].query(request, self.columns, (self.likestring,))
        results = connection['cur'].fetchall()
        dresults = []
        for r in results:
            dresults.append(dict(zip(self.columns, r)))
        return dresults

    def setlimit(self, nlimit):
        self.nlimit = nlimit
        self.desclimit = 'DESC LIMIT %d' % self.nlimit
        return

    def setlastdate(self, lastdate):
        self.lastdate = lastdate
        return

    def setlikestring(self, tech, pid):
        self.likestring = '%s/%s-%%' % (tech, pid)
        return

    def fetchall(self):
        self.cursor.query(self.selectbase,
                          self.columns)
        results = self.cursor.fetchall()
        return results

    def fetch_outgoing_calls(self):
        conditions = [
            "calldate > '%s'" % self.lastdate,
            "channel LIKE %s"
            ]
        condstring = 'WHERE %s' % (' AND '.join(conditions))
        requestbase = '%s %s %s %s' % (self.selectbase, condstring, self.orderstring, self.desclimit)
        dresults = self.fetch(requestbase)
        return dresults

    def fetch_answered_calls(self):
        conditions = [
            "calldate > '%s'" % self.lastdate,
            "disposition = 'ANSWERED'",
            "dstchannel LIKE %s"
            ]
        condstring = 'WHERE %s' % (' AND '.join(conditions))
        requestbase = '%s %s %s %s' % (self.selectbase, condstring, self.orderstring, self.desclimit)
        dresults = self.fetch(requestbase)
        return dresults

    def fetch_missed_calls(self):
        conditions = [
            "calldate > '%s'" % self.lastdate,
            "disposition != 'ANSWERED'",
            "dstchannel LIKE %s"
            ]
        condstring = 'WHERE %s' % (' AND '.join(conditions))
        requestbase = '%s %s %s %s' % (self.selectbase, condstring, self.orderstring, self.desclimit)
        dresults = self.fetch(requestbase)
        return dresults
