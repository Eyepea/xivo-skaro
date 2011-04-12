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
import random
import string

log = logging.getLogger('cti_command')

COMPULSORY_LOGIN_ID = ['company', 'userid', 'ident',
                       'xivoversion', 'git_hash', 'git_date']

COMMANDS = [
    'login_id', 'login_pass', 'login_capas', 'logout',
    'getlist',
    'availstate', 'keepalive',

    'featuresget', 'featuresput',
    'directory',
    'history',
    'faxsend',
    'filetransfer',
    'chitchat',

    'callcampaign',
    'logfromclient',
    'getqueuesstats',
    'parking', 'meetme',
    'sheet', 'actionfiche',
    'ipbxcommand'
    ]

IPBXCOMMANDS = [
    'dial', 'autodial', 'hangupme', 'answer', 'refuse',
    'originate', 'intercept', 'park',
    'transfer', 'atxfer', 'transfercancel',
    'hangup',
    'sipnotify',

    'record', 'listen',

    'agentlogin', 'agentlogout',
    'agentpausequeue', 'agentunpausequeue'
    ]

XIVOVERSION_NUM = '1.2'
XIVOVERSION_NAME = 'skaro'
__alphanums__ = string.uppercase + string.lowercase + string.digits

class Command:
    def __init__(self, connection, thiscommand):
        self.connection = connection
        self.ctid = self.connection.ctid
        self.commanddict = thiscommand
        return

    def parse(self):
        self.command = self.commanddict.pop('class', None)
        self.commandid = self.commanddict.pop('commandid', None)
        self.onbehalf = self.commanddict.pop('onbehalf', None)
        # should reply with commandid and onbehalf if they have been provided

        self.ipbxid = self.connection.connection_details.get('ipbxid')
        self.userid = self.connection.connection_details.get('userid')
        self.innerdata = self.ctid.safe.get(self.ipbxid)

        # identifiers for the requester
        self.ripbxid = self.ipbxid
        self.ruserid = self.userid
        self.rinnerdata = self.ctid.safe.get(self.ripbxid)

        z = None
        if self.command in COMMANDS:

            if self.ripbxid:
                profileclient = self.rinnerdata.xod_config['users'].keeplist[self.ruserid].get('profileclient')
                profilespecs = self.ctid.cconf.getconfig('profiles').get(profileclient)
                regcommands_id = profilespecs.get('regcommands')
                regcommands = self.ctid.cconf.getconfig('regcommands').get(regcommands_id)
                if self.command not in regcommands:
                    log.warning('profile %s : unallowed command %s (intermediate %s)'
                                % (profileclient, self.command, regcommands_id))
                    return {}

            methodname = 'handle_%s' % self.command
            if hasattr(self, methodname):
                try:
                    z = getattr(self, methodname)()
                except Exception:
                    log.exception('calling %s' % methodname)
                    z = { }
            else:
                z = { 'warning' : { 'class' : 'ack',
                                    'classname' : self.command,
                                    'commandid' : self.commandid } }
                log.warning('no such method %s' % methodname)
        else:
            z = { 'warning' : { 'class' : 'ack',
                                'classname' : self.command,
                                'commandid' : self.commandid } }
            log.warning('unknown command %s' % self.command)
        return z

    def handle_login_id(self):
        missings = []
        for argum in COMPULSORY_LOGIN_ID:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            log.warning('missing args in loginparams : %s' % missings)
            return 'missing:%s' % ','.join(missings)

        # warns that the former session did not exit correctly (on a given computer)
        if 'lastlogout-stopper' in self.commanddict and 'lastlogout-datetime' in self.commanddict:
            if not self.commanddict['lastlogout-stopper'] or not self.commanddict['lastlogout-datetime']:
                log.warning('lastlogout userid=%s stopper=%s datetime=%s'
                            % (self.commanddict['userid'],
                               self.commanddict['lastlogout-stopper'],
                               self.commanddict['lastlogout-datetime']))

        # trivial checks (version, client kind) dealing with the software used
        xivoversion = self.commanddict.get('xivoversion')
        if xivoversion != XIVOVERSION_NUM:
            return 'xivoversion_client:%s;%s' % (xivoversion, XIVOVERSION_NUM)
        rcsversion = '%s-%s' % (self.commanddict.get('git_date'), self.commanddict.get('git_hash'))

        ident = self.commanddict.get('ident')
        whatsmyos = ident.split('-')[0]
        if whatsmyos.lower() not in ['x11', 'win', 'mac',
                                     'web', 'android', 'ios']:
            return 'wrong_client_os_identifier:%s' % whatsmyos

        # user match
        userinfo = None
        if self.commanddict.get('userid'):
            for ipbxid, saferef in self.ctid.safe.iteritems():
                userid = saferef.user_find(self.commanddict.get('userid'),
                                           self.commanddict.get('company'))
                if userid:
                    self.connection.connection_details.update({ 'ipbxid' : ipbxid,
                                                                'userid' : userid })
                    break

        if not self.connection.connection_details.get('userid'):
            return 'user_not_found'
        self.connection.connection_details['prelogin'] = {'cticlientos' : whatsmyos,
                                               'version' : rcsversion,
                                               'sessionid' : ''.join(random.sample(__alphanums__, 10))}
        reply = { 'action' : 'ok',
                  'dest' : 'me',
                  'message' : { 'class' : 'login_id_ok',
                                'xivoversion' : XIVOVERSION_NUM,
                                'version' : '7777',
                                'sessionid' : self.connection.connection_details['prelogin']['sessionid']
                                }
                  }
        return reply

    def handle_login_pass(self):
            # user authentication
            missings = []
            for argum in ['hashedpassword']:
                if argum not in self.commanddict:
                    missings.append(argum)
            if len(missings) > 0:
                log.warning('missing args in loginparams : %s' % ','.join(missings))
                return 'missing:%s' % ','.join(missings)

            this_hashed_password = self.commanddict.get('hashedpassword')

            ipbxid = self.connection.connection_details['ipbxid']
            userid = self.connection.connection_details['userid']
            sessionid = self.connection.connection_details['prelogin']['sessionid']

            ref_hashed_password = self.ctid.safe[ipbxid].user_get_hashed_password(userid, sessionid)
            if ref_hashed_password != this_hashed_password:
                return 'login_password'

