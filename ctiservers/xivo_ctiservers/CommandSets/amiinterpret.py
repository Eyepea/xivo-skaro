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
from xivo_ctiservers import xivo_commandsets
from xivo_ctiservers.xivo_commandsets import BaseCommand

log = logging.getLogger('xivocti1.8')

log_ami_events_statusrequest = False
log_ami_events_complete = False

class XivoCTICommand_asterisk_1_8(BaseCommand):
    xdname = 'XiVO CTI Server'
    def __init__(self, amilist, ctiports, queued_threads_pipe):
        BaseCommand.__init__(self)
        self.rename_stack = {}
        return

    def ami_fullybooted(self, astid, event):
        log.info('%s ami_fullybooted : %s' % (astid, event))
        return
    def ami_shutdown(self, astid, event):
        log.info('%s ami_shutdown : %s' % (astid, event))
        return
    def ami_channelreload(self, astid, event):
        # Occurs when there is a reload and the SIP config has changed
        log.info('%s ami_channelreload : %s' % (astid, event))
        return
    def ami_reload(self, astid, event):
        # Occurs when there is a reload and the CDR or Manager config has changed
        log.info('%s ami_reload : %s' % (astid, event))
        return
    def ami_registry(self, astid, event):
        # Occurs when there is a reload and the IAX config has changed and there is a registered trunk
        log.info('%s ami_registry : %s' % (astid, event))
        return


    # NewXXX events
    def ami_newstate(self, astid, event):
        # log.info('%s ami_newstate %s' % (astid, event))
        return
    def ami_newchannel(self, astid, event):
##        INFO:xivocti1.8:xivomine ami_newchannel {u'AccountCode': u'',
##                                                 u'Uniqueid': u'1290443189.17',
##                                                 u'ChannelState': u'0',
##                                                 u'Exten': u'',
##                                                 u'CallerIDNum': u'',
##                                                 u'Context': u'from-sip',
##                                                 u'CallerIDName': u'',
##                                                 u'Channel': u'SIP/zlosfbpeajsxrn-0000000b',
##                                                 u'ChannelStateDesc': u'Down'}
        log.info('%s ami_newchannel %s' % (astid, event))
        return
    def ami_newcallerid(self, astid, event):
        log.info('%s ami_newcallerid %s' % (astid, event))
        return
    def ami_newexten(self, astid, event):
        # log.info('%s ami_newexten %s' % (astid, event))
        return
    def ami_newaccountcode(self, astid, event):
        log.info('%s ami_newaccountcode %s' % (astid, event))
        return


    # Call events
    def ami_hangup(self, astid, event):
        log.info('%s ami_hangup %s' % (astid, event))
        return
    def ami_dial(self, astid, event):
##        INFO:xivocti1.8:xivomine ami_dial {u'Destination': u'SIP/zlosfbpeajsxrn-0000000e',
##                                           u'CallerIDNum': u'hpueygdepcqbew',
##                                           u'DestUniqueID': u'1290444059.21',
##                                           u'SubEvent': u'Begin',
##                                           u'Dialstring': u'zlosfbpeajsxrn',
##                                           u'UniqueID': u'1290444059.20',
##                                           u'CallerIDName': u'Hpueygd Epcqbew',
##                                           u'Channel': u'SIP/hpueygdepcqbew-0000000d'}

##        INFO:xivocti1.8:xivomine ami_dial {u'DialStatus': u'CONGESTION',
##                                           u'SubEvent': u'End',
##                                           u'UniqueID': u'1290444169.22',
##                                           u'Channel': u'SIP/hpueygdepcqbew-0000000f'}

