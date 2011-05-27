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
from xivo_ctiservers import xivo_webservices

log = logging.getLogger('cti_command')

COMPULSORY_LOGIN_ID = ['company', 'userlogin', 'ident',
                       'xivoversion', 'git_hash', 'git_date']

REGCOMMANDS = [
    'login_id', 'login_pass', 'login_capas', 'logout',
    'getlist',

    'getipbxlist',
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
        self.othermessages = list()
        return

    def parse(self):
        self.command = self.commanddict.pop('class', None)
        self.commandid = self.commanddict.pop('commandid', None)

        self.ipbxid = self.connection.connection_details.get('ipbxid')
        self.userid = self.connection.connection_details.get('userid')
        self.innerdata = self.ctid.safe.get(self.ipbxid)

        # identifiers for the requester
        self.ripbxid = self.commanddict.get('ipbxid', self.ipbxid)
        self.ruserid = self.commanddict.get('userid', self.userid)
        self.rinnerdata = self.ctid.safe.get(self.ripbxid)

        # identifiers for the requested
        self.tipbxid = self.commanddict.get('tipbxid', self.ipbxid)
        self.tinnerdata = self.ctid.safe.get(self.tipbxid)

        messagebase = { 'class' : self.command }
        if self.commandid:
            messagebase['replyid'] = self.commandid

        if self.command in REGCOMMANDS:
            if self.ripbxid:
                regcommands = self.rinnerdata.get_user_permissions('regcommands', self.ruserid)
                if regcommands:
                    if self.command not in regcommands:
                        log.warning('user %s/%s : unallowed command %s'
                                    % (self.ripbxid, self.ruserid, self.command))
                        messagebase['warning_string'] = 'unallowed'
                else:
                    log.warning('user %s/%s : unallowed command %s - empty regcommands'
                                % (self.ripbxid, self.ruserid, self.command))
                    messagebase['warning_string'] = 'no_regcommands'

            methodname = 'regcommand_%s' % self.command
            if hasattr(self, methodname) and 'warning_string' not in messagebase:
                try:
                    ztmp = getattr(self, methodname)()
                    if ztmp is None:
                        messagebase['warning_string'] = 'return_is_none'
                    elif isinstance(ztmp, str):
                        messagebase['error_string'] = ztmp
                    else:
                        messagebase.update(ztmp)
                except Exception:
                    log.exception('calling %s' % methodname)
                    messagebase['warning_string'] = 'exception'
            else:
                log.warning('no such method %s' % methodname)
                messagebase['warning_string'] = 'unimplemented'
        else:
            log.warning('unknown command %s' % self.command)
            messagebase['warning_string'] = 'unknown'

        ackmessage = { 'message' : messagebase }
        if 'error_string' in messagebase:
            ackmessage['closemenow'] = True

        z = [ackmessage]
        for extramessage in self.othermessages:
            bmsg = extramessage.get('message')
            bmsg['class'] = self.command
            z.append( { 'dest' : extramessage.get('dest'),
                        'message' : bmsg } )
        return z

    def regcommand_login_id(self):
        head = '%s:%d - LOGINFAIL - login_id' % (self.connection.requester)
        missings = []
        for argum in COMPULSORY_LOGIN_ID:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            log.warning('%s - missing args - %s' % (head, missings))
            return 'missing:%s' % ','.join(missings)

        # warns that the former session did not exit correctly (on a given computer)
        if 'lastlogout-stopper' in self.commanddict and 'lastlogout-datetime' in self.commanddict:
            if not self.commanddict['lastlogout-stopper'] or not self.commanddict['lastlogout-datetime']:
                log.warning('lastlogout userlogin=%s stopper=%s datetime=%s'
                            % (self.commanddict['userlogin'],
                               self.commanddict['lastlogout-stopper'],
                               self.commanddict['lastlogout-datetime']))

        # trivial checks (version, client kind) dealing with the software used
        xivoversion = self.commanddict.get('xivoversion')
        if xivoversion != XIVOVERSION_NUM:
            log.warning('%s - wrong XiVO major version : %s' % (head, xivoversion))
            return 'xivoversion_client:%s;%s' % (xivoversion, XIVOVERSION_NUM)
        rcsversion = '%s-%s' % (self.commanddict.get('git_date'), self.commanddict.get('git_hash'))

        ident = self.commanddict.get('ident')
        whatsmyos = ident.split('-')[0]
        if whatsmyos.lower() not in ['x11', 'win', 'mac',
                                     'ctiserver',
                                     'web', 'android', 'ios']:
            log.warning('%s - wrong OS identifier : %s' % (head, ident))
            return 'wrong_client_os_identifier:%s' % whatsmyos

        # user match
        if self.commanddict.get('userlogin'):
            ipbxid = self.ctid.myipbxid
            saferef = self.ctid.safe.get(ipbxid)
            log.info('searching user %s in %s'
                     % (self.commanddict.get('userlogin'), ipbxid))
            userid = saferef.user_find(self.commanddict.get('userlogin'),
                                       self.commanddict.get('company'))
            if userid:
                self.connection.connection_details.update({ 'ipbxid' : ipbxid,
                                                            'userid' : userid })

        if not self.connection.connection_details.get('userid'):
            log.warning('%s - unknown login : %s' % (head, self.commanddict.get('userlogin')))
            # do not give a hint that the login might be good or wrong
            # since this is the first part of the handshake, we shall anyway proceed "as if"
            # until the password step, before sending a "wrong password" message ...

        self.connection.connection_details['prelogin'] = {
            'cticlientos' : whatsmyos,
            'version' : rcsversion,
            'sessionid' : ''.join(random.sample(__alphanums__, 10))
            }

        reply = { 'xivoversion' : XIVOVERSION_NUM,
                  'version' : '7777',
                  'sessionid' : self.connection.connection_details['prelogin']['sessionid']
                  }
        return reply


    def regcommand_login_pass(self):
        head = '%s:%d - LOGINFAIL - login_pass' % (self.connection.requester)
        # user authentication
        missings = []
        for argum in ['hashedpassword']:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            log.warning('%s - missing args : %s' % (head, missings))
            return 'missing:%s' % ','.join(missings)

        this_hashed_password = self.commanddict.get('hashedpassword')
        cdetails = self.connection.connection_details

        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        sessionid = cdetails.get('prelogin').get('sessionid')

        if ipbxid and userid:
            ref_hashed_password = self.ctid.safe[ipbxid].user_get_hashed_password(userid, sessionid)
            if ref_hashed_password != this_hashed_password:
                log.warning('%s - wrong hashed password' % head)
                return 'login_password'
        else:
            log.warning('%s - undefined user : probably the login_id step failed' % head)
            return 'login_password'

        reply = { 'capalist' : [self.ctid.safe[ipbxid].user_get_ctiprofile(userid)] }
        return reply

    def regcommand_login_capas(self):
        head = '%s:%d - LOGINFAIL - login_capas' % (self.connection.requester)
        missings = []
        for argum in ['state', 'capaid', 'lastconnwins', 'loginkind']:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            log.warning('%s - missing args : %s' % (head, missings))
            return 'missing:%s' % ','.join(missings)

        # settings (in agent mode for instance)
        # userinfo['agent']['phonenum'] = phonenum
        cdetails = self.connection.connection_details

        state = self.commanddict.get('state')
        capaid = self.commanddict.get('capaid')
        subscribe = self.commanddict.get('subscribe')
        lastconnwins = self.commanddict.get('lastconnwins')
        loginkind = self.commanddict.get('loginkind')

        iserr = self.__check_capa_connection__(capaid)
        if iserr is not None:
            log.warning('%s - wrong capaid : %s %s' % (head, iserr, capaid))
            return iserr

        iserr = self.__check_user_connection__()
        if iserr is not None:
            log.warning('%s - user connection : %s' % (head, iserr))
            return iserr

        self.__connect_user__(state, capaid)
        head = '%s:%d - LOGIN SUCCESSFUL' % (self.connection.requester)
        log.info('%s for %s' % (head, cdetails))

##            if loginkind == 'agent':
##                userinfo['agentphonenumber'] = self.commanddict.get('agentphonenumber')
##            if subscribe is not None:
##                userinfo['subscribe'] = 0
##            return userinfo

        profileclient = self.innerdata.xod_config['users'].keeplist[self.userid].get('profileclient')
        profilespecs = self.ctid.cconf.getconfig('profiles').get(profileclient)

        capastruct = {}
        summarycapas = {}
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
                    if details:
                        summarycapas[capakind] = tt
                else:
                    capastruct[capakind] = {}
                    # log.warning('no capakind %s in profilespecs %s' % (capakind, profilespecs.keys()))
        else:
            log.warning('empty profilespecs %s' % profilespecs)

        reply = { 'ipbxid' : self.ipbxid,
                  'userid' : self.userid,
                  # profile-specific data
                  'appliname' : profilespecs.get('name'),
                  'capaxlets' : profilespecs.get('xlets'),
                  'capas' : capastruct,
                  'presence' : 'available',
                  }

        self.connection.logintimer.cancel()
        return reply

    def regcommand_logout(self):
        reply = {}
##                        stopper = icommand.struct.get('stopper')
##                        log.info('logout request from user:%s : stopper=%s' % (userid, stopper))
        return reply

## "capaxlets": ["customerinfo-dock-fcms", "dial-dock-fcms", "queues-dock-fcms"],
##  "presencecounter": {"connected": 1},
## "capafuncs": ["switchboard", "dial", "presence", "customerinfo", "agents", "conference", "directory", "features", "history", "fax", "chitchat", "database"],

    def __check_user_connection__(self):
        cdetails = self.connection.connection_details
        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        # if self.ctid.safe[ipbxid].xod_status['users'][userid]['connection'] == 'yes':
        # return 'alreadythere'
        return

    def __check_capa_connection__(self, capaid):
        cdetails = self.connection.connection_details
        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        if capaid not in self.ctid.cconf.getconfig('profiles').keys():
            return 'unknownprofile'
        if capaid != self.ctid.safe[ipbxid].xod_config['users'].keeplist[userid]['profileclient']:
            return 'wrongprofile'
        # XXX : too much users ?
        return

    def __connect_user__(self, availstate, c):
        cdetails = self.connection.connection_details
        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        self.ctid.safe[ipbxid].xod_status['users'][userid]['connection'] = 'yes'
        self.ctid.safe[ipbxid].update_presence(userid, availstate)
        # connection : os, version, sessionid, socket data, capaid
        # {'prelogin': {'cticlientos': 'X11', 'version': '1305641743-87aa765', 'sessionid': 'deyLicgThU'}}
        return

    def __disconnect_user__(self):
        cdetails = self.connection.connection_details
        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        self.ctid.safe[ipbxid].xod_status['users'][userid]['connection'] = None
        # disconnected vs. invisible vs. recordstatus ?
        self.ctid.safe[ipbxid].update_presence(userid, availstate)
        return

    # end of login/logout related commands


    def regcommand_callcampaign(self):
        reply = {}
        return reply

    def regcommand_chitchat(self):
        reply = {}
        (ipbxid, userid) = self.commanddict.get('to').split('/')
        chitchattext = self.commanddict.get('text')
        self.othermessages.append( {'dest' : self.commanddict.get('to'),
                                    'message' : { 'to' : self.commanddict.get('to'),
                                                  'from' : '%s/%s' % (self.ripbxid, self.ruserid),
                                                  'text' : chitchattext}} )
        return reply

    def regcommand_meetme(self):
        print 'regcommand_meetme', self.commanddict, self.userid, self.ruserid
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

    def regcommand_featuresget(self):
        reply = {}
        z = xivo_webservices.xws(self.ctid.cconf.ipwebs, 443)
        z.connect()
        services = z.serviceget(self.ruserid)
        z.close()
        reply = { 'userfeatures' : services.get('userfeatures') }
        return reply

    def regcommand_featuresput(self):
        reply = {}
        print 'regcommand_featuresput', self.commanddict, self.userid, self.ruserid
        z = xivo_webservices.xws(self.ctid.cconf.ipwebs, 443)
        z.connect()
        z.serviceput(self.ruserid, self.commanddict.get('function'), self.commanddict.get('value'))
        z.close()
        return reply

    def regcommand_directory(self):
        reply = {}
        result = self.rinnerdata.getcustomers('maqsmaop', self.commanddict.get('pattern'))
        return reply

    def regcommand_history(self):
        reply = {}
        repstr = self.innerdata.gethistory(self.ruserid,
                                           self.commanddict.get('size'),
                                           self.commanddict.get('mode'),
                                           self.commanddict.get('morerecentthan'))
        return reply

    def regcommand_parking(self):
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

    def regcommand_logfromclient(self):
        log.warning('logfromclient from user %s (level %s) : %s : %s'
                    % (self.ruserid,
                       self.commanddict.get('level'),
                       self.commanddict.get('classmethod'),
                       self.commanddict.get('message')))
        return

    def regcommand_keepalive(self):
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

    def regcommand_availstate(self):
        reply = {}
        # if self.capas[capaid].match_funcs(ucapa, 'presence'):
        # self.__fill_user_ctilog__(userinfo, 'cticommand:%s' % classcomm)
        availstate = self.commanddict.get('availstate')
        self.rinnerdata.update_presence(self.ruserid, availstate)
        return reply

    def regcommand_getipbxlist(self):
        reply = { 'ipbxlist' : self.ctid.cconf.getconfig('ipbxes').keys() }
        return reply

    def regcommand_getlist(self):
        reply = {}
        listname = self.commanddict.get('listname')
        function = self.commanddict.get('function')

        if function == 'listid':
            if listname in self.tinnerdata.xod_config:
                g = list()
                for gg in self.tinnerdata.xod_config[listname].keeplist.keys():
                    if gg.isdigit():
                        # there could be other criteria, this one is to prevent displaying
                        # the account for remote cti servers
                        g.append(gg)
                reply = { 'function' : 'listid',
                          'listname' : listname,
                          'tipbxid' : self.tipbxid,
                          'list' : g }
            else:
                log.warning('no such list %s' % listname)

        elif function == 'updateconfig':
            tid = self.commanddict.get('tid')
            g = self.tinnerdata.get_config(listname, tid)
            reply = { 'function' : 'updateconfig',
                      'listname' : listname,
                      'tipbxid' : self.tipbxid,
                      'tid' : tid,
                      'config' : g }

        elif function == 'updatestatus':
            tid = self.commanddict.get('tid')
            g = self.tinnerdata.get_status(listname, tid)
            reply = { 'function' : 'updatestatus',
                      'listname' : listname,
                      'tipbxid' : self.tipbxid,
                      'tid' : tid,
                      'status' : g }

        return reply

    def regcommand_ipbxcommand(self):
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
