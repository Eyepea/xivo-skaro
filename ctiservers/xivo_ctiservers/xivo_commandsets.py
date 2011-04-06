# XiVO CTI Server

__version__   = '$Revision: 10129 $'
__date__      = '$Date: 2011-02-08 15:59:32 +0100 (Tue, 08 Feb 2011) $'
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
Base class for miscellaneous Command Sets
"""
import logging
log = logging.getLogger('commandset')

CMD_OTHER = 1 << 0
CMD_LOGIN_ID = 1 << 1
CMD_LOGIN_PASS = 1 << 2
CMD_LOGIN_CAPAS = 1 << 3
CMD_TRANSFER = 1 << 10

class Command:
    def __init__(self, commandname, commandargs):
        self.name = commandname
        self.args = commandargs
        self.type = None

class BaseCommand:

    ctiseparator = '\n'

    def __init__(self):
        self.transfers_ref = {}
        self.weblist = {}
        self.disconnlist = []
        return

    def checkqueue(self, buf):
        return

    def reset(self, mode, conn = None):
        return
    def transfer_addbuf(self, req, buf):
        return
    def transfer_addref(self, req, ref):
        return
    def transfer_endbuf(self, req):
        return
    def getmem(self):
        return 0

    def set_logintimeout(self, logintimeout):
        return
    # inits / updates
    def set_cticonfig(self, cticonfig):
        return

    def version(self):
        return 'NOVERSION'
    userfields = []
    def users(self):
        return {}
    def getdetails(self, itemname):
        return {}
    def uniqueids(self):
        return {}
    def connected_users(self):
        return {}

    def findreverse(self, dirlist, number):
        return

    def getuserslist(self):
        return
    def getqueueslist(self, qlist):
        return {}
    def getgroupslist(self, qlist):
        return {}
    def getagentslist(self, qlist):
        return {}

    def set_ctilog(self, ctilog):
        return
    def set_configs(self, configs):
        return
    def set_partings(self, parting_astid_context):
        return

    def set_urllist(self, astid, listname, urllist):
        return

    def set_userlist_urls(self, urls):
        return
    def set_userlist(self, ulist):
        return
    def set_userlist_ng(self, ulist):
        return
    def set_contextlist(self, ctxlist):
        return
    def updates(self, astid, what = None):
        return
    def read_internatprefixes(self, internatprefixfile):
        return
    def getprofilelist(self):
        return []
    # connection
    def connected(self, connid):
        return
    def disconnected(self, connid):
        return

    # login
    def required_login_params(self):
        return
    def get_login_params(self, astid, command, connid):
        return
    def manage_login(self, loginparams):
        return
    def manage_logout(self, userinfo, when):
        return
    def loginko(self, loginparams, connid, errorstring):
        return
    def loginok(self, loginparams, userinfo):
        return
    def telldisconn(self, connid):
        return

    # command events (~ CTI)
    def get_list_commands(self):
        return []
    def parsecommand(self, linein):
        return
    def manage_cticommand(self, userinfo, parsedcommand):
        return

    def regular_update(self):
        return

    # FAGI events
    def handle_fagi(self, astid, msg):
        return

    def phones_update(self, function, args):
        return

    def cliaction(self, connid, command):
        return

    def askstatus(self, astid, npl):
        return

    # QueueMemberStatus ExtensionStatus
    #                 0                  AST_DEVICE_UNKNOWN
    #                 1               0  AST_DEVICE_NOT_INUSE  /  libre
    #                 2               1  AST_DEVICE IN USE     / en ligne
    #                 3                  AST_DEVICE_BUSY
    #                                 4  AST_EXTENSION_UNAVAILABLE ?
    #                 5                  AST_DEVICE_UNAVAILABLE
    #                 6 AST_EXTENSION_RINGING = 8  appele

    # failure reasons (?)
    #define AST_CONTROL_HANGUP              1
    #define AST_CONTROL_RING                2
    #define AST_CONTROL_RINGING             3
    #define AST_CONTROL_ANSWER              4
    #define AST_CONTROL_BUSY                5
    #define AST_CONTROL_TAKEOFFHOOK         6
    #define AST_CONTROL_OFFHOOK             7
    #define AST_CONTROL_CONGESTION          8
    #define AST_CONTROL_FLASH               9
    #define AST_CONTROL_WINK                10

    # END of AMI events

CommandClasses = {}
from xivo import daemonize as ctidaemonize
