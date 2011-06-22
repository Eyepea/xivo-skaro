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
import threading
import time
from xivo_ctiservers import xivo_webservices

COMPULSORY_LOGIN_ID = ['company', 'userlogin', 'ident',
                       'xivoversion', 'git_hash', 'git_date']

LOGINCOMMANDS = [
    'login_id', 'login_pass', 'login_capas'
    ]

REGCOMMANDS = [
    'logout',
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
    'sheet',
    'actionfiche',

    'ipbxcommand'
    ]

IPBXCOMMANDS = [
    'dial', 'hangupme',
    'answer', 'refuse', 'cancel',
    'originate', 'intercept',
    'parking',
    'transfer', 'atxfer', 'transfercancel',
    'hangup',
    'sipnotify',

    'meetme',
    'record',
    'listen',

    'agentlogin', 'agentlogout',
    'agentjoinqueue', 'agentleavequeue',
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
        self.log = logging.getLogger('cti_command(%s:%d)' % self.connection.requester)
        return

    def parse(self):
        self.command = self.commanddict.get('class', None)
        self.commandid = self.commanddict.get('commandid', None)

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

        if self.command in REGCOMMANDS and not self.connection.connection_details.get('logged'):
            messagebase['error_string'] = 'notloggedyet'

        elif self.command in LOGINCOMMANDS or self.command in REGCOMMANDS:
            if self.ripbxid:
                regcommands = self.rinnerdata.get_user_permissions('regcommands', self.ruserid)
                if regcommands:
                    if self.command not in regcommands:
                        self.log.warning('user %s/%s : unallowed command %s'
                                         % (self.ripbxid, self.ruserid, self.command))
                        messagebase['warning_string'] = 'unallowed'
                else:
                    self.log.warning('user %s/%s : unallowed command %s - empty regcommands'
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
                    self.log.exception('calling %s' % methodname)
                    messagebase['warning_string'] = 'exception'
            else:
                self.log.warning('no such method %s' % methodname)
                messagebase['warning_string'] = 'unimplemented'
        else:
            self.log.warning('unknown command %s' % self.command)
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
        head = 'LOGINFAIL - login_id'
        missings = []
        for argum in COMPULSORY_LOGIN_ID:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            self.log.warning('%s - missing args - %s' % (head, missings))
            return 'missing:%s' % ','.join(missings)

        # warns that the former session did not exit correctly (on a given computer)
        if 'lastlogout-stopper' in self.commanddict and 'lastlogout-datetime' in self.commanddict:
            if not self.commanddict['lastlogout-stopper'] or not self.commanddict['lastlogout-datetime']:
                self.log.warning('lastlogout userlogin=%s stopper=%s datetime=%s'
                            % (self.commanddict['userlogin'],
                               self.commanddict['lastlogout-stopper'],
                               self.commanddict['lastlogout-datetime']))

        # trivial checks (version, client kind) dealing with the software used
        xivoversion = self.commanddict.get('xivoversion')
        if xivoversion != XIVOVERSION_NUM:
            self.log.warning('%s - wrong XiVO major version : %s' % (head, xivoversion))
            return 'xivoversion_client:%s;%s' % (xivoversion, XIVOVERSION_NUM)
        rcsversion = '%s-%s' % (self.commanddict.get('git_date'), self.commanddict.get('git_hash'))

        ident = self.commanddict.get('ident')
        whatsmyos = ident.split('-')[0]
        if whatsmyos.lower() not in ['x11', 'win', 'mac',
                                     'ctiserver',
                                     'web', 'android', 'ios']:
            self.log.warning('%s - wrong OS identifier : %s' % (head, ident))
            return 'wrong_client_os_identifier:%s' % whatsmyos

        # user match
        if self.commanddict.get('userlogin'):
            ipbxid = self.ctid.myipbxid
            saferef = self.ctid.safe.get(ipbxid)
            self.log.info('searching user %s in %s'
                     % (self.commanddict.get('userlogin'), ipbxid))
            userid = saferef.user_find(self.commanddict.get('userlogin'),
                                       self.commanddict.get('company'))
            if userid:
                self.connection.connection_details.update({ 'ipbxid' : ipbxid,
                                                            'userid' : userid })

        if not self.connection.connection_details.get('userid'):
            self.log.warning('%s - unknown login : %s' % (head, self.commanddict.get('userlogin')))
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
        head = 'LOGINFAIL - login_pass'
        # user authentication
        missings = []
        for argum in ['hashedpassword']:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            self.log.warning('%s - missing args : %s' % (head, missings))
            return 'missing:%s' % ','.join(missings)

        this_hashed_password = self.commanddict.get('hashedpassword')
        cdetails = self.connection.connection_details

        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        sessionid = cdetails.get('prelogin').get('sessionid')

        if ipbxid and userid:
            ref_hashed_password = self.ctid.safe[ipbxid].user_get_hashed_password(userid, sessionid)
            if ref_hashed_password != this_hashed_password:
                self.log.warning('%s - wrong hashed password' % head)
                return 'login_password'
        else:
            self.log.warning('%s - undefined user : probably the login_id step failed' % head)
            return 'login_password'

        reply = { 'capalist' : [self.ctid.safe[ipbxid].user_get_ctiprofile(userid)] }
        return reply

    def regcommand_login_capas(self):
        head = 'LOGINFAIL - login_capas'
        missings = []
        for argum in ['state', 'capaid', 'lastconnwins', 'loginkind']:
            if argum not in self.commanddict:
                missings.append(argum)
        if len(missings) > 0:
            self.log.warning('%s - missing args : %s' % (head, missings))
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
            self.log.warning('%s - wrong capaid : %s %s' % (head, iserr, capaid))
            return iserr

        iserr = self.__check_user_connection__()
        if iserr is not None:
            self.log.warning('%s - user connection : %s' % (head, iserr))
            return iserr

        self.__connect_user__(state, capaid)
        head = 'LOGIN SUCCESSFUL'
        self.log.info('%s for %s' % (head, cdetails))

        if self.userid.startswith('cs:'):
            notifyremotelogin = threading.Timer(2, self.ctid.cb_timer,
                                                ({'action' : 'xivoremote',
                                                  'properties' : None },))
            notifyremotelogin.setName('Thread-xivo-%s' % self.userid)
            notifyremotelogin.start()

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
                    # self.log.warning('no capakind %s in profilespecs %s' % (capakind, profilespecs.keys()))
        else:
            self.log.warning('empty profilespecs %s' % profilespecs)

        reply = { 'ipbxid' : self.ipbxid,
                  'userid' : self.userid,
                  # profile-specific data
                  'appliname' : profilespecs.get('name'),
                  'capaxlets' : profilespecs.get('xlets'),
                  'capas' : capastruct,
                  'presence' : 'available',
                  }

        self.connection.connection_details['logged'] = True
        self.connection.logintimer.cancel()
        return reply

    def regcommand_logout(self):
        reply = {}
##                        stopper = icommand.struct.get('stopper')
##                        self.log.info('logout request from user:%s : stopper=%s' % (userid, stopper))
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
        print self.commanddict
        userprops = self.rinnerdata.xod_config['users'].keeplist.get(self.ruserid)
        # userprops.get('entityid') => context ?
        result = self.rinnerdata.getcustomers('mamaop', self.commanddict.get('pattern'))
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
        self.log.warning('logfromclient from user %s (level %s) : %s : %s'
                    % (self.ruserid,
                       self.commanddict.get('level'),
                       self.commanddict.get('classmethod'),
                       self.commanddict.get('message')))
        return

    def regcommand_getqueuesstats(self):
        self.log.warning('getqueuesstats %s' % self.commanddict)
        return

    def regcommand_keepalive(self):
        nbytes = self.commanddict.get('rate-bytes', -1)
        nmsec = self.commanddict.get('rate-msec', -1)
        nsamples = self.commanddict.get('rate-samples', -1)
        if nbytes > 0:
            if nmsec > 0:
                rate = float(nbytes) / nmsec
                self.log.info('keepalive from user:%s (%d %d/%d = %.1f bytes/ms)'
                         % (self.ruserid, nsamples, nbytes, nmsec, rate))
            else:
                self.log.info('keepalive from user:%s (%d %d/0 > %.1f bytes/ms)'
                         % (self.ruserid, nsamples, nbytes, float(nbytes)))
        return

    def regcommand_availstate(self):
        reply = {}
        # if self.capas[capaid].match_funcs(ucapa, 'presence'):
        # self.__fill_user_ctilog__(userinfo, 'cticommand:%s' % classcomm)
        availstate = self.commanddict.get('availstate')
        self.rinnerdata.update_presence(self.ruserid, availstate)
        return reply

    def regcommand_filetransfer(self):
        reply = {}
        function = self.commanddict.get('command')
        if function == 'get_announce':
            self.ctid.set_transfer_socket(self.commanddict.get('socketref'), 's2c')
        elif function == 'put_announce':
            self.ctid.set_transfer_socket(self.commanddict.get('socketref'), 'c2s')
            # get size, filename
            # reply with a token id
        return reply

    def regcommand_faxsend(self):
        reply = {}
        print 'regcommand_faxsend', self.commanddict
        print reply
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
                self.log.warning('no such list %s' % listname)

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
        self.ipbxcommand = self.commanddict.get('command', None)
        if not self.ipbxcommand:
            self.log.warning('no command given')
            return reply
        reply['command'] = self.ipbxcommand # show the command issued in the reply
        if self.ipbxcommand not in IPBXCOMMANDS:
            self.log.warning('unknown ipbxcommand %s' % self.ipbxcommand)
            return reply
        profileclient = self.rinnerdata.xod_config['users'].keeplist[self.ruserid].get('profileclient')
        profilespecs = self.ctid.cconf.getconfig('profiles').get(profileclient)
        ipbxcommands_id = profilespecs.get('ipbxcommands')
        ipbxcommands = self.ctid.cconf.getconfig('ipbxcommands').get(ipbxcommands_id)
        if self.ipbxcommand not in ipbxcommands:
            self.log.warning('profile %s : unallowed ipbxcommand %s (intermediate %s)'
                        % (profileclient, self.ipbxcommand, ipbxcommands_id))
            return reply

        methodname = 'ipbxcommand_%s' % self.ipbxcommand

        # check whether ipbxcommand is in the users's profile capabilities
        z = {}
        if hasattr(self, methodname):
            try:
                z = getattr(self, methodname)()
            except Exception:
                self.log.warning('exception when calling %s' % methodname)
        else:
            self.log.warning('no such ipbx method %s' % methodname)

        # if some actions have been requested ...
        if z:
            if self.commandid: # pass the commandid on the actionid # 'user action - forwarded'
                actionid = 'uaf:%s' % self.commandid
            else: # 'user action - auto'
                actionid = 'uaa:%s' % ''.join(random.sample(__alphanums__, 10))
            params = {
                'mode' : 'useraction',
                'request' : {
                    'requester' : self.connection,
                    'ipbxcommand' : self.ipbxcommand,
                    'commandid' : self.commandid
                    },
                'amicommand' : z.get('amicommand'),
                'amiargs' : z.get('amiargs')
                }
            ipbxreply = self.ctid.myami.get(self.ipbxid).execute_and_track(actionid, params)
        else:
            ipbxreply = ''
        reply['ipbxreply'] = ipbxreply
        return reply


    # "any number" :
    # - an explicit number
    # - a phone line given by line:xivo/45
    # - a user given by user:xivo/45 : attempted line will be the first one

    # dial : the requester dials "any number" (originate with source = me)
    # originate : the source will call destination

    # intercept
    # transfer
    # transfercancel
    # atxfer
    # intercept
    # park

    # hangupme : the requester hangs up one of his channels
    # answer : the requester answers one of its calls
    # refuse : the requester refuses one of its calls

    # hangup : any channel is hanged up

    # for transfers, hangups, ...

    def ipbxcommand_hangupme(self):
        return

    def ipbxcommand_dial(self):
        self.commanddict['source'] = 'user:%s/%s' % (self.ripbxid, self.ruserid)
        reply = self.ipbxcommand_originate()
        return reply

    # origination
    def ipbxcommand_originate(self):
        try:
            src = self.commanddict.get('source')
            [type_src, who_src] = src.split(':', 1)
            [ipbxid_src, id_src] = who_src.split('/')
        except Exception:
            self.log.warning('(%s) cannot parse source field %s'
                        % (self.commanddict.get('command'), src))
            return
        try:
            dst = self.commanddict.get('destination')
            [type_dst, who_dst] = dst.split(':', 1)
            [ipbxid_dst, id_dst] = who_dst.split('/')
        except Exception:
            self.log.warning('(%s) cannot parse destination field %s'
                        % (self.commanddict.get('command'), dst))
            return
        if ipbxid_src != ipbxid_dst:
            return
        if ipbxid_src not in self.ctid.safe:
            self.log.warning('%s not in %s' % (ipbxid_src, self.ctid.safe.keys()))
            return
        innerdata = self.ctid.safe.get(ipbxid_src)

        orig_protocol = None
        orig_name = None
        orig_number = None

        if type_src == 'user':
            if id_src in innerdata.xod_config.get('users').keeplist:
                useridstruct = innerdata.xod_config.get('users').keeplist.get(id_src)
                # useridstruct, innerdata.xod_status.get('users').get(id_src)
                # XXX lookup among phones the one(s) that belong to this user
        elif type_src == 'phone':
            if id_src in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct = innerdata.xod_config.get('phones').keeplist.get(id_src)
                orig_protocol = phoneidstruct.get('protocol')
                # XXX 'local' might break the XIVO_ORIGSRCNUM mechanism (trick for thomson)
                orig_name = phoneidstruct.get('name')
                orig_number = phoneidstruct.get('number')
                orig_identity = phoneidstruct.get('useridentity')
        elif type_src == 'exten':
            # in android cases
            # there was a warning back to revision 6095 - maybe to avoid making arbitrary calls on behalf
            # of the local telephony system ?
            pass

        extentodial = None
        dst_identity = None

        if type_dst == 'user':
            # if no phone, could default to agent and/or agent phone number ?
            pass
        elif type_dst == 'phone':
            if id_dst in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct = innerdata.xod_config.get('phones').keeplist.get(id_dst)
                extentodial = phoneidstruct.get('number')
                dst_identity = phoneidstruct.get('useridentity')
                dst_context = phoneidstruct.get('context')
        elif type_dst == 'voicemail':
            extentodial = '*98'
            # XXX especially for the 'dial' command, actually
            # XXX display password on phone in order for the user to know what to type
        elif type_dst == 'exten':
            # XXX how to define
            extentodial = who_dst

        rep = {}
        if orig_protocol and orig_name and orig_number and extentodial:
            rep = {'amicommand' : 'originate',
                   'amiargs' : (orig_protocol,
                                orig_name,
                                orig_number,
                                orig_identity,
                                extentodial,
                                dst_identity,
                                dst_context)
                   }
            # {'XIVO_USERID' : userinfo.get('xivo_userid')})
        return rep


    def ipbxcommand_meetme(self):
        print 'ipbxcommand_meetme', self.commanddict, self.userid, self.ruserid
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

    def ipbxcommand_sipnotify(self):
        if 'variables' in self.commanddict:
            variables = self.commanddict.get('variables')
        channel = self.commanddict.get('channel')
        if channel == 'user:special:me':
            uinfo = self.rinnerdata.xod_config['users'].keeplist[self.userid] 
            # TODO: Choose the appropriate line if more than one                 
            line = self.rinnerdata.xod_config['phones'].keeplist[uinfo['linelist'][0]]              
            channel = line['identity'].replace('\\','')       
        reply = {'amicommand': 'sipnotify', 'amiargs': (channel, variables)}
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
                self.log.warning('unknown typesrc %s for %s' % (typesrc, commname))

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
                    self.log.warning('no voicemail allowed or defined for %s' % dstuinfo)
        else:
                self.log.warning('unknown typedst %s for %s' % (typedst, commname))

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
                self.log.exception('unable to %s' % commname)
        return

    def ipbxcommand_parking(self):
        rep = {}
        src = self.commanddict.get('source')
        srcsplit = src.split(':', 1)
        [typesrc, whosrc] = srcsplit
        if typesrc not in ['chan']:
            self.log.warning('unallowed typesrc %s for %s' % (typesrc, self.ipbxcommand))
            return

        [ipbxid, channel] = whosrc.split('/', 1)
        print self.ctid.safe.get(ipbxid).channels.keys()
        peerchannel = self.ctid.safe.get(ipbxid).channels.get(channel).peerchannel
        rep = {'amicommand' : 'park', 'amiargs' : (channel, peerchannel)}
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
            self.log.warning('unallowed typesrc %s for %s' % (typesrc, self.ipbxcommand))
            return
        if typedst not in ['user', 'ext', 'phone']:
            self.log.warning('unallowed typedst %s for %s' % (typedst, self.ipbxcommand))
            return

        [ipbxid, channel] = whosrc.split('/', 1)
        if typedst == 'user':
            rep = {'amicommand' : 'transfer', 'amiargs' : (channel, '1431', 'from-sip')}
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
            self.log.warning('unallowed typesrc %s for %s' % (typesrc, self.ipbxcommand))
            return
        if typedst not in ['user', 'ext', 'phone']:
            self.log.warning('unallowed typedst %s for %s' % (typedst, self.ipbxcommand))
            return

        [ipbxid, channel] = whosrc.split('/', 1)
        if typedst == 'user':
            rep = {'amicommand' : 'atxfer', 'amiargs' : (channel, '1431', 'from-sip')}
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
                self.log.warning('unknown typesrc %s for %s' % (typesrc, commname))

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
                    self.log.warning('no voicemail allowed or defined for %s' % dstuinfo)
        else:
                self.log.warning('unknown typedst %s for %s' % (typedst, commname))

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
                self.log.exception('unable to %s' % commname)
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
        return {'amicommand' : 'agentlogin', 'amiargs' : ('a', 'b', 'c')}

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
    def ipbxcommand_record(self):
        subcommand = self.commanddict.pop('subcommand')
        channel = self.commanddict.pop('channel')
        # XX take into account ipbxid
        if subcommand == 'start':
            datestring = time.strftime('%Y%m%d-%H%M%S', time.localtime())
            # kind agent => channel = logged-on channel
            # other kind => according to what is provided
            kind = 'phone'
            id = '7'
            filename = 'cti-monitor-%s-%s-%s' % (datestring, kind, id)
            rep = { 'amicommand' : 'monitor',
                    'amiargs' : (channel, filename, 'false') }
            # wait the AMI event ack in order to fill status for channel
        elif subcommand == 'stop':
            rep = { 'amicommand' : 'stopmonitor',
                    'amiargs' : (channel,) }
        return rep

    def ipbxcommand_listen(self):
        subcommand = self.commanddict.pop('subcommand')
        channel = self.commanddict.pop('channel')
        # channel might not exist any more
        if subcommand == 'start':
            listener = self.commanddict.pop('listener')
            (listener_protocol, listener_id) = listener.split('/')
            rep = { 'amicommand' : 'origapplication',
                    'amiargs' : ('ChanSpy',
                                 '%s,q' % channel,
                                 listener_protocol,
                                 listener_id,
                                 '000',
                                 'mamaop') }
        elif subcommand == 'stop':
            # XXX hangup appropriate channel
            rep = {}
        return rep
