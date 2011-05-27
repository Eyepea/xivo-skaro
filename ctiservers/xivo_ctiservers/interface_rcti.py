# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision: 10843 $'
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

import cjson
import hashlib
import logging
import ssl
import socket
import time

class RCTI:
    kind = 'RCTI'

    def __init__(self, ctid, ipbxid, config):
        self.ctid = ctid
        self.ipbxid = ipbxid
        self.log = logging.getLogger('interface_rcti(%s)' % self.ipbxid)
        self.innerdata = self.ctid.safe.get(self.ipbxid)
        self.ipaddress = config.get('ipaddress')
        self.ipport = int(config.get('ipport'))
        self.username = config.get('username')
        self.password = config.get('password')
        self.encrypt = config.get('encrypt', False)
        return

    def connect(self):
        ret = None
        gai = socket.getaddrinfo(self.ipaddress, self.ipport, 0, socket.SOCK_STREAM, socket.SOL_TCP)
        if gai:
            (afinet, socktype, proto, dummy, bindtuple) = gai[0]
            self.socket = socket.socket(afinet, socktype)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                if self.encrypt:
                    ssl_sock = ssl.wrap_socket(self.socket, ssl_version = ssl.PROTOCOL_TLSv1)
                    ssl_sock.connect(bindtuple)
                    self.socket = ssl_sock
                else:
                    self.socket.connect(bindtuple)
                ret = self.socket
            except Exception, exc:
                self.log.warning('unable to connect to %s:%d - reason %d'
                                 % (self.ipaddress, self.ipport, exc.errno))
        return ret

    def disconnect(self):
        self.socket.close()
        return

    def connected(self):
        ret = None
        if self.socket:
            try:
                ret = self.socket.getpeername()
            except Exception:
                pass
        return ret

    def handle_reply(self, reply):
        t = None
        try:
            t = cjson.decode(reply.replace('\\/', '/'))
        except Exception, exc:
            print 'exception', exc
        return t

    initsequence = ['users', 'groups', 'queues', 'agents', 'phones']

    def handle_event(self, buf):
        for b in buf.strip().split('\n'):
            self.handle_event_line(b)
        return

    def handle_event_line(self, buf):
        if buf.startswith('XiVO'):
            self.log.info('got banner : %s' % (buf.strip()))
            self.login_id(self.username)
        else:
            t = self.handle_reply(buf)
            if not t:
                return
            if 'class' in t:
                classname = t.get('class')
                if classname == 'login_id':
                    if 'error_string' in t:
                        self.log.warning('step %s error %s' % (classname, t.get('error_string')))
                    else:
                        sessionid = t.get('sessionid')
                        self.login_pass(sessionid, self.password)
                elif classname == 'login_pass':
                    if 'error_string' in t:
                        self.log.warning('step %s error %s' % (classname, t.get('error_string')))
                    else:
                        self.login_capas('onlystate', t.get('capalist')[0])
                elif classname == 'login_capas':
                    self.log.info('got my capabilities : %s' % t)
                    self.getlist('users')
                elif classname == 'getlist':
                    tipbxid = t.get('tipbxid')
                    if tipbxid == self.ipbxid:
                        function = t.get('function')
                        ln = t.get('listname')
                        if function == 'listid':
                            if ln in self.initsequence and ln != self.initsequence[-1]:
                                idx = self.initsequence.index(ln)
                                self.getlist(self.initsequence[idx + 1])
                            if self.innerdata:
                                self.innerdata.config_from_external(ln, t)
                                for k in t.get('list'):
                                    self.getconfig(ln, k)
                        elif function == 'updateconfig':
                            if self.innerdata:
                                self.innerdata.config_from_external(ln, t)
                                k = t.get('tid')
                                self.getstatus(ln, k)
                        elif function == 'updatestatus':
                            if self.innerdata:
                                self.innerdata.config_from_external(ln, t)
                elif classname == 'chitchat':
                    self.log.info('got %s' % t)
                    self.ctid.send_to_cti_client(t.get('to'), t)
                else:
                    self.log.warning('unknown class : %s' % classname)
            else:
                print 'unknown value', t
        return

    def login_id(self, userlogin):
        z = { 'class' : 'login_id',
              'company' : 'default',
              'userlogin' : userlogin,
              'ident' : 'ctiserver-%s' % self.ctid.myipbxid,
              'xivoversion' : '1.2',
              'git_hash' : 'f',
              'git_date' : '0'
              }
        self.sendsock(z)
        return

    def login_pass(self, sessionid, password):
        tohash = '%s:%s' % (sessionid, password)
        sha1sum = hashlib.sha1(tohash).hexdigest()
        z = { 'class' : 'login_pass',
              'hashedpassword' : sha1sum
              }
        self.sendsock(z)
        return

    def login_capas(self, state, capaid):
        z = { 'class' : 'login_capas',
              'state' : state,
              'capaid' : capaid,
              'lastconnwins' : True,
              'loginkind' : 'user'
              }
        self.sendsock(z)
        return

    def getlist(self, listname):
        z = { 'class' : 'getlist',
              'function' : 'listid',
              'listname' : listname
              }
        self.sendsock(z)
        return

    def getconfig(self, listname, itemkey):
        z = { 'class' : 'getlist',
              'function' : 'updateconfig',
              'listname' : listname,
              'tid' : itemkey
              }
        self.sendsock(z)
        return

    def getstatus(self, listname, itemkey):
        z = { 'class' : 'getlist',
              'function' : 'updatestatus',
              'listname' : listname,
              'tid' : itemkey
              }
        self.sendsock(z)
        return

    def sendsock(self, z):
        self.socket.sendall(cjson.encode(z) + '\n')
        return