##            iserr = self.__check_user_connection__(userinfo)
##            if iserr is not None:
##                return iserr

            reply = { 'action' : 'ok',
                      'dest' : 'me',
                      'message' : { 'class' : 'login_pass_ok',
                                    'capalist' : [self.ctid.safe[ipbxid].user_get_ctiprofile(userid)] },
                      }
            return reply

    def handle_login_capas(self):
            missings = []
            for argum in ['state', 'capaid', 'lastconnwins', 'loginkind']:
                if argum not in self.commanddict:
                    missings.append(argum)
            if len(missings) > 0:
                log.warning('missing args in loginparams : %s' % ','.join(missings))
                return 'missing:%s' % ','.join(missings)

            # settings (in agent mode for instance)
            # userinfo['agent']['phonenum'] = phonenum
            userinfo = self.connection.connection_details

            state = self.commanddict.get('state')
            capaid = self.commanddict.get('capaid')
            subscribe = self.commanddict.get('subscribe')
            lastconnwins = self.commanddict.get('lastconnwins')
            loginkind = self.commanddict.get('loginkind')

##            iserr = self.__check_capa_connection__(userinfo, capaid)
##            if iserr is not None:
##                return iserr

            self.__connect_user__(userinfo, state, capaid, lastconnwins)

##            if loginkind == 'agent':
##                userinfo['agentphonenumber'] = self.commanddict.get('agentphonenumber')
##            if subscribe is not None:
##                userinfo['subscribe'] = 0
##            return userinfo

            profileclient = self.innerdata.xod_config['users'].keeplist[self.userid].get('profileclient')
            profilespecs = self.ctid.cconf.getconfig('profiles').get(profileclient)

            capastruct = {}
            if profilespecs:
                for capakind in ['regcommands', 'ipbxcommands',
                                 'services', 'functions',
                                 'userstatus', 'phonestatus', 'channelstatus', 'agentstatus']:
                    if profilespecs.get(capakind):
                        tt = profilespecs.get(capakind)
                        cfg_capakind = self.ctid.cconf.getconfig(capakind)
                        if cfg_capakind:
                            details = cfg_capakind.get(tt)
                        else:
                            details = {}
                        capastruct[capakind] = details
                    else:
                        log.warning('no capakind %s in profilespecs %s'
                                    % (capakind, profilespecs.keys()))
            else:
                log.warning('empty profilespecs %s' % profilespecs)

            reply = {
                'action' : 'ok',
                'dest' : 'me',
                'message' : { 'class' : 'login_capas_ok',
                              'ipbxid' : self.ipbxid,
                              'userid' : self.userid,
                              # profile-specific data
                              'appliname' : profilespecs.get('name'),
                              'capaxlets' : profilespecs.get('xlets'),
                              'capas' : capastruct,
                              'presence' : 'available',
                              }
                }
            self.connection.logintimer.cancel()
            return reply

    def handle_logout(self):
        reply = {}
