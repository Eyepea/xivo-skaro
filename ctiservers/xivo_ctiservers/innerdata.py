# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision: 10133 $'
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

import copy
import hashlib
import logging
import os
import sys
import threading
import time
import Queue
from xivo_ctiservers import lists
from xivo_ctiservers.lists import *
from xivo_ctiservers import cti_sheets

log = logging.getLogger('safedeposit')

class Safe:
    # matches between CTI lists and WEBI-given fields
    urlvars = {
        'users'  : 'urllist_users',
        'phones' : 'urllist_lines',
        # 'devices' : 'urllist_devices',
        'trunks' : 'urllist_trunks',

        'agents' : 'urllist_agents',
        'queues' : 'urllist_queues',
        'groups' : 'urllist_groups',
        'meetmes' : 'urllist_meetmes',
        'voicemails' : 'urllist_voicemails',
        'incalls' : 'urllist_incalls',
        'outcalls' : 'urllist_outcalls',
        'contexts' : 'urllist_contexts',

        'phonebooks' : 'urllist_phonebook'
        }

##[{"id":1,"firstname":"Bmwgsjr","lastname":"Ponciuj","voicemailtype":null,"voicemailid":null,"agentid":null,
##  "entityid":1,"callerid":"\"Bmwgsjr Ponciuj\"","ringseconds":"30","simultcalls":"5","enableclient":true,
##  "loginclient":"dsfsdf","passwdclient":"azeae","profileclient":"client","enablehint":true,"enablevoicemail":false,
##  "enablexfer":false,"enableautomon":false,"callrecord":false,"incallfilter":false,"enablednd":false,
##  "enableunc":false,"destunc":"","enablerna":false,"destrna":"","enablebusy":false,"destbusy":"","musiconhold":"",
##  "outcallerid":"default","mobilephonenumber":"","bsfilter":"no","preprocess_subroutine":null,"timezone":"",
##  "language":null,"ringintern":"","ringextern":"","ringgroup":"","ringforward":"","rightcallcode":"",
##  "alarmclock":"00:00","pitch":null,"pitchdirection":null,"commented":false,"description":"",
##  "fullname":"Bmwgsjr Ponciuj","identity":"Bmwgsjr Ponciuj","queueskills":[]}]

