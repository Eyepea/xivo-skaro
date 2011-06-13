# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date: 2011-02-09 16:12:04 +0100 (Wed, 09 Feb 2011) $'
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

import logging

from xivo_ctiservers.interfaces import Interfaces

class FAGI(Interfaces):
    kind = 'FAGI'
    sep = '\n'
    def __init__(self, ctid):
        Interfaces.__init__(self, ctid)
        self.stack = list()
        return

    def connected(self, connid):
        Interfaces.connected(self, connid)
        global log
        log = logging.getLogger('interface_fagi(%s:%d)' % self.requester)
        return

    def disconnected(self, msg):
        Interfaces.disconnected(self, msg)
        return

    def set_ipbxid(self, ipbxid):
        self.ipbxid = ipbxid
        self.innerdata = self.ctid.safe[self.ipbxid]

    def manage_connection(self, msg):
        for t in msg.split(self.sep):
            self.stack.append(t)
        if self.stack[-1] == '' and self.stack[-2] == '':
            # that should be when we have received the whole event
            self.agidetails = {}
            for k in self.stack:
                if k:
                    o = k.split(': ')
                    self.agidetails[o[0]] = o[1]
            self.channel = self.agidetails.get('agi_channel')
            nscript = self.agidetails.get('agi_network_script')
            log.info('%s %s' % (self.channel, nscript))
            self.innerdata.fagi_setup(self)
            if self.innerdata.fagi_sync('get', self.channel, 'ami'):
                self.innerdata.fagi_sync('clear', self.channel)
                self.innerdata.fagi_handle(self.channel, 'AGI')
            else:
                self.innerdata.fagi_sync('set', self.channel, 'agi')
        return []

    def reply(self, replylines):
        print 'FAGI reply', replylines
        return