##                        stopper = icommand.struct.get('stopper')
##                        log.info('logout request from user:%s : stopper=%s' % (userid, stopper))
        return reply

## "capaxlets": ["customerinfo-dock-fcms", "dial-dock-fcms", "queues-dock-fcms"],
##  "presencecounter": {"connected": 1},
## "capafuncs": ["switchboard", "dial", "presence", "customerinfo", "agents", "conference", "directory", "features", "history", "fax", "chitchat", "database"],

    def __connect_user__(self, u, s, c, l):
        print u, s, c, l
        return

    # end of login/logout related commands


    def handle_callcampaign(self):
        reply = {}
        return reply

    def handle_chitchat(self):
        reply = {}
        to_userid = icommand.struct.get('to')
        to_userinfo = self.ulist_ng.keeplist[to_userid]
        message = icommand.struct.get('text')
        tosend = { 'class' : 'chitchat',
                   'from' : self.ruserid,
                   'text' : message }
        return reply

    def handle_meetme(self):
        function = icommand.struct.get('function')
        argums = icommand.struct.get('functionargs')
        if function == 'record' and len(argums) == 3 and argums[2] in ['start' , 'stop']:
                                castid = argums[0]
                                confno = argums[1]
                                command = argums[2]
                                chan = ''
                                validuid = ''
                                for uid, info in self.xod_config['meetme'][astid]. \
                                                 keeplist[confno]['uniqueids'].iteritems():
                                    if info['usernum'] == castid:
                                        chan = info['channel']
                                        validuid = uid
                                        break

                                roomname = self.xod_config['meetme'][astid].keeplist[confno]['roomname']
                                datestring = time.strftime('%Y%m%d-%H%M%S', time.localtime())
                                if argums[1] == "start":
                                    self.__ami_execute__(astid, "monitor", chan,
                                                         'cti-meetme-%s-%s' % (roomname, datestring))
                                else:
                                    self.__ami_execute__(astid, "stopmonitor", chan)

        elif function in ['MeetmePause']:
                                confno = argums[0]
                                status = argums[1]
                                roomname = self.xod_config['meetme'][astid].keeplist[confno]['roomname']
                                self.__ami_execute__(astid, 'sendcommand',
                                                     function, [('Meetme', '%s' % (roomname)),
                                                                ('status', '%s' % (status))])

        elif function in ['MeetmeKick', 'MeetmeAccept', 'MeetmeTalk']:
                                castid = argums[0]
                                confno = argums[1]
                                adminnum = self.xod_config['meetme'][astid].keeplist[confno]['adminnum']
                                roomname = self.xod_config['meetme'][astid].keeplist[confno]['roomname']
                                self.__ami_execute__(astid, 'sendcommand',
                                                     function, [('Meetme', '%s' % (roomname)),
                                                                ('Usernum', '%s' % (castid)),
                                                                ('Adminnum', '%s' % (adminnum[0]))])

        elif function in ['kick', 'mute', 'unmute']:
                                castid = argums[0]
                                confno = argums[1]
                                roomname = self.xod_config['meetme'][astid].keeplist[confno]['roomname']
                                self.__ami_execute__(astid, 'sendcommand',
                                                            'Command', [('Command', 'meetme %s %s %s' %
                                                                        (function, roomname, castid))])

        elif function == 'getlist':
                                fullstat = {}
                                for iastid, v in self.xod_config['meetme'].iteritems():
                                    fullstat[iastid] = v.keeplist
                                tosend = { 'class' : 'meetme',
                                           'function' : 'sendlist',
                                           'payload' : fullstat }
                                repstr = self.__cjson_encode__(tosend)

        return

    def handle_featuresget(self):
        reply = {}
        # if anything is done, requests the status for enable XXX from the user-lists
        return reply

    def handle_featuresput(self):
        reply = {}
        # XXX update the status through webservice
        return reply

    def handle_directory(self):
        reply = {}
        result = self.innerdata.getcustomers('maqsmaop', self.commanddict.get('pattern'))
        return reply

    def handle_history(self):
        reply = {}
        repstr = self.innerdata.gethistory(self.ruserid,
                                           self.commanddict.get('size'),
                                           self.commanddict.get('mode'),
                                           self.commanddict.get('morerecentthan'))
        return reply

    def handle_parking(self):
        reply = {}
        for ipbxid, pcalls in self.parkedcalls.iteritems():
            for parkingbay, pprops in pcalls.iteritems():
                tosend = { 'class' : 'parkcall',
                           'eventkind' : 'parkedcall',
                           'ipbxid' : ipbxid,
                           'parkingbay' : parkingbay,
                           'payload' : pprops }
                repstr = self.__cjson_encode__(tosend)
        return reply

    def handle_logfromclient(self):
        log.warning('logfromclient from user %s (level %s) : %s : %s'
                    % (self.ruserid,
                       self.commanddict.get('level'),
                       self.commanddict.get('classmethod'),
                       self.commanddict.get('message')))
        return

    def handle_keepalive(self):
        nbytes = self.commanddict.get('rate-bytes', -1)
        nmsec = self.commanddict.get('rate-msec', -1)
        nsamples = self.commanddict.get('rate-samples', -1)
        if nbytes > 0:
            if nmsec > 0:
                rate = float(nbytes) / nmsec
                log.info('keepalive from user:%s (%d %d/%d = %.1f bytes/ms)'
                         % (self.ruserid, nsamples, nbytes, nmsec, rate))
            else:
                log.info('keepalive from user:%s (%d %d/0 > %.1f bytes/ms)'
                         % (self.ruserid, nsamples, nbytes, float(nbytes)))
        return

    def handle_availstate(self):
        reply = {}
