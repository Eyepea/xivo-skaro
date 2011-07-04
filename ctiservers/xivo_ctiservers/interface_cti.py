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

import cjson
import logging
import os
import time

from xivo_ctiservers.interfaces import Interfaces
from xivo_ctiservers import cti_command

class serialJson():
    def __init__(self):
        return
    def decode(self, linein):
        v = cjson.decode(linein.replace('\\/', '/'))
        return v
    def encode(self, obj):
        obj['timenow'] = time.time()
        return cjson.encode(obj)

class CTI(Interfaces):
    kind = 'CTI'
    sep = '\n'
    def __init__(self, ctid):
        Interfaces.__init__(self, ctid)
        self.connection_details = {}
        self.serial = serialJson()
        self.transferconnection = {}
        return

    def connected(self, connid):
        """
        Send a banner at login time
        """
        Interfaces.connected(self, connid)
        self.log = logging.getLogger('interface_cti(%s:%d)' % self.requester)
        self.connid.sendall('XiVO CTI Server Version xx (on %s)\n'
                            % (' '.join(os.uname()[:3])))
        return

    def disconnected(self, msg):
        self.log.info('disconnected %s' % msg)
        self.logintimer.cancel()
        if self.transferconnection and self.transferconnection.get('direction') == 'c2s':
            self.log.info('%s got the file ...' % self.transferconnection.get('faxobj').fileid)
        # self.connid.sendall(msg)
        # tosend = { 'class' : 'serverdown',
        # 'mode' : mode }
        return

        Interfaces.disconnected(self, msg)
        # call to manage_logout
        return

    def manage_connection(self, msg):
        z = list()
        if self.transferconnection:
            if self.transferconnection.get('direction') == 'c2s':
                faxobj = self.transferconnection.get('faxobj')
                self.logintimer.cancel()
                self.log.info('%s transfer connection : %d received' % (faxobj.fileid, len(msg)))
                faxobj.setbuffer(msg)
                faxobj.launchasyncs()
        else:
            multimsg = msg.split(self.sep)
            for usefulmsgpart in multimsg:
                cmd = self.serial.decode(usefulmsgpart)
                nc = cti_command.Command(self, cmd)
                z.extend(nc.parse())
                # print nc.commandid
        return z

    def set_as_transfer(self, direction, faxobj):
        self.log.info('%s set_as_transfer %s' % (faxobj.fileid, direction))
        self.transferconnection = { 'direction' : direction,
                                    'faxobj' : faxobj }
        return

    def reply(self, msg):
        if self.transferconnection:
            if self.transferconnection.get('direction') == 's2c':
                self.connid.sendall(msg)
                self.log.info('transfer connection %d sent' % len(msg))
        else:
            self.connid.sendall(self.serial.encode(msg) + '\n')

    def manage_logout(self, userinfo, when):
        self.log.info('logout (%s) user:%s/%s'
                      % (when, userinfo.get('astid'), userinfo.get('xivo_userid')))
        userinfo['last-logouttimestamp'] = time.time()
        # XXX one could not always logout here + optionnally logout from the client side
        self.__logout_agent__(userinfo.get('astid'), userinfo.get('agentid'))

        self.__disconnect_user__(userinfo)
        self.__fill_user_ctilog__(userinfo, 'cti_logout')
        return


    def loginko(self, errorstring):
        self.log.warning('user can not connect (%s) : sending %s'
                         % (self.details, errorstring))
        # self.logintimer.cancel() + close
        tosend = { 'class' : 'loginko',
                   'error_string' : errorstring }
        return self.serial.encode(tosend)

class CTIS(CTI):
    kind = 'CTIS'

# previous code that was in main daemon file
# XXX : take back the error cases

##    def manage_cti_connections(daemon, connid, msg, sep):
##        """
##        Handles CTI connections.
##        """
##        requester = '%s:%d' % connid.getpeername()
##        if requester in daemon.commandclass.transfers_ref:
##            daemon.commandclass.transfer_addbuf(requester, msg)
##            return

##        multimsg = msg.split(sep)
##        for usefulmsgpart in multimsg:
##            # remove tailing \r
##            usefulmsg = usefulmsgpart.split('\r')[0]
##            if len(usefulmsg) == 0:
##                break
##            command = daemon.commandclass.parsecommand(usefulmsg)
##            if command.name in daemon.commandclass.get_list_commands():
##                try:
##                    commandtype_list = [xivo_commandsets.CMD_LOGIN_ID,
##                                        xivo_commandsets.CMD_LOGIN_PASS,
##                                        xivo_commandsets.CMD_LOGIN_CAPAS]
##                    if command.type in commandtype_list:
##                        # log.info('LOGIN(%s) %s : args   %s' % (command.type, requester, command.args))
##                        loginparams = daemon.commandclass.get_login_params(command, daemon.asterisklist[0], connid)
##                        # log.info('LOGIN(%s) %s : params %s' % (command.type, requester, loginparams))
##                        uinfo = daemon.commandclass.manage_login(loginparams, command.type, daemon.userinfo_current.get(connid))
##                        # log.info('LOGIN(%s) %s : uinfo  %s' % (command.type, requester, uinfo))