##[{"id":1,"name":"0c624c","type":"friend","username":null,"secret":"JZ7JIJ",
##  "md5secret":"11e29f53222b746c4f6c563c7ee23a29","context":"mamaop","language":null,"accountcode":null,
##  "amaflags":"default","allowtransfer":null,"fromuser":null,"fromdomain":null,"mailbox":null,"subscribemwi":"0",
##  "buggymwi":null,"call-limit":"10","callerid":"\"Bmwgsjr Ponciuj\" <1111>","fullname":null,"cid_number":null,
##  "maxcallbitrate":null,"insecure":null,"nat":null,"promiscredir":null,"usereqphone":null,"videosupport":null,
##  "trustrpid":null,"sendrpid":null,"allowsubscribe":null,"allowoverlap":null,"dtmfmode":null,
##  "rfc2833compensate":null,"qualify":null,"g726nonstandard":null,"disallow":null,"allow":null,"autoframing":null,
##  "mohinterpret":null,"mohsuggest":null,"useclientcode":null,"progressinband":null,"t38pt_udptl":null,
##  "t38pt_usertpsource":null,"rtptimeout":null,"rtpholdtimeout":null,"rtpkeepalive":null,"deny":null,"permit":null,
##  "defaultip":null,"setvar":"","host":"dynamic","port":null,"regexten":null,"subscribecontext":null,"vmexten":null,
##  "callingpres":null,"ipaddr":"","regseconds":"0","regserver":null,"lastms":"","parkinglot":null,"protocol":"sip",
##  "category":"user","outboundproxy":null,"transport":null,"remotesecret":null,"directmedia":null,"callcounter":null,
##  "busylevel":null,"ignoresdpversion":null,"session-timers":null,"session-expires":null,"session-minse":null,
##  "session-refresher":null,"callbackextension":null,"registertrying":null,"timert1":null,"timerb":null,
##  "qualifyfreq":null,"contactpermit":null,"contactdeny":null,"unsolicited_mailbox":null,"use_q850_reason":null,
##  "encryption":false,"snom_aoc_enabled":null,"maxforwards":null,"disallowed_methods":null,"textsupport":null,
##  "commented":false,"callgroup":null,"pickupgroup":null,"initialized":false,"identity":"SIP\/0c624c",
##  "protocolid":7,"iduserfeatures":1,"number":"1111","provisioningid":119921,"rules_type":"","rules_time":"",
##  "rules_order":0,"rules_group":"","internal":false,"description":"","useridentity":"Bmwgsjr Ponciuj"}]

    # defines the list of parameters that might be sent to xivo clients
    props_config = { 'users' : ['loginclient',
                                'number',
                                'mobilephonenumber',
                                'firstname', 'lastname', 'fullname',
                                'entityid', # XXX (for entity/context relations)

                                'id', # since users and phones are the same, this is a pointer to the phone id
                                'agentid',
                                'voicemailid',
                                #
                                'simultcalls'
                                ],
                     'phones' : ['context', 'protocol', 'number',
                                 'firstname', 'lastname',
                                 'call-limit', 'simultcalls', 'dtmfmode', 'language', 'ringseconds',
                                 # rpid's
                                 # services
                                 'enablerna', 'enableunc', 'enablebusy',
                                 'destrna', 'destunc', 'destbusy',
                                 # 'bsfilter',
                                 'enablevoicemail', 'enablednd', 'enableautomon', 'enablexfer',
                                 'callrecord', 'incallfilter',
                                 # other
                                 'initialized', 'outcallerid', 'allowtransfer'],
                     'agents' : ['context', 'firstname', 'lastname', 'number', 'ackcall', 'wrapuptime'],
                     'queues' : ['context', 'name', 'number'],
                     'groups': ['context', 'name', 'number'],
                     'trunks': ['context', 'protocol', 'name', 'host', 'type'],
                     'voicemails' : ['context', 'fullname', 'mailbox', 'email'], # password
                     'meetmes' : ['context', 'number', 'name', 'admin_moderationmode',
                                  'pin_needed'], # 'pin', 'pinadmin' should not be transmitted
                     'incalls' : ['context', 'exten', 'destidentity', 'action'],
                     'outcalls' : [],
                     'contexts' : [],
                     }

    props_status = { 'users' : { 'mwi' : [],
                                 'availstate' : 'unknown'
                                 },
                     'phones' : { 'hintstatus' : '-4',
                                  'channels' : [],
                                  'queues' : [],
                                  'groups' : []
                                  },
                     'trunks' : { 'hintstatus' : '-4',
                                  'channels' : [],
                                  'queues' : [],
                                  'groups' : []
                                  },

                     'agents' : { 'phonenumber' : '',
                                  # channel for static login cases
                                  'status' : '', # statuses are AGENT_LOGGEDOFF, _ONCALL, _IDLE and '' (undefined)
                                  'queues' : [],
                                  'groups' : []
                                  },

                     'queues' : { 'agentmembers' : [],
                                  'phonemembers' : [],
                                  'incalls' : []
                                  },
                     'groups' : { 'agentmembers' : [],
                                  'phonemembers' : [],
                                  'incalls' : []
                                  },
                     'meetmes' : { 'pseudochan' : None,
                                   'channels' : []
                                   },
                     'voicemails' : {},
                     'incalls' : {},
                     'outcalls' : {},
                     'contexts' : {},
                     }

    user_props_send_extra = ['mailbox', 'subscribemwi', 'pickupgroup', 'callgroup', 'callerid']
    # 'queueskills',
    # links towards other properties

    def __init__(self, ctid, ipbxid, cnf):
        self.ctid = ctid
        self.ipbxid = ipbxid
        self.weblist = {}
        self.webstatus = {}

        self.events_cti = Queue.Queue()
        self.timeout_queue = Queue.Queue()

        self.channels = {}
        self.queuemembers = {}

        self.ctistack = []

        self.fagisync = {}
        self.fagichannels = {}

        for listname, urllistkey in self.urlvars.iteritems():
            try:
                if cnf.has_key(urllistkey):
                    cf = eval('lists.cti_%slist' % listname[:-1])
                    cn = '%s%sList' % (listname[0].upper(), listname[1:-1])
                    self.weblist[listname] = getattr(cf, cn)(cnf.get(urllistkey)) # urllist, { 'conf' : self.lconf })
                    self.weblist[listname].setcommandclass(self)
                    self.weblist[listname].setgetter('get_x_list')
                    self.webstatus[listname] = {}
                else:
                    log.warning('no such key %s in configuration' % urllistkey)
            except Exception:
                log.exception(listname)
        return

    def update_config_list_all(self):
        for listname, urllistkey in self.urlvars.iteritems():
            self.update_config_list(listname)
        return

    def update_config_list(self, listname):
        if listname not in self.weblist:
            log.warning('no such listname %s' % listname)
        try:
            deltas = self.weblist[listname].update()
            for k in deltas.get('add'):
                self.webstatus[listname][k] = {}
                for prop, defaultvalue in self.props_status.get(listname, {}).iteritems():
                    self.webstatus[listname][k][prop] = copy.copy(defaultvalue)
                # tells clients about new object XXX
                self.events_cti.put( { 'class' : 'getlist',
                                       'listname' : listname,
                                       'function' : 'addconfig',
                                       'ipbxid' : self.ipbxid,
                                       'list' : [k]
                                       } )
            if deltas.get('del'):
                for k in deltas.get('del'):
                    del self.webstatus[listname][k]
                # tells clients about deleted object XXX
                self.events_cti.put( { 'class' : 'getlist',
                                       'listname' : listname,
                                       'function' : 'delconfig',
                                       'ipbxid' : self.ipbxid,
                                       'list' : deltas.get('del')
                                       } )
            for id, v in deltas.get('change').iteritems():
                props = self.weblist[listname].keeplist[id]
                newc = {}
                for p in v:
                    if p in self.props_config.get(listname):
                        newc[p] = props[p]
                # tells clients about changed object
                self.events_cti.put( { 'class' : 'getlist',
                                       'listname' : listname,
                                       'function' : 'updateconfig',
                                       'ipbxid' : self.ipbxid,
                                       'id' : id,
                                       'config' : newc
                                       } )
        except Exception:
            log.exception('update_config_list %s' % listname)
        return

    def get_x_list(self, xlist):
        lxlist = {}
        for xitem in xlist:
            try:
                if not xitem.get('commented'):
                    if 'id' in xitem:
                        key = xitem.get('id')
                    else:
                        key = xitem.get('uniqueid') # this is the case for voicemail XXX
                    lxlist[key] = xitem
                    # meetme : admin_moderationmode => moderated
                    # meetme : uniqueids and adminnum statuses
            except Exception:
                log.exception('(get_x_list : %s)' % xitem)
        return lxlist



    def user_find(self, ctilogin, company):
        uinfo = self.weblist['users'].finduser(ctilogin, company)
        return uinfo.get('id')

    def user_status(self, userid):
        print self.weblist['users'].keeplist[userid]
        return

    def user_get_hashed_password(self, userid, sessionid):
        tohash = '%s:%s' % (sessionid,
                            self.weblist['users'].keeplist[userid].get('passwdclient'))
        sha1sum = hashlib.sha1(tohash).hexdigest()
        return sha1sum

    def user_get_ctiprofile(self, userid):
        return self.weblist['users'].keeplist[userid].get('profileclient')

    def user_get_all(self):
        return self.weblist['users'].keeplist.keys()

    def get_config(self, listname, id, limit = None):
        reply = {}
        configdict = self.weblist.get(listname).keeplist
        if not isinstance(configdict, dict):
            log.warning('get_config : problem with listname %s' % listname)
            return reply
        periddict = configdict.get(id)
        if not isinstance(periddict, dict):
            log.warning('get_config : problem with id %s in listname %s' % (id, listname))
            return reply

        if limit:
            for k in limit:
                if k in self.props_config.get(listname, []):
                    reply[k] = periddict.get(k)
        else:
            for k in self.props_config.get(listname, []):
                reply[k] = periddict.get(k)
        return reply

    def get_status_channel(self, id, limit = None):
        reply = {}
        if id in self.channels:
            reply = self.channels[id].properties
        return reply

    def get_status_queuemembers(self, id, limit = None):
        reply = {}
        if id in self.queuemembers:
            reply = self.queuemembers[id]
        return reply

    def get_status(self, listname, id, limit = None):
        if listname == 'channels':
            return self.get_status_channel(id, limit)
        if listname == 'queuemembers':
            return self.get_status_queuemembers(id, limit)
        reply = {}
        statusdict = self.webstatus.get(listname)
        if not isinstance(statusdict, dict):
            log.warning('get_status : problem with listname %s' % listname)
            return reply
        periddict = statusdict.get(id)
        if not isinstance(periddict, dict):
            log.warning('get_status : problem with id %s in listname %s' % (id, listname))
            return reply

        if limit:
            for k in limit:
                if k in self.props_status.get(listname, {}):
                    reply[k] = periddict.get(k)
        else:
            for k in self.props_status.get(listname, {}):
                reply[k] = periddict.get(k)

        return reply

    def autocall(self, channel, actionid):
        log.info('autocall %s %s' % (channel, actionid))

    def newstate(self, channel, state):
        self.channels[channel].update_state(state)

    def newchannel(self, channel, context, state):
        if not channel:
            return
        if channel not in self.channels:
            # might occur when requesting channels at launch time
            self.channels[channel] = Channel(channel, context)
            self.handle_cti_stack('setforce', ('channels', 'updatestatus', channel))
        self.updaterelations(channel)
        self.channels[channel].update_state(state)
        self.handle_cti_stack('empty_stack')
        return

    def meetmeupdate(self, confno, channel = None, opts = {}):
        mid = self.weblist['meetmes'].idbyroomnumber(confno)
        self.handle_cti_stack('set', ('meetmes', 'updatestatus', mid))
        if channel:
            self.handle_cti_stack('set', ('channels', 'updatestatus', channel))
            usernum = opts.get('usernum')
            pseudochan = opts.get('pseudochan')
            admin = opts.get('admin')
            if pseudochan:
                # (join)
                self.webstatus['meetmes'][mid]['pseudochan'] = pseudochan
                if channel not in self.webstatus['meetmes'][mid]['channels']:
                    self.webstatus['meetmes'][mid]['channels'].append(channel)
                self.channels[channel].properties['meetme_isadmin'] = admin
                self.channels[channel].properties['meetme_usernum'] = usernum
            else:
                # (leave)
                if channel in self.webstatus['meetmes'][mid]['channels']:
                    self.webstatus['meetmes'][mid]['channels'].remove(channel)
        else:
            self.webstatus['meetmes'][mid]['pseudochan'] = None
            self.webstatus['meetmes'][mid]['channels'] = []
        self.handle_cti_stack('empty_stack')
        return

    def agentlogin(self, agentnumber, channel):
        idx = self.weblist['agents'].idbyagentnumber(agentnumber)
        self.handle_cti_stack('set', ('agents', 'updatestatus', idx))
        agstatus = self.webstatus['agents'].get(idx)
        agstatus['channel'] = channel
        agstatus['status'] = 'AGENT_IDLE'
        # define relations for agent:x : channel:y and phone:z
        self.handle_cti_stack('empty_stack')
        return

    def agentlogout(self, agentnumber):
        idx = self.weblist['agents'].idbyagentnumber(agentnumber)
        self.handle_cti_stack('set', ('agents', 'updatestatus', idx))
        agstatus = self.webstatus['agents'].get(idx)
        agstatus['status'] = 'AGENT_LOGGEDOFF'
        del agstatus['channel']
        # define relations for agent:x : channel:y and phone:z
        self.handle_cti_stack('empty_stack')
        return

    def agentstatus(self, agentnumber, status):
        idx = self.weblist['agents'].idbyagentnumber(agentnumber)
        self.handle_cti_stack('set', ('agents', 'updatestatus', idx))
        agstatus = self.webstatus['agents'].get(idx)
        agstatus['status'] = status
        # define relations for agent:x : channel:y and phone:z
        self.handle_cti_stack('empty_stack')
        return

    def queuememberupdate(self, queuename, location, props = None):
        qid = self.weblist['queues'].idbyqueuename(queuename)
        # send a notification event if no new member
        self.handle_cti_stack('set', ('queues', 'updatestatus', qid))
        midx = None
        if location.startswith('Agent/'):
            aid = self.weblist['agents'].idbyagentnumber(location[6:])
            self.handle_cti_stack('set', ('agents', 'updatestatus', aid))
            midx = 'qa:%s-%s' % (qid, aid)
            # todo : group all this stuff, take care of relations
            if props:
                if aid not in self.webstatus['queues'][qid]['agentmembers']:
                    self.webstatus['queues'][qid]['agentmembers'].append(aid)
                if qid not in self.webstatus['agents'][aid]['queues']:
                    self.webstatus['agents'][aid]['queues'].append(qid)
            else:
                if aid in self.webstatus['queues'][qid]['agentmembers']:
                    self.webstatus['queues'][qid]['agentmembers'].remove(aid)
                if qid in self.webstatus['agents'][aid]['queues']:
                    self.webstatus['agents'][aid]['queues'].remove(qid)
        else:
            termination = self.ast_channel_to_termination(location)
            pid = self.zphones(termination.get('protocol'), termination.get('name'))
            if pid:
                self.handle_cti_stack('set', ('phones', 'updatestatus', pid))
                midx = 'qp:%s-%s' % (qid, pid)
                if props:
                    if pid not in self.webstatus['queues'][qid]['phonemembers']:
                        self.webstatus['queues'][qid]['phonemembers'].append(pid)
                    if qid not in self.webstatus['phones'][pid]['queues']:
                        self.webstatus['phones'][pid]['queues'].append(qid)
                else:
                    if pid in self.webstatus['queues'][qid]['phonemembers']:
                        self.webstatus['queues'][qid]['phonemembers'].remove(pid)
                    if qid in self.webstatus['phones'][pid]['queues']:
                        self.webstatus['phones'][pid]['queues'].remove(qid)

        if props:
            self.handle_cti_stack('set', ('queuemembers', 'updatestatus', midx))
            if len(props) == 6:
                (status, paused, membership, callstaken, penalty, lastcall) = props
                snew = {
                    'status' : status,
                    'paused' : paused,
                    'membership' : membership,
                    'callstaken' : callstaken,
                    'penalty' : penalty,
                    'lastcall' : lastcall,
                    }
            elif len(props) == 1:
                (paused,) = props
                snew = { 'paused' : paused }
            if midx not in self.queuemembers:
                self.queuemembers[midx] = {}
            for k, v in snew.iteritems():
                self.queuemembers[midx][k] = v

        else:
            del self.queuemembers[midx]
            self.events_cti.put({'class' : 'getlist',
                                 'listname' : 'queuemembers',
                                 'function' : 'delconfig',
                                 'ipbxid' : self.ipbxid,
                                 'list' : [midx]
                                 })

        # send cti events in reverse order in order for the queuemember details to be received first
        self.handle_cti_stack('empty_stack')
        return

    def queueentryupdate(self, queuename, channel, position, timestart = None):
        qid = self.weblist['queues'].idbyqueuename(queuename)
        # send a notification event if no new member
        self.handle_cti_stack('set', ('queues', 'updatestatus', qid))
        incalls = self.webstatus['queues'][qid]['incalls']
        if timestart:
            if channel not in incalls:
                if int(position) != len(incalls) + 1:
                    # can it occur ? : for meetme, it occurs when 2 people join the room almost
                    # simultaneously as first and second members
                    log.warning('queueentryupdate (add) : mismatch between %d and %d'
                                % (int(position), len(incalls) + 1))
                incalls.append(channel)
            if channel in self.channels:
                self.handle_cti_stack('set', ('channels', 'updatestatus', channel))
                self.channels[channel].addrelation('queue:%s' % qid)
        else:
            if int(position) != incalls.index(channel) + 1:
                log.warning('queueentryupdate (del) : mismatch between %d and %d'
                            % (int(position), incalls.index(channel) + 1))
            incalls.remove(channel)
            if channel in self.channels:
                self.handle_cti_stack('set', ('channels', 'updatestatus', channel))
                self.channels[channel].delrelation('queue:%s' % qid)

        self.handle_cti_stack('empty_stack')
        return

    def update(self, channel):
        chanprops = self.channels.get(channel)
        relations = chanprops.relations
        for r in relations:
            if r.startswith('user:'):
                self.handle_cti_stack('setforce', ('users', 'updatestatus', r[5:]))
            elif r.startswith('phone:'):
                self.handle_cti_stack('setforce', ('phones', 'updatestatus', r[6:]))
        self.handle_cti_stack('setforce', ('channels', 'updatestatus', channel))
        self.handle_cti_stack('empty_stack')
        return

    def statusbylist(self, listname, id):
        status = None
        if listname == 'channels':
            if id in self.channels:
                status = self.channels.get(id).properties
            else:
                log.warning('%s not in channels' % id)
        elif listname == 'queuemembers':
            if id in self.queuemembers:
                status = self.queuemembers.get(id)
            else:
                log.warning('%s not in queuemembers' % id)
        else:
            if id in self.webstatus[listname]:
                status = self.webstatus[listname].get(id)
            else:
                log.warning('%s not in webstatus for %s' % (id, listname))
        return status

    def appendcti(self, listname, which, id, status = None):
        if status is None:
            status = self.statusbylist(listname, id)
        if status:
            evt = {
                'class' : 'getlist',
                'listname' : listname,
                'function' : which,
                'ipbxid' : self.ipbxid,
                'id' : id,
                'status' : status
                }
            self.events_cti.put(evt)
        return

    def handle_cti_stack(self, action, event = None):
        """
        The idea behind this method is to fill a list of would-be cti events
        with 'set', retrieve the statuses at this point.
        Later on, with 'empty_stack', one might compare whether and how the statuses
        have changed and send them accordingly ...
        'setforce' empties the first status, in order for the event to be always sent.
        """
        if action == 'set':
            (x, y, z) = event
            thisstatus = copy.deepcopy(self.statusbylist(x, z))
            self.ctistack.append((event, thisstatus))
        elif action == 'setforce':
            self.ctistack.append((event, {}))
        elif action == 'empty_stack':
            while self.ctistack:
                (oldevent, oldstatus) = self.ctistack.pop()
                (x, y, z) = oldevent
                newstatus = self.statusbylist(x, z)
                if oldstatus != newstatus:
                    if oldstatus is None:
                        sendstatus = newstatus
                    else:
                        sendstatus = {}
                        for k, v in newstatus.iteritems():
                            if v != oldstatus.get(k):
                                sendstatus[k] = v
                    oldevent_list = list(oldevent)
                    oldevent_list.append(sendstatus)
                    self.appendcti(* oldevent_list)
        return

    def hangup(self, channel):
        if channel in self.channels:
            relations = self.channels[channel].relations
            for r in relations:
                if r.startswith('phone:'):
                    phoneid = r[6:]
                    chanlist = self.webstatus['phones'][phoneid]['channels']
                    if channel in chanlist:
                        chanlist.remove(channel)
                        self.appendcti('phones', 'updatestatus', phoneid)
                    else:
                        log.warning('%s not in channel list for phoneid %s' % (channel, phoneid))
            del self.channels[channel]
            self.events_cti.put({'class' : 'getlist',
                                 'listname' : 'channels',
                                 'function' : 'delconfig',
                                 'ipbxid' : self.ipbxid,
                                 'list' : [channel]
                                 })
        else:
            log.warning('channel %s not there ...' % channel)
        log.info('remaining channels : %s' % self.channels.keys())
        return

    def updatehint(self, hint, status):
        termination = self.ast_channel_to_termination(hint)
        p = self.zphones(termination.get('protocol'), termination.get('name'))
        if p:
            oldstatus = self.webstatus['phones'][p]['hintstatus']
            self.webstatus['phones'][p]['hintstatus'] = status
            if status != oldstatus:
                self.events_cti.put( { 'class' : 'getlist',
                                       'listname' : 'phones',
                                       'function' : 'updatestatus',
                                       'ipbxid' : self.ipbxid,
                                       'id' : p,
                                       'status' : {'hintstatus' : status}
                                       } )
        return

    def updaterelations(self, channel):
        self.channels[channel].relations = []
        if channel.startswith('SIPPeer/'):
            return
        if channel.startswith('Parking/'):
            return
        try:
            termination = self.ast_channel_to_termination(channel)
            p = self.zphones(termination.get('protocol'), termination.get('name'))
            if p:
                self.channels[channel].addrelation('phone:%s' % p)
                self.channels[channel].properties['thisdisplay'] = self.weblist['phones'].keeplist[p]['fullname']
                oldchans = self.webstatus['phones'][p].get('channels')
                if channel not in oldchans:
                    oldchans.append(channel)
                self.webstatus['phones'][p]['channels'] = oldchans
            t = self.ztrunks(termination.get('protocol'), termination.get('name'))
            if t:
                self.channels[channel].addrelation('trunk:%s' % t)
                oldchans = self.webstatus['trunks'][t].get('channels')
                if channel not in oldchans:
                    oldchans.append(channel)
                self.webstatus['phones'][t]['channels'] = oldchans
        except Exception:
            log.exception('find termination according to channel %s' % channel)
        return

    def masquerade(self, oldchannel, newchannel):
        log.info('masquerading channel %s into %s' % (oldchannel, newchannel))
        oldrelations = self.channels[oldchannel].relations
        newrelations = self.channels[newchannel].relations

        oldchannelz = oldchannel + '<ZOMBIE>'
        self.channels[oldchannelz] = self.channels.pop(newchannel)
        self.channels[oldchannelz].channel = oldchannelz
        self.channels[newchannel] = self.channels.pop(oldchannel)
        self.channels[newchannel].channel = newchannel

        for r in oldrelations:
            if r.startswith('phone:'):
                p = r[6:]
                self.webstatus['phones'][p]['channels'].remove(oldchannel)
                self.channels[newchannel].delrelation(r)
        self.channels[newchannel].relations = newrelations
        newfirstchannel = self.channels[newchannel].peerchannel
        if newfirstchannel:
            self.setpeerchannel(newfirstchannel, newchannel)
        else:
            if oldchannel.startswith('SIPPeer'):
                log.info('no peerchannel setting, since parking action (A) (%s %s)'
                         % (oldchannel, newchannel))
            elif oldchannel.startswith('Parking'):
                log.info('no peerchannel setting, since parking action (B) (%s %s)'
                         % (oldchannel, newchannel))
            else:
                log.warning('no peerchannel setting ... why ? %s %s'
                            % (oldchannel, newchannel))
        return

    def setpeerchannel(self, channel, peerchannel):
        self.channels[channel].peerchannel = peerchannel
        self.channels[channel].properties['talkingto_id'] = peerchannel # XXX
        if peerchannel and self.channels.get(peerchannel).relations:
            for k in self.channels.get(peerchannel).relations:
                if k.startswith('phone'):
                    phoneid = k[6:]
                    self.channels[channel].properties['peerdisplay'] = self.weblist['phones'].keeplist[phoneid]['fullname']
        return

    def currentstatus(self):
        rep = []
        rep.append('* full status on %s' % time.asctime())
        rep.append('* channels')
        for k, v in self.channels.iteritems():
            rep.append('  * %s' % k)
            rep.append('    * relations : %s' % v.relations)
            if v.peerchannel:
                rep.append('    * peerchannel : %s' % v.peerchannel)
            rep.append('    * properties : %s' % v.properties)
        rep.append('* phones')
        for k, v in self.webstatus['phones'].iteritems():
            rep.append('  * %s :' % k)
            if v.get('hintstatus'):
                rep.append('    * hintstatus : %s' % v.get('hintstatus'))
            if v.get('channels'):
                rep.append('    * channels : %s' % v.get('channels'))
        rep.append('* agents')
        for k, v in self.webstatus['agents'].iteritems():
            rep.append('  * %s :' % k)
        rep.append('* queues')
        for k, v in self.webstatus['queues'].iteritems():
            rep.append('  * %s :' % k)
        rep.append('--------------')
        return rep

    def update_presence(self, userid, newstate):
        oldstate = self.webstatus.get('users').get(userid)['availstate']

        profileid = self.user_get_ctiprofile(userid)
        if profileid not in self.ctid.cconf.getconfig('profiles'):
            log.warning('profileid %s (for user %s) not defined in config' % (profileid, userid))
            return
        presenceid = self.ctid.cconf.getconfig('profiles').get(profileid).get('userstatus')
        if presenceid not in self.ctid.cconf.getconfig('userstatus'):
            log.warning('presenceid %s (for user %s) not defined in config' % (presenceid, userid))
            return
        profdetails = self.ctid.cconf.getconfig('userstatus').get(presenceid)

        # allow oldstate to be 'unknown' (as might be the case when connecting ...)
        if oldstate not in profdetails and oldstate not in ['unknown']:
            log.warning('old state %s (for user %s) not defined in config' % (oldstate, userid))
            return
        if newstate not in profdetails:
            log.warning('new state %s (for user %s) not defined in config' % (newstate, userid))
            return

        # XXX check on allowed states old => new
        # XXX check on ipbx-related state
        # XXX check on connected state of userid
        truestate = newstate
        if truestate != oldstate:
            self.webstatus.get('users').get(userid)['availstate'] = truestate
            self.appendcti('users', 'updatestatus', userid)
            # XXX call presence_action
        return

    def presence_action(self):
        # XXX
        return

    def ast_channel_to_termination(self, channel):
        term = {}
        # special cases : AsyncGoto/IAX2/asteriskisdn-13622<ZOMBIE>
        # Parked/SIP, Parked/IAX2, SCCP, DAHDI, Parked/SCCP ...
        # what about a peer called a-b-c ?
        cutchan1 = channel.split('/')
        if len(cutchan1) == 2:
            protocol = cutchan1[0]
            cutchan2 = cutchan1[1].split('-')
            name = cutchan2[0]
            term = {'protocol' : protocol, 'name' : name}
            if len(cutchan2) > 1:
                chanid = cutchan2[1]
            else:
                log.warning('%s is not a channel per-se' % cutchan2)
        elif len(cutchan1) < 2:
            log.warning('not enough /es in %s' % cutchan1)
        elif len(cutchan1) > 2:
            log.warning('too much /es in %s ?' % cutchan1)
        return term

    def zphones(self, protocol, name):
        idfound = None
        for k, v in self.weblist['phones'].keeplist.iteritems():
            if v.get('protocol') == protocol.lower() and v.get('name') == name:
                idfound = k
                break
        # print self.webstatus['phones']
        return idfound

    def ztrunks(self, protocol, name):
        idfound = None
        for k, v in self.weblist['trunks'].keeplist.iteritems():
            if v.get('protocol') == protocol.lower() and v.get('name') == name:
                idfound = k
                break
        # print self.webstatus['trunks']
        return idfound

    def sheetsend(self, where, channel, outdest = None):
        if 'sheets' not in self.ctid.cconf.getconfig():
            return
        bsheets = self.ctid.cconf.getconfig('sheets')
        self.sheetevents = bsheets.get('sheetevents')
        self.sheetdisplays = bsheets.get('sheetdisplays')
        self.sheetoptions = bsheets.get('sheetoptions')
        self.sheetconditions = bsheets.get('sheetconditions')

        if where not in self.sheetevents:
            return
        if channel not in self.channels:
            return
        for se in self.sheetevents[where]:
            display_id, condition_id, option_id = se
            if not self.sheetdisplays.get(display_id):
                continue
            # print channel, self.sheetdisplays.get(display_id), self.sheetconditions.get(condition_id)
            c = self.channels[channel]

            sheet = cti_sheets.Sheet(where, self.ipbxid, channel)
            if self.sheetoptions.get(option_id):
                sheet.setoptions(self.sheetoptions.get(option_id))
            # 1. whom / userinfos : according to outdest or destlist to update in Channel structure
            # 2. make an extra call to a db if requested ? could be done elsewhere (before) also ...
            # 3. build sheet items (according to values)
            # 4. sheet construct (according to serialization)
            sheet.makexml()
            sheet.buildpayload()
            # 5. sheet manager ?
            # 6. json message / zip or not / b64 / ...
            self.events_cti.put( { 'class' : 'sheet',
                                   'channel' : channel,
                                   'compressed' : sheet.compressed,
                                   'payload' : sheet.payload,
                                   } )
            # 7. send the payload

    # Timers/Synchro stuff - begin

    def checkqueue(self):
        log.info('entering checkqueue')
        ncount = 0
        while self.timeout_queue.qsize() > 0:
            ncount += 1
            (toload,) = self.timeout_queue.get()
            action = toload.get('action')
            if action == 'fagi_noami':
                fagistruct = toload.get('properties')
                # XXX maybe we could handle the AGI data nevertheless ?
                self.fagi_close(fagistruct, {'XIVO_CTI_AGI' : 'FAIL'})
            # other cases to handle : login, agentlogoff (would that still be true ?)
        return ncount

    def cb_timer(self, *args):
        try:
            log.info('cb_timer (timer finished at %s) %s' % (time.asctime(), args))
            self.timeout_queue.put(args)
            os.write(self.ctid.pipe_queued_threads[1], 'innerdata:%s\n' % self.ipbxid)
        except Exception:
            log.exception('cb_timer %s' % args)
        return

    # Timers/Synchro stuff - end

    # FAGI stuff - begin
    # all this should handle the following cases (see also interface_fagi file) :
    # - AMI is connected and newexten 'AGI' (on ~ 5003) comes before the AGI (on ~ 5002) (often)
    # - AMI is connected and newexten 'AGI' (on ~ 5003) comes after the AGI (on ~ 5002) (sometimes)
    # - AMI is NOT connected and an AGI comes (on ~ 5002)

    def fagi_sync(self, action, channel, where = None):
        if action == 'set':
            if channel not in self.fagisync:
                self.fagisync[channel] = []
            self.fagisync[channel].append(where)
        elif action == 'get':
            if channel not in self.fagisync:
                self.fagisync[channel] = []
            return (where in self.fagisync[channel])
        elif action == 'clear':
            if channel in self.fagisync:
                del self.fagisync[channel]
        return

    def fagi_close(self, fagistruct, varstoset):
        channel = fagistruct.channel
        try:
            cid = fagistruct.connid
            for k, v in varstoset.iteritems():
                cid.sendall('SET VARIABLE %s "%s"\n' % (k, v))
            cid.close()
            del self.ctid.fdlist_established[cid]
            del self.fagichannels[channel]
        except Exception:
            log.exception('problem when closing channel %s' % channel)
        return

    def fagi_setup(self, fagistruct):
        if fagistruct.channel in self.fagichannels:
            log.warning('fagi_setup for %s already done ... (%s)'
                        % (fagistruct.channel, fagistruct.agidetails.get('agi_network_script')))
        tm = threading.Timer(0.2, self.cb_timer, ({'action' : 'fagi_noami',
                                                   'properties' : fagistruct},))
        self.fagichannels[fagistruct.channel] = { 'timer' : tm,
                                                  'fagistruct' : fagistruct }
        tm.setName('Thread-fagi-%s' % fagistruct.channel)
        tm.start()
        return

    def fagi_handle(self, channel, where):
        log.info('handle FAGI for channel %s, sync comes from %s' % (channel, where))
        if channel not in self.fagichannels:
            log.warning('fagi_setup for %s not done' % channel)
            return

        # handle fagi event
        fagistruct = self.fagichannels[channel]['fagistruct']
        timer = self.fagichannels[channel]['timer']
        timer.cancel()
        agievent = fagistruct.agidetails
        log.info('handle FAGI for channel %s : %s' % (channel, agievent))

        try:
            varstoset = self.fagi_handle_real(agievent)
        except:
            log.exception('for channel %s' % channel)
            varstoset = {}

        # the AGI handling has been done, exiting ...
        self.fagi_close(fagistruct, varstoset)
        return

    def fagi_handle_real(self, agievent):
        # check capas !
        varstoset = {}
        log.info('agievent %s' % agievent)
        try:
            function = agievent.get('agi_network_script')
            uniqueid = agievent.get('agi_uniqueid')
            channel  = agievent.get('agi_channel')

            # context = fastagi.get_variable('XIVO_REAL_CONTEXT')

            calleridnum = agievent.get('agi_callerid')
            calleridani = agievent.get('agi_calleridani')
            callingani2 = agievent.get('agi_callingani2')

            cidnumstrs = ['agi_callerid=%s' % calleridnum]
            if calleridnum != calleridani:
                cidnumstrs.append('agi_calleridani=%s' % calleridani)
            if callingani2 != '0':
                cidnumstrs.append('agi_callingani2=%s' % callingani2)

            log.info('handle_fagi (%s) context=%s uid=%s chan=%s %s'
                     % (function,
                        context, uniqueid, channel, ' '.join(cidnumstrs)))
        except Exception:
            log.exception('handle_fagi %s' % (agievent))
            return varstoset

        if function == 'presence':
            try:
                if len(fastagi.args) > 0:
                    # input : 'xivo', 'presencegroup-agents', ...
                    presenceid = fastagi.args[0]
                    aststatus = []
                    for var, val in self.__counts__(context, presenceid).iteritems():
                        aststatus.append('%s:%d' % (var, val))
                    varstoset['XIVO_PRESENCE'] = ','.join(aststatus)
                    # XIVO_PRESENCE = available:37,onlineoutgoing:2,fastpickup:6
            except Exception:
                log.exception('handle_fagi %s : %s' % (function, fastagi.args))
            return varstoset

        elif function == 'queuestatus':
            try:
                if len(fastagi.args) > 0:
                    queuename = fastagi.args[0]
                    if self.weblist['queues'].hasqueue(queuename):
                        queueid = self.weblist['queues'].reverse_index.get(queuename)
                        qprops = self.weblist['queues'].keeplist[queueid]['agents_in_queue']
                        lst = []
                        for ag, agc in qprops.iteritems():
                            sstatus = 'unknown'
                            status = agc.get('Status')
                            if status == '1':
                                if agc.get('Paused') == '1':
                                    sstatus = 'paused'
                                else:
                                    sstatus = 'available'
                            elif status == '3':
                                sstatus = 'busy'
                            elif status == '5':
                                sstatus = 'away'
                            lst.append('%s:%s' % (ag, sstatus))
                        fastagi.set_variable('XIVO_QUEUESTATUS', ','.join(lst))
                        fastagi.set_variable('XIVO_QUEUEID', queueid)
            except Exception:
                log.exception('handle_fagi %s : %s' % (function, fastagi.args))
            return varstoset

        elif function == 'queueentries':
            try:
                if len(fastagi.args) > 0:
                    queuename = fastagi.args[0]
                    if self.weblist['queues'].hasqueue(queuename):
                        queueid = self.weblist['queues'].reverse_index.get(queuename)
                        qentries = self.weblist['queues'].keeplist[queueid]['channels']
                        lst = []
                        for chan, chanprops in qentries.iteritems():
                            lst.append('%s:%d' % (chan, int(round(time.time() - chanprops.get('entrytime')))))
                        fastagi.set_variable('XIVO_QUEUEENTRIES', ','.join(lst))
            except Exception:
                log.exception('handle_fagi %s : %s' % (function, fastagi.args))
            return varstoset

        elif function == 'queueholdtime':
            try:
                if len(fastagi.args) > 0:
                    queuename = fastagi.args[0]
                    if self.weblist['queues'].hasqueue(queuename):
                        queueid = self.weblist['queues'].reverse_index.get(queuename)
                        fastagi.set_variable('XIVO_QUEUEHOLDTIME',
                                             self.weblist['queues'].keeplist[queueid]['queuestats']['Holdtime'])
                else:
                    lst = []
                    for queuename, qprops in self.weblist['queues'].keeplist.iteritems():
                        if 'Holdtime' in qprops['queuestats']:
                            lst.append('%s:%s' % (queuename, qprops['queuestats']['Holdtime']))
                        else:
                            log.warning('handle_fagi %s : no Holdtime defined in queuestats for %s'
                                        % (function, queuename))
                    fastagi.set_variable('XIVO_QUEUEHOLDTIME', ','.join(lst))
            except Exception:
                log.exception('handle_fagi %s : %s' % (function, fastagi.args))
            return varstoset


        elif function == 'callerid_extend':
            if 'agi_callington' in agievent:
                fastagi.set_variable('XIVO_SRCTON', agievent.get('agi_callington'))
            return varstoset

        elif function == 'callerid_forphones':
            if self.uniqueids.has_key(uniqueid):
                uniqueiddefs = self.uniqueids[uniqueid]
                if uniqueiddefs.has_key('dialplan_data'):
                    dialplan_data = uniqueiddefs['dialplan_data']
                    calleridsolved = dialplan_data.get('dbr-display')
                else:
                    log.warning('handle_fagi %s no dialplan_data received yet'
                                % (function))
                    calleridsolved = None
            else:
                log.warning('handle_fagi %s no such uniqueid received yet : %s %s'
                            % (function, uniqueid, channel))
                calleridsolved = None

            calleridname = agievent.get('agi_calleridname')
            if calleridsolved:
                td = 'handle_fagi %s : calleridsolved="%s"' % (function, calleridsolved)
                log.info(td.encode('utf8'))
                if calleridname in ['', 'unknown', calleridnum]:
                    calleridname = calleridsolved
                else:
                    log.warning('handle_fagi %s : (solved) there is already a calleridname="%s"'
                                % (function, calleridname))

            # to set according to os.getenv('LANG') or os.getenv('LANGUAGE') later on ?
            if calleridnum in ['', 'unknown']:
                calleridnum = CALLERID_UNKNOWN_NUM
            if calleridname in ['', 'unknown']:
                calleridname = calleridnum
            else:
                log.warning('handle_fagi %s : (number) there is already a calleridname="%s"'
                            % (function, calleridname))

            calleridtoset = '"%s"<%s>' % (calleridname, calleridnum)
            td = 'handle_fagi %s : the callerid will be set to %s' % (function,
                                                                      calleridtoset.decode('utf8'))
            log.info(td.encode('utf8'))
            fastagi.set_callerid(calleridtoset)
            return varstoset

        elif function == 'cti2dialplan':
            if len(fastagi.args) > 1:
                dp_varname = fastagi.args[0]
                cti_varname = fastagi.args[1]
            else:
                log.warning('handle_fagi %s not enough arguments : %s'
                            % (function, fastagi.args))
                return
            if self.uniqueids.has_key(uniqueid):
                uniqueiddefs = self.uniqueids[uniqueid]
                if uniqueiddefs.has_key('dialplan_data'):
                    dialplan_data = uniqueiddefs['dialplan_data']
                    if dialplan_data.has_key(cti_varname):
                        fastagi.set_variable(dp_varname, dialplan_data[cti_varname])
                    else:
                        log.warning('handle_fagi %s no such variable %s in dialplan data'
                                    % (function, cti_varname))
                        ## XXX fastagi.set_variable(empty)
                else:
                    log.warning('handle_fagi %s no dialplan_data received yet'
                                % (function))
                    ## XXX fastagi.set_variable(not yet)
            else:
                log.warning('handle_fagi %s no such uniqueid received yet : %s %s'
                            % (function, uniqueid, channel))
                ## XXX fastagi.set_variable(not yet (uniqueid))
            return varstoset

        else:
            log.warning('handle_fagi %s : unknown function' % (function))

        return varstoset

    # FAGI stuff - end

    def regular_update(self):
        """
        Define here the tasks one would like to complete on a regular basis.
        """
        # like self.logout_all_agents(), according to 'regupdates'
        return

    def version(self):
        return '1.2-skaro-githash-gitdate'

    def set_configs(self, cfgs):
        # fetch faxcallerid, db settings (cdr and features)
        return
    def set_ctilog(self, ctilog):
        # ctilog db
        return
    def set_contextlist(self, ctx):
        return

    def read_internatprefixes(self, ipf):
        return

    def set_partings(self, pic):
        return

    def gethistory(self, userid, s, m, r):
        print 'gethistory', userid, s, m, r
        return

    # directory lookups entry points - START

    def get_matching_dirs(self, context, exten = None):
        if context in self.ctid.cconf.ctxlist:
            ctxdef = self.ctid.cconf.ctxlist.get(context)
        else:
            ctxdef = self.ctid.cconf.ctxlist.get('*', None)
        if not ctxdef:
            log.warning('context %s not defined' % context)
            return [], None
        # ctxdef defines the context properties : list of directories + display options
        if exten is None:
            # exten will be None in direct search cases
            return ctxdef.directories, ctxdef.display
        else:
            if exten in ctxdef.didextens:
                dirids = ctxdef.didextens.get(exten)
            else:
                dirids = ctxdef.didextens.get('*', [])
            return dirids, None
        return [], None

    def findreverse(self, context, exten, number):
        log.info('findreverse %s %s %s' % (context, exten, number))
        if not number.isdigit():
            return
        dirlist, dummy = self.get_matching_dirs(context, exten)

        itemdir = {}
        for dirid in dirlist:
            dirdef = self.ctid.cconf.dirlist.get(dirid)
            try:
                y = dirdef.findpattern(number, True)
            except Exception:
                log.exception('(findreverse) %s %s %s' % (dirlist, dirid, number))
                y = []
            if y:
                itemdir['xivo-reverse-nresults'] = str(len(y))
                for g, gg in y[0].iteritems():
                    itemdir[g] = gg
        return itemdir

    def getcustomers(self, context, pattern):
        fulllist = []

        dirids, dpyid = self.get_matching_dirs(context)

        for dirid in dirids:
            dirdef = self.ctid.cconf.dirlist.get(dirid)
            try:
                y = dirdef.findpattern(pattern, False)
                fulllist.extend(y)
            except Exception:
                log.exception('getcustomers (%s)' % dirid)

        # fulllist is the unformatted list of results, coming from all directories

        mylines = []

        if not dpyid or dpyid not in self.ctid.cconf.dpylist:
            log.warning('display %s not defined' % dpyid)
            return {'status' : 'ko', 'reason' : 'undefined_display'}

        dpydef = self.ctid.cconf.dpylist.get(dpyid)
        for itemdir in fulllist:
            basestr = dpydef.outputformat
            for k, v in itemdir.iteritems():
                # loop over set variables
                try:
                    basestr = basestr.replace('{%s}' % k, v.decode('utf8'))
                except UnicodeEncodeError:
                    basestr = basestr.replace('{%s}' % k, v)
            mylines.append(basestr)

        uniq = {}
        uniq_mylines = []
        for fsl in [uniq.setdefault(e,e) for e in sorted(mylines) if e not in uniq]:
            uniq_mylines.append(fsl)

        tosend = { 'status' : 'ok', 'header' : dpydef.display_header,
                   'result' : uniq_mylines }
        return tosend

    # directory lookups entry points - STOP