##        INFO:xivocti1.8:xivomine ami_dial {u'DialStatus': u'CANCEL',
##                                           u'SubEvent': u'End',
##                                           u'UniqueID': u'1290443189.16',
##                                           u'Channel': u'SIP/hpueygdepcqbew-0000000a'}
        log.info('%s ami_dial %s' % (astid, event))
        return
    def ami_bridge(self, astid, event):
        log.info('%s ami_bridge %s' % (astid, event))
        return
    def ami_unlink(self, astid, event):
        log.info('%s ami_unlink %s' % (astid, event))
        return
    def ami_transfer(self, astid, event):
        log.info('%s ami_transfer %s' % (astid, event))
        return
    def ami_masquerade(self, astid, event):
        log.info('%s ami_masquerade %s' % (astid, event))
        return
    def ami_pickup(self, astid, event):
        log.info('%s ami_pickup %s' % (astid, event))
        return
    def ami_rename(self, astid, event):
        if astid not in self.rename_stack:
            self.rename_stack[astid] = {}

        if len(self.rename_stack[astid]) == 0:
            self.rename_stack[astid]['tomasq'] = event
        elif len(self.rename_stack[astid]) == 1:
            self.rename_stack[astid]['new'] = event
        elif len(self.rename_stack[astid]) == 2:
            self.rename_stack[astid]['new'] = event
            log.info('%s ami_rename %s' % (astid, self.rename_stack[astid]))
            self.rename_stack[astid] = {}
        return


    # Meetme events
    def ami_meetmeleave(self, astid, event):
        # log.info('%s ami_meetmeleave %s' % (astid, event))
        return
    def ami_meetmejoin(self, astid, event):
        # log.info('%s ami_meetmejoin %s' % (astid, event))
        return
    def ami_meetmeend(self, astid, event):
        # log.info('%s ami_meetmeend %s' % (astid, event))
        return


    # Queue and agents events
    def ami_join(self, astid, event):
        # log.info('%s ami_join %s' % (astid, event))
        return
    def ami_leave(self, astid, event):
        # log.info('%s ami_leave %s' % (astid, event))
        return
    def ami_queuememberstatus(self, astid, event):
        # log.info('%s ami_queuememberstatus %s' % (astid, event))
        return
    def ami_queuecallerabandon(self, astid, event):
        # log.info('%s ami_queuecallerabandon %s' % (astid, event))
        return

    def ami_agentcalled(self, astid, event):
        # log.info('%s ami_agentcalled %s' % (astid, event))
        return
    def ami_agentconnect(self, astid, event):
        # log.info('%s ami_agentconnect %s' % (astid, event))
        return
    def ami_agentcomplete(self, astid, event):
        # log.info('%s ami_agentcomplete %s' % (astid, event))
        return

    def ami_agentlogin(self, astid, event):
        # log.info('%s ami_agentlogin %s' % (astid, event))
        return
    def ami_agentlogoff(self, astid, event):
        # log.info('%s ami_agentlogoff %s' % (astid, event))
        return
    # XXX TODO handle former AgentCallBacklogin & logoff


    # Parking events
    def ami_parkedcall(self, astid, event):
        log.info('%s ami_parkedcall %s' % (astid, event))
        return
    def ami_unparkedcall(self, astid, event):
        # log.info('%s ami_unparkedcall %s' % (astid, event))
        return
    def ami_parkedcalltimeout(self, astid, event):
        # log.info('%s ami_parkedcalltimeout %s' % (astid, event))
        return
    def ami_parkedcallgiveup(self, astid, event):
        # log.info('%s ami_parkedcallgiveup %s' % (astid, event))
        return


    def ami_varset(self, astid, event):
        # log.info('%s ami_varset %s' % (astid, event))
        return
    def ami_peerstatus(self, astid, event):
        # log.info('%s ami_peerstatus %s' % (astid, event))
        return
    def ami_cdr(self, astid, event):
        # log.info('%s ami_cdr %s' % (astid, event))
        return
    def ami_dtmf(self, astid, event):
        # log.info('%s ami_dtmf %s' % (astid, event))
        return


    # Status replies events
    def ami_peerentry(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_peerentry %s' % (astid, event))
##        INFO:xivocti1.8:xivomine ami_peerentry {u'IPport': u'6103',
##                                                u'Status': u'Unmonitored',
##                                                u'ChanObjectType': u'peer',
##                                                u'ObjectName': u'zlosfbpeajsxrn',
##                                                u'RealtimeDevice': u'no',
##                                                u'Dynamic': u'yes',
##                                                u'TextSupport': u'no',
##                                                u'ACL': u'no',
##                                                u'ActionID': u'init-sippeers-jme6vDMkdE-1290444382',
##                                                u'VideoSupport': u'no',
##                                                u'Channeltype': u'SIP',
##                                                u'IPaddress': u'192.168.0.147',
##                                                u'Forcerport': u'no'}
        return
    def ami_parkedcallstatus(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_parkedcallstatus %s' % (astid, event))
        return
    def ami_meetmelist(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_meetmelist %s' % (astid, event))
        return
    def ami_status(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_status %s' % (astid, event))
        return
    def ami_agents(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_agents %s' % (astid, event))
        return
    def ami_queueparams(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_queueparams %s' % (astid, event))
        return
    def ami_queueentry(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_queueentry %s' % (astid, event))
        return
    def ami_queuemember(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_queuemember %s' % (astid, event))
        return
    def ami_queuesummary(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_queuesummary %s' % (astid, event))
        return
    def ami_coreshowchannel(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_coreshowchannel %s' % (astid, event))
        return
    def ami_registryentry(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_registryentry %s' % (astid, event))
        return
    def ami_listdialplan(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_listdialplan %s' % (astid, event))
        return
    # XXX dahdi channels
    def ami_voicemailuserentry(self, astid, event):
        if log_ami_events_statusrequest:
            log.info('%s ami_voicemailuserentry %s' % (astid, event))
        return


    # Monitor, Spy
    def ami_monitorstart(self, astid, event):
        log.info('%s ami_monitorstart %s' % (astid, event))
        return
    def ami_monitorstop(self, astid, event):
        log.info('%s ami_monitorstop %s' % (astid, event))
        return
    def ami_chanspystart(self, astid, event):
        log.info('%s ami_chanspystart %s' % (astid, event))
        return
    def ami_chanspystop(self, astid, event):
        log.info('%s ami_chanspystop %s' % (astid, event))
        return


    # End of status requests
    def ami_peerlistcomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_peerlistcomplete %s' % (astid, event))
        return
    def ami_parkedcallscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_parkedcallscomplete %s' % (astid, event))
        return
    def ami_meetmelistcomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_meetmelistcomplete %s' % (astid, event))
        return
    def ami_statuscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_statuscomplete %s' % (astid, event))
        return
    def ami_agentscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_agentscomplete %s' % (astid, event))
        return
    def ami_queuestatuscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_queuestatuscomplete %s' % (astid, event))
        return
    def ami_queuesummarycomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_queuesummarycomplete %s' % (astid, event))
        return
    def ami_coreshowchannelscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_coreshowchannelscomplete %s' % (astid, event))
        return
    def ami_registrationscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_registrationscomplete %s' % (astid, event))
        return
    def ami_showdialplancomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_showdialplancomplete %s' % (astid, event))
        return
    def ami_dahdishowchannelscomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_dahdishowchannelscomplete %s' % (astid, event))
        return
    def ami_voicemailuserentrycomplete(self, astid, event):
        if log_ami_events_complete:
            log.info('%s ami_voicemailuserentrycomplete %s' % (astid, event))
        return

    # receive this kind of events once DTMF has been exchanged between 2 SIP phones
    def ami_rtcpreceived(self, astid, event):
        # log.info('%s ami_rtcpreceived %s' % (astid, event))
        return
    def ami_rtcpsent(self, astid, event):
        # log.info('%s ami_rtcpsent %s' % (astid, event))
        return


    # Responses
    def amiresponse_success(self, astid, event, nocolon):
        return
    def amiresponse_error(self, astid, event, nocolon):
        return
    def amiresponse_follows(self, astid, event, nocolon):
        return

xivo_commandsets.CommandClasses['xivoctidummy'] = XivoCTICommand_asterisk_1_8
