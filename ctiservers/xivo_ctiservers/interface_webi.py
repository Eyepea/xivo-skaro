# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision: 10133 $'
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
"""
WEBI Interface
"""

import logging
import time

from xivo_ctiservers.interfaces import Interfaces

XIVO_CLI_WEBI_HEADER = 'XIVO-CLI-WEBI'

AMI_REQUESTS = [
    'core show version',
    'core show channels',
    'dialplan reload',
    'sccp reload',
    'moh reload',
    'module reload',
    'module reload app_queue.so',
    'module reload chan_agent.so',
    ]

UPDATE_REQUESTS = [
    'xivo[userlist,update]',
    'xivo[devicelist,update]',
    'xivo[linelist,update]',
    'xivo[phonelist,update]',

    'xivo[trunklist,update]',
    'xivo[agentlist,update]',
    'xivo[queuelist,update]',
    'xivo[grouplist,update]',
    'xivo[meetmelist,update]',
    'xivo[voicemaillist,update]',
    'xivo[incalllist,update]',
    ]

class WEBI(Interfaces):
    kind = 'WEBI'
    sep = '\n'
    def __init__(self, ctid):
        Interfaces.__init__(self, ctid)
        return

    def connected(self, connid):
        Interfaces.connected(self, connid)
        global log
        log = logging.getLogger('interface_webi(%s:%d)' % self.requester)
        return

    def disconnected(self, msg):
        Interfaces.disconnected(self, msg)
        return

    def set_ipbxid(self, ipbxid):
        self.ipbxid = ipbxid

    def manage_connection(self, msg):
        multimsg = msg.replace('\r', '').split(self.sep)
        clireply = []
        closemenow = True

        for iusefulmsg in multimsg:
            usefulmsg = iusefulmsg.strip()
            if len(usefulmsg) == 0:
                break
            try:
                if usefulmsg == 'xivo[ctiprofilelist,get]':
                    clireply.extend(['%s:ID <%s>' % (XIVO_CLI_WEBI_HEADER, self.ipbxid),
                                     '%s' % self.ctid.cconf.getconfig('profiles').keys(),
                                     '%s:OK' % XIVO_CLI_WEBI_HEADER])
                    log.info('WEBI requested %s' % usefulmsg)

                elif usefulmsg == 'xivo[daemon,reload]':
                    self.ctid.askedtoquit = True
                    log.info('WEBI requested %s' % usefulmsg)

                elif usefulmsg in UPDATE_REQUESTS:
                    self.ctid.update_userlist[self.ipbxid].append(usefulmsg)
                    log.info('WEBI requested %s' % usefulmsg)

                elif usefulmsg in AMI_REQUESTS:
                    self.ctid.myami.get(self.ipbxid).delayed_action(usefulmsg, self)
                    closemenow = False

                else:
                    log.warning('WEBI did an unexpected request %s' % usefulmsg)

            except Exception:
                log.exception('WEBI connection [%s] : KO when defining for %s'
                              % (usefulmsg, self.requester))

        freply = { 'message' : clireply,
                   'closemenow' : closemenow }
        return freply

    def reply(self, replylines):
        try:
            for replyline in replylines:
                self.connid.sendall('%s\n' % replyline)
        except Exception:
            log.exception('WEBI connection [%s] : KO when sending to %s'
                          % (replylines, self.requester))
        return

    def makereply_close(self, actionid, status, reply = []):
        self.connid.sendall('%s:ID <%s>\n' % (XIVO_CLI_WEBI_HEADER, self.ipbxid))
        for r in reply:
            self.connid.sendall('%s\n' % r)
        self.connid.sendall('%s:%s\n' % (XIVO_CLI_WEBI_HEADER, status))
        log.info('did a WEBI reply %s for %s' % (status, actionid))

        del self.ctid.fdlist_established[self.connid]
        self.connid.close()
        return