class Channel:
    def __init__(self, channel, context):
        self.channel = channel
        self.peerchannel = None
        self.context = context
        # destlist to update along the incoming channel path
        self.properties = {
            'monitor' : False, # for meetme as well as for regular calls ? agent calls ?
            'spy' : False, # spier or spied ?
            'holded' : False,
            'parked' : False,
            # meetme statuses
            'muted' : False,
            'meetme_isauthed' : False,
            'meetme_isadmin' : False,
            'meetme_usernum' : 0,
            # agent/queue relations ?
            'agent' : False,
            'direction' : None,
            'commstatus' : 'ready',
            'timestamp' : time.time(),
            'thisdisplay' : None,
            # peerdisplay : to be used in order to override a default value
            'peerdisplay' : None,
            'talkingto_kind' : None,
            'talkingto_id' : None,
            'history' : [],
            'extra' : None
            }
        self.relations = []
        return

    def setparking(self, exten, parkinglot):
        self.properties['peerdisplay'] = 'Parking (%s in %s)' % (exten, parkinglot)
        self.properties['parked'] = True
        self.properties['talkingto_kind'] = 'parking'
        self.properties['talkingto_id'] = '%s@%s' % (exten, parkinglot)
        return

    def unsetparking(self):
        self.properties['peerdisplay'] = None
        self.properties['parked'] = False
        self.properties['talkingto_kind'] = None
        self.properties['talkingto_id'] = None
        return

    def addrelation(self, relation):
        if relation not in self.relations:
            self.relations.append(relation)
        return

    def delrelation(self, relation):
        if relation in self.relations:
            self.relations.remove(relation)
        return

    def update_state(self, state):
        self.state = state
        return

    def update_term(self):
        # define what (agent, queue, ...)
        # define index
        return
