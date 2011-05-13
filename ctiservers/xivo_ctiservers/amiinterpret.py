# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
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
This is the XivoCTI class.
"""

import logging
import random
import string
import time

from queue_logger import queue_logger

log_ami_events_statusrequest = True
log_ami_events_complete = False

__alphanums__ = string.uppercase + string.lowercase + string.digits

class AMI_1_8:
    def __init__(self, ctid, ipbxid):
        # BaseCommand.__init__(self)
        self.ctid = ctid
        self.ipbxid = ipbxid
        self.innerdata = self.ctid.safe[self.ipbxid]
        global log
        log = logging.getLogger('AMI_1.8(%s)' % self.ipbxid)

        self.getvar_requests = {}
        self.a2c = {}
        return

    def ami_fullybooted(self, event):
        log.info('ami_fullybooted : %s' % (event))
        return
    def ami_shutdown(self, event):
        log.info('ami_shutdown : %s' % (event))
        return
    def ami_channelreload(self, event):
        # Occurs when there is a reload and the SIP config has changed
        log.info('ami_channelreload : %s' % (event))
        return
    def ami_reload(self, event):
        # Occurs when there is a reload and the CDR or Manager config has changed
        log.info('ami_reload : %s' % (event))
        return
    def ami_registry(self, event):
        # Occurs when there is a reload and the IAX config has changed and there is a registered trunk
        log.info('ami_registry : %s' % (event))
        return


    # NewXXX events
    def ami_newstate(self, event):
        event.pop('ChannelStateDesc')
        event.pop('Uniqueid')
        channel = event.pop('Channel')
        channelstate = event.pop('ChannelState')
        self.innerdata.newstate(channel, channelstate)
        # log.info('ami_newstate %s : %s' % (channel, event))
        return

    def ami_newchannel(self, event):
        event.pop('ChannelStateDesc')
        event.pop('AccountCode')
        channel = event.pop('Channel')
        uniqueid = event.pop('Uniqueid')
        channelstate = event.pop('ChannelState')
        context = event.pop('Context')

        actionid = ''.join(random.sample(__alphanums__, 10))
        self.a2c[actionid] = channel
        self.ctid.myami[self.ipbxid].amicl.actionid = actionid
        self.ctid.myami[self.ipbxid].amicl.getvar(channel, 'XIVO_ORIGACTIONID')
        self.innerdata.newchannel(channel, context, channelstate)
        # log.info('ami_newchannel %s : %s' % (channel, event))
        return

    def ami_newcallerid(self, event):
        # log.info('ami_newcallerid %s' % (event))
        return
    def ami_newexten(self, event):
        application = event.pop('Application')
        if application == 'AGI':
            channel = event.pop('Channel')
            log.info('ami_newexten %s %s : %s' % (application, channel, event))
            # warning : this might cause problems if AMI not connected
            if self.innerdata.fagi_sync('get', channel, 'agi'):
                self.innerdata.fagi_sync('clear', channel)
                self.innerdata.fagi_handle(channel, 'AMI')
            else:
                self.innerdata.fagi_sync('set', channel, 'ami')
        return
    def ami_newaccountcode(self, event):
        # log.info('ami_newaccountcode %s' % (event))
        return


    # Call events
    def ami_hangup(self, event):
        channel = event.pop('Channel')
        cause = event.pop('Cause')
        #  0 - Unknown
        #  3 - No route to destination
        # 16 - Normal Clearing
        # 17 - User busy (see Orig #5)
        # 18 - No user responding (see Orig #1)
        # 19 - User alerting, no answer (see Orig #8, Orig #3, Orig #1 (soft hup))
        # 21 - Call rejected (attempting *8 when noone to intercept)
        # 24 - "lost" Call suspended
        # 27 - Destination out of order
        # 28 - Invalid number format (incomplete number)
        # 34 - Circuit/channel congestion
        # log.info('ami_hangup %s - %s' % (channel, event))
        self.innerdata.hangup(channel)
        self.innerdata.sheetsend('hangup', channel)
        return

    def ami_hanguprequest(self, event):
        log.info('ami_hanguprequest : %s' % event)
        return

    def ami_softhanguprequest(self, event):
        log.info('ami_softhanguprequest : %s' % event)
        return

    def ami_dial(self, event):
        channel = event.pop('Channel')
        uniqueid = event.pop('UniqueID')
        subevent = event.pop('SubEvent')
        if subevent == 'Begin':
            destination = event.pop('Destination')
            if channel in self.innerdata.channels:
                self.innerdata.channels[channel].properties['direction'] = 'out'
                self.innerdata.channels[channel].properties['commstatus'] = 'calling'
                self.innerdata.channels[channel].properties['timestamp'] = time.time()
                self.innerdata.setpeerchannel(channel, destination)
                self.innerdata.update(channel)
            if destination in self.innerdata.channels:
                self.innerdata.channels[destination].properties['direction'] = 'in'
                self.innerdata.channels[destination].properties['commstatus'] = 'ringing'
                self.innerdata.channels[destination].properties['timestamp'] = time.time()
                self.innerdata.setpeerchannel(destination, channel)
                self.innerdata.update(destination)
            log.info('ami_dial (%s) %s %s - %s' % (subevent, channel, destination, event))
            self.innerdata.sheetsend('dial', channel)
        elif subevent == 'End':
            # one receives this one just before the hangup (in regular calls)
            dialstatus = event.pop('DialStatus')
            if dialstatus in ['CONGESTION', 'CANCEL', 'BUSY', 'ANSWER']:
                log.info('ami_dial %s %s %s %s'
                         % (subevent, dialstatus, channel, uniqueid))
            else:
                log.info('ami_dial %s %s %s %s - %s'
                         % (subevent, dialstatus, channel, uniqueid, event))
        else:
            log.info('ami_dial %s %s %s - %s'
                     % (subevent, channel, uniqueid, event))
        return

##        INFO:xivocti1.8:xivomine ami_dial {u'Destination': u'SIP/zlosfbpeajsxrn-0000000e',
##                                           u'CallerIDNum': u'hpueygdepcqbew',
##                                           u'DestUniqueID': u'1290444059.21',
##                                           u'Dialstring': u'zlosfbpeajsxrn',
##                                           u'CallerIDName': u'Hpueygd Epcqbew',

    def ami_extensionstatus(self, event):
        exten = event.pop('Exten')
        context = event.pop('Context')
        hint = event.pop('Hint')
        status = event.pop('Status')
        log.info('ami_extensionstatus : %s %s %s %s' % (exten, context, hint, status))
        self.innerdata.updatehint(hint, status)
        return

    def ami_bridge(self, event):
        channel1 = event.pop('Channel1')
        channel2 = event.pop('Channel2')
        uniqueid1 = event.pop('Uniqueid1')
        uniqueid2 = event.pop('Uniqueid2')
        bridgetype = event.pop('Bridgetype')
        bridgestate = event.pop('Bridgestate')
        log.info('ami_bridge %s %s (%s %s) - %s'
                 % (channel1, channel2, bridgetype, bridgestate, event))
        if channel1 in self.innerdata.channels:
            self.innerdata.channels[channel1].properties['talkingto_kind'] = 'channel'
            self.innerdata.channels[channel1].properties['talkingto_id'] = channel2
            self.innerdata.channels[channel1].properties['timestamp'] = time.time()
            self.innerdata.channels[channel1].properties['commstatus'] = 'linked-caller'
            self.innerdata.setpeerchannel(channel1, channel2)
            self.innerdata.update(channel1)
        if channel2 in self.innerdata.channels:
            self.innerdata.channels[channel2].properties['talkingto_kind'] = 'channel'
            self.innerdata.channels[channel2].properties['talkingto_id'] = channel1
            self.innerdata.channels[channel2].properties['timestamp'] = time.time()
            self.innerdata.channels[channel2].properties['commstatus'] = 'linked-called'
            self.innerdata.setpeerchannel(channel2, channel1)
            self.innerdata.update(channel2)
        return
    def ami_unlink(self, event):
        channel1 = event.pop('Channel1')
        channel2 = event.pop('Channel2')
        uniqueid1 = event.pop('Uniqueid1')
        uniqueid2 = event.pop('Uniqueid2')
        log.info('ami_unlink %s %s : %s' % (channel1, channel2, event))
        # usefulness of the unlink event ?
        return
    def ami_inherit(self, event):
        log.info('ami_inherit %s' % (event))
        return

    def ami_transfer(self, event):
        log.info('ami_transfer %s' % (event))
        # one gets here when there is a blind or attended transfer
        # not in case of an interception, it seems
        return

    def ami_masquerade(self, event):
        original = event.pop('Original')
        clone = event.pop('Clone')
        originalstate = event.pop('OriginalState')
        clonestate = event.pop('CloneState')
        log.info('ami_masquerade %s %s : %s' % (original, clone, event))
        if originalstate == 'Ringing':
            log.info('ami_masquerade %s %s (Interception ?) %s %s'
                     % (original, clone, originalstate, clonestate))
        elif originalstate == 'Up':
            log.info('ami_masquerade %s %s (Regular Transfer ?) %s %s'
                     % (original, clone, originalstate, clonestate))
        self.innerdata.masquerade(original, clone)
        # handle sheet transfer if appropriate
        return

    def ami_hold(self, event):
        log.info('ami_hold %s' % (event))
        return
    def ami_channelupdate(self, event):
        # called when there is a trunk : links callno-remote and callno-local
        log.info('ami_channelupdate %s' % (event))
        return
    def ami_pickup(self, event):
        log.info('ami_pickup %s' % (event))
        return
    def ami_rename(self, event):
        # it looks like we don't need this event and that Masquerade event already
        #    provides all the data for this, but this could happen to be wrong one day
        # log.info('ami_rename %s' % (event))
        return
    def ami_originateresponse(self, event):
        channel = event.pop('Channel')
        actionid = event.pop('ActionID')
        # this way, one knows which actionid has given which channel
        log.info('ami_originateresponse %s %s %s' % (actionid, channel, event))
        return


    # Meetme events
    def ami_meetmejoin(self, event):
        log.info('ami_meetmejoin %s' % (event))
        confno = event.pop('Meetme')
        channel = event.get('Channel')
        usernum = event.get('Usernum')
        pseudochan = event.get('PseudoChan')
        admin = event.get('Admin')
        opts = { 'usernum' : usernum,
                 'pseudochan' : pseudochan,
                 'admin' : (admin == 'Yes')
                 }
        self.innerdata.meetmeupdate(confno, channel, opts)
        return

        #{u'Talking': u'Not monitored',
        #u'Muted': u'No',
        #u'MarkedUser': u'No',
        #u'Role': u'Talk and listen',

    def ami_meetmeleave(self, event):
        confno = event.pop('Meetme')
        channel = event.pop('Channel')
        usernum = event.pop('Usernum')
        opts = { 'usernum' : usernum }
        self.innerdata.meetmeupdate(confno, channel, opts)
        log.info('ami_meetmeleave %s' % (event))
        return

    def ami_meetmeend(self, event):
        confno = event.pop('Meetme')
        self.innerdata.meetmeupdate(confno)
        return

    def ami_meetmemute(self, event):
        log.info('ami_meetmemute %s' % (event))
        return

    def ami_meetmetalking(self, event):
        log.info('ami_meetmetalking %s' % (event))
        return
    def ami_meetmetalkrequest(self, event):
        log.info('ami_meetmetalkrequest %s' % (event))
        return

    # XiVO events
    def ami_meetmenoauthed(self, event):
        log.info('ami_meetmenoauthed %s' % (event))
        return
    def ami_meetmepause(self, event):
        log.info('ami_meetmepause %s' % (event))
        return

    def ami_dahdichannel(self, event):
        log.info('ami_dahdichannel %s' % (event))
        return

    # Queue and agents events
    def ami_join(self, event):
        queue_logger.Join(event)
        queuename = event.pop('Queue')
        position = event.pop('Position')
        channel = event.pop('Channel')
        timestart = time.time()
        log.info('ami_join %s' % (event))
        self.innerdata.queueentryupdate(queuename, channel, position, timestart)
        # Count exists ... usefulness ? check against our count ?
        return

    def ami_leave(self, event):
        queue_logger.Leave(event)
        queuename = event.pop('Queue')
        position = event.pop('Position')
        channel = event.pop('Channel')
        log.info('ami_leave %s' % (event))
        self.innerdata.queueentryupdate(queuename, channel, position)
        return

    def ami_queuememberstatus(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('MemberName')
        location = event.pop('Location')
        if location != membername:
            log.warning('ami_queuememberstatus : %s and %s are not the same' (location, membername))

        status = event.pop('Status')
        paused = event.pop('Paused')
        membership = event.pop('Membership')
        callstaken = event.pop('CallsTaken')
        penalty = event.pop('Penalty')
        lastcall = event.pop('LastCall')

        self.innerdata.queuememberupdate(queuename, location,
                                         (status, paused, membership,
                                          callstaken, penalty, lastcall))
        return

    def ami_queuememberadded(self, event):
        self.ami_queuememberstatus(event)
        return

    def ami_queuememberremoved(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('MemberName')
        location = event.pop('Location')
        if location != membername:
            log.warning('ami_queuememberremoved : %s and %s are not the same' (location, membername))

        self.innerdata.queuememberupdate(queuename, location)
        return

    def ami_queuememberpaused(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('MemberName')
        location = event.pop('Location')
        if location != membername:
            log.warning('ami_queuememberremoved : %s and %s are not the same' (location, membername))
        paused = event.pop('Paused')

        self.innerdata.queuememberupdate(queuename, location, (paused,))
        return

    def ami_queuecallerabandon(self, event):
        # was used for stats : usefulness now ?
        log.info('ami_queuecallerabandon %s' % (event))
        return

    def ami_agentcalled(self, event):
        queue = event.pop('Queue')
        cchannel = event.pop('ChannelCalling')
        dchannel = event.pop('DestinationChannel')
        agentname = event.pop('AgentName')
        agentcalled = event.pop('AgentCalled')
        if agentname != agentcalled:
            log.warning('ami_agentcalled : %s %s' % (agentname, agentcalled))
        # agent case : dchannel = agentcalled
        log.info('ami_agentcalled %s->%s->%s %s'
                 % (cchannel, queue, dchannel, event))
        return

    def ami_agentconnect(self, event):
        queue_logger.AgentConnect(event)

        queuename = event.pop('Queue')
        member = event.pop('Member')
        membername = event.pop('MemberName')
        if member != membername:
            log.warning('ami_agentconnect %s %s' % (member, membername))
        log.info('ami_agentconnect %s %s : %s' % (queuename, member, event))
        return

    def ami_agentcomplete(self, event):
        log.info('ami_agentcomplete %s' % (event))
        queue_logger.AgentComplete(event)
        return

    def ami_agentringnoanswer(self, event):
        log.info('ami_agentringnoanswer %s' % (event))
        return

    def ami_agentlogin(self, event):
        agent = event.pop('Agent')
        channel = event.pop('Channel')
        self.innerdata.agentlogin(agent, channel)
        log.info('ami_agentlogin %s %s : %s' % (agent, channel, event))
        return

    def ami_agentlogoff(self, event):
        agent = event.pop('Agent')
        self.innerdata.agentlogout(agent)
        log.info('ami_agentlogoff %s : %s' % (agent, event))
        return

    # XXX TODO handle former AgentCallBacklogin & logoff


    # Parking events
    def ami_parkedcall(self, event):
        channel = event.pop('Channel')
        exten = event.pop('Exten')
        parkinglot = event.pop('Parkinglot')
        log.info('ami_parkedcall %s %s' % (channel, event))
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].setparking(exten, parkinglot)
        return
    def ami_unparkedcall(self, event):
        channel = event.pop('Channel')
        log.info('ami_unparkedcall %s %s' % (channel, event))
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()
        return
    def ami_parkedcalltimeout(self, event):
        channel = event.pop('Channel')
        log.info('ami_parkedcalltimeout %s %s' % (channel, event))
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()
        return
    def ami_parkedcallgiveup(self, event):
        channel = event.pop('Channel')
        log.info('ami_parkedcallgiveup %s %s' % (channel, event))
        return


    def ami_varset(self, event):
        # log.info('ami_varset %s' % (event))
        return
    def ami_peerstatus(self, event):
        # log.info('ami_peerstatus %s' % (event))
        return
    def ami_cdr(self, event):
        log.info('ami_cdr %s' % (event))
        return
    def ami_cel(self, event):
        # log.info('ami_cel %s' % (event))
        return
    def ami_dtmf(self, event):
        log.info('ami_dtmf %s' % (event))
        return

    def userevent_did(self):
        return

    def userevent_lookupdirectory(self):
        return

    def userevent_user(self):
        return

    def userevent_group(self):
        return

    def userevent_queue(self):
        return

    def userevent_outcall(self):
        return

    def userevent_meetme(self):
        return

    def userevent_localcall(self):
        return

    def userevent_feature(self):
        return

    def userevent_custom(self):
        return

    def userevent_dialplan2cti(self):
        return

    userevents = ['Queue', 'User', 'Custom', 'Meetme', 'Group',
                  'LocalCall']

    def ami_userevent(self, event):
        eventname = event.pop('UserEvent')
        channel = event.pop('CHANNEL', None)
        # syntax in dialplan : exten = xx,n,UserEvent(myevent,var1: ${var1},var2: ${var2})
        if eventname in self.userevents:
            methodname = 'userevent_%s' % eventname.lower()
            if hasattr(self, methodname):
                log.info('ami_userevent %s %s : %s' % (eventname, channel, event))
                getattr(self, methodname)()
        return

    def ami_agiexec(self, event):
        # occurs when there is a variable set
        command = event.pop('Command')
        commandid = event.pop('CommandId')
        channel = event.pop('Channel')
        subevent = event.pop('SubEvent')
        if subevent == 'End':
            resultcode = event.pop('ResultCode')
            # log.info('ami_agiexec %s %s %s' % (channel, resultcode, command))
        # command = 'VERBOSE "" 4'
        return

    def handle_fagi(self, fastagi):
        envdict = fastagi.env
        args = fastagi.args
        channel = envdict.pop('agi_channel')
        function = envdict.pop('agi_network_script')
        # syntax in dialplan : exten = xx,n,AGI(agi://ip:port/function,arg1,arg2)
        log.info('handle_fagi %s %s : %s' % (function, channel, args))
        return

    def ami_messagewaiting(self, event):
        old = event.pop('Old')
        new = event.pop('New')
        waiting = event.pop('Waiting')
        mailbox = event.pop('Mailbox')
        self.innerdata.voicemailupdate(mailbox, new, old, waiting)

    # Status replies events
    def ami_peerentry(self, event):
        if log_ami_events_statusrequest:
            # log.info('ami_peerentry %s' % (event))
            pass
        return
    def ami_registryentry(self, event):
        if log_ami_events_statusrequest:
            # log.info('ami_registryentry %s' % (event))
            pass
        return

    def ami_parkedcallstatus(self, event):
        if log_ami_events_statusrequest:
            log.info('ami_parkedcallstatus %s' % (event))
        return

    def ami_meetmelist(self, event):
        log.info('ami_meetmelist %s' % (event))
        confno = event.pop('Conference')
        channel = event.pop('Channel')
        usernum = event.pop('UserNumber')
        pseudochan = event.pop('PseudoChan')
        admin = event.get('Admin')
        opts = { 'usernum' : usernum,
                 'pseudochan' : pseudochan,
                 'admin' : (admin == 'Yes')
                 }
        self.innerdata.meetmeupdate(confno, channel, opts)
        # we have no information about 'since when the channels are in the meetme room'
        # => see the by-channel information
        return

    #    u'Talking': u'Not monitored',
    #    u'Muted': u'No',
    #    u'MarkedUser': u'No',
    #    u'Role': u'Talk and listen',

    def ami_status(self, event):
        if log_ami_events_statusrequest:
            log.info('ami_status %s' % (event))
        return

    def ami_coreshowchannel(self, event):
        channel = event.pop('Channel')
        uniqueid = event.pop('UniqueID')
        context = event.pop('Context')
        application = event.pop('Application')
        bridgedchannel = event.pop('BridgedChannel')
        state = event.pop('ChannelState')

        duration = event.pop('Duration')
        timestamp_start = self.timeconvert(duration)

        if log_ami_events_statusrequest:
            log.info('ami_coreshowchannel %s application=%s : %s' % (channel, application, event))

        self.innerdata.newchannel(channel, context, state)
        channelstruct = self.innerdata.channels[channel]

        channelstruct.properties['timestamp'] = timestamp_start
        if application == 'Dial':
            channelstruct.properties['direction'] = 'out'
            if state == '6':
                channelstruct.properties['commstatus'] = 'linked-caller'
            elif state == '4':
                channelstruct.properties['commstatus'] = 'calling'
        elif application == 'AppDial':
            channelstruct.properties['direction'] = 'in'
            if state == '6':
                channelstruct.properties['commstatus'] = 'linked-called'
            elif state == '5':
                channelstruct.properties['commstatus'] = 'ringing'

        if state != '6': # Up
            return
        if not bridgedchannel:
            # we come here when there is a parked call
            return
        self.innerdata.newchannel(bridgedchannel, context, state)
        self.innerdata.setpeerchannel(channel, bridgedchannel)
        self.innerdata.setpeerchannel(bridgedchannel, channel)
        return

    def ami_agents(self, event):
        if log_ami_events_statusrequest:
            log.info('ami_agents %s' % (event))
            pass
        agent = event.get('Agent')
        status = event.get('Status')
        loggedinchan = event.get('LoggedInChan')
        loggedintime  = event.get('LoggedInTime')
        talkingto = event.get('TalkingTo')
        talkingtochan = event.get('TalkingToChan')
        self.innerdata.agentstatus(agent, status)
        return

    def ami_queueparams(self, event):
        queuename = event.pop('Queue')
        # log.info('ami_queueparams %s : %s' % (queuename, event))
        return

    def ami_queuesummary(self, event):
        # log.info('ami_queuesummary %s' % (event))
        return

    def ami_queuemember(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('Name')
        location = event.pop('Location')
        if location != membername:
            log.warning('ami_queuemember : %s and %s are not the same' (location, membername))

        status = event.pop('Status')
        paused = event.pop('Paused')
        membership = event.pop('Membership')
        callstaken = event.pop('CallsTaken')
        penalty = event.pop('Penalty')
        lastcall = event.pop('LastCall')

        self.innerdata.queuememberupdate(queuename, location,
                                         (status, paused, membership,
                                          callstaken, penalty, lastcall))
        return

    def timeconvert(self, duration):
        if duration.find(':') >= 0:
            # like in core show channels output
            vdur = duration.split(':')
            duration_secs = int(vdur[0]) * 3600 + int(vdur[1]) * 60 + int(vdur[2])
        else:
            # like in queue entry output
            duration_secs = int(duration)
        timestamp_start = time.time() - duration_secs
        return timestamp_start

    def ami_queueentry(self, event):
        queuename = event.pop('Queue')
        channel = event.pop('Channel')
        position = event.pop('Position')
        wait = event.pop('Wait')
        timestart = self.timeconvert(wait)
        # might be useful to use CallerId Name/Num
        self.innerdata.queueentryupdate(queuename, channel, position, timestart)
        return

    def ami_listdialplan(self, event):
        if log_ami_events_statusrequest:
            log.info('ami_listdialplan %s' % (event))
        return

    # XXX dahdi channels

    def ami_voicemailuserentry(self, event):
        mailbox = event.pop('VoiceMailbox')
        context = event.pop('VMContext')
        new = event.pop('NewMessageCount')
        fullmailbox = '%s@%s' % (mailbox, context)
        # only NewMessageCount here - OldMessageCount only when IMAP compiled
        # relation to Old/New/Waiting in MessageWaiting UserEvent ?
        self.innerdata.voicemailupdate(fullmailbox, new)
        return

    # Monitor, Spy
    def ami_monitorstart(self, event):
        log.info('ami_monitorstart %s' % (event))
        return
    def ami_monitorstop(self, event):
        log.info('ami_monitorstop %s' % (event))
        return
    def ami_chanspystart(self, event):
        log.info('ami_chanspystart %s' % (event))
        return
    def ami_chanspystop(self, event):
        log.info('ami_chanspystop %s' % (event))
        return

    # End of status requests
    def ami_peerlistcomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_peerlistcomplete %s' % (event))
        return
    def ami_parkedcallscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_parkedcallscomplete %s' % (event))
        return
    def ami_meetmelistcomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_meetmelistcomplete %s' % (event))
        return
    def ami_statuscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_statuscomplete %s' % (event))
        return
    def ami_agentscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_agentscomplete %s' % (event))
        return
    def ami_queuestatuscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_queuestatuscomplete %s' % (event))
        return
    def ami_queuesummarycomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_queuesummarycomplete %s' % (event))
        return
    def ami_coreshowchannelscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_coreshowchannelscomplete %s' % (event))
        return
    def ami_registrationscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_registrationscomplete %s' % (event))
        return
    def ami_showdialplancomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_showdialplancomplete %s' % (event))
        return
    def ami_dahdishowchannelscomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_dahdishowchannelscomplete %s' % (event))
        return
    def ami_voicemailuserentrycomplete(self, event):
        if log_ami_events_complete:
            log.info('ami_voicemailuserentrycomplete %s' % (event))
        return

    # receive this kind of events once DTMF has been exchanged between 2 SIP phones
    def ami_rtcpreceived(self, event):
        # log.info('ami_rtcpreceived %s' % (event))
        return
    def ami_rtcpsent(self, event):
        # log.info('ami_rtcpsent %s' % (event))
        return

    def ami_receivefax(self, event):
        return
    def ami_receivefaxstatus(self, event):
        return
    def ami_sendfax(self, event):
        return
    def ami_sendfaxstatus(self, event):
        return

##    def ami_agiexec(self, event): return
##    def ami_aoc_d(self, event): return
##    def ami_aoc_e(self, event): return
##    def ami_aoc_s(self, event): return
##    def ami_asyncagi(self, event): return
##    def ami_bridgeaction(self, event): return
##    def ami_bridgeexec(self, event): return
##    def ami_ccavailable(self, event): return
##    def ami_cccallerrecalling(self, event): return
##    def ami_cccallerstartmonitoring(self, event): return
##    def ami_cccallerstopmonitoring(self, event): return
##    def ami_ccfailure(self, event): return
##    def ami_ccmonitorfailed(self, event): return
##    def ami_ccoffertimerstart(self, event): return
##    def ami_ccrecallcomplete(self, event): return
##    def ami_ccrequestacknowledged(self, event): return
##    def ami_ccrequested(self, event): return
##    def ami_channelupdate(self, event): return
##    def ami_dahdishowchannels(self, event): return
##    def ami_dataget_tree(self, event): return
##    def ami_dbgetcomplete(self, event): return
##    def ami_dbgetresponse(self, event): return
##    def ami_deviceentry(self, event): return
##    def ami_devicelistcomplete(self, event): return
##    def ami_jabberevent(self, event): return
##    def ami_jabberstatus(self, event): return
##    def ami_jitterbufstats(self, event): return
##    def ami_lineentry(self, event): return
##    def ami_linelistcomplete(self, event): return
##    def ami_logchannel(self, event): return
##    def ami_mcid(self, event): return
##    def ami_minivoicemail(self, event): return
##    def ami_mobilestatus(self, event): return
##    def ami_moduleloadreport(self, event): return
##    def ami_musiconhold(self, event): return
##    def ami_newpeeraccount(self, event): return
##    def ami_peerentry(self, event): return
##    def ami_placeholder(self, event): return
##    def ami_queuememberpenalty(self, event): return
##    def ami_spanalarm(self, event): return
##    def ami_spanalarmclear(self, event): return
##    def ami_waiteventcomplete(self, event): return

    # Responses
    def amiresponse_success(self, event, nocolon):
        log.info('amiresponse_success %s' % event)
        actionid = event.get('ActionID')
        if actionid in self.getvar_requests:
            del self.getvar_requests[actionid]
        if actionid in self.a2c: # created at newchannel event
            value = event.get('Value')
            if value:
                channel = self.a2c.get(actionid)
                self.innerdata.autocall(channel, value)
            del self.a2c[actionid]
        return

    def amiresponse_error(self, event, nocolon):
        log.info('amiresponse_error %s' % event)
        actionid = event.get('ActionID')
        if actionid in self.getvar_requests:
            print actionid, 'was in getvar_requests'
            del self.getvar_requests[actionid]
        if actionid in self.a2c: # created at newchannel event
            print actionid, 'was in a2c', self.a2c.get(actionid)
            del self.a2c[actionid]
        return

    def amiresponse_follows(self, event, nocolon):
        log.info('amiresponse_follows %s' % event)
        actionid = event.get('ActionID')
        if actionid in self.getvar_requests:
            del self.getvar_requests[actionid]
        return
