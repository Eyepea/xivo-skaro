# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date: 2011-04-06 17:20:05 +0200 (Wed, 06 Apr 2011) $'
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
Asterisk AMI utilities.
"""

import logging
import random
import re
import socket
import string
import time

__alphanums__ = string.uppercase + string.lowercase + string.digits
__dialallowed__ = '[0-9*#+]'
__specialextensions__ = ['s', 'BUSY']

switch_originates = True

## \class AMIClass
# AMI definition in order to interact with the Asterisk AMI.
class AMIClass:
    class AMIError(Exception):
        def __init__(self, msg):
            self.msg = msg
        def __str__(self):
            return self.msg

    # \brief Class initialization.
    def __init__(self, ipbxid, ipaddress, ipport, loginname, password, events):
        self.ipbxid    = ipbxid
        self.log = logging.getLogger('xivo_ami(%s)' % self.ipbxid)
        self.ipaddress = ipaddress
        self.ipport    = ipport
        self.loginname = loginname
        self.password  = password
        self.events    = events
        self.actionid = None
        return

    # \brief Connection to a socket.
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockret = self.sock.connect_ex((self.ipaddress, self.ipport))
        if sockret:
            self.log.warning('unable to connect to %s:%d - reason %d'
                             % (self.ipaddress, self.ipport, sockret))
        else:
            self.sock.settimeout(30)
            self.fd = self.sock.fileno()
            self.log.info('connection properties : here=%s remote=%s fd=%s'
                          % (self.sock.getsockname(), self.sock.getpeername(), self.fd))
        return

    # \brief Sending any AMI command.
    def sendcommand(self, action, args, loopnum = 0):
        ret = False
        try:
            t0 = time.time()
            towritefields = ['Action: %s' % action]
            for (name, value) in args:
                try:
                    towritefields.append('%s: %s' % (name, value))
                except Exception:
                    self.log.exception('(sendcommand build %s : %s = %s (%r))'
                                  % (action, name, value, value))
            if self.actionid:
                towritefields.append('ActionId: %s' % self.actionid)
            towritefields.append('\r\n')

            rawstr = '\r\n'.join(towritefields)
            if isinstance(rawstr, unicode):
                ustr = rawstr.encode('utf8')
            else:
                ustr = rawstr
            self.sock.sendall(ustr)
            ret = True
        except UnicodeEncodeError:
            self.log.exception('(sendcommand UnicodeEncodeError (%s %s %s))'
                               % (towritefields, self.actionid, self.fd))
            ret = True
        except UnicodeDecodeError:
            self.log.exception('(sendcommand UnicodeDecodeError (%s %s %s))'
                               % (action, self.actionid, self.fd))
            ret = True
        except socket.timeout:
            t1 = time.time()
            self.log.exception('(sendcommand timeout (%s %s %s) timespent=%f)'
                               % (action, self.actionid, self.fd, (t1 - t0)))
            ret = False
        except Exception:
            t1 = time.time()
            self.log.exception('(sendcommand other (%s %s %s) timespent=%f)'
                               % (action, self.actionid, self.fd, (t1 - t0)))
            ret = False
        if ret == False:
            if loopnum == 0:
                self.log.warning('second attempt for AMI command (%s %s %s)'
                                 % (action, self.actionid, self.fd))
                # tries to reconnect
                try:
                    self.sock.close()

                    self.connect()
                    self.login()
                    if self:
                        # "retrying AMI command=<%s> args=<%s>" % (action, str(args)))
                        self.sendcommand(action, args, 1)
                    else:
                        self.log.warning('self is undefined %s' % self)
                except Exception:
                    self.log.exception('reconnection (%s %s %s)'
                                       % (action, self.actionid, self.fd))
            else:
                self.log.warning('2 attempts have failed for AMI command (%s %s %s)'
                                 % (action, self.actionid, self.fd))
        if self.actionid:
            self.actionid = None
        return ret

    def setactionid(self, actionid):
        self.actionid = actionid
        return

    # \brief Requesting the Queues' Status.
    def sendqueuestatus(self, queue = None):
        if queue is None:
            ret = self.sendcommand('QueueStatus', [])
        else:
            ret = self.sendcommand('QueueStatus',
                                   [('Queue', queue)])
        return ret

    # \brief Requesting an ExtensionState.
    def sendextensionstate(self, exten, context):
        ret = self.sendcommand('ExtensionState',
                               [('Exten', exten),
                                ('Context', context)])
        return ret

    def sendparkedcalls(self):
        ret = self.sendcommand('ParkedCalls', [])
        return ret

    def sendmeetmelist(self):
        ret = self.sendcommand('MeetMeList', [])
        return ret

    # \brief Logins to the AMI.
    def login(self):
        try:
            ret = False
            if self.events:
                onoff = 'on'
            else:
                onoff = 'off'
            ret = self.sendcommand('Login',
                                   [('Username', self.loginname),
                                    ('Secret', self.password),
                                    ('Events', onoff)])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Hangs up a Channel.
    def hangup(self, channel, channel_peer = None):
        ret = 0
        try:
            self.log.info('hanging up %s as requested' % (channel))
            self.sendcommand('Hangup',
                             [('Channel', channel)])
            ret += 1
        except self.AMIError:
            pass
        except Exception:
            pass

        if channel_peer:
            try:
                self.log.info('hanging up %s (peer) as requested' % (channel_peer))
                self.sendcommand('Hangup',
                                 [('Channel', channel_peer)])
                ret += 2
            except self.AMIError:
                pass
            except Exception:
                pass
        return ret

    def setvar(self, var, val, chan = None):
        try:
            if chan is None:
                ret = self.sendcommand('Setvar', [('Variable', var),
                                                  ('Value', val)])
            else:
                ret = self.sendcommand('Setvar', [('Channel', chan),
                                                  ('Variable', var),
                                                  ('Value', val)])
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    def park(self, channel, channel_timeout, parkinglot, timeout = 45000):
        try:
            ret = self.sendcommand('Park',
                                   [('Channel', channel),
                                    ('Channel2', channel_timeout),
                                    ('Parkinglot', parkinglot),
                                    ('Timeout', timeout)
                                    ])
            return ret
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    def origapplication(self, application, data, phoneproto, phonesrcname, phonesrcnum, context):
        try:
            ret = self.sendcommand('Originate', [('Channel', '%s/%s' % (phoneproto, phonesrcname)),
                                                 ('Context', context),
                                                 ('Priority', '1'),
                                                 ('Application', application),
                                                 ('Data', data),
                                                 ('Variable', 'XIVO_ORIGACTIONID=%s' % self.actionid),
                                                 ('Variable', 'XIVO_ORIGAPPLI=%s' % application),
                                                 ('Async', 'true')])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Originates a call from a phone towards another.
    def originate(self, phoneproto, phonesrcname, phonesrcnum, cidnamesrc,
                  phonedst, cidnamedst,
                  locext, extravars = {}, timeout = 3600):
        # originate a call btw src and dst
        # src will ring first, and dst will ring when src responds
        ph = re.sub(__dialallowed__, '', phonedst)
        if len(ph) > 0 and phonedst not in __specialextensions__:
            return False
        try:
            command_details = [('Channel', '%s/%s' % (phoneproto, phonesrcname)),
                               ('Exten', phonedst),
                               ('Context', locext),
                               ('Priority', '1'),
                               ('Timeout', str(timeout * 1000)),
                               ('Variable', 'XIVO_ORIGAPPLI=%s' % 'OrigDial'),
                               ('Async', 'true')]
            if switch_originates:
                command_details.append(('CallerID', '"%s"<%s>' % (cidnamedst, phonedst)))
                command_details.append(('Variable', 'XIVO_ORIGSRCNAME=%s' % cidnamesrc))
                command_details.append(('Variable', 'XIVO_ORIGSRCNUM=%s'  % phonesrcnum))
            else:
                command_details.append(('CallerID', '"%s"<%s>' % (cidnamesrc, phonesrcnum)))
            for var, val in extravars.iteritems():
                command_details.append(('Variable', '%s=%s'  % (var, val)))
            command_details.append(('Variable', 'XIVO_ORIGACTIONID=%s' % self.actionid ))
            ret = self.sendcommand('Originate', command_details)
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Requests the Extension Statuses
    def extensionstate(self, extension, context):
        try:
            ret = self.sendcommand('ExtensionState', [('Exten', extension),
                                                      ('Context', context)])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Logs in an Agent
    def agentcallbacklogin(self, agentnum, extension, context, ackcall):
        try:
            ret = self.sendcommand('AgentCallbackLogin', [('Agent', agentnum),
                                                          ('Context', context),
                                                          ('Exten', extension),
                                                          ('AckCall' , ackcall)])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Logs off an Agent
    def agentlogoff(self, agentnum):
        try:
            ret = self.sendcommand('AgentLogoff', [('Agent', agentnum)])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Adds an Interface into a Queue
    def queueadd(self, queuename, interface, paused, skills = ''):
        try:
            # it looks like not specifying Paused is the same as setting it to false
            ret = self.sendcommand('QueueAdd', [('Queue', queuename),
                                                ('Interface', interface),
                                                ('Penalty', '1'),
                                                ('Paused', paused),
                                                ('Skills', skills)])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Removes a Queue
    def queueremove(self, queuename, interface):
        try:
            ret = self.sendcommand('QueueRemove', [('Queue', queuename),
                                                   ('Interface', interface)])
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief (Un)Pauses a Queue
    def queuepause(self, queuename, interface, paused):
        try:
            ret = self.sendcommand('QueuePause', [('Queue', queuename),
                                                  ('Interface', interface),
                                                  ('Paused', paused)])
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Logs a Queue Event
    def queuelog(self, queuename, event,
                 uniqueid = None,
                 interface = None,
                 message = None):
        command_details = [('Queue', queuename),
                           ('Event', event)]
        if uniqueid:
            command_details.append(('Uniqueid', uniqueid))
        if interface:
            command_details.append(('Interface', interface))
        if message:
            command_details.append(('Message', message))
        try:
            ret = self.sendcommand('QueueLog', command_details)
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Requests the Mailbox informations
    def mailbox(self, phone, context):
        try:
            ret1 = self.sendcommand('MailboxCount', [('Mailbox', '%s@%s' % (phone, context))])
            ret2 = self.sendcommand('MailboxStatus', [('Mailbox', '%s@%s' % (phone, context))])
            ret = ret1 and ret2
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Starts monitoring a channel
    def monitor(self, channel, filename, mixme = 'true'):
        try:
            ret = self.sendcommand('Monitor',
                                   [('Channel', channel),
                                    ('File', filename),
                                    ('Mix', mixme)])
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Stops monitoring a channel
    def stopmonitor(self, channel):
        try:
            ret = self.sendcommand('StopMonitor',
                                   [('Channel', channel)])
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Retrieves the value of Variable in a Channel
    def getvar(self, channel, varname):
        try:
            ret = self.sendcommand('Getvar', [('Channel', channel),
                                              ('Variable', varname)])
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Sends a sipnotify
    def sipnotify(self, *variables):
        try:
            channel = variables[0]
            arglist = [('Variable', '%s=%s' % (k, v.replace('"', '\\"')))
                for k, v in variables[len(variables) - 1].iteritems()]
            arglist.append(('Channel', channel))
            ret = self.sendcommand('SIPNotify', arglist)
        except self.AMIError:
            ret = False
        except Exception:
            ret = False
        return ret

    # \brief Transfers a channel towards a new extension.
    def transfer(self, channel, extension, context):
        ph = re.sub(__dialallowed__, '', extension)
        if len(ph) > 0 and extension not in __specialextensions__:
            return False
        try:
            command_details = [('Channel', channel),
                               ('Exten', extension),
                               ('Context', context),
                               ('Priority', '1')]
            ret = self.sendcommand('Redirect', command_details)
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    # \brief Atxfer a channel towards a new extension.
    def atxfer(self, channel, extension, context):
        ph = re.sub(__dialallowed__, '', extension)
        if len(ph) > 0 and extension not in __specialextensions__:
            return False
        try:
            ret = self.sendcommand('Atxfer', [('Channel', channel),
                                              ('Exten', extension),
                                              ('Context', context),
                                              ('Priority', '1')])
            return ret
        except self.AMIError:
            return False
        except Exception:
            return False

    def txfax(self, faxdir, faxid, userid, callerid, number, context, reference):
        # originate a call btw src and dst
        # src will ring first, and dst will ring when src responds
        try:
            ret = self.sendcommand('Originate', [('Channel', 'Local/%s@%s' % (number, context)),
                                                 ('CallerID', callerid),
                                                 ('Variable', 'FAXDIR=%s' % faxdir),
                                                 ('Variable', 'FAXID=%s' % faxid),
                                                 ('Variable', 'XIVO_USERID=%s' % userid),
                                                 ('Context', 'macro-txfax'),
                                                 ('Exten', 's'),
                                                 ('Async', 'true'),
                                                 ('ActionID', reference),
                                                 ('Priority', '1')])
            return ret
        except self.AMIError:
            return False
        except socket.timeout:
            return False
        except socket:
            return False
        except Exception:
            return False
