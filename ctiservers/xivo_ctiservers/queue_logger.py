# vim: set expandtab ts=4 sw=4 sts=4 fileencoding=utf-8:
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

import time
import logging

from xivo_ctiservers import db_connection_manager

class queue_logger:
    _uri = None
    last_transaction = None
    cache = None
    cache_threshold = 10    # Time to wait in sec before removing from the
                            # from the cache when a call is not answered

    @staticmethod
    def init(uri):
        global log
        log = logging.getLogger('XiVO queue logger')
        queue_logger._uri = uri
        queue_logger.last_transaction = time.time()
        queue_logger.cache = {}

    @staticmethod
    def _store_in_db(sql):
        with db_connection_manager.DbConnectionPool(queue_logger._uri) as connection:
            connection['cur'].query(str(sql))
            connection['conn'].commit()

    @staticmethod
    def _trace_event(ev):
        if not queue_logger.cache.has_key(ev['Queue']):
            queue_logger.cache[ev['Queue']] = {}

        if not queue_logger.cache[ev['Queue']].has_key(ev['Uniqueid']):
            queue_logger.cache[ev['Queue']][ev['Uniqueid']] = ev
        else:
            queue_logger.cache[ev['Queue']][ev['Uniqueid']] = \
                dict(queue_logger.cache[ev['Queue']][ev['Uniqueid']].items() + ev.items())

    @staticmethod
    def _is_traced_event(ev):
        return queue_logger.cache.has_key(ev['Queue']) and  queue_logger.cache[ev['Queue']].has_key(ev['Uniqueid'])

    @staticmethod
    def _show_cache():
        count = 0
        for key, value in queue_logger.cache.iteritems():
            count += len(value)
        log.info('Cache size: %s\ncache = %s' % (count, queue_logger.cache))

    @staticmethod
    def _clean_cache():
        '''If a call has left the queue for cache_threshold amount of time
        without being answered by an agent, we can remove it from the cache'''
        max_time = time.time() - queue_logger.cache_threshold
        to_delete = []
        for queue, events in queue_logger.cache.iteritems():
            for event, values in events.iteritems():
                if 'Holdtime' not in values:
                    continue
                leave_time = values['call_time_t'] + values['Holdtime']
                if 'Member' not in values and leave_time < max_time:
                    to_delete.append((queue, event))
        for queue, event in to_delete:
            del queue_logger.cache[queue][event]

    @staticmethod
    def Join(ev):
        ev['call_time_t'] = time.time()

        sql = '''INSERT INTO queue_info (call_time_t, queue_name, ''' \
                          '''caller, caller_uniqueid) ''' \
              '''VALUES (%d, '%s', '%s', '%s');''' % \
              (ev['call_time_t'], ev['Queue'], ev['CallerIDNum'], ev['Uniqueid'])

        queue_logger._trace_event(ev)
        queue_logger._store_in_db(sql)
        return

    @staticmethod
    def AgentConnect(ev):
        if not queue_logger._is_traced_event(ev):
            return ""

        ct = queue_logger.cache[ev['Queue']][ev['Uniqueid']]['call_time_t']

        sql = '''UPDATE queue_info '''\
              '''SET call_picker = '%s', hold_time = %s '''\
              '''WHERE call_time_t = %d and caller_uniqueid = '%s'; ''' %\
              (ev["Member"], ev["Holdtime"], ct, ev["Uniqueid"]);

        queue_logger._trace_event(ev)
        queue_logger._store_in_db(sql)
        return

    @staticmethod
    def AgentComplete(ev):
        if not queue_logger._is_traced_event(ev):
            return ""

        ct = queue_logger.cache[ev['Queue']][ev['Uniqueid']]['call_time_t']

        sql = '''UPDATE queue_info ''' \
              '''SET talk_time = %s ''' \
              '''WHERE call_time_t = %d and caller_uniqueid = '%s'; ''' % \
              (ev['TalkTime'], ct, ev['Uniqueid'])

        del queue_logger.cache[ev['Queue']][ev['Uniqueid']]

        queue_logger._store_in_db(sql)
        return

    @staticmethod
    def Leave(ev):
        if not queue_logger._is_traced_event(ev):
            return ""

        ev['Holdtime'] = time.time() - queue_logger.cache[ev['Queue']][ev['Uniqueid']]['call_time_t']
        ct = queue_logger.cache[ev['Queue']][ev['Uniqueid']]['call_time_t']

        sql = '''UPDATE queue_info ''' \
              '''SET hold_time = %d ''' \
              '''WHERE call_time_t = %d and caller_uniqueid = '%s'; ''' % \
              (ev['Holdtime'], ct, ev['Uniqueid'])

        queue_logger._trace_event(ev)
        queue_logger._store_in_db(sql)

        # if the patch to get the reason is not applied, the cache is cleaned
        # manually
        if 'Reason' in ev:
            if ev['Reason'] == "0":
                del queue_logger.cache[ev['Queue']][ev['Uniqueid']]
        else:
            queue_logger._clean_cache()
        return