##                        if isinstance(uinfo, str):
##                            daemon.commandclass.loginko(loginparams, uinfo, connid)
##                            log.info('TCP socket %s closed(loginko) on %s'
##                                     % (daemon.fdlist_established[connid], requester))
##                            del daemon.fdlist_established[connid]
##                            connid.close()
##                        else:
##                            if command.type == xivo_commandsets.CMD_LOGIN_CAPAS:
##                                uinfo['login']['connection'] = connid
##                                daemon.userinfo_by_requester[connid] = uinfo
##                                if connid in daemon.userinfo_current:
##                                    del daemon.userinfo_current[connid]
##                            else:
##                                daemon.userinfo_current[connid] = uinfo
##                            daemon.commandclass.loginok(loginparams, uinfo, connid, command.type)
##                    elif command.type == xivo_commandsets.CMD_TRANSFER:
##                        log.info('TRANSFER on %s : %s' % (requester, command.struct))
##                        daemon.commandclass.transfer_addref(connid, command.struct)
##                    else:
##                        if connid in daemon.userinfo_by_requester:
##                            daemon.commandclass.manage_cticommand(daemon.userinfo_by_requester[connid], command)
##                        else:
##                            log.warning('unlogged %s is attempting a %s (TCP) : %s'
##                                        % (requester, command.name, command.args))
##                except Exception:
##                    log.exception('CTI connection when managing [%s, %s] for %s'
##                                  % (command.name, command.type, requester))
##            else:
##                connid.sendall('Unknown Command <%s>\n' % command.name)



