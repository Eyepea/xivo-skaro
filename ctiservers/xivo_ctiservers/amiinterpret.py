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
        self.innerdata = self.ctid.safe.get(self.ipbxid)
        self.log = logging.getLogger('AMI_1.8(%s)' % self.ipbxid)
        fagiport = self.ctid.cconf.getconfig('main').get('incoming_tcp').get('FAGI')[1]
        self.fagiportstring = ':%s/' % fagiport
        return

    def ami_fullybooted(self, event):
        self.log.info('ami_fullybooted : %s' % (event))
        return
    def ami_shutdown(self, event):
        self.log.info('ami_shutdown : %s' % (event))
        return
    def ami_channelreload(self, event):
        # Occurs when there is a reload and the SIP config has changed
        self.log.info('ami_channelreload : %s' % (event))
        return
    def ami_reload(self, event):
        # Occurs when there is a reload and the CDR or Manager config has changed
        self.log.info('ami_reload : %s' % (event))
        return
    def ami_registry(self, event):
        # Occurs when there is a reload and the IAX config has changed and there is a registered trunk
        self.log.info('ami_registry : %s' % (event))
        return


    # NewXXX events
    def ami_newstate(self, event):
        event.pop('Uniqueid')
        channelstatedesc = event.pop('ChannelStateDesc')
        channel = event.pop('Channel')
        channelstate = event.pop('ChannelState')
        self.innerdata.newstate(channel, channelstate)
        # self.log.info('ami_newstate %s %s %s : %s' % (channel, channelstate, channelstatedesc, event))
        return

    def ami_newchannel(self, event):
        event.pop('AccountCode')
        event.pop('Uniqueid')
        channelstatedesc = event.pop('ChannelStateDesc')
        channel = event.pop('Channel')
        channelstate = event.pop('ChannelState')
        context = event.pop('Context')

        actionid = 'nc:%s' % ''.join(random.sample(__alphanums__, 10))
        params = {
            'mode' : 'newchannel',
            'amicommand' : 'getvar',
            'amiargs' : [channel, 'XIVO_ORIGACTIONID']
            }
        self.ctid.myami.get(self.ipbxid).execute_and_track(actionid, params)
        self.innerdata.newchannel(channel, context, channelstate)
        # self.log.info('ami_newchannel %s %s %s : %s' % (channel, channelstate, channelstatedesc, event))
        return

    def ami_newcallerid(self, event):
        # self.log.info('ami_newcallerid %s' % (event))
        self.innerdata.update_parking_cid(event['Channel'], event['CallerIDName'], event['CallerIDNum'])
        return

    def ami_newexten(self, event):
        event.pop('Uniqueid')
        application = event.pop('Application')
        appdata = event.pop('AppData')
        channel = event.pop('Channel')
        if application == 'AGI':
            if self.fagiportstring in appdata: # match against ~ ':5002/' in appdata
                self.log.info('ami_newexten %s %s : %s %s' % (application, channel, appdata, event))
                # warning : this might cause problems if AMI not connected
                if self.innerdata.fagi_sync('get', channel, 'agi'):
                    self.innerdata.fagi_sync('clear', channel)
                    self.innerdata.fagi_handle(channel, 'AMI')
                else:
                    self.innerdata.fagi_sync('set', channel, 'ami')
        elif application == 'VoiceMail':
            self.log.info('ami_newexten %s %s : %s' % (application, channel, appdata))
        elif application in ['BackGround', 'WaitExten', 'Read']:
            pass
        elif application == 'Set':
            # why "Newexten + Set" and not "UserEvent + dialplan2cti" ?
            # - catched without need to add a dialplan line
            # - convenient when one is sure the variable is set only with this method
            # - channel and uniqueid already there
            # (myvar, myval) = event.get('AppData').split('=')
            pass
        return

    def ami_newaccountcode(self, event):
        # self.log.info('ami_newaccountcode %s' % (event))
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
        # self.log.info('ami_hangup %s - %s' % (channel, event))
        self.innerdata.hangup(channel)
        self.innerdata.sheetsend('hangup', channel)
        return

    def ami_hanguprequest(self, event):
        self.log.info('ami_hanguprequest : %s' % event)
        return

    def ami_softhanguprequest(self, event):
        self.log.info('ami_softhanguprequest : %s' % event)
        return

    def ami_dial(self, event):
        event.pop('UniqueID')
        if 'DestUniqueID' in event:
            event.pop('DestUniqueID')
        channel = event.pop('Channel')
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
            self.log.info('ami_dial (%s) %s %s - %s' % (subevent, channel, destination, event))
            self.innerdata.sheetsend('dial', channel)
        elif subevent == 'End':
            # one receives this one just before the hangup (in regular calls)
            dialstatus = event.pop('DialStatus')
            if dialstatus in ['CONGESTION', 'CANCEL', 'BUSY', 'ANSWER']:
                self.log.info('ami_dial %s %s %s'
                              % (subevent, dialstatus, channel))
            else:
                self.log.info('ami_dial %s %s %s - %s'
                         % (subevent, dialstatus, channel, event))
        else:
            self.log.info('ami_dial %s %s - %s'
                     % (subevent, channel, event))
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
        # self.log.info('ami_extensionstatus : %s %s exten=%s %s' % (hint, context, exten, status))
        self.innerdata.updatehint(hint, status)
        return

    def ami_bridge(self, event):
        channel1 = event.pop('Channel1')
        channel2 = event.pop('Channel2')
        uniqueid1 = event.pop('Uniqueid1')
        uniqueid2 = event.pop('Uniqueid2')
        bridgetype = event.pop('Bridgetype')
        bridgestate = event.pop('Bridgestate')
        self.log.info('ami_bridge %s %s (%s %s) - %s'
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
        self.log.info('ami_unlink %s %s : %s' % (channel1, channel2, event))
        # usefulness of the unlink event ?
        self.innerdata.sheetsend('unlink', channel1)
        return

    def ami_inherit(self, event):
        parentchannel = event.pop('Parent')
        childchannel = event.pop('Child')
        self.log.info('ami_inherit %s => %s' % (parentchannel, childchannel))
        if parentchannel.startswith('Local/') and parentchannel.endswith(';2'):
            # print 'ZZZZ', self.innerdata.channels.get(childchannel).properties
            # the key use case was especially in meetme
            pass
        return

    def ami_transfer(self, event):
        self.log.info('ami_transfer %s' % (event))
        # one gets here when there is a blind or attended transfer
        # not in case of an interception, it seems
        return

    def ami_masquerade(self, event):
        original = event.pop('Original')
        clone = event.pop('Clone')
        originalstate = event.pop('OriginalState')
        clonestate = event.pop('CloneState')
        self.log.info('ami_masquerade %s %s : %s' % (original, clone, event))
        if originalstate == 'Ringing':
            self.log.info('ami_masquerade %s %s (Interception ?) %s %s'
                     % (original, clone, originalstate, clonestate))
        elif originalstate == 'Up':
            self.log.info('ami_masquerade %s %s (Regular Transfer ?) %s %s'
                     % (original, clone, originalstate, clonestate))
        self.innerdata.masquerade(original, clone)
        self.innerdata.update_parking_parked(original, clone)
        # handle sheet transfer if appropriate
        return

    def ami_hold(self, event):
        channel = event.pop('Channel')
        status = event.pop('Status')
        if channel in self.innerdata.channels:
            self.innerdata.channels.get(channel).properties['holded'] = (status == 'On')
        else:
            self.log.warning('ami_hold : unknown channel %s' % channel)
        return

    def ami_channelupdate(self, event):
        # could be especially useful when there is a trunk : links callno-remote and callno-local
        # when the call is outgoing, one never receives the callno-remote
        channeltype = event.pop('Channeltype')
        if channeltype == 'IAX2':
            cnlocal = event.pop('IAX2-callno-local')
            cnremote = event.pop('IAX2-callno-remote')
            # cnremote = 0 : first step, when remote not joined yet
            self.log.info('ami_channelupdate %s : %s - %s : %s'
                          % (channeltype, cnlocal, cnremote, event))
        else:
            # self.log.info('ami_channelupdate %s : %s' % (channeltype, event))
            pass
        return

    def ami_pickup(self, event):
        self.log.info('ami_pickup %s' % (event))
        return

    def ami_rename(self, event):
        # it looks like we don't need this event and that Masquerade event already
        #    provides all the data for this, but this could happen to be wrong one day
        # self.log.info('ami_rename %s' % (event))
        return

    def ami_originateresponse(self, event):
        event.pop('Uniqueid')
        event.pop('Response') # response is included in reason (4 for Success)
        channel = event.pop('Channel')
        actionid = event.pop('ActionID', None)
        reason = event.pop('Reason')
        # reasons ...
        # 4 : Success
        # 0 : 1st phone unregistered
        # 1 : CLI 'channel request hangup' on the 1st phone's channel
        # 5 : 1st phone rejected the call (reject button or all lines busy)
        # 8 : 1st phone did not answer early enough
        if actionid in self.ctid.myami.get(self.ipbxid).originate_actionids:
            properties = self.ctid.myami.get(self.ipbxid).originate_actionids.pop(actionid)
            request = properties.get('request')
            cn = request.get('requester')
            try:
                cn.reply( { 'class' : 'ipbxcommand',
                            'command' : request.get('ipbxcommand'),
                            'replyid' : request.get('commandid'),
                            'channel' : channel,
                            'originatereason' : reason
                            } )
            except Exception:
                # when requester is not connected any more ...
                pass
            self.log.info('ami_originateresponse %s %s %s %s'
                          % (actionid, channel, reason, event))
        else:
            self.log.warning('ami_originateresponse %s %s %s %s (not in list)'
                             % (actionid, channel, reason, event))
        # print 'originate_actionids left', self.ctid.myami.get(self.ipbxid).originate_actionids.keys()
        return

    # Meetme events
    def ami_meetmejoin(self, event):
        self.log.info('ami_meetmejoin %s' % event)
        opts = {'usernum': event['Usernum'],
                'pseudochan': event['PseudoChan'],
                'admin': 'Yes' in event['Admin'],
                'authed': 'No' in event['NoAuthed'],
                'displayname': event['CallerIDname'],
                'phonenumber': event['CallerIDnum'], }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

        #{u'Talking': u'Not monitored',
        #u'Muted': u'No',
        #u'MarkedUser': u'No',
        #u'Role': u'Talk and listen',

    def ami_meetmeleave(self, event):
        self.log.info('ami_meetmeleave %s' % event)
        opts = {'usernum': event['Usernum'], 'leave': True, }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmeend(self, event):
        self.log.info('ami_meetmeend %s' % event)
        return self.innerdata.meetmeupdate(event['Meetme'])

    def ami_meetmemute(self, event):
        self.log.info('ami_meetmemute %s' % event)
        opts = {'muted': 'on' in event['Status'],
                'usernum': event['Usernum'], }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmetalking(self, event):
        self.log.info('ami_meetmetalking %s' % (event))
        return

    def ami_meetmetalkrequest(self, event):
        self.log.info('ami_meetmetalkrequest %s' % (event))
        return

    # XiVO events
    def ami_meetmenoauthed(self, event):
        self.log.info('ami_meetmenoauthed %s' % event)
        opts = {'usernum': event['Usernum'],
                'authed': 'off' in event['Status'], }
        return self.innerdata.meetmeupdate(event['Meetme'],
                                           event['Channel'],
                                           opts)

    def ami_meetmepause(self, event):
        self.log.info('ami_meetmepause %s' % event)
        opts = {'paused': 'on' in event['Status'], }
        return self.innerdata.meetmeupdate(event['Meetme'], opts=opts)

    def ami_dahdichannel(self, event):
        self.log.info('ami_dahdichannel %s' % (event))
        return

    # Queue and agents events
    def ami_join(self, event):
        queue_logger.Join(event)
        queuename = event.pop('Queue')
        position = event.pop('Position')
        channel = event.pop('Channel')
        timestart = time.time()
        self.log.info('ami_join %s' % (event))
        self.innerdata.queueentryupdate(queuename, channel, position, timestart)
        # Count exists ... usefulness ? check against our count ?
        return

    def ami_leave(self, event):
        queue_logger.Leave(event)
        queuename = event.pop('Queue')
        position = event.pop('Position')
        channel = event.pop('Channel')
        self.log.info('ami_leave %s' % (event))
        self.innerdata.queueentryupdate(queuename, channel, position)
        return

    def ami_queuememberstatus(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('MemberName')
        location = event.pop('Location')
        if location != membername:
            self.log.warning('ami_queuememberstatus : %s and %s are not the same' (location, membername))

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
            self.log.warning('ami_queuememberremoved : %s and %s are not the same' (location, membername))

        self.innerdata.queuememberupdate(queuename, location)
        return

    def ami_queuememberpaused(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('MemberName')
        location = event.pop('Location')
        if location != membername:
            self.log.warning('ami_queuememberremoved : %s and %s are not the same' (location, membername))
        paused = event.pop('Paused')

        self.innerdata.queuememberupdate(queuename, location, (paused,))
        return

    def ami_queuecallerabandon(self, event):
        # was used for stats : usefulness now ?
        self.log.info('ami_queuecallerabandon %s' % (event))
        return

    def ami_agentcalled(self, event):
        queue = event.pop('Queue')
        cchannel = event.pop('ChannelCalling')
        dchannel = event.pop('DestinationChannel')
        agentname = event.pop('AgentName')
        agentcalled = event.pop('AgentCalled')
        if agentname != agentcalled:
            self.log.warning('ami_agentcalled : %s %s' % (agentname, agentcalled))
        # agent case : dchannel = agentcalled
        self.log.info('ami_agentcalled %s->%s->%s %s'
                 % (cchannel, queue, dchannel, event))
        return

    def ami_agentconnect(self, event):
        queue_logger.AgentConnect(event)

        queuename = event.pop('Queue')
        member = event.pop('Member')
        membername = event.pop('MemberName')
        if member != membername:
            self.log.warning('ami_agentconnect %s %s' % (member, membername))
        self.log.info('ami_agentconnect %s %s : %s' % (queuename, member, event))
        return

    def ami_agentcomplete(self, event):
        self.log.info('ami_agentcomplete %s' % (event))
        queue_logger.AgentComplete(event)
        return

    def ami_agentringnoanswer(self, event):
        self.log.info('ami_agentringnoanswer %s' % (event))
        return

    def ami_agentlogin(self, event):
        agent = event.pop('Agent')
        channel = event.pop('Channel')
        self.innerdata.agentlogin(agent, channel)
        self.log.info('ami_agentlogin %s %s : %s' % (agent, channel, event))
        return

    def ami_agentlogoff(self, event):
        agent = event.pop('Agent')
        self.innerdata.agentlogout(agent)
        self.log.info('ami_agentlogoff %s : %s' % (agent, event))
        return

    def ami_agentcallbacklogin(self, event):
        agent = event.pop('Agent')
        loginchan = event.pop('Loginchan')
        self.innerdata.agentlogin(agent, loginchan)
        self.log.info('ami_agentcallbacklogin %s %s : %s' % (agent, loginchan, event))
        return

    def ami_agentcallbacklogoff(self, event):
        agent = event.pop('Agent')
        self.innerdata.agentlogout(agent)
        self.log.info('ami_agentcallbacklogoff %s : %s' % (agent, event))
        return

    def ami_musiconhold(self, event):
        channel = event.pop('Channel')
        state = event.pop('State')
        classname = event.pop('Class', None)
        self.log.info('ami_musiconhold %s %s %s' % (channel, state, classname))
        return

    # Parking events
    def ami_parkedcall(self, event):
        channel = event.pop('Channel')
        exten = event.pop('Exten')
        parkinglot = event.pop('Parkinglot')
        if parkinglot.startswith('parkinglot_'):
            parkinglot = '_'.join(parkinglot.split('_')[1:])
        self.log.info('ami_parkedcall %s %s %s %s' % (channel, parkinglot, exten, event))
        parkingevent = {
            'parker': event.pop('From'),
            'parked': channel,
            'exten': exten,
            'cid_name': event.pop('CallerIDName'),
            'cid_num': event.pop('CallerIDNum'),
            'parktime': time.time(),
            }
        self.innerdata.update_parking(parkinglot, exten, parkingevent)
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].setparking(exten, parkinglot)
        return
    def ami_unparkedcall(self, event):
        channel = event.pop('Channel')
        self.log.info('ami_unparkedcall %s %s' % (channel, event))
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()
        self.innerdata.unpark(channel)
        return
    def ami_parkedcalltimeout(self, event):
        channel = event.pop('Channel')
        self.log.info('ami_parkedcalltimeout %s %s' % (channel, event))
        if channel in self.innerdata.channels:
            self.innerdata.channels[channel].unsetparking()
        self.innerdata.unpark(channel)
        return
    def ami_parkedcallgiveup(self, event):
        channel = event.pop('Channel')
        self.log.info('ami_parkedcallgiveup %s %s' % (channel, event))
        self.innerdata.unpark(channel)
        return

    def ami_jitterbufstats(self, event):
        owner = event.pop('Owner')
        # self.log.info('ami_jitterbufstats %s : %s' % (owner, event))
        return

    def ami_varset(self, event):
        # self.log.info('ami_varset %s' % (event))
        return

    def ami_peerstatus(self, event):
        channeltype = event.pop('ChannelType')
        peer = event.pop('Peer')
        peerstatus = event.pop('PeerStatus')
        address = event.pop('Address', '')
        self.innerdata.updateregistration(peer, address)
        return

    def ami_cdr(self, event):
        #self.log.info('ami_cdr %s' % (event))
        return

    def ami_cel(self, event):
        # self.log.info('ami_cel %s' % (event))
        return

    def ami_dtmf(self, event):
        self.log.info('ami_dtmf %s' % (event))
        return

    def userevent_user(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        userprops = self.innerdata.xod_config.get('users').keeplist.get(xivo_userid)
        xivo_srcnum = event.get('XIVO_SRCNUM')
        usersummary_src = { 'fullname' : userprops.get('fullname'),
                            'phonenumber' : xivo_srcnum }

        xivo_lineid = event.get('XIVO_LINEID')
        usersummary_dst = self.innerdata.usersummary_from_phoneid(xivo_lineid)

        chanprops.set_extra_data('xivo', 'desttype', 'user')
        chanprops.set_extra_data('xivo', 'destid', usersummary_dst.get('userid'))
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        chanprops.set_extra_data('xivo', 'origin', 'internal')
        chanprops.set_extra_data('xivo', 'direction', 'internal')
        chanprops.set_extra_data('xivo', 'calleridnum', usersummary_src.get('phonenumber'))
        chanprops.set_extra_data('xivo', 'calleridname', usersummary_src.get('fullname'))
        chanprops.set_extra_data('xivo', 'calledidnum', usersummary_dst.get('phonenumber'))
        chanprops.set_extra_data('xivo', 'calledidname', usersummary_dst.get('fullname'))
        return

    def userevent_group(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        xivo_dstid = event.get('XIVO_DSTID')
        calleridnum = event.get('XIVO_SRCNUM')
        calledidnum = event.get('XIVO_DSTNUM')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        return

    def userevent_queue(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        xivo_dstid = event.get('XIVO_DSTID')
        calleridnum = event.get('XIVO_SRCNUM')
        calledidnum = event.get('XIVO_DSTNUM')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        return

    def userevent_meetme(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        xivo_dstid = event.get('XIVO_DSTID')
        calleridnum = event.get('XIVO_SRCNUM')
        calledidnum = event.get('XIVO_DSTNUM')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        # chanprops.set_extra_data('xivo', 'calledidname', xivo_dstid)
        return

    def userevent_outcall(self, chanprops, event):
        xivo_userid = event.get('XIVO_USERID')
        xivo_dstid = event.get('XIVO_DSTID')
        calleridnum = event.get('XIVO_SRCNUM')
        calledidnum = event.get('XIVO_DSTNUM')
        chanprops.set_extra_data('xivo', 'userid', xivo_userid)
        chanprops.set_extra_data('xivo', 'origin', 'outcall')
        chanprops.set_extra_data('xivo', 'direction', 'outgoing')
        self.innerdata.sheetsend('outcall', chanprops.channel)
        return

    def userevent_did(self, chanprops, event):
        calleridnum = event.get('XIVO_SRCNUM')
        calleridname = event.get('XIVO_SRCNAME')
        calleridton = event.get('XIVO_SRCTON')
        calleridrdnis = event.get('XIVO_SRCRDNIS')
        didnumber = event.get('XIVO_EXTENPATTERN')

        chanprops.set_extra_data('xivo', 'origin', 'did')
        chanprops.set_extra_data('xivo', 'direction', 'incoming')
        chanprops.set_extra_data('xivo', 'did', didnumber)
        chanprops.set_extra_data('xivo', 'calleridnum', calleridnum)
        chanprops.set_extra_data('xivo', 'calleridname', calleridname)
        chanprops.set_extra_data('xivo', 'calleridrdnis', calleridrdnis)
        chanprops.set_extra_data('xivo', 'calleridton', calleridton)
        for k, v in self.innerdata.xod_config.get('incalls').keeplist.iteritems():
            if v.get('exten') == didnumber:
                for kk, vv in v.iteritems():
                    if kk != 'context' and kk.endswith('context') and vv:
                        chanprops.set_extra_data('xivo', 'context', vv)
                        # print didnumber, k, v.get('action'), kk, vv
        # directory lookup : update chanprops
        self.innerdata.sheetsend('incomingdid', chanprops.channel)
        return

    def userevent_lookupdirectory(self, chanprops, event):
        calleridnum = event.get('XIVO_SRCNUM')
        calleridname = event.get('XIVO_SRCNAME')
        calleridton = event.get('XIVO_SRCTON')
        calleridrdnis = event.get('XIVO_SRCRDNIS')
        context = event.get('XIVO_CONTEXT')

        chanprops.set_extra_data('xivo', 'origin', 'forcelookup')
        chanprops.set_extra_data('xivo', 'context', context)
        chanprops.set_extra_data('xivo', 'calleridnum', calleridnum)
        chanprops.set_extra_data('xivo', 'calleridname', calleridname)
        chanprops.set_extra_data('xivo', 'calleridrdnis', calleridrdnis)
        chanprops.set_extra_data('xivo', 'calleridton', calleridton)
        # directory lookup : update chanprops
        return

    def userevent_localcall(self, chanprops, event):
        # for ChanSpy + XIVO_ORIGAPPLI + XIVO_ORIGACTIONID
        return

    def userevent_feature(self, chanprops, event):
        return

    def userevent_custom(self, chanprops, event):
        customname = event.get('NAME')
        # sheet alert
        return

    def userevent_dialplan2cti(self, chanprops, event):
        # why "UserEvent + dialplan2cti" and not "Newexten + Set" ?
        # - more selective
        # - variables declarations are not always done with Set (Read(), AGI(), ...)
        # - if there is a need for extra useful data (XIVO_USERID, ...)
        # - (future ?) multiple settings at once
        cti_varname = event.get('VARIABLE')
        dp_value = event.get('VALUE')
        chanprops.set_extra_data('dp', cti_varname, dp_value)
        return

    userevents = ['Feature',
                  'OutCall', 'Custom', 'LocalCall', 'dialplan2cti', 'LookupDirectory',
                  'User', 'Queue', 'Group','Meetme', 'Did',
                  ]

    def ami_userevent(self, event):
        eventname = event.pop('UserEvent')
        channel = event.pop('CHANNEL', None)
        # syntax in dialplan : exten = xx,n,UserEvent(myevent,var1: ${var1},var2: ${var2})
        chanprops = self.innerdata.channels.get(channel)
        if not chanprops:
            return
        if eventname in self.userevents:
            methodname = 'userevent_%s' % eventname.lower()
            if hasattr(self, methodname):
                self.log.info('ami_userevent %s %s : %s' % (eventname, channel, event))
                getattr(self, methodname)(chanprops, event)
        return

    def ami_agiexec(self, event):
        # occurs when there is a variable set
        command = event.pop('Command')
        commandid = event.pop('CommandId')
        channel = event.pop('Channel')
        subevent = event.pop('SubEvent')
        if subevent == 'End':
            resultcode = event.pop('ResultCode')
            # self.log.info('ami_agiexec %s %s %s' % (channel, resultcode, command))
        # command = 'VERBOSE "" 4'
        return

    def handle_fagi(self, fastagi):
        envdict = fastagi.env
        args = fastagi.args
        channel = envdict.pop('agi_channel')
        function = envdict.pop('agi_network_script')
        # syntax in dialplan : exten = xx,n,AGI(agi://ip:port/function,arg1,arg2)
        self.log.info('handle_fagi %s %s : %s' % (function, channel, args))
        return

    def ami_messagewaiting(self, event):
        old = event.pop('Old')
        new = event.pop('New')
        waiting = event.pop('Waiting')
        mailbox = event.pop('Mailbox')
        self.innerdata.voicemailupdate(mailbox, new, old, waiting)

    # Status replies events
    def ami_peerentry(self, event):
        ipaddress = event.pop('IPaddress')
        ipport = event.pop('IPport')
        if ipport != '0' and ipaddress != '-none-':
            channeltype = event.pop('Channeltype')
            objectname = event.pop('ObjectName')
            self.log.info('ami_peerentry %s:%s %s %s'
                     % (ipaddress, ipport, channeltype, objectname))
            # {u'Status': u'Unmonitored', u'ChanObjectType': u'peer', u'RealtimeDevice': u'no',
            # u'Dynamic': u'yes', u'TextSupport': u'no', u'ACL': u'no', u'VideoSupport': u'no',
            # u'Forcerport': u'no'}
        return

    def ami_registryentry(self, event):
        if log_ami_events_statusrequest:
            self.log.info('ami_registryentry %s' % (event))
            pass
        return

    def ami_parkedcallstatus(self, event):
        if log_ami_events_statusrequest:
            self.log.info('ami_parkedcallstatus %s' % (event))
        return

    def ami_meetmelist(self, event):
        # pseudochan = event.pop('PseudoChan') # Not in the Asterisk 1.8 event
        opts = { 'usernum': event['UserNumber'],
                 'admin': 'Yes' in event['Admin'],
                 'muted': 'No' not in event['Muted'],
                 'displayname': event['CallerIDName'],
                 'phonenumber': event['CallerIDNum'],
                 }
        return self.innerdata.meetmeupdate(event['Conference'],
                                           event['Channel'], opts)
        # we have no information about 'since when the channels are in the meetme room'
        # => see the by-channel information

    #    u'Talking': u'Not monitored',
    #    u'Muted': u'No',
    #    u'MarkedUser': u'No',
    #    u'Role': u'Talk and listen',

    def ami_status(self, event):
        if log_ami_events_statusrequest:
            self.log.info('ami_status %s' % (event))
        return

    def ami_coreshowchannel(self, event):
        event.pop('UniqueID')
        channel = event.pop('Channel')
        context = event.pop('Context')
        application = event.pop('Application')
        bridgedchannel = event.pop('BridgedChannel')
        state = event.pop('ChannelState')

        duration = event.pop('Duration')
        timestamp_start = self.timeconvert(duration)

        if log_ami_events_statusrequest:
            self.log.info('ami_coreshowchannel %s application=%s : %s' % (channel, application, event))

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
            self.log.info('ami_agents %s' % (event))
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
        # self.log.info('ami_queueparams %s : %s' % (queuename, event))
        return

    def ami_queuesummary(self, event):
        # self.log.info('ami_queuesummary %s' % (event))
        return

    def ami_queuemember(self, event):
        queuename = event.pop('Queue')
        membername = event.pop('Name')
        location = event.pop('Location')
        if location != membername:
            self.log.warning('ami_queuemember : %s and %s are not the same' (location, membername))

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
        if 'Extension' not in event:
            return
        extension = event.pop('Extension')
        if extension.isdigit():
            context = event.pop('Context')
            priority = event.pop('Priority')
            if priority == '1':
                actionid = 'exten:%s' % ''.join(random.sample(__alphanums__, 10))
                params = {
                    'mode' : 'extension',
                    'amicommand' : 'sendextensionstate',
                    'amiargs' : (extension, context)
                    }
                self.ctid.myami.get(self.ipbxid).execute_and_track(actionid, params)
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
        channel = event.pop('Channel')
        if channel in self.innerdata.channels:
            self.innerdata.channels.get(channel).properties['monitored'] = True
        self.log.info('ami_monitorstart %s %s' % (channel, event))
        return

    def ami_monitorstop(self, event):
        channel = event.pop('Channel')
        if channel in self.innerdata.channels:
            self.innerdata.channels.get(channel).properties['monitored'] = False
        self.log.info('ami_monitorstop %s %s' % (channel, event))
        return

    def ami_chanspystart(self, event):
        spyeechannel = event.pop('SpyeeChannel')
        spyerchannel = event.pop('SpyerChannel')
        # update spyer vs. spyee channels
        self.log.info('ami_chanspystart : %s spied by %s' % (spyeechannel, spyerchannel))
        return

    def ami_chanspystop(self, event):
        spyeechannel = event.pop('SpyeeChannel')
        # actually, we get here only once the spied channel has hangup
        self.log.info('ami_chanspystop %s spied by nobody' % spyeechannel)
        return

    # End of status requests
    def ami_peerlistcomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_peerlistcomplete %s' % (event))
        return
    def ami_parkedcallscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_parkedcallscomplete %s' % (event))
        return
    def ami_meetmelistcomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_meetmelistcomplete %s' % (event))
        return
    def ami_statuscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_statuscomplete %s' % (event))
        return
    def ami_agentscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_agentscomplete %s' % (event))
        return
    def ami_queuestatuscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_queuestatuscomplete %s' % (event))
        return
    def ami_queuesummarycomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_queuesummarycomplete %s' % (event))
        return
    def ami_coreshowchannelscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_coreshowchannelscomplete %s' % (event))
        return
    def ami_registrationscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_registrationscomplete %s' % (event))
        return
    def ami_showdialplancomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_showdialplancomplete %s' % (event))
        return
    def ami_dahdishowchannelscomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_dahdishowchannelscomplete %s' % (event))
        return
    def ami_voicemailuserentrycomplete(self, event):
        if log_ami_events_complete:
            self.log.info('ami_voicemailuserentrycomplete %s' % (event))
        return

    # receive this kind of events once DTMF has been exchanged between 2 SIP phones
    def ami_rtcpreceived(self, event):
        # self.log.info('ami_rtcpreceived %s' % (event))
        return
    def ami_rtcpsent(self, event):
        # self.log.info('ami_rtcpsent %s' % (event))
        return

    def ami_moduleloadreport(self, event):
        self.log.info('ami_moduleloadreport %s' % (event))
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
##    def ami_dahdishowchannels(self, event): return
##    def ami_dataget_tree(self, event): return
##    def ami_dbgetcomplete(self, event): return
##    def ami_dbgetresponse(self, event): return
##    def ami_deviceentry(self, event): return
##    def ami_devicelistcomplete(self, event): return
##    def ami_jabberevent(self, event): return
##    def ami_jabberstatus(self, event): return
##    def ami_lineentry(self, event): return
##    def ami_linelistcomplete(self, event): return
##    def ami_logchannel(self, event): return
##    def ami_mcid(self, event): return
##    def ami_minivoicemail(self, event): return
##    def ami_mobilestatus(self, event): return
##    def ami_newpeeraccount(self, event): return
##    def ami_placeholder(self, event): return
##    def ami_queuememberpenalty(self, event): return
##    def ami_spanalarm(self, event): return
##    def ami_spanalarmclear(self, event): return
##    def ami_waiteventcomplete(self, event): return

    # Responses
    def amiresponse_extensionstatus(self, event):
        exten = event.pop('Exten')
        context = event.pop('Context')
        hint = event.pop('Hint')
        status = event.pop('Status')
        if hint:
            # self.log.info('amiresponse_extensionstatus : %s %s %s %s' % (exten, context, hint, status))
            self.innerdata.updatehint(hint, status)
        return
