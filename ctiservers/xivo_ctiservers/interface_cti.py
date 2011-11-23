# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011  Avencall'
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

import cjson
import logging
import os
import time

from xivo_ctiservers.interfaces import Interfaces
from xivo_ctiservers import cti_command

class serialJson():
    def __init__(self):
        return
    def decode(self, linein):
        v = cjson.decode(linein.replace('\\/', '/'))
        return v
    def encode(self, obj):
        obj['timenow'] = time.time()
        return cjson.encode(obj)

class CTI(Interfaces):
    kind = 'CTI'
    sep = '\n'
    def __init__(self, ctid):
        Interfaces.__init__(self, ctid)
        self.connection_details = {}
        self.serial = serialJson()
        self.transferconnection = {}
        return

    def connected(self, connid):
        """
        Send a banner at login time
        """
        Interfaces.connected(self, connid)
        self.log = logging.getLogger('interface_cti(%s:%d)' % self.requester)
        self.connid.sendall('XiVO CTI Server Version xx (on %s)\n'
                            % (' '.join(os.uname()[:3])))
        return

    def disconnected(self, msg):
        self.log.info('disconnected %s' % msg)
        self.logintimer.cancel()
        if self.transferconnection and self.transferconnection.get('direction') == 'c2s':
            self.log.info('%s got the file ...' % self.transferconnection.get('faxobj').fileid)
        try:
            ipbxid = self.connection_details['ipbxid']
            id = self.connection_details['userid']
            self._manage_logout(ipbxid, id, msg)
        except KeyError:
            self.log.warning('Could not retrieve the user id %s',
                             self.connection_details)

    def manage_connection(self, msg):
        z = list()
        if self.transferconnection:
            if self.transferconnection.get('direction') == 'c2s':
                faxobj = self.transferconnection.get('faxobj')
                self.logintimer.cancel()
                self.log.info('%s transfer connection : %d received' % (faxobj.fileid, len(msg)))
                faxobj.setbuffer(msg)
                faxobj.launchasyncs()
        else:
            multimsg = msg.split(self.sep)
            for usefulmsgpart in multimsg:
                cmd = self.serial.decode(usefulmsgpart)
                self.log.debug('commanddict: %s', cmd)
                nc = cti_command.Command(self, cmd)
                z.extend(nc.parse())
                # print nc.commandid
        return z

    def set_as_transfer(self, direction, faxobj):
        self.log.info('%s set_as_transfer %s' % (faxobj.fileid, direction))
        self.transferconnection = { 'direction' : direction,
                                    'faxobj' : faxobj }
        return

    def reply(self, msg):
        if self.transferconnection:
            if self.transferconnection.get('direction') == 's2c':
                self.connid.sendall(msg)
                self.log.info('transfer connection %d sent' % len(msg))
        else:
            self.connid.sendall(self.serial.encode(msg) + '\n')

    def _manage_logout(self, ipbxid, id, msg):
        """
        Clean up code for user disconnection
        """
        self.log.info('logout (%s) user:%s/%s', msg, ipbxid, id)
        self._disconnect_user(ipbxid, id)

    def loginko(self, errorstring):
        self.log.warning('user can not connect (%s) : sending %s'
                         % (self.details, errorstring))
        # self.logintimer.cancel() + close
        tosend = { 'class' : 'loginko',
                   'error_string' : errorstring }
        return self.serial.encode(tosend)

    def _disconnect_user(self, ipbxid, id):
        """
        Change the user's status to disconnected
        """
        try:
            innerdata = self.ctid.safe[ipbxid]
            userstatus = innerdata.xod_status['users'][id]
            innerdata.handle_cti_stack('set', ('users', 'updatestatus', id))
            userstatus['availstate'] = 'disconnected'
            userstatus['connection'] = None
            userstatus['last-logouttimestamp'] = time.time()
            innerdata.handle_cti_stack('empty_stack')
        except KeyError:
            self.log.warning('Could not update user status %s', id)

class CTIS(CTI):
    kind = 'CTIS'
