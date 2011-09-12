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

import logging
import os
import random
import Queue
import string
import threading
import time

from xivo_ctiservers import xivo_ami
from xivo_ctiservers import asterisk_ami_definitions

__alphanums__ = string.uppercase + string.lowercase + string.digits

class AMI:
    kind = 'AMI'

    def __init__(self, ctid, ipbxid, config):
        self.ctid = ctid
        self.ipbxid = ipbxid
        self.innerdata = self.ctid.safe.get(self.ipbxid)
        self.log = logging.getLogger('interface_ami(%s)' % self.ipbxid)

        self.save_for_next_packet_events = ''
        self.waiting_actionid = {}
        self.actionids = {}
        self.originate_actionids = {}
        self.ipaddress = config.get('ipaddress', '127.0.0.1')
        self.ipport = int(config.get('ipport', 5038))
        self.ami_login = config.get('username', 'xivouser')
        self.ami_pass = config.get('password', 'xivouser')
        self.timeout_queue = Queue.Queue()
        self.amicl = None
        return

    def connect(self):
        ret = None
        try:
            self.amicl = xivo_ami.AMIClass(self.ipbxid,
                                           self.ipaddress, self.ipport,
                                           self.ami_login, self.ami_pass,
                                           True)
            self.amicl.connect()
            self.amicl.login()
            ret = self.amicl.sock
        except Exception:
            self.log.exception('unable to connect/login')
        return ret

    def disconnect(self):
        self.amicl.sock.close()
        self.amicl = None
        return

    def connected(self):
        ret = None
        if self.amicl and self.amicl.sock:
            try:
                ret = self.amicl.sock.getpeername()
            except Exception:
                pass
        return ret

    def initrequest(self, phaseid):
        # 'CoreSettings', 'CoreStatus', 'ListCommands',
        for initrequest in asterisk_ami_definitions.manager_commands.get('fetchstatuses'):
            actionid = 'init_%s:%s-%d' % (initrequest.lower(),
                                          phaseid,
                                          int(time.time()))
            params = {
                'mode' : 'init',
                'amicommand' : 'sendcommand',
                'amiargs' : (initrequest.lower(), [])
                }
            ipbxreply = self.execute_and_track(actionid, params)
        self.amicl.setactionid('init_close_%s' % phaseid)
        return

    def cb_timer(self, *args):
        try:
            self.log.info('cb_timer (timer finished at %s) %s' % (time.asctime(), args))
            self.timeout_queue.put(args)
            os.write(self.ctid.pipe_queued_threads[1], 'ami:%s\n' % self.ipbxid)
        except Exception:
            self.log.exception('cb_timer %s' % args)
        return

    def checkqueue(self):
        self.log.info('entering checkqueue')
        ncount = 0
        while self.timeout_queue.qsize() > 0:
            ncount += 1
            (toload,) = self.timeout_queue.get()
            action = toload.get('action')
            if action == 'commandrequest':
                actionid = toload.get('properties')
                if actionid in self.waiting_actionid:
                    sockparams = self.waiting_actionid.get(actionid)
                    sockparams.makereply_close(actionid, 'timeout')
                    del self.waiting_actionid[actionid]
                else:
                    self.log.warning('timeout on actionid %s but no more in our structure' % actionid)
        return ncount

    def delayed_action(self, usefulmsg, replyto):
        actionid = ''.join(random.sample(__alphanums__, 10))
        self.amicl.sendcommand('Command', [('Command', usefulmsg), ('ActionID', actionid)])
        self.waiting_actionid[actionid] = replyto
        replyto.replytimer = threading.Timer(2, self.cb_timer,
                                             ({'action' : 'commandrequest',
                                               'properties' : actionid },))
        replyto.replytimer.setName('Thread-ami-%s' % actionid)
        replyto.replytimer.start()
        return

    def handle_event(self, idata):
        """
        Handles the AMI events occuring on Asterisk.
        If the Event field is there, calls the handle_ami_function() function.
        """
        full_idata = self.save_for_next_packet_events + idata
        evlist = full_idata.split('\r\n\r\n')
        self.save_for_next_packet_events = evlist.pop()

        for ievt in evlist:
            try:
                evt = ievt.decode('utf8')
            except Exception:
                self.log.exception('could not decode event %r' % (ievt))
                continue
            this_event = {}
            nocolon = []
            for myline in evt.split('\r\n'):
                if myline.find('\n') < 0:
                    if myline != '--END COMMAND--': # occurs when requesting "module reload xxx.so" for instance
                        myfieldvalue = myline.split(': ', 1)
                        if len(myfieldvalue) == 2:
                            this_event[myfieldvalue[0]] = myfieldvalue[1]
                        else:
                            if myline.startswith('Asterisk Call Manager'):
                                self.log.info('%s' % (myline))
                            elif myline == 'ReportBlock:':
                                # single line in RTCPSent events - ignoring it for the time being
                                pass
                            else:
                                # comment these lines out, while RTCPSent and RTCPReceived events are crappy
                                # self.log.warning('unable to parse <%s> : %s'
                                # % (myline, evt.split('\r\n')))
                                pass
                else:
                    nocolon.append(myline)

            if len(nocolon) > 1:
                self.log.warning('nocolon is %s' % (nocolon))

            evfunction = this_event.pop('Event', None)
            # self.log.info('(all)  %s  : %s' % (evfunction, this_event))
            if evfunction is not None:
                for ik, iv in self.ctid.fdlist_established.iteritems():
                    if not isinstance(iv, str) and iv.kind == 'INFO' and iv.dumpami_enable:
                        todisp = this_event
                        efn = evfunction
                        if iv.dumpami_enable == ['all'] or efn in iv.dumpami_enable:
                            doallow = True
                            if iv.dumpami_disable and efn in iv.dumpami_disable:
                                doallow = False
                            if doallow:
                                ik.sendall('%.3f %s %s %s\n' % (time.time(), self.ipbxid, efn, todisp))
                self.handle_ami_function(evfunction, this_event)

                if evfunction not in ['Newexten', 'Newchannel', 'Newstate', 'Newcallerid']:
                    pass
                    # verboselog('%s %s' % (self.ipbxid, this_event), True, False)
            else: # {
                response = this_event.pop('Response', None)
                if response is not None:
                    if response == 'Follows' and this_event.get('Privilege') == 'Command':
                        reply = []
                        try:
                            for noc in nocolon:
                                arggs = noc.split('\n')
                                for toremove in ['', '--END COMMAND--']:
                                    while toremove in arggs:
                                        arggs.remove(toremove)
                                if arggs:
                                    self.log.info('Response : %s' % (arggs))
                                    for argg in arggs:
                                        reply.append(argg)

                            if 'ActionID' in this_event:
                                actionid = this_event.get('ActionID')
                                if actionid in self.waiting_actionid:
                                    connreply = self.waiting_actionid.get(actionid)
                                    if connreply is not None:
                                        connreply.replytimer.cancel()
                                        connreply.makereply_close(actionid, 'OK', reply)
                                    del self.waiting_actionid[actionid]

                        except Exception, e:
                            # self.log.exception('(command reply to %s, %s)' % (connreply, actionid))
                            self.log.exception('(command reply)')
                            print e
                        try:
                            self.amiresponse_follows(this_event)
                        except Exception:
                            self.log.exception('response_follows (%s) (%s)' % (this_event, nocolon))

                    elif response == 'Success':
                        try:
                            self.amiresponse_success(this_event)
                        except Exception:
                            self.log.exception('response_success (%s) (%s)' % (this_event, nocolon))

                    elif response == 'Error':
                        if 'ActionID' in this_event:
                            actionid = this_event.get('ActionID')
                            if actionid in self.waiting_actionid:
                                connreply = self.waiting_actionid.get(actionid)
                                if connreply is not None:
                                    connreply.replytimer.cancel()
                                    connreply.makereply_close(actionid, 'KO')
                                del self.waiting_actionid[actionid]
                        try:
                            self.amiresponse_error(this_event)
                        except Exception:
                            self.log.exception('response_error (%s) (%s)' % (this_event, nocolon))
                    else:
                        self.log.warning('Response=%s (untracked) : %s' % (response, this_event))

                elif len(this_event) > 0:
                    self.log.warning('XXX: %s' % (this_event))
                else:
                    self.log.warning('Other : %s' % (this_event))
            # }
        nevts = len(evlist)
        if nevts > 200:
            self.log.info('handled %d (> 200) events' % (nevts))
        return

    def handle_ami_function(self, evfunction, this_event):
        """
        Handles the AMI events related to a given function (i.e. containing the Event field).
        It roughly only dispatches them to the relevant commandset's methods.
        """
        try:
            if 'Privilege' in this_event:
                this_event.pop('Privilege')
            if (evfunction in asterisk_ami_definitions.evfunction_to_method_name):
                methodname = asterisk_ami_definitions.evfunction_to_method_name.get(evfunction)
                if hasattr(self.ctid.commandclass, methodname):
                    getattr(self.ctid.commandclass, methodname)(this_event)
                else:
                    self.log.warning('this event (%s) is tracked but no %s method is defined : %s'
                                     % (evfunction, methodname, this_event))
            else:
                self.log.warning('this event (%s) is not tracked : %s'
                                 % (evfunction, this_event))

        except Exception:
            self.log.exception('%s : event %s' % (evfunction, this_event))
        return


    def amiresponse_success(self, event):
        if 'ActionID' in event:
            actionid = event.pop('ActionID')
        else:
            self.log.info('amiresponse_success (no ActionID) %s' % event)
            return

        if actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties.pop('mode')
            if mode == 'newchannel':
                value = event.pop('Value')
                if value:
                    # self.log.info('amiresponse_success %s %s : %s %s : %s'
                    # % (actionid, mode, value, properties, event))
                    (channel, dummyvarname) = properties.get('amiargs')
                    self.innerdata.autocall(channel, value)
                    # we tell the original requester of the ipbxcommand action
                    # about the channel he actually created
                    if value in self.originate_actionids:
                        request = self.originate_actionids.get(value).get('request')
                        cn = request.get('requester')
                        cn.reply( { 'class' : 'ipbxcommand',
                                    'autocall_channel' : channel,
                                    'command' : request.get('ipbxcommand'),
                                    'replyid' : request.get('commandid') } )
            elif mode == 'useraction':
                self.log.info('amiresponse_success %s %s : %s - %s'
                              % (actionid, mode, event, properties))
                request = properties.get('request')
                cn = request.get('requester')
                try:
                    cn.reply( { 'class' : 'ipbxcommand',
                                'response' : 'ok',
                                'command' : request.get('ipbxcommand'),
                                'replyid' : request.get('commandid') } )
                except Exception:
                    # when requester is not connected any more ...
                    pass

                if 'amicommand' in properties:
                    if properties['amicommand'] in ['originate',
                                                    'origapplication',
                                                    'txfax']:
                        self.originate_actionids[actionid] = properties
                    elif ('mailboxcount' in properties['amicommand']
                          and 'amiargs' in properties
                          and len(properties['amiargs']) > 1):
                        # The context is not part of this event, it's only part
                        # of the request when using track_and_execute with an
                        # extra argument
                        context = properties['amiargs'][1]
                        fullmailbox = event['Mailbox'] + '@' + context
                        self.innerdata.voicemailupdate(fullmailbox,
                                                       event['NewMessages'],
                                                       event['OldMessages'])
            elif mode == 'extension':
                # this is the reply to 'ExtensionState'
                # too much verbose log output
                # self.log.info('amiresponse_success %s %s : %s - %s' % (actionid, mode, event, properties))
                msg = event.pop('Message')
                if msg == 'Extension Status':
                    self.ctid.commandclass.amiresponse_extensionstatus(event)
                else:
                    self.log.warning('amiresponse_success %s %s : %s - %s - unknown msg %s'
                                     % (actionid, mode, event, properties, msg))
            elif mode == 'init':
                self.log.info('amiresponse_success %s %s : %s'
                              % (actionid, mode, event))
            elif mode == 'presence':
                # self.log.info('amiresponse_success %s %s : %s' % (actionid, mode, event))
                # too verbose, since occurs each time a user changes its presence
                pass
            elif mode == 'vmupdate':
                try:
                    self.innerdata.voicemailupdate(
                        event['Mailbox'] + '@' + properties['amiargs'][1],
                        event['NewMessages'],
                        event['OldMessages'])
                except KeyError:
                    self.log.warning('Could not update voicemail info: %s', event)
            else:
                self.log.info('amiresponse_success %s %s (?) : %s'
                              % (actionid, mode, event))
            # print 'actionids left', self.actionids.keys()
        else:
            self.log.warning('amiresponse_success %s (no record) : %s'
                             % (actionid, event))
        return

    def amiresponse_error(self, event):
        if 'ActionID' in event:
            actionid = event.pop('ActionID')
        else:
            self.log.warning('amiresponse_error (no ActionID) %s' % event)
            return

        if actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties.pop('mode')
            self.log.warning('amiresponse_error %s %s : %s - %s'
                             % (actionid, mode, event, properties))
            if mode == 'useraction':
                request = properties.get('request')
                cn = request.get('requester')
                cn.reply({'class' : 'ipbxcommand',
                          'response' : 'ko',
                          'command' : request.get('ipbxcommand'),
                          'replyid' : request.get('commandid')})
                # at this (time) point of code complexity, it does not make sense
                # sending back the AMI event message 'as is', even if it is written
                # 'no such channel', since maybe the asterisk command behind is not
                # known ... for the time being, the best thing is to grep the commandid
                # from the CTI server log file
            # print 'actionids left', self.actionids.keys()
        else:
            self.log.warning('amiresponse_error %s (no record) : %s'
                             % (actionid, event))
        return

    def amiresponse_follows(self, event):
        if 'ActionID' in event:
            actionid = event.pop('ActionID')
        else:
            self.log.warning('amiresponse_follows (no ActionID) %s' % event)
            return

        if actionid in self.actionids:
            properties = self.actionids.pop(actionid)
            mode = properties.pop('mode')
            self.log.info('amiresponse_follows %s %s : %s - %s'
                          % (actionid, mode, event, properties))
            # print 'actionids left', self.actionids.keys()
        else:
            self.log.warning('amiresponse_follows %s (no record) : %s'
                             % (actionid, event))
        return

    def execute_and_track(self, actionid, params):
        conn_ami = self.amicl
        amicommand = params.get('amicommand')
        amiargs = params.get('amiargs')
        mode = params.get('mode')
        if conn_ami:
            if hasattr(conn_ami, amicommand):
                conn_ami.actionid = actionid
                self.actionids[actionid] = params
                ret = getattr(conn_ami, amicommand)(* amiargs)
            else:
                self.log.warning('mode %s : no such AMI command %s' % (mode, amicommand))
                ret = 'unknown'
        else:
            self.log.warning('mode %s : no AMI connection' % mode)
            ret = 'noconn'
        return ret