class OldLoginFromXivoCTIDummy:
    def manage_login(self, loginparams, phase, uinfo):
        if phase == xivo_commandsets.CMD_LOGIN_ID:

            # warns that the former session did not exit correctly (on a given computer)
            if 'lastlogout-stopper' in loginparams and 'lastlogout-datetime' in loginparams:
                if not loginparams['lastlogout-stopper'] or not loginparams['lastlogout-datetime']:
                    log.warning('lastlogout userid=%s stopper=%s datetime=%s'
                                % (loginparams['userid'],
                                   loginparams['lastlogout-stopper'],
                                   loginparams['lastlogout-datetime']))


        elif phase == xivo_commandsets.CMD_LOGIN_PASS:

            iserr = self.__check_user_connection__(userinfo)

        elif phase == xivo_commandsets.CMD_LOGIN_CAPAS:
            iserr = self.__check_capa_connection__(userinfo, capaid)
            if iserr is not None:
                return iserr

            self.__connect_user__(userinfo, state, capaid, lastconnwins)

            if loginkind == 'agent':
                userinfo['agentphonenumber'] = loginparams.get('agentphonenumber')
            if subscribe is not None:
                userinfo['subscribe'] = 0
        else:
            userinfo = None
        return userinfo

    def manage_logout(self, userinfo, when):
        log.info('logout (%s) user:%s/%s'
                 % (when, userinfo.get('astid'), userinfo.get('xivo_userid')))
        userinfo['last-logouttimestamp'] = time.time()
        # XXX one could not always logout here + optionnally logout from the client side
        self.__logout_agent__(userinfo.get('astid'), userinfo.get('agentid'))

        self.__disconnect_user__(userinfo)
        self.__fill_user_ctilog__(userinfo, 'cti_logout')
        return

    def __check_user_connection__(self, userinfo):
        if userinfo.has_key('login') and userinfo['login'].has_key('sessiontimestamp'):
            dt = time.time() - userinfo['login']['sessiontimestamp']
            log.warning('user %s already connected from %s (%.1f s)'
                        % (userinfo['user'], userinfo['login']['connection'].getpeername(), dt))
            # TODO : make it configurable.
            lastconnectedwins = True
            #lastconnectedwins = False
            if lastconnectedwins:
                self.manage_logout(userinfo, 'newconnection')
            else:
                return 'already_connected:%s:%d' % userinfo['login']['connection'].getpeername()
        return None

    def __connect_user__(self, userinfo, state, capaid, lastconnwins):
        try:
            userinfo['capaid'] = capaid
            userinfo['login'] = {}
            userinfo['login']['sessiontimestamp'] = userinfo['login']['logintimestamp'] = time.time()
            for v, vv in userinfo['prelogin'].iteritems():
                userinfo['login'][v] = vv
            del userinfo['prelogin']
            # lastconnwins was introduced in the aim of forcing a new connection to take on for
            # a given user, however it might breed problems if the previously logged-in process
            # tries to reconnect ... unless we send something asking to Kill the process
            userinfo['lastconnwins'] = lastconnwins

            # we first check if 'state' has already been set for this customer, in which case
            # the CTI clients will be sent back this previous state
            presenceid = self.capas[capaid].presenceid
            if 'state' in userinfo:
                futurestate = userinfo.get('state')
                # only if it was a "defined" state anyway
                if presenceid in self.presence_sections and futurestate in self.presence_sections[presenceid].getstates():
                    state = futurestate

            if presenceid in self.presence_sections:
                if state in self.presence_sections[presenceid].getstates() and state not in ['onlineoutgoing', 'onlineincoming']:
                    userinfo['state'] = state
                else:
                    log.warning('(user %s) : state <%s> is not an allowed one => <%s>'
                                % (userinfo.get('user'), state,
                                   self.presence_sections[presenceid].getdefaultstate()))
                    userinfo['state'] = self.presence_sections[presenceid].getdefaultstate()
            else:
                userinfo['state'] = 'xivo_unknown'

            self.__presence_action__(userinfo.get('astid'),
                                     userinfo.get('agentid'),
                                     userinfo)

            self.capas[capaid].conn_inc()
        except Exception:
            log.exception('connect_user %s' % userinfo)
        return

    def __disconnect_user__(self, userinfo, type = 'force'):
        try:
            # state is unchanged
            if 'login' in userinfo:
                capaid = userinfo.get('capaid')
                self.capas[capaid].conn_dec()
                userinfo['last-version'] = userinfo['login']['version']
                # ask the client to disconnect
                if not userinfo['login']['connection'].isClosed:
                    userinfo['login']['connection'].send(self.__cjson_encode__({'class' : 'disconnect', 'type' : type}) + '\n')
                    # make sure everything is sent before closing the connection
                    userinfo['login']['connection'].toClose = True
                del userinfo['login']
                if 'agentphonenumber' in userinfo:
                    del userinfo['agentphonenumber']
                userinfo['state'] = 'xivo_unknown'
                self.__update_availstate__(userinfo, userinfo.get('state'))
                # do not remove 'capaid' in order to keep track of it
                # del userinfo['capaid'] # after __update_availstate__
            else:
                log.warning('userinfo does not contain login field : %s' % userinfo)
        except Exception:
            log.exception('disconnect_user %s' % userinfo)
        return

    def loginko(self, loginparams, errorstring, connid):
        log.warning('user can not connect (%s) : sending %s' % (loginparams, errorstring))
        # self.logintimer.cancel() + close
        tosend = { 'class' : 'loginko',
                   'error_string' : errorstring }
        connid.sendall('%s\n' % self.__cjson_encode__(tosend))
        return

    def telldisconn(self, connid):
        tosend = { 'class' : 'disconn' }
        connid.sendall('%s\n' % self.__cjson_encode__(tosend))
        return

    def loginok(self, loginparams, userinfo, connid, phase):
        if phase == xivo_commandsets.CMD_LOGIN_ID:
            tosend = { 'class' : 'login_id_ok',
                       'xivoversion' : XIVOVERSION_NUM,
                       'version' : __revision__,
                       'sessionid' : userinfo['prelogin']['sessionid'] }
            repstr = self.__cjson_encode__(tosend)
        elif phase == xivo_commandsets.CMD_LOGIN_PASS:
            tosend = { 'class' : 'login_pass_ok',
                       'capalist' : userinfo.get('capaids') }
            repstr = self.__cjson_encode__(tosend)
        elif phase == xivo_commandsets.CMD_LOGIN_CAPAS:
            astid = userinfo.get('astid')
            context = userinfo.get('context')
            capaid = userinfo.get('capaid')

            presenceid = self.capas[capaid].presenceid
            if presenceid in self.presence_sections:
                allowed = self.presence_sections[presenceid].allowed(userinfo.get('state'))
                details = self.presence_sections[presenceid].getdisplaydetails()
                statedetails = self.presence_sections[presenceid].displaydetails[userinfo.get('state')]
            else:
                allowed = {}
                details = {}
                statedetails = {}

            tosend = { 'class' : 'login_capas_ok',
                       'astid' : astid,
                       'xivo_userid' : userinfo.get('xivo_userid'),
                       'capafuncs' : self.capas[capaid].tostringlist(self.capas[capaid].all()),
                       'capaxlets' : self.capas[capaid].capadisps,
                       'appliname' : self.capas[capaid].appliname,
                       'guisettings' : self.capas[capaid].getguisettings(),
                       'capapresence' : { 'names'   : details,
                                          'state'   : statedetails,
                                          'allowed' : allowed },
                       'capaservices' : self.capas[capaid].capaservices
                       }

            repstr = self.__cjson_encode__(tosend)
            # if 'features' in capa_user:
            # repstr += ';capas_features:%s' %(','.join(configs[astid].capafeatures))
            # logintimer.cancel() + close
            self.__fill_user_ctilog__(userinfo, 'cti_login',
                                      'ip=%s,port=%d,version=%s,os=%s,capaid=%s'
                                      % (connid.getpeername()[0],
                                         connid.getpeername()[1],
                                         userinfo.get('login').get('version'),
                                         userinfo.get('login').get('cticlientos'),
                                         userinfo.get('capaid')
                                         ))
        connid.sendall(repstr + '\n')

        if phase == xivo_commandsets.CMD_LOGIN_CAPAS:
            self.__update_availstate__(userinfo, userinfo.get('state'))

        return