##                        if self.capas[capaid].match_funcs(ucapa, 'presence'):
##                            # updates the new status and sends it to other people
##                            repstr = self.__update_availstate__(userinfo, icommand.struct.get('availstate'))
##                            self.__presence_action__(astid, userinfo.get('agentid'), userinfo)
##                            self.__fill_user_ctilog__(userinfo, 'cticommand:%s' % classcomm)
        state = self.commanddict.get('availstate')
        self.rinnerdata.update_presence(self.ruserid, state)
        return reply

    def handle_getlist(self):
        reply = {}
        listname = self.commanddict.get('listname')
        function = self.commanddict.get('function')

        if function == 'listid':
            if listname in self.rinnerdata.xod_config:
                g = self.rinnerdata.xod_config[listname].keeplist.keys()
                reply = { 'action' : 'ok',
                          'dest' : 'me',
                          'message' : { 'class' : 'getlist',
                                        'function' : 'listid',
                                        'listname' : listname,
                                        'ipbxid' : self.ripbxid,
                                        'list' : g} }
                # print listname, self.rinnerdata.xod_config[listname].keeplist
            else:
                log.warning('no such list %s' % listname)

        elif function == 'updateconfig':
            rid = self.commanddict.get('id')
            g = self.rinnerdata.get_config(listname, rid)
            reply = { 'action' : 'ok',
                      'dest' : 'me',
                      'message' : { 'class' : 'getlist',
                                    'function' : 'updateconfig',
                                    'listname' : listname,
                                    'ipbxid' : self.ripbxid,
                                    'id' : rid,
                                    'config' : g} }

        elif function == 'updatestatus':
            rid = self.commanddict.get('id')
            g = self.rinnerdata.get_status(listname, rid)
            reply = { 'action' : 'ok',
                      'dest' : 'me',
                      'message' : { 'class' : 'getlist',
                                    'function' : 'updatestatus',
                                    'listname' : listname,
                                    'ipbxid' : self.ripbxid,
                                    'id' : rid,
                                    'status' : g} }
        return reply

    def handle_ipbxcommand(self):
        reply = {}
        self.ipbxcommand = self.commanddict.pop('command')
        if self.ipbxcommand not in IPBXCOMMANDS:
            log.warning('unknown ipbxcommand %s' % self.ipbxcommand)
            return reply
        profileclient = self.rinnerdata.xod_config['users'].keeplist[self.ruserid].get('profileclient')
        profilespecs = self.ctid.cconf.getconfig('profiles').get(profileclient)
        ipbxcommands_id = profilespecs.get('ipbxcommands')
        ipbxcommands = self.ctid.cconf.getconfig('ipbxcommands').get(ipbxcommands_id)
        if self.ipbxcommand not in ipbxcommands:
            log.warning('profile %s : unallowed ipbxcommand %s (intermediate %s)'
                        % (profileclient, self.ipbxcommand, ipbxcommands_id))
            return reply

        methodname = 'ipbxcommand_%s' % self.ipbxcommand

        # check whether ipbxcommand is in the users's profile capabilities
        if hasattr(self, methodname):
            z = getattr(self, methodname)()
        else:
            log.warning('no such ipbx method %s' % methodname)

        # if some actions have been requested ...
        if z:
            conn_ami = self.ctid.myami.get(self.ripbxid).amicl
            ipbxcmd = z.get('comm')
            if hasattr(conn_ami, ipbxcmd):
                conn_ami.actionid = ''.join(random.sample(__alphanums__, 10))
                log.info('method %s : starting ipbxcommand %s with actionid %s'
                         % (methodname, ipbxcmd, conn_ami.actionid))
                r = getattr(conn_ami, ipbxcmd)(* z.get('args'))
            else:
                log.warning('no such AMI command %s' % ipbxcmd)
        return reply












    def ipbxcommand_hangupme(self):
        return
    def ipbxcommand_dial(self):
        return

    # origination
    def ipbxcommand_originate(self):
        src = self.commanddict.get('source')
        dst = self.commanddict.get('destination')
        srcsplit = src.split(':', 1)
        dstsplit = dst.split(':', 1)

        [typesrc, whosrc] = srcsplit
        [typedst, whodst] = dstsplit

        rep = {'comm' : 'originate', 'args' : ['SIP', 'bmwgsjrponciuj', '1177', 'Kr',
                                                dstsplit[1], 'Wawa', 'from-sip']}
        return rep

        # others than 'user:special:me' should only be allowed to switchboard-like users
        if typesrc == 'user':
                if whosrc == 'special:me':
                    srcuinfo = userinfo
                else:
                    srcuinfo = self.ulist_ng.keeplist.get(whosrc)
                if srcuinfo is not None:
                    astid_src = srcuinfo.get('astid')
                    context_src = srcuinfo.get('context')
                    techdetails = srcuinfo.get('techlist')[0]
                    proto_src = techdetails.split('.')[0]
                    # XXXX 'local' might break the XIVO_ORIGSRCNUM mechanism (trick for thomson)
                    phonename_src = techdetails.split('.')[2]
                    phonenum_src = techdetails.split('.')[3]
                    ### srcuinfo.get('phonenum')
                    # if termlist empty + agentphonenumber not empty => call this one
                    cidname_src = srcuinfo.get('fullname')
            # 'agent:', 'queue:', 'group:', 'meetme:' ?
        elif typesrc == 'ext':
                context_src = userinfo['context']
                astid_src = userinfo['astid']
                proto_src = 'local'
                phonename_src = whosrc
                phonenum_src = whosrc
                cidname_src = whosrc
        else:
                log.warning('unknown typesrc <%s>' % typesrc)
                return

        # dst
        if typedst == 'ext':
                context_dst = context_src
                # this string will appear on the caller's phone, before he calls someone
                # for internal calls, one could solve the name of the called person,
                # but it could be misleading with an incoming call from the given person
                cidname_dst = whodst
                exten_dst = whodst
                # 'agent:', 'queue:', 'group:', 'meetme:' ?
        elif typedst == 'user':
                dstuinfo = None
                if whodst == 'special:me':
                    dstuinfo = userinfo
                elif whodst == 'special:myvoicemail':
                    context_dst = context_src
                    cidname_dst = '*98 (%s)' % self.xod_config['voicemail'][astid_src].keeplist[userinfo["voicemailid"]]["password"]
                    exten_dst = '*98'
                else:
                    dstuinfo = self.ulist_ng.keeplist[whodst]

                if dstuinfo is not None:
                    astid_dst = dstuinfo.get('astid')
                    exten_dst = dstuinfo.get('phonenum')
                    cidname_dst = dstuinfo.get('fullname')
                    context_dst = dstuinfo.get('context')
        else:
                log.warning('unknown typedst <%s>' % typedst)
                return

        if typesrc == typedst and typedst == 'ext' and len(whosrc) > 8 and len(whodst) > 8:
                log.warning('ORIGINATE : Trying to call two external phone numbers (%s and %s)'
                            % (whosrc, whodst))
                # this warning dates back to revision 6095 - maybe to avoid making arbitrary calls on behalf
                # of the local telephony system ?
                # let's keep the warning, without disabling the ability to do it ...

        try:
                if len(exten_dst) > 0:
                    ret = self.__ami_execute__(astid_src, AMI_ORIGINATE,
                                               proto_src, phonename_src, phonenum_src, cidname_src,
                                               exten_dst, cidname_dst,  context_dst,
                                               {'XIVO_USERID' : userinfo.get('xivo_userid')})
        except Exception:
                log.exception('unable to originate')

        return

    def ipbxcommand_sipnotify(self):
        if 'variables' in self.commanddict:
            variables = self.commanddict.get('variables')
        channel = self.commanddict.get('channel')
        if channel == 'user:special:me':
            uinfo = self.rinnerdata.xod_config['users'].keeplist[self.userid] 
            # TODO: Choose the appropriate line if more than one                 
            line = self.rinnerdata.xod_config['phones'].keeplist[uinfo['linelist'][0]]              
            channel = line['identity'].replace('\\','')       
        reply = {'comm': 'sipnotify', 'args': (channel, variables)}
        return reply

    # transfers
    def ipbxcommand_transferold(self):
        print self.ipbxcommand, self.commanddict
        srcsplit = src.split(':', 1)
        dstsplit = dst.split(':', 1)
        [typesrc, whosrc] = srcsplit
        [typedst, whodst] = dstsplit

        if typesrc == 'chan':
                if whosrc.startswith('special:me:'):
                    srcuinfo = userinfo
                    chan_src = whosrc[len('special:me:'):]
                else:
                    [uid, chan_src] = whosrc.split(':')
                    srcuinfo = self.ulist_ng.keeplist[uid]
                if srcuinfo is not None:
                    astid_src = srcuinfo.get('astid')
                    context_src = srcuinfo.get('context')
                    proto_src = 'local'
                    # phonename_src = srcuinfo.get('phonenum')
                    phonenum_src = srcuinfo.get('phonenum')
                    # if termlist empty + agentphonenumber not empty => call this one
                    cidname_src = srcuinfo.get('fullname')
        else:
                log.warning('unknown typesrc %s for %s' % (typesrc, commname))

        if typedst == 'ext':
                exten_dst = whodst
                if whodst == 'special:parkthecall':
                    for uid, vuid in self.uniqueids[astid_src].iteritems():
                        if 'dial' in vuid and vuid['dial'] == chan_src and 'channel' in vuid:
                            nchan = vuid['channel']
                        if 'link' in vuid and vuid['link'] == chan_src and 'channel' in vuid:
                            nchan = vuid['channel']
                    chan_park = nchan
                    #exten_dst = '700'   # cheat code !
                    #chan_src = nchan    # cheat code !
        elif typedst == 'user':
                if whodst == 'special:me':
                    dstuinfo = userinfo
                else:
                    dstuinfo = self.ulist_ng.keeplist[whodst]
                if dstuinfo is not None:
                    astid_dst = dstuinfo.get('astid')
                    exten_dst = dstuinfo.get('phonenum')
                    cidname_dst = dstuinfo.get('fullname')
                    context_dst = dstuinfo.get('context')
        elif typedst == 'voicemail':
                if whodst == 'special:me':
                    dstuinfo = userinfo
                else:
                    dstuinfo = self.ulist_ng.keeplist[whodst]

                if dstuinfo.get('voicemailid'):
                    voicemail_id = dstuinfo['voicemailid']
                    self.__ami_execute__(astid_src, 'setvar', 'XIVO_VMBOXID', voicemail_id, chan_src)
                    exten_dst = 's'
                    context_src = 'macro-voicemail'
                else:
                    log.warning('no voicemail allowed or defined for %s' % dstuinfo)
        else:
                log.warning('unknown typedst %s for %s' % (typedst, commname))

        # print astid_src, commname, chan_src, exten_dst, context_src
        ret = False
        try:
                # cheat code !
                if whodst == 'special:parkthecall':
                    ret = self.__ami_execute__(astid_src, 'park', chan_park, chan_src)
                else:
                    if exten_dst:
                        ret = self.__ami_execute__(astid_src, commname,
                                                   chan_src,
                                                   exten_dst, context_src)
        except Exception:
                log.exception('unable to %s' % commname)
        return

    def ipbxcommand_park(self):
        rep = {}
        src = self.commanddict.get('source')
        srcsplit = src.split(':', 1)
        [typesrc, whosrc] = srcsplit
        if typesrc not in ['chan']:
            log.warning('unallowed typesrc %s for %s' % (typesrc, self.ipbxcommand))
            return

        [ipbxid, channel] = whosrc.split('/', 1)
        print self.ctid.safe.get(ipbxid).channels.keys()
        peerchannel = self.ctid.safe.get(ipbxid).channels.get(channel).peerchannel
        rep = {'comm' : 'park', 'args' : [channel, peerchannel]}
        return rep

    def ipbxcommand_transfer(self):
        rep = {}
        src = self.commanddict.get('source')
        dst = self.commanddict.get('destination')
        srcsplit = src.split(':', 1)
        dstsplit = dst.split(':', 1)
        [typesrc, whosrc] = srcsplit
        [typedst, whodst] = dstsplit
        if typesrc not in ['chan']:
            log.warning('unallowed typesrc %s for %s' % (typesrc, self.ipbxcommand))
            return
        if typedst not in ['user', 'ext', 'phone']:
            log.warning('unallowed typedst %s for %s' % (typedst, self.ipbxcommand))
            return

        [ipbxid, channel] = whosrc.split('/', 1)
        if typedst == 'user':
            rep = {'comm' : 'transfer', 'args' : [channel, '1431', 'from-sip']}
        return rep

    def ipbxcommand_atxfer(self):
        rep = {}
        src = self.commanddict.get('source')
        dst = self.commanddict.get('destination')
        srcsplit = src.split(':', 1)
        dstsplit = dst.split(':', 1)
        [typesrc, whosrc] = srcsplit
        [typedst, whodst] = dstsplit
        if typesrc not in ['chan']:
            log.warning('unallowed typesrc %s for %s' % (typesrc, self.ipbxcommand))
            return
        if typedst not in ['user', 'ext', 'phone']:
            log.warning('unallowed typedst %s for %s' % (typedst, self.ipbxcommand))
            return

        [ipbxid, channel] = whosrc.split('/', 1)
        if typedst == 'user':
            rep = {'comm' : 'atxfer', 'args' : [channel, '1431', 'from-sip']}
        return rep


    # old stuff, kept there for record XXXX
    def tt():
        if whosrc.startswith('special:me:'):
            srcuinfo = userinfo
            chan_src = whosrc[len('special:me:'):]
        else:
            [uid, chan_src] = whosrc.split(':')
            srcuinfo = self.ulist_ng.keeplist[uid]
            if srcuinfo is not None:
                    astid_src = srcuinfo.get('astid')
                    context_src = srcuinfo.get('context')
                    proto_src = 'local'
                    # phonename_src = srcuinfo.get('phonenum')
                    phonenum_src = srcuinfo.get('phonenum')
                    # if termlist empty + agentphonenumber not empty => call this one
                    cidname_src = srcuinfo.get('fullname')
            else:
                log.warning('unknown typesrc %s for %s' % (typesrc, commname))

        if typedst == 'ext':
                exten_dst = whodst
                if whodst == 'special:parkthecall':
                    for uid, vuid in self.uniqueids[astid_src].iteritems():
                        if 'dial' in vuid and vuid['dial'] == chan_src and 'channel' in vuid:
                            nchan = vuid['channel']
                        if 'link' in vuid and vuid['link'] == chan_src and 'channel' in vuid:
                            nchan = vuid['channel']
                    chan_park = nchan
                    #exten_dst = '700'   # cheat code !
                    #chan_src = nchan    # cheat code !
        elif typedst == 'user':
                if whodst == 'special:me':
                    dstuinfo = userinfo
                else:
                    dstuinfo = self.ulist_ng.keeplist[whodst]
                if dstuinfo is not None:
                    astid_dst = dstuinfo.get('astid')
                    exten_dst = dstuinfo.get('phonenum')
                    cidname_dst = dstuinfo.get('fullname')
                    context_dst = dstuinfo.get('context')
        elif typedst == 'voicemail':
                if whodst == 'special:me':
                    dstuinfo = userinfo
                else:
                    dstuinfo = self.ulist_ng.keeplist[whodst]

                if dstuinfo.get('voicemailid'):
                    voicemail_id = dstuinfo['voicemailid']
                    self.__ami_execute__(astid_src, 'setvar', 'XIVO_VMBOXID', voicemail_id, chan_src)
                    exten_dst = 's'
                    context_src = 'macro-voicemail'
                else:
                    log.warning('no voicemail allowed or defined for %s' % dstuinfo)
        else:
                log.warning('unknown typedst %s for %s' % (typedst, commname))

        # print astid_src, commname, chan_src, exten_dst, context_src
        ret = False
        try:
                # cheat code !
                if whodst == 'special:parkthecall':
                    ret = self.__ami_execute__(astid_src, 'park', chan_park, chan_src)
                else:
                    if exten_dst:
                        ret = self.__ami_execute__(astid_src, commname,
                                                   chan_src,
                                                   exten_dst, context_src)
        except Exception:
                log.exception('unable to %s' % commname)
        return

    def ipbxcommand_transfercancel(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_intercept(self):
        print self.ipbxcommand, self.commanddict
        return

    # hangup and one's own line management
    def ipbxcommand_hangup(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_answer(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_cancel(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_refuse(self):
        print self.ipbxcommand, self.commanddict
        return

    # agents and queues
    def ipbxcommand_agentlogin(self):
        print self.ipbxcommand, self.commanddict
        return {'comm' : 'agentlogin', 'args' : ['a', 'b', 'c']}

    def ipbxcommand_agentlogout(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_agentjoinqueue(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_agentleavequeue(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_agentpausequeue(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_agentunpausequeue(self):
        print self.ipbxcommand, self.commanddict
        return

    # record, listen actions
    def ipbxcommand_recordstart(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_recordstop(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_listenstart(self):
        print self.ipbxcommand, self.commanddict
        return
    def ipbxcommand_listenstop(self):
        print self.ipbxcommand, self.commanddict
        return
