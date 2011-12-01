# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2007-2011  Avencall'
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
from xivo_ctiservers import cti_fax
from xivo_ctiservers import cti_config
from xivo_ctiservers.statistics.queuestatisticmanager import QueueStatisticManager
from xivo_ctiservers.statistics.queuestatisticencoder import QueueStatisticEncoder

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
    'answer', 'refuse',
    # originate-like commands
    'dial', 'originate',
    # transfer-like commands
    'intercept', 'parking',
    'transfer', 'atxfer',
    # hangup-like commands
    'hangup', 'hangupme', 'cancel', 'transfercancel',

    'sipnotify',
    'mailboxcount',
    'meetme',
    'record',
    'listen',

    'agentlogin', 'agentlogout',
    'queueadd', 'queueremove',
    'queuepause', 'queueunpause',
    'queueremove_all',
    'queuepause_all', 'queueunpause_all',
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
        self._queue_statistic_manager = QueueStatisticManager()
        self._queue_statistic_encoder = QueueStatisticEncoder()
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
                    if ztmp is None or len(ztmp) == 0:
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
        profilespecs = cti_config.cconf.getconfig('profiles').get(profileclient)

        capastruct = {}
        summarycapas = {}
        if profilespecs:
            for capakind in ['regcommands', 'ipbxcommands',
                             'services', 'preferences',
                             'userstatus', 'phonestatus', 'channelstatus', 'agentstatus']:
                if profilespecs.get(capakind):
                    tt = profilespecs.get(capakind)
                    cfg_capakind = cti_config.cconf.getconfig(capakind)
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
        if capaid not in cti_config.cconf.getconfig('profiles').keys():
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
        availstate = self.commanddict.get('availstate')
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

    def regcommand_actionfiche(self):
        reply = {}
        infos = self.commanddict.get('infos')
        uri = cti_config.cconf.getconfig('ipbxes').get(self.ripbxid).get('cdr_db_uri')
        self.rinnerdata.fill_user_ctilog(uri,
                                         self.ruserid,
                                         'cticommand:actionfiche',
                                         infos.get('buttonname'))
        return reply

    def regcommand_featuresget(self):
        reply = {}
        z = xivo_webservices.xws(cti_config.cconf.ipwebs, 80)
        z.connect()
        services = z.serviceget(self.ruserid)
        z.close()
        # looks like this nice information is in userfeatures
        services.get('userfeatures').pop('passwdclient')
        reply = { 'userfeatures' : services.get('userfeatures') }
        return reply

    def regcommand_featuresput(self):
        user = self.rinnerdata.xod_config.get('users').finduser(self.ruserid)
        if user is None:
            return {'status': 'KO', 'error_string': 'unknown %d user' % self.ruserid}

        func   = self.commanddict.get('function')
        values = self.commanddict.get('value') if func == 'fwd' else\
            {func: self.commanddict.get('value')}
    
        changed = False
        for k, v in values.iteritems():
            if v != user.get(k, None):
                changed = True; break

        # feature values has not been changed
        if not changed:
            return {'status': 'OK', 'warning_string': 'no changes'}

        #user.update(values)
        z = xivo_webservices.xws(cti_config.cconf.ipwebs, 80)
        z.connect()
        z.serviceput(self.ruserid, values)
        z.close()

        return {'status': 'OK'}

    def regcommand_directory(self):
        # Since there's no direct, unique link between a user and a context in
        # xivo 1.2, contrarily to xivo 1.1, we always search for "customers"
        # in the "default" directory context.
        #
        # This implies is that it's useless to add more "directory context"
        # in the CTI server configuration.
        result = self.rinnerdata.getcustomers('default', self.commanddict.get('pattern'))
        return result

    def regcommand_history(self):
        phone = self._get_phone_from_user_id(self.ruserid, self.rinnerdata)
        if phone is None:
            reply = self._format_history_reply(None)
        else:
            history = self._get_history_for_phone(phone)
            reply = self._format_history_reply(history)
        return reply

    def _get_phone_from_user_id(self, user_id, innerdata):
        for phone in innerdata.xod_config['phones'].keeplist.itervalues():
            if str(phone['iduserfeatures']) == user_id:
                return phone
        return None

    def _get_history_for_phone(self, phone):
        mode = int(self.commanddict['mode'])
        limit = int(self.commanddict['size'])
        endpoint = self._get_endpoint_from_phone(phone)
        if mode == 0:
            return self._get_outgoing_history_for_endpoint(endpoint, limit)
        elif mode == 1:
            return self._get_answered_history_for_endpoint(endpoint, limit)
        elif mode == 2:
            return self._get_missed_history_for_endpoint(endpoint, limit)
        else:
            return None

    def _get_outgoing_history_for_endpoint(self, endpoint, limit):
        call_history_mgr = self.rinnerdata.call_history_mgr
        result = []
        for sent_call in call_history_mgr.outgoing_calls_for_endpoint(endpoint, limit):
            result.append({'calldate': sent_call.date.isoformat(),
                           'duration': sent_call.duration,
                           # XXX this is not fullname, this is just an extension number like in 1.1
                           'fullname': sent_call.extension})
        return result

    def _get_answered_history_for_endpoint(self, endpoint, limit):
        call_history_mgr = self.rinnerdata.call_history_mgr
        result = []
        for received_call in call_history_mgr.answered_calls_for_endpoint(endpoint, limit):
            result.append({'calldate': received_call.date.isoformat(),
                           'duration': received_call.duration,
                           'fullname': received_call.caller_name})
        return result

    def _get_missed_history_for_endpoint(self, endpoint, limit):
        call_history_mgr = self.rinnerdata.call_history_mgr
        result = []
        for received_call in call_history_mgr.missed_calls_for_endpoint(endpoint, limit):
            result.append({'calldate': received_call.date.isoformat(),
                           'duration': received_call.duration,
                           'fullname': received_call.caller_name})
        return result

    def _get_endpoint_from_phone(self, phone):
        return "%s/%s" % (phone['protocol'].upper(), phone['name'])

    def _format_history_reply(self, history):
        if history is None:
            return {}
        else:
            mode = int(self.commanddict['mode'])
            return {'mode': mode, 'history': history}

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
        if 'on' not in self.commanddict:
            return {}
        statistic_results = {}
        for queue_id, params in self.commanddict['on'].iteritems():
            queue_name = self.innerdata.xod_config['queues'].keeplist[queue_id]['name']
            statistic_results[queue_id] = self._queue_statistic_manager.get_statistics(queue_name,
                                                                                        int(params['xqos']),
                                                                                        int(params['window']))
        return self._queue_statistic_encoder.encode(statistic_results)

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
        socketref = self.commanddict.get('socketref')
        fileid = self.commanddict.get('fileid')
        if fileid:
            self.rinnerdata.faxes[fileid].setsocketref(socketref)
            self.rinnerdata.faxes[fileid].setfileparameters(self.commanddict.get('file_size'))
            if function == 'get_announce':
                self.ctid.set_transfer_socket(self.rinnerdata.faxes[fileid], 's2c')
            elif function == 'put_announce':
                self.ctid.set_transfer_socket(self.rinnerdata.faxes[fileid], 'c2s')
        else:
            self.log.warning('empty fileid given %s' % self.commanddict)
        return reply

    def regcommand_faxsend(self):
        fileid = ''.join(random.sample(__alphanums__, 10))
        reply = {'fileid' : fileid}
        self.rinnerdata.faxes[fileid] = cti_fax.Fax(self.rinnerdata, fileid)
        # ruserid gives an entity, which doesn't give a context right away ...
        context = 'default'
        self.rinnerdata.faxes[fileid].setfaxparameters(self.ruserid,
                                                       context,
                                                       self.commanddict.get('destination'),
                                                       self.commanddict.get('hide'))
        self.rinnerdata.faxes[fileid].setrequester(self.connection)
        return reply

    def regcommand_getipbxlist(self):
        reply = { 'ipbxlist' : cti_config.cconf.getconfig('ipbxes').keys() }
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
        profilespecs = cti_config.cconf.getconfig('profiles').get(profileclient)
        ipbxcommands_id = profilespecs.get('ipbxcommands')
        ipbxcommands = cti_config.cconf.getconfig('ipbxcommands').get(ipbxcommands_id)
        if self.ipbxcommand not in ipbxcommands:
            self.log.warning('profile %s : unallowed ipbxcommand %s (intermediate %s)'
                        % (profileclient, self.ipbxcommand, ipbxcommands_id))
            return reply

        methodname = 'ipbxcommand_%s' % self.ipbxcommand

        # check whether ipbxcommand is in the users's profile capabilities
        zs = []
        if hasattr(self, methodname):
            try:
                zs = getattr(self, methodname)()
            except Exception:
                self.log.warning('exception when calling %s' % methodname)
        else:
            self.log.warning('no such ipbx method %s' % methodname)

        # if some actions have been requested ...
        if self.commandid: # pass the commandid on the actionid # 'user action - forwarded'
            baseactionid = 'uaf:%s' % self.commandid
        else: # 'user action - auto'
            baseactionid = 'uaa:%s' % ''.join(random.sample(__alphanums__, 10))
        ipbxreply = 'noaction'
        idz = 0
        for z in zs:
            if 'amicommand' in z:
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
                actionid = '%s-%03d' % (baseactionid, idz)
                ipbxreply = self.ctid.myami.get(self.ipbxid).execute_and_track(actionid, params)
            else:
                ipbxreply = z.get('error')
            idz += 1

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
    # park

    # hangupme : the requester hangs up one of his channels
    # answer : the requester answers one of its calls
    # refuse : the requester refuses one of its calls

    # hangup : any channel is hanged up

    # for transfers, hangups, ...

    def ipbxcommand_hangupme(self):
        return []

    def ipbxcommand_dial(self):
        self.commanddict['source'] = 'user:%s/%s' % (self.ripbxid, self.ruserid)
        reply = self.ipbxcommand_originate()
        return reply

    def parseid(self, item):
        id_as_obj = {}
        try:
            [typev, who] = item.split(':', 1)
            [ipbxid, idv] = who.split('/', 1)
            id_as_obj = { 'type' : typev,
                          'ipbxid' : ipbxid,
                          'id' : idv }
        except Exception:
            pass
        return id_as_obj

    # origination
    def ipbxcommand_originate(self):
        src = self.parseid(self.commanddict.get('source'))
        if not src:
            return [{'error' : 'source'}]
        dst = self.parseid(self.commanddict.get('destination'))
        if not dst:
            return [{'error' : 'destination'}]

        if src.get('ipbxid') != dst.get('ipbxid'):
            return [{'error' : 'ipbxids'}]
        if src.get('ipbxid') not in self.ctid.safe:
            return [{'error' : 'ipbxid'}]

        innerdata = self.ctid.safe.get(src.get('ipbxid'))

        orig_protocol = None
        orig_name = None
        orig_number = None
        orig_context = None
        phoneidstruct_src = {}
        phoneidstruct_dst = {}

        if src.get('type') == 'user':
            if src.get('id') in innerdata.xod_config.get('users').keeplist:
                for k, v in innerdata.xod_config.get('phones').keeplist.iteritems():
                    if src.get('id') == str(v.get('iduserfeatures')):
                        phoneidstruct_src = innerdata.xod_config.get('phones').keeplist.get(k)
                        break
                # if not phoneidstruct_src: lookup over agents ?
        elif src.get('type') == 'phone':
            if src.get('id') in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct_src = innerdata.xod_config.get('phones').keeplist.get(src.get('id'))
        elif src.get('type') == 'exten':
            # in android cases
            # there was a warning back to revision 6095 - maybe to avoid making arbitrary calls on behalf
            # of the local telephony system ?
            orig_context = 'mamaop' # XXX how should we define or guess the proper context here ?
            orig_protocol = 'local'
            orig_name = '%s@%s' % (src.get('id'), orig_context) # this is the number actually dialed, in local channel mode
            orig_number = src.get('id') # this is the number that will be displayed as ~ callerid
            orig_identity = '' # how would we know the identity there ?

        if phoneidstruct_src:
            orig_protocol = phoneidstruct_src.get('protocol')
            # XXX 'local' might break the XIVO_ORIGSRCNUM mechanism (trick for thomson)
            orig_name = phoneidstruct_src.get('name')
            orig_number = phoneidstruct_src.get('number')
            orig_identity = phoneidstruct_src.get('useridentity')
            orig_context = phoneidstruct_src.get('context')

        extentodial = None
        dst_identity = None

        if dst.get('type') == 'user':
            if dst.get('id') in innerdata.xod_config.get('users').keeplist:
                for k, v in innerdata.xod_config.get('phones').keeplist.iteritems():
                    if dst.get('id') == str(v.get('iduserfeatures')):
                        phoneidstruct_dst = innerdata.xod_config.get('phones').keeplist.get(k)
                        break
                # if not phoneidstruct_dst: lookup over agents ?
        elif dst.get('type') == 'phone':
            if dst.get('id') in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct_dst = innerdata.xod_config.get('phones').keeplist.get(dst.get('id'))
        elif dst.get('type') == 'voicemail':
            try:
                vmusermsg = innerdata.extenfeatures['extenfeatures']['vmusermsg']
                vm = innerdata.xod_config['voicemails'].keeplist[dst['id']]
                if not vmusermsg['commented']:
                    extentodial = vmusermsg['exten']
                    dst_context = vm['context']
                    dst_identity = 'Voicemail'
                else:
                    extentodial = None
            except KeyError:
                self.log.info('Missing info to call this voicemail')
                extentodial = None
            # XXX especially for the 'dial' command, actually
            # XXX display password on phone in order for the user to know what to type
        elif dst.get('type') == 'meetme':
            if dst.get('id') in innerdata.xod_config.get('meetmes').keeplist:
                meetmestruct = innerdata.xod_config.get('meetmes').keeplist.get(dst.get('id'))
                extentodial = meetmestruct.get('confno')
                dst_identity = 'meetme %s' % meetmestruct.get('name')
                dst_context = meetmestruct.get('context')
            else:
                extentodial = None
        elif dst.get('type') == 'exten':
            # XXX how to define
            extentodial = dst.get('id')
            dst_identity = extentodial
            dst_context = orig_context

        if phoneidstruct_dst:
            extentodial = phoneidstruct_dst.get('number')
            dst_identity = phoneidstruct_dst.get('useridentity')
            dst_context = phoneidstruct_dst.get('context')

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
        return [rep]

    def ipbxcommand_meetme(self):
        self.log.info('ipbxcommand_meetme %s' % self.commanddict)
        function = self.commanddict['function']
        args = self.commanddict['functionargs']

        if function in ('record', ) and len(args) >= 4:
            mxid, usernum, adminnum, status = args[:4]
        elif (function in ('MeetmeMute', 'MeetmeUnmute')
              and len(args) >= 2):
            mxid, usernum = args[:2]
        elif (len(args) >= 3 and function in
              ('MeetmeAccept', 'MeetmeKick', 'MeetmeTalk')):
            mxid, usernum, adminnum = args[:3]
        mid = mxid.split("/", 1)[1]

        meetme_conf = self.innerdata.xod_config['meetmes'].keeplist[mid]
        meetme_status = self.innerdata.xod_status['meetmes'][mid]

        if 'record' in function and status in ('start', 'stop'):
            chan = ''
            for key, value in meetme_status.iteritems():
                if value['usernum'] == usernum:
                    chan = key
            if status == 'start' and chan:
                datestring = time.strftime('%Y%m%d-%H%M%S', time.localtime())
                filename = ('cti-meetme-%s-%s' %
                            (meetme_conf['name'], datestring))
                return [{'amicommand': 'monitor',
                          'amiargs': (chan, filename)}]
            elif status == 'stop':
                return [{'amicommand': 'stopmonitor',
                          'amiargs': (chan, )}]
        elif function in ('MeetmePause',):
            return [{'amicommand': function.lower(),
                      'amiargs': (meetme_conf['confno'], status)}]
        elif function in ('MeetmeKick', 'MeetmeAccept', 'MeetmeTalk'):
            return [{'amicommand': 'meetmemoderation',
                      'amiargs': (function, meetme_conf['confno'],
                                    usernum, adminnum)}]
        elif function in ['MeetmeMute', 'MeetmeUnmute']:
            return [{'amicommand': function.lower(),
                     'amiargs': (meetme_conf['confno'], usernum)}]
        # elif function == 'kick':
        #     pass
        # elif function == 'getlist':
        #     fullstat = {}
        #     for iastid, v in self.xod_config['meetme'].iteritems():
        #         fullstat[iastid] = v.keeplist
        #     tosend = {'class': 'meetme', 'function': 'sendlist',
        #               'payload': fullstat}
        #     repstr = self.__cjson_encode__(tosend)

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
        return [reply]

    def ipbxcommand_mailboxcount(self):
        """
        Send a MailboxCount ami command
        """
        if 'mailbox' in self.commanddict:
            return [{'amicommand': 'mailboxcount',
                      'amiargs': (self.commanddict['mailbox'],
                                    self.commanddict['context'])}]

    # transfers
    def ipbxcommand_parking(self):
        src = self.parseid(self.commanddict.get('source'))
        if not src:
            return [{'error' : 'source'}]
        dst = self.parseid(self.commanddict.get('destination'))
        if not dst:
            return {'error' : 'destination'}

        if src.get('ipbxid') != dst.get('ipbxid'):
            return {'error' : 'ipbxids'}
        if src.get('ipbxid') not in self.ctid.safe:
            return {'error' : 'ipbxid'}

        innerdata = self.ctid.safe.get(src.get('ipbxid'))

        if src.get('type') == 'chan':
            if src.get('id') in innerdata.channels:
                channel = src.get('id')
                peerchannel = innerdata.channels.get(channel).peerchannel
        else:
            pass

        if dst.get('type') == 'parking':
            try:
                parkinglot = innerdata.xod_config['parkinglots'].keeplist[dst['id']]['name']
                if parkinglot is not 'default':
                    parkinglot = 'parkinglot_' + parkinglot
            except Exception:
                parkinglot = 'default'

        rep = {'amicommand' : 'park',
               'amiargs' : (channel, peerchannel, parkinglot, 120000)
               }
        return [rep, ]

    # direct transfers
    def ipbxcommand_transfer(self):
        src = self.parseid(self.commanddict.get('source'))
        if not src:
            return [{'error' : 'source'}]
        dst = self.parseid(self.commanddict.get('destination'))
        if not dst:
            return [{'error' : 'destination'}]

        if src.get('ipbxid') != dst.get('ipbxid'):
            return [{'error' : 'ipbxids'}]
        if src.get('ipbxid') not in self.ctid.safe:
            return [{'error' : 'ipbxid'}]

        innerdata = self.ctid.safe.get(src.get('ipbxid'))

        if 'type' in src and 'chan' in src['type']:
            if src.get('id') in innerdata.channels:
                channel = src.get('id')
                src_context = innerdata.channels.get(channel).context
                # phone relations ('phone:24') innerdata.channels.get(channel).relations
        else:
            pass

        dst_context = src_context
        phoneidstruct_dst = {}
        extentodial = None

        if dst.get('type') == 'user':
            if dst.get('id') in innerdata.xod_config.get('users').keeplist:
                for k, v in innerdata.xod_config.get('phones').keeplist.iteritems():
                    if dst.get('id') == str(v.get('iduserfeatures')):
                        phoneidstruct_dst = innerdata.xod_config.get('phones').keeplist.get(k)
                        break
                # if not phoneidstruct_dst: lookup over agents ?
        elif dst.get('type') == 'phone':
            if dst.get('id') in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct_dst = innerdata.xod_config.get('phones').keeplist.get(dst.get('id'))
        elif dst.get('type') == 'exten':
            extentodial = dst.get('id')
        elif dst.get('type') == 'voicemail':
            # *97 vm number
            self.log.debug('transfer to voicemail %s', self.commanddict)
            if dst['id'] in innerdata.xod_config['voicemails'].keeplist:
                voicemail = innerdata.xod_config['voicemails'].keeplist[dst['id']]
                vm_number = voicemail['mailbox']
                prefix = innerdata.extenfeatures['extenfeatures']['vmboxslt']['exten']
                prefix = prefix[:len(prefix) - 1]
                extentodial = prefix + vm_number
                dst_context = voicemail['context']
        elif dst.get('type') == 'meetme':
            if dst.get('id') in innerdata.xod_config.get('meetmes').keeplist:
                meetmestruct = innerdata.xod_config.get('meetmes').keeplist.get(dst.get('id'))
                extentodial = meetmestruct.get('confno')
        else:
            pass

        if phoneidstruct_dst:
            extentodial = phoneidstruct_dst.get('number')

        rep = {}
        if extentodial:
            rep = {'amicommand' : 'transfer',
                   'amiargs' : (channel,
                                extentodial,
                                dst_context)
                   }
        return [rep]

    def ipbxcommand_atxfer(self):
        # no reply was received from this :
        # http://lists.digium.com/pipermail/asterisk-users/2011-March/260508.html
        # however some clues could be found here :
        # https://issues.asterisk.org/view.php?id=12158
        rep = {}
        try:
            src = self.parseid(self.commanddict.get('source'))
            dst = self.parseid(self.commanddict.get('destination'))
            exten = dst['id']
            if src['id'] in self.innerdata.channels:
                channel = self.innerdata.channels[src['id']]
                context = channel.context
                rep = {'amicommand': 'atxfer',
                       'amiargs': (src['id'],
                                   exten,
                                   context)}
        except KeyError:
            self.log.warning('Atxfer failed %s', self.commanddict)
        return [rep,]


    def ipbxcommand_transfercancel(self):
        print self.ipbxcommand, self.commanddict
        return []

    def ipbxcommand_intercept(self):
        self.commanddict['source'] = self.commanddict.pop('tointercept')
        self.commanddict['destination'] = self.commanddict.pop('catcher')
        # ami transfer mode
        reps = self.ipbxcommand_transfer()
        # what about origination with '*8' ?
        return reps

    # hangup and one's own line management
    def ipbxcommand_hangup(self):
        channel = self.parseid(self.commanddict.get('channelids'))
        rep = { 'amicommand': 'hangup',
                'amiargs': (channel.get('id'), )
                }
        return [rep, ]

    def ipbxcommand_answer(self):
        print self.ipbxcommand, self.commanddict
        return []
    def ipbxcommand_cancel(self):
        print self.ipbxcommand, self.commanddict
        return []
    def ipbxcommand_refuse(self):
        print self.ipbxcommand, self.commanddict
        return []

    # agents and queues
    def ipbxcommand_agentlogin(self):
        agentphonenumber = self.commanddict.get('agentphonenumber')
        memberstatus = None
        agentnumber = None
        agentcontext = None
        if 'member' in self.commanddict:
            member = self.parseid(self.commanddict.get('member'))
            innerdata = self.ctid.safe.get(member.get('ipbxid'))
            if member.get('id') in innerdata.xod_config.get('agents').keeplist:
                memberstruct = innerdata.xod_config.get('agents').keeplist.get(member.get('id'))
                memberstatus = innerdata.xod_status.get('agents').get(member.get('id'))
                agentnumber = memberstruct.get('number')
                agentcontext = memberstruct.get('context')
        else:
            agentid = self.rinnerdata.xod_config.get('users').keeplist.get(self.ruserid).get('agentid')
            if agentid:
                memberstruct = self.rinnerdata.xod_config.get('agents').keeplist.get(agentid)
                memberstatus = self.rinnerdata.xod_status.get('agents').get(agentid)
                agentnumber = memberstruct.get('number')
                agentcontext = memberstruct.get('context')

        rep = list()
        if agentnumber and agentcontext and memberstatus:
            if memberstatus.get('status') not in ['AGENT_IDLE', 'AGENT_ONCALL']:
                rep = [{ 'amicommand' : 'agentcallbacklogin',
                         'amiargs' : (agentnumber, agentphonenumber, agentcontext, True)
                         }]
        return rep

    def ipbxcommand_agentlogout(self):
        agentnumber = None
        memberstatus = None
        if 'member' in self.commanddict:
            member = self.parseid(self.commanddict.get('member'))
            innerdata = self.ctid.safe.get(member.get('ipbxid'))
            if member.get('id') in innerdata.xod_config.get('agents').keeplist:
                memberstruct = innerdata.xod_config.get('agents').keeplist.get(member.get('id'))
                memberstatus = innerdata.xod_status.get('agents').get(member.get('id'))
                agentnumber = memberstruct.get('number')
        else:
            agentid = self.rinnerdata.xod_config.get('users').keeplist.get(self.ruserid).get('agentid')
            if agentid:
                memberstruct = self.rinnerdata.xod_config.get('agents').keeplist.get(agentid)
                memberstatus = self.rinnerdata.xod_status.get('agents').get(agentid)
                agentnumber = memberstruct.get('number')

        rep = list()
        if agentnumber and memberstatus:
            if memberstatus.get('status') != 'AGENT_LOGGEDOFF':
                rep = [{ 'amicommand' : 'agentlogoff',
                         'amiargs' : (agentnumber,)
                         }]
        return rep

    def whenmember(self, innerdata, command, dopause, listname, k, member):
        memberlist = []
        midx = '%s%s:%s-%s' % (listname[0], member.get('type')[0], k, member.get('id'))
        membership = innerdata.queuemembers.get(midx).get('membership')
        paused = innerdata.queuemembers.get(midx).get('paused')
        doit = False
        if command == 'remove' and membership != 'static':
            doit = True
        if command == 'pause':
            if dopause == 'true' and paused == '0':
                doit = True
            if dopause == 'false' and paused == '1':
                doit = True
        if doit:
            memberlist.append(member)
        return memberlist

    def defmemberlist(self, innerdata, command, dopause, listname, k, member):
        memberlist = []
        if member.get('type') in ['phone', 'agent']:
            membersname = member.get('type') + 'members'
            lname = member.get('type') + 's'
            any_members = innerdata.xod_status.get(listname).get(k).get(membersname)
            if member.get('id') in innerdata.xod_config.get(lname).keeplist:
                if command == 'add':
                    if member.get('id') not in any_members:
                        memberlist = [member]
                else:
                    if member.get('id') in any_members:
                        memberlist = self.whenmember(innerdata, command, dopause, listname, k, member)
            elif member.get('id') == 'all':
                if command != 'add':
                    for any_id in any_members:
                        member = {'type' : member.get('type'), 'id' : any_id}
                        memberlist = self.whenmember(innerdata, command, dopause, listname, k, member)
        return memberlist

    def makeinterfaces(self, innerdata, memberlist):
        interfaces = []
        for member in memberlist:
            interface = None
            if member.get('type') == 'phone':
                memberstruct = innerdata.xod_config.get('phones').keeplist.get(member.get('id'))
                interface = '%s/%s' % (memberstruct.get('protocol'), memberstruct.get('name'))
            elif member.get('type') == 'agent':
                memberstruct = innerdata.xod_config.get('agents').keeplist.get(member.get('id'))
                interface = 'Agent/%s' % memberstruct.get('number')

            if interface and interface not in interfaces:
                interfaces.append(interface)
        return interfaces

    def queue_generic(self, command, dopause = None):
        member = self.parseid(self.commanddict.get('member'))
        if not member:
            return [{'error' : 'member'}]
        queue = self.parseid(self.commanddict.get('queue'))
        if not queue:
            return [{'error' : 'queue'}]

        innerdata = self.ctid.safe.get(queue.get('ipbxid'))

        listname = None
        if queue.get('type') == 'queue':
            listname = 'queues'
        elif queue.get('type') == 'group':
            listname = 'groups'

        queuenames = []
        interfaces = []

        if listname:
            if queue.get('id') in innerdata.xod_config.get(listname).keeplist:
                lst = self.defmemberlist(innerdata, command, dopause, listname, queue.get('id'), member)
                if lst:
                    interfaces = self.makeinterfaces(innerdata, lst)
                    queuestruct = innerdata.xod_config.get(listname).keeplist.get(queue.get('id'))
                    queuename = queuestruct.get('name')
                    if queuename not in queuenames:
                        queuenames.append(queuename)
            elif queue.get('id') == 'all':
                for k, queuestruct in innerdata.xod_config.get(listname).keeplist.iteritems():
                    lst = self.defmemberlist(innerdata, command, dopause, listname, k, member)
                    if lst:
                        interfaces = self.makeinterfaces(innerdata, lst)
                        queuename = queuestruct.get('name')
                        print queuename, interfaces
                        if queuename not in queuenames:
                            queuenames.append(queuename)

        reps = []
        amicommand = 'queue%s' % command
        for queuename in queuenames:
            for interface in interfaces:
                if command == 'remove':
                    amiargs = (queuename, interface)
                elif command == 'add':
                    amiargs = (queuename, interface, dopause)
                elif command == 'pause':
                    amiargs = (queuename, interface, dopause)
                rep = {
                    'amicommand' : amicommand,
                    'amiargs' : amiargs
                    }
                reps.append(rep)
        print reps
        return reps

    def ipbxcommand_queueadd(self):
        return self.queue_generic('add', self.commanddict.get('paused'))

    def ipbxcommand_queueremove(self):
        return self.queue_generic('remove')

    def ipbxcommand_queuepause(self):
        return self.queue_generic('pause', 'true')

    def ipbxcommand_queueunpause(self):
        return self.queue_generic('pause', 'false')

    # 'all' can mean :
    # - all members (phones, agents, ...) of a queue or a group
    # - all queues or groups a member belongs to
    # the one that is most useful is the second case

    def ipbxcommand_queuepause_all(self):
        self.commanddict['queue'] = 'queue:xivo/all'
        return self.queue_generic('pause', 'true')

    def ipbxcommand_queueunpause_all(self):
        self.commanddict['queue'] = 'queue:xivo/all'
        return self.queue_generic('pause', 'false')

    def ipbxcommand_queueremove_all(self):
        self.commanddict['queue'] = 'queue:xivo/all'
        return self.queue_generic('remove')


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
            idv = '7'
            filename = 'cti-monitor-%s-%s-%s' % (datestring, kind, idv)
            rep = { 'amicommand' : 'monitor',
                    'amiargs' : (channel, filename, 'false') }
            # wait the AMI event ack in order to fill status for channel
        elif subcommand == 'stop':
            rep = { 'amicommand' : 'stopmonitor',
                    'amiargs' : (channel,) }
        return [rep]

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
        return [rep]
