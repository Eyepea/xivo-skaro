# -*- coding: utf-8 -*-

"""Object classes for XIVO AGI

Copyright (C) 2007-2010  Avencall

This module provides a set of objects that are used by several AGI scripts
in XIVO.

"""

__license__ = """
    Copyright (C) 2007-2010  Avencall

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import re
import time
from xivo_agid.schedule import ScheduleAction, SchedulePeriodBuilder, Schedule,\
    AlwaysOpenedSchedule

logger = logging.getLogger(__name__)


class DBUpdateException(Exception):
    pass


class ExtenFeatures:
    FEATURES = {
        'agents':   (('agentdynamiclogin',),
                     ('agentstaticlogin',),
                     ('agentstaticlogoff',),
                     ('agentstaticlogtoggle',)),

        'groups':   (('groupaddmember',),
                     ('groupremovemember',),
                     ('grouptogglemember',),
                     ('queueaddmember',),
                     ('queueremovemember',),
                     ('queuetogglemember',)),

        'forwards': (('fwdbusy', 'busy'),
                     ('fwdrna', 'rna'),
                     ('fwdunc', 'unc')),

        'services': (('enablevm', 'enablevoicemail'),
                     ('callrecord', 'callrecord'),
                     ('incallfilter', 'incallfilter'),
                     ('enablednd', 'enablednd'))}

    def __init__(self, agi, cursor):
        self.agi = agi
        self.cursor = cursor

        featureslist = []

        for xtype in self.FEATURES.itervalues():
            for x in xtype:
                featureslist.append(x[0])

        self.featureslist = tuple(featureslist)

        self.cursor.query("SELECT ${columns} FROM extensions "
                          "WHERE name IN (" + ", ".join(["%s"] * len(self.featureslist)) + ") "
                          "AND commented = 0",
                          ('name',),
                          self.featureslist)
        res = self.cursor.fetchall()

        if not res:
            enabled_features = []
        else:
            enabled_features = [row['name'] for row in res]

        for feature in self.featureslist:
            setattr(self, feature, (feature in enabled_features))

    def get_name_by_exten(self, exten):
        self.cursor.query("SELECT ${columns} FROM extensions "
                          "WHERE name IN (" + ", ".join(["%s"] * len(self.featureslist)) + ") "
                          "AND (exten = %s "
                          "OR (SUBSTR(exten,1,1) = '_' "
                              "AND SUBSTR(exten, 2, %s) LIKE %s)) "
                          "AND commented = 0",
                          ('name',),
                          self.featureslist + (exten, len(exten), "%s%%" % exten))

        res = self.cursor.fetchone()

        if not res:
            raise LookupError("Unable to find feature by exten (exten = %r)" % exten)

        return res['name']

    def get_exten_by_name(self, name, commented=None):
        query = "SELECT ${columns} FROM extensions WHERE name = %s"
        params = [name]

        if commented is not None:
            params.append(int(bool(commented)))
            query += " AND commented = %s"

        self.cursor.query(query, ('exten',), params)

        res = self.cursor.fetchone()

        if not res:
            raise LookupError("Unable to find feature by name (name = %r)" % name)

        return res['exten']


class BossSecretaryFilterMember:
    """This class represents a boss-secretary filter member (e.g. a boss
    or a secretary).

    """

    def __init__(self, agi, active, xtype, xid, number, ringseconds):
        self.agi = agi
        self.active = bool(active)
        self.type = xtype
        self.id = xid
        self.number = number
        self.interface = None

        if ringseconds == 0:
            self.ringseconds = ""
        else:
            self.ringseconds = ringseconds

    def __str__(self):
        return ("Call filter member object :\n"
                "Type:        %s\n"
                "User ID:     %s\n"
                "Number:      %s\n"
                "Interface:   %s\n"
                "RingSeconds: %s"
                % (self.type, self.id, self.number, self.interface, self.ringseconds))

    def agi_str(self):
        s = str(self)

        for line in s.splitlines():
            self.agi.verbose(line)


# TODO: refactor this.
class BossSecretaryFilter:
    """Boss-secretary filter class. Creating a boss-secretary filter
    automatically load everything related to the filter (its properties,
    those of its boss, its secretaries). Creating a filter is also a way
    to check its existence. Trying to construct a filter that doesn't
    exist or has no secretary raises a LookupError.

    """

    def __init__(self, agi, cursor, line):
        self.agi = agi
        self.cursor = cursor
        self.id = None
        self.active = False
        self.context = None
        self.mode = None
        self.callfrom = None
        self.ringseconds = None
        self.boss = None
        self.secretaries = None        
        self.line = line;
        
        boss_number = self.line['number']
        boss_context = self.line['context']

        contextinclude = Context(agi, cursor, boss_context).include

        columns = ('callfilter.id', 
                   'callfilter.bosssecretary',
                   'callfilter.callfrom', 
                   'callfilter.ringseconds',
                   'callfiltermember.ringseconds',
                   'userfeatures.id', 
                   'linefeatures.protocol',
                   'linefeatures.protocolid',
                   'linefeatures.number',
                   'linefeatures.context')

        t = tuple([boss_number] + contextinclude)
        
        cursor.query("SELECT ${columns} FROM callfilter "
                     "INNER JOIN callfiltermember "
                     "ON callfilter.id = callfiltermember.callfilterid "
                     "INNER JOIN userfeatures "
                     "ON " + cursor.cast('callfiltermember.typeval', 'int') + " = userfeatures.id "
                     "INNER JOIN linefeatures "
                     "ON linefeatures.iduserfeatures = userfeatures.id "
                     "WHERE callfilter.type = 'bosssecretary' "
                     "AND callfilter.commented = 0 "
                     "AND callfiltermember.type = 'user' "
                     "AND callfiltermember.bstype = 'boss' "
                     "AND userfeatures.bsfilter = 'boss' "
                     "AND linefeatures.number = %s "
                     "AND linefeatures.context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                     "AND linefeatures.internal = 0 "
                     "AND linefeatures.commented = 0",
                     columns,
                     t)
        
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find call filter ID for boss (number = %r, context = %r)" % (boss_number, boss_context))

        protocol = res['linefeatures.protocol']
        protocolid = res['linefeatures.protocolid']

        self.id = res['callfilter.id']
        self.context = boss_context
        self.mode = res['callfilter.bosssecretary']
        self.callfrom = res['callfilter.callfrom']
        self.ringseconds = res['callfilter.ringseconds']
        self.boss = BossSecretaryFilterMember(self.agi, True, 'boss', res['userfeatures.id'],
                                              boss_number, res['callfiltermember.ringseconds'])
        self.secretaries = []

        if self.ringseconds == 0:
            self.ringseconds = ""

        try:
            self.boss.interface = protocol_intf_and_suffix(cursor, protocol, 'user', protocolid)[0]
        except (ValueError, LookupError), e:
            self.agi.dp_break(str(e))

        columns = ('callfiltermember.active', 
                   'userfeatures.id', 
                   'linefeatures.protocol',
                   'linefeatures.protocolid', 
                   'linefeatures.number',
                   'userfeatures.ringseconds')
        
        t = tuple([self.id] + contextinclude)

        cursor.query("SELECT ${columns} FROM callfiltermember "
                     "INNER JOIN userfeatures "
                     "ON " + cursor.cast('callfiltermember.typeval', 'int') + " = userfeatures.id "
                     "INNER JOIN linefeatures "
                     "ON linefeatures.iduserfeatures = userfeatures.id "
                     "WHERE callfiltermember.callfilterid = %s "
                     "AND callfiltermember.type = 'user' "
                     "AND callfiltermember.bstype = 'secretary' "
                     "AND COALESCE(linefeatures.number,'') != '' "
                     "AND linefeatures.context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                     "AND linefeatures.internal = 0 "
                     "AND userfeatures.bsfilter = 'secretary' "
                     "AND userfeatures.commented = 0 "
                     "ORDER BY priority ASC",
                     columns,
                     t)
        res = cursor.fetchall()

        if not res:
            raise LookupError("Unable to find secretaries for call filter ID %d (context = %r)" % (self.id, boss_context))

        for row in res:
            protocol = row['linefeatures.protocol']
            protocolid = row['linefeatures.protocolid']
            secretary = BossSecretaryFilterMember(self.agi,
                                                  row['callfiltermember.active'],
                                                  'secretary',
                                                  row['userfeatures.id'],
                                                  row['linefeatures.number'],
                                                  row['userfeatures.ringseconds'])

            if secretary.active:
                self.active = True

            try:
                secretary.interface = protocol_intf_and_suffix(cursor, protocol, 'user', protocolid)[0]
            except (ValueError, LookupError), e:
                self.agi.dp_break(str(e))

            self.secretaries.append(secretary)

    def __str__(self):
        return ("Call filter object :\n"
                "Context:       %s\n"
                "Mode:          %s\n"
                "Callfrom:      %s\n"
                "RingSeconds:   %s\n"
                "Boss:\n%s\n"
                "Secretaries:\n%s"
                % (self.context, self.mode, self.callfrom,
                   self.ringseconds, self.boss, '\n'.join((str(secretary) for secretary in self.secretaries))))

    def agi_str(self):
        s = str(self)

        for line in s.splitlines():
            self.agi.verbose(line)

    def check_zone(self, zone):
        if self.callfrom == "all":
            return True
        elif self.callfrom == "internal" and zone == "intern":
            return True
        elif self.callfrom == "external" and zone == "extern":
            return True
        else:
            return False

    def get_secretary_by_number(self, number, context=None):
        if context and context != self.context:
            return None

        for secretary in self.secretaries:
            if number == secretary.number:
                return secretary
        else:
            return None

    def get_secretary_by_id(self, xid):
        for secretary in self.secretaries:
            if xid == secretary.id:
                return secretary
        else:
            return None

    def set_dial_actions(self):
        DialAction(self.agi, self.cursor, "noanswer", "callfilter", self.id).set_variables()

    def rewrite_cid(self):
        CallerID(self.agi, self.cursor, "callfilter", self.id).rewrite(force_rewrite=True)


class VMBox:
    def __init__(self, agi, cursor, xid=None, mailbox=None, context=None, commentcond=True):
        self.agi = agi
        self.cursor = cursor

        vm_columns = ('uniqueid', 'mailbox', 'context', 'password', 'email', 'commented', 'language')
        vmf_columns = ('skipcheckpass',)
        columns = ["voicemail." + c for c in vm_columns] + ["voicemailfeatures." + c for c in vmf_columns]

        if commentcond:
            where_comment = "AND voicemail.commented = 0"
        else:
            where_comment = ""

        if xid:
            cursor.query("SELECT ${columns} FROM voicemail "
                         "INNER JOIN voicemailfeatures "
                         "ON voicemail.uniqueid = voicemailfeatures.voicemailid "
                         "WHERE voicemail.uniqueid = %s " + 
                         where_comment,
                         columns,
                         (xid,))
        elif mailbox and context:
            contextinclude = Context(agi, cursor, context).include
            cursor.query("SELECT ${columns} FROM voicemail "
                         "INNER JOIN voicemailfeatures "
                         "ON voicemail.uniqueid = voicemailfeatures.voicemailid "
                         "WHERE voicemail.mailbox = %s "
                         "AND voicemail.context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") " + 
                         where_comment,
                         columns,
                         [mailbox] + contextinclude)
        else:
            raise LookupError("id or mailbox@context must be provided to look up a voicemail entry")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find voicemail box (id: %s, mailbox: %s, context: %s)" % (xid, mailbox, context))

        self.id = res['voicemail.uniqueid']
        self.mailbox = res['voicemail.mailbox']
        self.context = res['voicemail.context']
        self.password = res['voicemail.password']
        self.email = res['voicemail.email']
        self.commented = res['voicemail.commented']
        self.language = res['voicemail.language']
        self.skipcheckpass = res['voicemailfeatures.skipcheckpass']

    def toggle_enable(self, enabled=None):
        if enabled is None:
            enabled = int(not self.commented)
        else:
            enabled = int(not bool(enabled))

        self.cursor.query("UPDATE voicemail "
                          "SET commented = %s "
                          "WHERE uniqueid = %s",
                          parameters=(enabled, self.id))

        if self.cursor.rowcount != 1:
            raise DBUpdateException("Unable to perform the requested update")
        else:
            self.commented = enabled

class Paging:
    def __init__(self, agi, cursor, number, userid):
        self.agi = agi
        self.cursor = cursor
        self.lines = []

        columns = ('id', 'number', 'duplex', 'ignore', 'record', 'quiet', 'callnotbusy', 'timeout', 'announcement_file', 'announcement_play', 'announcement_caller', 'commented')


        cursor.query("SELECT ${columns} FROM paging "
                     "WHERE number = %s "
                     "AND commented = 0",
                     columns,
                     (number,))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find paging entry (id: %s)" % (number,))

        id = res['id']
        self.number = res['number']
        self.duplex = res['duplex']
        self.ignore = res['ignore']
        self.record = res['record']
        self.quiet = res['quiet']
        self.callnotbusy = res['callnotbusy']
        self.timeout = res['timeout']
        self.announcement_file = res['announcement_file']
        self.announcement_play = res['announcement_play']
        self.announcement_caller = res['announcement_caller']

        columns = ('userfeaturesid',)

        cursor.query("SELECT ${columns} FROM paginguser "
                     "WHERE userfeaturesid = %s AND pagingid = %s "
                     "AND caller = 1",
                     columns,
                     (userid, id))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find paging caller entry (userfeaturesid: %s)" % (userid,))

        columns = ('protocol', 'name')

        cursor.query("SELECT ${columns} FROM linefeatures "
                     "INNER JOIN paginguser on paginguser.pagingid = %s "
                     "WHERE linefeatures.iduserfeatures = paginguser.userfeaturesid "
                     "AND paginguser.caller = 0",
                     columns,
                     (id,))
        res = cursor.fetchall()

        if not res:
            raise LookupError("Unable to find paging users entry (id: %s)" % (id,))

        for l in res:
            line = l['protocol'].upper() + '/' + l['name']
            self.lines.append(line)

class Lines:
    def __init__(self, agi, cursor, xid=None, exten=None, context=None, name=None, protocol=None):
        self.agi = agi
        self.cursor = cursor
        self.lines = []

        columns = ('id', 'number', 'context', 'protocol', 'protocolid',
                   'iduserfeatures', 'name', 'line_num', 'rules_type',
                   'rules_time', 'rules_order', 'rules_group')

        if xid:
            cursor.query("SELECT ${columns} FROM linefeatures "
                         "WHERE iduserfeatures = %s "
                         "AND internal = 0 "
                         "AND commented = 0 "
                         "ORDER BY line_num ASC, rules_order ASC",
                         columns,
                         (xid,))
        elif exten and context:
            contextinclude = Context(agi, cursor, context).include
            cursor.query("SELECT ${columns} FROM linefeatures "
                         "WHERE number = %s "
                         "AND context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                         "AND internal = 0 "
                         "AND commented = 0",
                         columns,
                         [exten] + contextinclude)
        elif name and protocol:
            protocol = protocol.lower()

            if protocol == 'iax2':
                protocol = 'iax'

            cursor.query("SELECT ${columns} FROM linefeatures "
                         "WHERE name = %s "
                         "AND protocol = %s "
                         "AND internal = 0 "
                         "AND commented = 0",
                         columns,
                         (name, protocol))
        else:
            raise LookupError("id or exten@context must be provided to look up an user entry")

        res = cursor.fetchall()

        if not res:
            raise LookupError("Unable to find line entry (id: %s, exten: %s, context: %s)" % (xid, exten, context))

        for l in res:
            line = {
                'id'          : l['id'],
                'number'      : l['number'],
                'context'     : l['context'],
                'protocol'    : l['protocol'].upper(),
                'protocolid'  : l['protocolid'],
                'iduserfeatures': l['iduserfeatures'],
                'name'        : l['name'],
                'num'         : l['line_num'],
                'rules_type'  : l['rules_type'],
                'rules_time'  : l['rules_time'],
                'rules_order' : l['rules_order'],
                'rules_group' : l['rules_group']
            }

            self.lines.append(line)


class MasterLineUser:
    def __init__(self, agi, cursor, xid):
        self.agi = agi
        self.cursor = cursor
        self.line = {}
        
        columns = ('id', 'number', 'context', 'protocol', 'protocolid', 'name', 'line_num',
                   'rules_type', 'rules_time', 'rules_order', 'rules_group')
        
        cursor.query("SELECT ${columns} FROM linefeatures "
                     "WHERE iduserfeatures = %s "
                     "AND internal = 0 "
                     "AND commented = 0 "
                     "AND line_num = 0 "
                     "AND rules_order = 1 "
                     "ORDER BY line_num ASC, rules_order ASC",
                     columns,
                     (xid,))
        
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find master line entry (id: %s)" % (xid))

        self.line = {
            'id'          : res['id'],
            'number'      : res['number'],
            'context'     : res['context'],
            'protocol'    : res['protocol'].upper(),
            'protocolid'  : res['protocolid'],
            'name'        : res['name'],
            'num'         : res['line_num'],
            'rules_type'  : res['rules_type'],
            'rules_time'  : res['rules_time'],
            'rules_order' : res['rules_order'],
            'rules_group' : res['rules_group']
        }


class User:
    def __init__(self, agi, cursor, xid=None, exten=None, context=None):
        self.agi = agi
        self.cursor = cursor

        columns = ('id', 'firstname', 'lastname', 'callerid',
                   'ringseconds', 'simultcalls', 'enablevoicemail',
                   'voicemailid', 'enablexfer', 'enableautomon',
                   'callrecord', 'incallfilter', 'enablednd',
                   'enableunc', 'destunc', 'enablerna', 'destrna',
                   'enablebusy', 'destbusy', 'musiconhold', 'language',
                   'ringintern', 'ringextern', 'ringforward', 'ringgroup',
                   'outcallerid', 'bsfilter', 'preprocess_subroutine',
                   'pitch', 'pitchdirection', 'mobilephonenumber')

        if xid:
            cursor.query("SELECT ${columns} FROM userfeatures "
                         "WHERE id = %s "
                         "AND commented = 0",
                         columns,
                         (xid,))
        elif exten and context:
            line = Lines(agi, cursor, exten=exten, context=context)
            for line_dict in line.lines:
                if line_dict['iduserfeatures']:
                    cursor.query("SELECT ${columns} FROM userfeatures "
                                 "WHERE id = %s "
                                 "AND commented = 0",
                                 columns,
                                 (line_dict['iduserfeatures'],))
                    break
        else:
            raise LookupError("id or exten@context must be provided to look up an user entry")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find user entry (id: %s)" % xid)

        self.id = res['id']
        self.firstname = res['firstname']
        self.lastname = res['lastname']
        self.callerid = res['callerid']
        self.ringseconds = int(res['ringseconds'])
        self.simultcalls = res['simultcalls']
        self.enablevoicemail = res['enablevoicemail']
        self.voicemailid = res['voicemailid']
        self.enablexfer = res['enablexfer']
        self.enableautomon = res['enableautomon']
        self.callrecord = res['callrecord']
        self.incallfilter = res['incallfilter']
        self.enablednd = res['enablednd']
        self.enableunc = res['enableunc']
        self.destunc = res['destunc']
        self.enablerna = res['enablerna']
        self.destrna = res['destrna']
        self.enablebusy = res['enablebusy']
        self.destbusy = res['destbusy']
        self.musiconhold = res['musiconhold']
        self.outcallerid = res['outcallerid']
        self.preprocess_subroutine = res['preprocess_subroutine']
        self.mobilephonenumber = res['mobilephonenumber']
        self.bsfilter = res['bsfilter']
        self.language = res['language']
        self.ringintern = res['ringintern']
        self.ringextern = res['ringextern']
        self.ringforward = res['ringforward']
        self.ringgroup = res['ringgroup']
        self.pitch = res['pitch']
        self.pitchdirection = res['pitchdirection']

        if self.destunc == '':
            self.enableunc = 0

        if self.destrna == '':
            self.enablerna = 0

        if self.destbusy == '':
            self.enablebusy = 0

        if self.bsfilter == "boss":
            master_line = MasterLineUser(agi, cursor, xid) 
            try:
                self.filter = BossSecretaryFilter(agi, cursor, master_line.line)        
            except LookupError:
                import traceback
                traceback.print_exc()
                self.filter = None
        else:
            self.filter = None

        self.vmbox = None

        if self.enablevoicemail and self.voicemailid:
            try:
                self.vmbox = VMBox(agi, cursor, self.voicemailid)
            except LookupError:
                self.vmbox = None

        if not self.vmbox:
            self.enablevoicemail = 0

        # user skills
        cursor.query("SELECT count(*) FROM userqueueskill WHERE userid = %s", parameters=(xid,))
        res = cursor.fetchone()
        if not res:
            raise LookupError("Unable to find user queueskills")

        self.skills = ''
        if res[0] > 0:
            self.skills = xid


    def disable_forwards(self):
        self.cursor.query("UPDATE userfeatures "
                          "SET enablebusy = 0, "
                          "    enablerna = 0, "
                          "    enableunc = 0 "
                          "WHERE id = %s",
                          parameters=(self.id,))

        if self.cursor.rowcount != 1:
            raise DBUpdateException("Unable to perform the requested update")
        else:
            self.enablebusy = 0
            self.enablerna = 0
            self.enableunc = 0

    def set_feature(self, feature, enabled, arg):
        enabled = int(bool(enabled))

        if enabled and arg is not "":
            dest = arg
        else:
            dest = None

        if feature not in ("unc", "rna", "busy"):
            raise ValueError("invalid feature")

        if dest is not None:
            self.cursor.query("UPDATE userfeatures "
                              "SET enable%s = %%s, "
                              "    dest%s = %%s "
                              "WHERE id = %%s" % (feature, feature),
                              parameters=(enabled, dest, self.id))
        else:
            self.cursor.query("UPDATE userfeatures "
                              "SET enable%s = %%s "
                              "WHERE id = %%s" % feature,
                              parameters=(enabled, self.id))

        if self.cursor.rowcount != 1:
            raise DBUpdateException("Unable to perform the requested update")
        else:
            setattr(self, "enable%s" % feature, enabled)

            if dest is not None:
                setattr(self, "dest%s" % feature, dest)

    def toggle_feature(self, feature):
        if feature == "vm":
            feature = "enablevoicemail"
        elif feature == "dnd":
            feature = "enablednd"

        if feature not in ("enablevoicemail", "enablednd", "callrecord", "incallfilter"):
            raise ValueError("invalid feature")

        enabled = int(not getattr(self, feature))

        self.cursor.query("UPDATE userfeatures "
                          "SET %s = %%s "
                          "WHERE id = %%s" % feature,
                          parameters=(enabled, self.id))

        if self.cursor.rowcount != 1:
            raise DBUpdateException("Unable to perform the requested update")
        else:
            setattr(self, feature, enabled)


class Group:
    def __init__(self, agi, cursor, xid=None, number=None, context=None):
        self.agi = agi
        self.cursor = cursor

        groupfeatures_columns = ('id', 'number', 'context', 'name',
                                 'timeout', 'transfer_user', 'transfer_call',
                                 'write_caller', 'write_calling', 'preprocess_subroutine')
        queue_columns = ('musicclass',)
        columns = ["groupfeatures." + c for c in groupfeatures_columns] + ["queue." + c for c in queue_columns]

        if xid:
            cursor.query("SELECT ${columns} FROM groupfeatures "
                         "INNER JOIN queue "
                         "ON groupfeatures.name = queue.name "
                         "WHERE groupfeatures.id = %s "
                         "AND groupfeatures.deleted = 0 "
                         "AND queue.category = 'group' "
                         "AND queue.commented = 0",
                         columns,
                         (xid,))
        elif number and context:
            contextinclude = Context(agi, cursor, context).include
            cursor.query("SELECT ${columns} FROM groupfeatures "
                         "INNER JOIN queue "
                         "ON groupfeatures.name = queue.name "
                         "WHERE groupfeatures.number = %s "
                         "AND groupfeatures.context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                         "AND groupfeatures.deleted = 0 "
                         "AND queue.category = 'group' "
                         "AND queue.commented = 0",
                         columns,
                         [number] + contextinclude)
        else:
            raise LookupError("id or number@context must be provided to look up a group")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find group (id: %s, number: %s, context: %s)" % (xid, number, context))

        self.id = res['groupfeatures.id']
        self.number = res['groupfeatures.number']
        self.context = res['groupfeatures.context']
        self.name = res['groupfeatures.name']
        self.timeout = res['groupfeatures.timeout']
        self.transfer_user = res['groupfeatures.transfer_user']
        self.transfer_call = res['groupfeatures.transfer_call']
        self.write_caller = res['groupfeatures.write_caller']
        self.write_calling = res['groupfeatures.write_calling']
        self.preprocess_subroutine = res['groupfeatures.preprocess_subroutine']
        self.musicclass = res['queue.musicclass']

    def set_dial_actions(self):
        for event in ('noanswer', 'congestion', 'busy', 'chanunavail'):
            DialAction(self.agi, self.cursor, event, "group", self.id).set_variables()

    def rewrite_cid(self):
        CallerID(self.agi, self.cursor, "group", self.id).rewrite(force_rewrite=False)


class MeetMe:
    FLAG_ADMIN = (1 << 0)
    FLAG_USER = (1 << 1)

    OPTIONS_GLOBAL = {'talkeroptimization':        '', # Disabled
                       'record':                    'r',
                       'talkerdetection':           '', # Disabled
                       'noplaymsgfirstenter':       '1',
                       'closeconfdurationexceeded': 'L'}

    OPTIONS_COMMON = {'mode':              {'listen':  'l',
                                             'talk':    't',
                                             'all':     ''},
                       'announceusercount': 'c',
                       'announcejoinleave': {'no':          '',
                                             'yes':         'i',
                                             'noreview':    'I'},
                       'initiallymuted':    'm',
                       'musiconhold':       'M',
                       'poundexit':         'p',
                       'quiet':             'q',
                       'starmenu':          's',
                       'enableexitcontext': 'X'}

    OPTIONS_ADMIN = {'moderationmode':            'k',
                       'closeconflastmarkedexit':   'x'}

    OPTIONS_USER = {'hiddencalls':   'h'}

    def __init__(self, agi, cursor, xid=None, name=None, number=None, context=None):
        self.agi = agi
        self.cursor = cursor

        meetmefeatures_columns = (('id', 'name', 'confno', 'context',
                                      'admin_typefrom', 'admin_internalid', 'admin_externalid',
                                      'admin_identification', 'admin_exitcontext') + 
                                      tuple(["admin_%s" % x for x in (self.OPTIONS_COMMON.keys() + 
                                                                      self.OPTIONS_ADMIN.keys())]) + 
                                      ('user_exitcontext',) + \
                                      tuple(["user_%s" % x for x in (self.OPTIONS_COMMON.keys() + 
                                                                     self.OPTIONS_USER.keys())]) + 
                                      tuple(x for x in self.OPTIONS_GLOBAL.keys()) + 
                                      ('durationm', 'nbuserstartdeductduration',
                                       'timeannounceclose', 'maxusers',
                                       'startdate', 'preprocess_subroutine'))

        columns = ["meetmefeatures." + c for c in meetmefeatures_columns] + \
                  ['staticmeetme.var_val'] + \
                  ['linefeatures.number']

        if xid:
            cursor.query("SELECT ${columns} FROM meetmefeatures "
                         "INNER JOIN staticmeetme "
                         "ON meetmefeatures.meetmeid = staticmeetme.id "
                         "LEFT JOIN userfeatures "
                         "ON meetmefeatures.admin_internalid = userfeatures.id "
                         "LEFT JOIN linefeatures "
                         "ON userfeatures.id = linefeatures.iduserfeatures "
                         "WHERE meetmefeatures.id = %s "
                         "AND staticmeetme.commented = 0",
                         columns,
                         (xid,))
        elif name:
            cursor.query("SELECT ${columns} FROM meetmefeatures "
                         "INNER JOIN staticmeetme "
                         "ON meetmefeatures.meetmeid = staticmeetme.id "
                         "LEFT JOIN userfeatures "
                         "ON meetmefeatures.admin_internalid = userfeatures.id "
                         "LEFT JOIN linefeatures "
                         "ON userfeatures.id = linefeatures.iduserfeatures "
                         "WHERE meetmefeatures.name = %s "
                         "AND staticmeetme.commented = 0",
                         columns,
                         (name,))
        elif number and context:
            contextinclude = Context(agi, cursor, context).include
            cursor.query("SELECT ${columns} FROM meetmefeatures "
                         "INNER JOIN staticmeetme "
                         "ON meetmefeatures.meetmeid = staticmeetme.id "
                         "LEFT JOIN userfeatures "
                         "ON meetmefeatures.admin_internalid = userfeatures.id "
                         "LEFT JOIN linefeatures "
                         "ON userfeatures.id = linefeatures.iduserfeatures "
                         "WHERE meetmefeatures.confno = %s "
                         "AND meetmefeatures.context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                         "AND staticmeetme.commented = 0",
                         columns,
                         [number] + contextinclude)
        else:
            raise LookupError("id or name or number@context must be provided to look up a conference room")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find conference room "
                              "(id: %s, name: %s, number: %s, context: %s)"
                              % (xid, name, number, context))

        (self.confno, self.pin, self.pinadmin) = (res['staticmeetme.var_val'] + ",,").split(',', 3)[:3]
        self.admin_number = res['linefeatures.number']

        if res['meetmefeatures.startdate']:
            self.starttime = time.mktime(
                                time.strptime(res['meetmefeatures.startdate'],
                                              '%Y-%m-%d %H:%M:%S'))
        else:
            self.starttime = None

        for name, value in res.iteritems():
            if name not in('staticmeetme.var_val', 'linefeatures.number'):
                setattr(self, name.split('.', 1)[1], value)

        self.options = ()

    def _get_options(self, xdict, prefix=None):
        options = set()

        for name, opt in xdict.iteritems():
            if prefix:
                name = prefix + name

            attrvalue = getattr(self, name)

            if not attrvalue:
                continue
            elif isinstance(opt, dict):
                options.add(opt[attrvalue])
            elif isinstance(opt, basestring):
                options.add(opt)
            else:
                raise TypeError("Invalid type for option: %r" % opt)

        return options

    def get_global_options(self):   # pylint: disable-msg=E1101
        options = self._get_options(self.OPTIONS_GLOBAL.copy())

        if self.OPTIONS_GLOBAL['closeconfdurationexceeded'] in options:
            options.remove(self.OPTIONS_GLOBAL['closeconfdurationexceeded'])
            if self.durationm:
                opt = [str(int(self.durationm) * 60)]

                if self.nbuserstartdeductduration:
                    opt.append(str(self.nbuserstartdeductduration))
                else:
                    opt.append("")

                if self.timeannounceclose:
                    opt.append(str(self.timeannounceclose))

                options.add("%s(%s)" % (self.OPTIONS_GLOBAL['closeconfdurationexceeded'],
                                        "|".join(opt).rstrip("|")))

        return set(options)

    def get_admin_options(self):    # pylint: disable-msg=E1101
        admin_options = self.OPTIONS_COMMON.copy()
        admin_options.update(self.OPTIONS_ADMIN)
        options = self._get_options(admin_options, "admin_")

        if self.OPTIONS_COMMON['enableexitcontext'] in options \
           and not self.admin_exitcontext:
            options.remove(self.OPTIONS_COMMON['enableexitcontext'])

        options.add('a')    # Admin mode
        options.add('A')    # Marked mode

        return set(options)

    def get_user_options(self): # pylint: disable-msg=E1101
        user_options = self.OPTIONS_COMMON.copy()
        user_options.update(self.OPTIONS_USER)
        options = self._get_options(user_options, "user_")

        if self.admin_moderationmode:
            options.add(self.OPTIONS_ADMIN['moderationmode'])

        if self.OPTIONS_COMMON['enableexitcontext'] in options \
           and not self.user_exitcontext:
            options.remove(self.OPTIONS_COMMON['enableexitcontext'])

        return set(options)

    def get_option_by_flag(self, option, flag):
        if flag & self.FLAG_USER:
            return getattr(self, "user_%s" % option)
        elif flag & self.FLAG_ADMIN:
            return getattr(self, "admin_%s" % option)
        else:
            raise ValueError("Unable to find option %r, unknown MeetMe FLAG (flag: %r)"
                             % (option, flag))

    def get_admin_identifiers(self):    # pylint: disable-msg=E1101
        if self.admin_typefrom in (None, 'none'):
            return None

        r = {'calleridnum': None,
             'pin':         None}

        if self.admin_identification in ('calleridnum', 'all'):
            if self.admin_typefrom == 'internal':
                if self.admin_number:
                    r['calleridnum'] = self.admin_number
                else:
                    raise ValueError("Missing internal number to identify the administrator")
            elif self.admin_typefrom == 'external':
                if self.admin_externalid:
                    r['calleridnum'] = self.admin_externalid
                else:
                    raise ValueError("Missing external number to identify the administrator")

        if self.admin_identification in ('pin', 'all'):
            if self.pinadmin:
                r['pin'] = self.pinadmin
            else:
                raise ValueError("Missing administrator PIN to identify the administrator")

        if not r['calleridnum'] and not r['pin']:
            raise NotImplementedError("Identification method not implemented: %r" % self.admin_identification)

        return r

    def is_admin(self, pinadmin=None, calleridnum=None):
        admin_identifiers = self.get_admin_identifiers()

        if not admin_identifiers:
            return False
        elif admin_identifiers['calleridnum'] \
             and admin_identifiers['calleridnum'] != calleridnum:
            return False
        elif admin_identifiers['pin'] \
             and admin_identifiers['pin'] != pinadmin:
            return False

        return True

    def authenticate(self, pin=None, calleridnum=None):
        if self.is_admin(pin, calleridnum):
            return self.FLAG_ADMIN
        elif not self.pin or self.pin == pin:
            return self.FLAG_USER

        return False

    def pin_len_max(self):
        xlen = 0

        if self.pin:
            xlen = len(self.pin)

        if self.pinadmin and len(self.pinadmin) > xlen:
            xlen = len(self.pinadmin)

        return xlen


class Queue:
    def __init__(self, agi, cursor, xid=None, number=None, context=None):
        self.agi = agi
        self.cursor = cursor

        columns = ('id', 'number', 'context', 'name', 'data_quality',
                   'hitting_callee', 'hitting_caller',
                   'retries', 'ring',
                   'transfer_user', 'transfer_call',
                   'write_caller', 'write_calling',
                   'url', 'announceoverride', 'timeout',
                   'preprocess_subroutine', 'announce_holdtime',
                                     'ctipresence', 'nonctipresence', 'waittime', 'waitratio')
        columns = ["queuefeatures." + c for c in columns]

        if xid:
            cursor.query("SELECT ${columns} FROM queuefeatures "
                         "INNER JOIN queue "
                         "ON queuefeatures.name = queue.name "
                         "WHERE queuefeatures.id = %s "
                         "AND queue.commented = 0 "
                         "AND queue.category = 'queue'",
                         columns,
                         (xid,))
        elif number and context:
            contextinclude = Context(agi, cursor, context).include
            cursor.query("SELECT ${columns} FROM queuefeatures "
                         "INNER JOIN queue "
                         "ON queuefeatures.name = queue.name "
                         "WHERE queuefeatures.number = %s "
                         "AND queuefeatures.context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                         "AND queue.commented = 0 "
                         "AND queue.category = 'queue'",
                         columns,
                         [number] + contextinclude)
        else:
            raise LookupError("id or number@context must be provided to look up a queue")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find queue (id: %s, number: %s, context: %s)" % (xid, number, context))

        self.id = res['queuefeatures.id']
        self.number = res['queuefeatures.number']
        self.context = res['queuefeatures.context']
        self.name = res['queuefeatures.name']
        self.data_quality = res['queuefeatures.data_quality']
        self.hitting_callee = res['queuefeatures.hitting_callee']
        self.hitting_caller = res['queuefeatures.hitting_caller']
        self.retries = res['queuefeatures.retries']
        self.ring = res['queuefeatures.ring']
        self.transfer_user = res['queuefeatures.transfer_user']
        self.transfer_call = res['queuefeatures.transfer_call']
        self.write_caller = res['queuefeatures.write_caller']
        self.write_calling = res['queuefeatures.write_calling']
        self.url = res['queuefeatures.url']
        self.announceoverride = res['queuefeatures.announceoverride']
        self.timeout = res['queuefeatures.timeout']
        self.preprocess_subroutine = res['queuefeatures.preprocess_subroutine']
        self.announce_holdtime = res['queuefeatures.announce_holdtime']
        pres = res['queuefeatures.ctipresence']
        if pres is None:
            self.ctipresence = {} 
        else:
            self.ctipresence = dict([[int(y) for y in s.split(':')] for s in pres.split(',')])

        pres = res['queuefeatures.nonctipresence']
        if pres is None:
            self.nonctipresence = {}
        else:
            self.nonctipresence = dict([[int(y) for y in x.split(':')] for x in pres.split(',')])
        self.waittime = res['queuefeatures.waittime']
        self.waitratio = res['queuefeatures.waitratio']

    def set_dial_actions(self):
        for event in ('congestion', 'busy', 'chanunavail', 'qctipresence', 'qnonctipresence',
                                          'qwaittime', 'qwaitratio'):
            DialAction(self.agi, self.cursor, event, "queue", self.id).set_variables()

        # case NOANSWER (timeout): we also set correct queuelog event
        action = DialAction(self.agi, self.cursor, 'noanswer', "queue", self.id)
        action.set_variables()
        if action.action in ('voicemail', 'voicemenu', 'sound'):
            self.agi.set_variable("XIVO_QUEUELOG_EVENT", "REROUTEGUIDE")
        else:
            self.agi.set_variable("XIVO_QUEUELOG_EVENT", "REROUTENUMBER")

    def rewrite_cid(self):
        CallerID(self.agi, self.cursor, "queue", self.id).rewrite(force_rewrite=False)

    def pickupgroups(self):
        self.cursor.query("SELECT ${columns} FROM pickup p, pickupmember pm "
            "WHERE p.commented = 0 AND p.id = pm.pickupid "
            "AND pm.category = 'member' AND pm.membertype = 'queue'"
            "AND pm.memberid = %s",
            ('p.id',), (self.id,))

        res = self.cursor.fetchall()
        if res is None:
            raise LookupError("Unable to fetch queue %s pickupgroups" % (self.id))

        return [str(row[0]) for row in res]

 

class Agent:
    def __init__(self, agi, cursor, xid=None, number=None):
        self.agi = agi
        self.cursor = cursor

        columns = ('id', 'number', 'passwd', 'firstname', 'lastname', 'language', 'silent')

        if xid:
            cursor.query("SELECT ${columns} FROM agentfeatures "
                         "WHERE id = %s "
                         "AND commented = 0",
                         columns,
                         (xid,))
        elif number:
            cursor.query("SELECT ${columns} FROM agentfeatures "
                         "WHERE number = %s "
                         "AND commented = 0",
                         columns,
                         (number,))
        else:
            raise LookupError("id or number must be provided to look up an agent")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find agent (id: %s, number: %s)" % (xid, number))

        self.id = res['id']
        self.number = res['number']
        self.passwd = res['passwd']
        self.firstname = res['firstname']
        self.lastname = res['lastname']
        self.language = res['language']
        self.silent = res['silent']


class DialAction:
    @staticmethod
    def set_agi_variables(agi, event, category, action, actionarg1, actionarg2, isda=True):
        xtype = ("%s_%s" % (category, event)).upper()
        agi.set_variable("XIVO_FWD_%s_ACTION" % xtype, action)

        # Sometimes, it's useful to know whether these variables were
        # set manually, or by this object.
        if isda:
            agi.set_variable("XIVO_FWD_%s_ISDA" % xtype, "1")

        if actionarg1:
            actionarg1 = actionarg1.replace('|', ';')
        else:
            actionarg1 = ""

        if actionarg2:
            actionarg2 = actionarg2
        else:
            actionarg2 = ""

        agi.set_variable("XIVO_FWD_%s_ACTIONARG1" % xtype,
                         actionarg1)
        agi.set_variable("XIVO_FWD_%s_ACTIONARG2" % xtype,
                         actionarg2)

    def __init__(self, agi, cursor, event, category, categoryval):
        self.agi = agi
        self.cursor = cursor
        self.event = event
        self.category = category

        cursor.query("SELECT ${columns} FROM dialaction "
                     "WHERE event = %s "
                     "AND category = %s "
                     "AND " + cursor.cast('categoryval', 'int') + " = %s "
                     "AND linked = 1",
                     ('action', 'actionarg1', 'actionarg2'),
                     (event, category, categoryval))
        res = cursor.fetchone()

        if not res:
            self.action = "none"
            self.actionarg1 = None
            self.actionarg2 = None
        else:
            self.action = res['action']
            self.actionarg1 = res['actionarg1']
            self.actionarg2 = res['actionarg2']

    def set_variables(self):
        category_no_isda = ('none',
                            'endcall:busy',
                            'endcall:congestion',
                            'endcall:hangup')

        DialAction.set_agi_variables(self.agi,
                                     self.event,
                                     self.category,
                                     self.action,
                                     self.actionarg1,
                                     self.actionarg2,
                                     (self.category not in category_no_isda))


class Trunk:
    def __init__(self, agi, cursor, xid):
        self.agi = agi
        self.cursor = cursor

        columns = ('protocol', 'protocolid')

        cursor.query("SELECT ${columns} FROM trunkfeatures "
                     "WHERE id = %s",
                     columns,
                     (xid,))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find trunk (id: %d)" % xid)

        self.id = xid
        self.protocol = res['protocol']
        self.protocolid = res['protocolid']

        (self.interface, self.intfsuffix) = protocol_intf_and_suffix(cursor,
                                                                     self.protocol,
                                                                     'trunk',
                                                                     self.protocolid)


class DID:
    def __init__(self, agi, cursor, xid=None, exten=None, context=None):
        self.agi = agi
        self.cursor = cursor

        columns = ('id', 'exten', 'context', 'preprocess_subroutine')

        if xid:
            cursor.query("SELECT ${columns} FROM incall "
                         "WHERE id = %s "
                         "AND commented = 0",
                         columns,
                         (xid,))
        elif exten and context:
            contextinclude = Context(agi, cursor, context).include
            cursor.query("SELECT ${columns} FROM incall "
                         "WHERE exten = %s "
                         "AND context IN (" + ", ".join(["%s"] * len(contextinclude)) + ") "
                         "AND commented = 0",
                         columns,
                         [exten] + contextinclude)
        else:
            raise LookupError("id or exten@context must be provided to look up a DID entry")

        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find DID entry (id: %s, exten: %s, context: %s)" % (xid, exten, context))

        self.id = res['id']
        self.exten = res['exten']
        self.context = res['context']
        self.preprocess_subroutine = res['preprocess_subroutine']

    def set_dial_actions(self):
        DialAction(self.agi, self.cursor, "answer", "incall", self.id).set_variables()

    def rewrite_cid(self):
        CallerID(self.agi, self.cursor, "incall", self.id).rewrite(force_rewrite=True)


class Outcall:
    def __init__(self, agi, cursor):
        self.agi = agi
        self.cursor = cursor

    def retrieve_values(self, xid):
        self.xid = xid
        columns = ('outcall.name', 'outcall.context', 'outcall.useenum', 'outcall.internal',
                   'outcall.preprocess_subroutine', 'outcall.hangupringtime', 'outcall.commented',
                   'outcall.id', 'dialpattern.typeid', 'dialpattern.type','dialpattern.exten', 
                   'dialpattern.stripnum', 'dialpattern.externprefix', 
                   'dialpattern.callerid', 'dialpattern.prefix')

        if self.xid:
            self.cursor.query("SELECT ${columns} FROM outcall, dialpattern "
                         "WHERE dialpattern.typeid = outcall.id "
                         "AND dialpattern.type = 'outcall' "
                         "AND dialpattern.id = %s"
                         "AND outcall.commented = 0",
                         columns,
                         (self.xid,))
        else:
            raise LookupError("id or exten@context must be provided to look up an outcall entry")

        res = self.cursor.fetchone()

        if not res:
            raise LookupError("Unable to find outcall entry (id: %s)" % (self.xid))


        self.id = res['outcall.id']
        self.exten = res['dialpattern.exten']
        self.context = res['outcall.context']
        self.externprefix = res['dialpattern.externprefix']
        self.stripnum = res['dialpattern.stripnum']
        self.callerid = res['dialpattern.callerid']
        self.useenum = res['outcall.useenum']
        self.internal = res['outcall.internal']
        self.preprocess_subroutine = res['outcall.preprocess_subroutine']
        self.hangupringtime = res['outcall.hangupringtime']

        self.cursor.query("SELECT ${columns} FROM outcalltrunk "
                     "WHERE outcallid = %s "
                     "ORDER BY priority ASC",
                     ('trunkfeaturesid',),
                     (self.id,))
        res = self.cursor.fetchall()

        if not res:
            raise ValueError("No trunk associated with outcall (id: %d)" % (self.xid,))

        self.trunks = []

        for row in res:
            try:
                trunk = Trunk(self.agi, self.cursor, row['trunkfeaturesid'])
            except LookupError:
                continue

            self.trunks.append(trunk)


class ScheduleDataMapper(object):
    @classmethod
    def get_from_path(cls, cursor, path, path_id):
        # fetch schedule info
        columns = ('id', 'timezone', 'fallback_action', 'fallback_actionid', 'fallback_actionargs')
        cursor.query("SELECT ${columns} FROM schedule_path p "
                     "LEFT JOIN schedule s ON p.schedule_id = s.id "
                     "WHERE p.path = %s "
                     "AND p.pathid = %s "
                     "AND s.commented = 0",
                     columns,
                     (path, path_id))
        res = cursor.fetchone()

        if not res:
            return AlwaysOpenedSchedule()

        schedule_id = res['id']
        timezone = res['timezone']
        default_action = ScheduleAction(res['fallback_action'],
                                        res['fallback_actionid'],
                                        res['fallback_actionargs'])

        # fetch schedule periods
        columns = ('mode', 'hours', 'weekdays', 'monthdays', 'months', 'action', 'actionid', 'actionargs')
        cursor.query("SELECT ${columns} FROM schedule_time "
                     "WHERE schedule_id = %s",
                     columns,
                     (schedule_id,))
        res = cursor.fetchall()

        opened_periods = []
        closed_periods = []
        for res_period in res:
            period_builder = SchedulePeriodBuilder()
            period_builder.hours(res_period['hours'])
            period_builder.weekdays(res_period['weekdays'])
            period_builder.days(res_period['monthdays'])
            period_builder.months(res_period['months'])

            if res_period['mode'] == 'opened':
                opened_periods.append(period_builder.build())
            else:
                action = ScheduleAction(res_period['action'],
                                        res_period['actionid'],
                                        res_period['actionargs'])
                period_builder.action(action)
                closed_periods.append(period_builder.build())

        return Schedule(opened_periods, closed_periods, default_action, timezone)


class VoiceMenu:
    def __init__(self, agi, cursor, xid):
        self.agi = agi
        self.cursor = cursor

        columns = ('name', 'context')

        cursor.query("SELECT ${columns} FROM voicemenu "
                     "WHERE id = %s "
                     "AND commented = 0",
                     columns,
                     (xid,))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find voicemenu entry (id: %d)" % (xid,))

        self.id = xid
        self.name = res['name']
        self.context = res['context']


class Context:
    # TODO: Recursive inclusion
    def __init__(self, agi, cursor, context):
        self.agi = agi
        self.cursor = cursor

        columns = ('context.name', 'context.displayname',
                   'context.entity', 'contextinclude.include')

        cursor.query("SELECT ${columns} FROM context "
                     "LEFT JOIN contextinclude "
                     "ON context.name = contextinclude.context "
                     "LEFT JOIN context AS contextinc "
                     "ON contextinclude.include = contextinc.name "
                     "AND context.commented = contextinc.commented "
                     "WHERE context.name = %s "
                     "AND context.commented = 0 "
                     "AND (contextinclude.include IS NULL "
                          "OR contextinc.name IS NOT NULL) "
                     "ORDER BY contextinclude.priority ASC",
                     columns,
                     (context,))
        res = cursor.fetchall()

        if not res:
            raise LookupError("Unable to find context entry (name: %s)" % (context,))

        self.name = res[0]['context.name']
        self.displayname = res[0]['context.displayname']
        self.entity = res[0]['context.entity']
        self.include = [self.name]

        for row in res:
            if row['contextinclude.include']:
                self.include.append(row['contextinclude.include'])


CALLERID_MATCHER = re.compile('^(?:"(.+)"|([a-zA-Z0-9\-\.\!%\*_\+`\'\~]+)) ?(?:<([0-9\*#]+)>)?$').match
CALLERIDNUM_MATCHER = re.compile('^[0-9\*#]+$').match

class CallerID:
    @staticmethod
    def parse(callerid):
        m = CALLERID_MATCHER(callerid)

        if not m:
            return

        calleridname = m.group(1)
        calleridnum = m.group(3)

        if calleridname is None:
            calleridname = m.group(2)

            if calleridnum is None and CALLERIDNUM_MATCHER(calleridname):
                calleridnum = m.group(2)

        return (calleridname, calleridnum)

    @staticmethod
    def set(agi, callerid):
        cid_parsed = CallerID.parse(callerid)

        if not cid_parsed:
            return

        calleridname, calleridnum = cid_parsed

        if calleridname is None and calleridnum is not None:
            calleridname = calleridnum

        if calleridname is not None and calleridnum is None:
            agi.set_variable('CALLERID(name)', calleridname)
        else:
            agi.set_variable('CALLERID(all)', '"%s" <%s>' % (calleridname, calleridnum))

        return True

    def __init__(self, agi, cursor, xtype, typeval):
        self.agi = agi
        self.cursor = cursor
        self.type = xtype
        self.typeval = typeval

        cursor.query("SELECT ${columns} FROM callerid "
                     "WHERE type = %s "
                     "AND typeval = %s "
                     "AND mode IS NOT NULL",
                     ('mode', 'callerdisplay'),
                     (xtype, typeval))
        res = cursor.fetchone()

        self.mode = None
        self.callerdisplay = ''
        self.calleridname = None
        self.calleridnum = None

        if res:
            cid_parsed = self.parse(res['callerdisplay'])

            if cid_parsed:
                self.mode = res['mode']
                self.callerdisplay = res['callerdisplay']
                self.calleridname, self.calleridnum = cid_parsed

    def rewrite(self, force_rewrite):
        """
        Set/Modify the caller ID if needed and allowed and create
        the XIVO_CID_REWRITTEN channel variable in some cases.

        @force_rewrite:
            True <=> CID modification is always allowed in this case.
                XIVO_CID_REWRITTEN is neither taken into account nor
                written.
            False <=> CID modification is only allowed if the channel
                variable XIVO_CID_REWRITTEN is not set prior to the
                call to this method.  If the CID modification really
                took place, XIVO_CID_REWRITTEN is created.
        """
        if not self.mode:
            return

        cidrewritten = self.agi.get_variable('XIVO_CID_REWRITTEN')

        if force_rewrite or not cidrewritten:

            calleridname = self.agi.get_variable('CALLERID(name)')
            calleridnum = self.agi.get_variable('CALLERID(num)')

            if self.calleridnum is not None:
                calleridnum = self.calleridnum
            elif calleridnum in (None, ''):
                calleridnum = 'unknown'

            if calleridname in (None, '', '""'):
                calleridname = calleridnum
            elif calleridname[0] == '"' and calleridname[-1] == '"':
                calleridname = calleridname[1:-1]

            if self.mode in ('prepend', 'append') \
               and self.calleridname == calleridname \
               and calleridnum == calleridname:
                name = calleridname
            elif self.mode == 'prepend':
                name = "%s - %s" % (self.calleridname, calleridname)
            elif self.mode == 'overwrite':
                name = self.calleridname
            elif self.mode == 'append':
                name = "%s - %s" % (calleridname, self.calleridname)
            else:
                raise RuntimeError("Unknown callerid mode: %r" % self.mode)

            self.agi.appexec('SetCallerPres', 'allowed')
            self.agi.set_variable('CALLERID(all)', '"%s" <%s>' % (name, calleridnum))

            if not force_rewrite:
                self.agi.set_variable('XIVO_CID_REWRITTEN', 1)

class CTIPresence:
    @staticmethod
    def status(agi, cursor, status_ids=None):
        """
                    we get a list of status ids, and want in return the presence+status names
                    in the form:
                        "pname:sname"
        """
        columns = ('s.id', 's.name', 'p.name')
        cursor.query("SELECT ${columns} FROM ctistatus s, ctipresences p "
          "WHERE s.id IN (" + ','.join([str(id) for id in status_ids]) + ") "
          "AND s.presence_id = p.id",
          columns)

        return dict([(r['s.id'], "%s:%s" % (r['p.name'], r['s.name'])) for r in cursor.fetchall()])


class ChanSIP:
    @staticmethod
    def get_intf_and_suffix(cursor, category, xid):

        cursor.query("SELECT ${columns} FROM usersip "
                     "WHERE id = %s "
                     "AND category = %s "
                     "AND commented = 0",
                     ('name',),
                     (xid, category))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find usersip entry (category: %s, id: %s)" % (category, xid))

        return ("SIP/%s" % res['name'], None)


class ChanIAX2:
    @staticmethod
    def get_intf_and_suffix(cursor, category, xid):

        cursor.query("SELECT ${columns} FROM useriax "
                     "WHERE id = %s "
                     "AND category = %s "
                     "AND commented = 0",
                     ('name',),
                     (xid, category))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find useriax entry (category: %s, id: %s)" % (category, xid))

        return ("IAX2/%s" % res['name'], None)

class ChanSCCP:
    @staticmethod
    def get_intf_and_suffix(cursor, category, xid):
        """NOTE: category is ignored as for now, sccp channel can only be a user
        """
        cursor.query("SELECT ${columns} FROM usersccp u, sccpline l "
                     "WHERE u.id = %s "
                     "AND u.defaultline = l.id "
                     "AND u.commented = 0",
                     ('l.name',),
                     (xid,))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find usersccp entry (category: %s, id: %s)" % (category, xid))

        return ("SCCP/%s" % res['l.name'], None)

class ChanCustom:
    @staticmethod
    def get_intf_and_suffix(cursor, category, xid):

        cursor.query("SELECT ${columns} FROM usercustom "
                     "WHERE id = %s "
                     "AND category = %s "
                     "AND commented = 0",
                     ('interface', 'intfsuffix'),
                     (xid, category))
        res = cursor.fetchone()

        if not res:
            raise LookupError("Unable to find usercustom entry (category: %s, id: %s)" % (category, xid))

        # In case the suffix is the integer 0, bool(intfsuffix)
        # returns False though there is a suffix. Casting it to
        # a string prevents such an error.

        return (res['interface'], str(res['intfsuffix']))


CHAN_PROTOCOL = {
    'sip'   : ChanSIP,
    'iax'   : ChanIAX2,
    'sccp'  : ChanSCCP,
    'custom': ChanCustom,
}

def protocol_intf_and_suffix(cursor, protocol, category, xid):
    """
    Lookup by protocol, category, xid and return the interface and interface suffix.
    On error, raise LookupError, ValueError, or an exception coming from the SQL backend.
    """
    if protocol in CHAN_PROTOCOL:
        return CHAN_PROTOCOL[protocol].get_intf_and_suffix(cursor, category, xid)
    else:
        raise ValueError("Unknown protocol %r" % protocol)        

class Static:
    def __init__(self, cursor, protocol):
        if protocol not in ('sip', 'iax', 'sccp'):
            raise ValueError("invalid type")

        cursor.query("SELECT ${columns} FROM static" + protocol + " WHERE commented = 0",
                     ('var_name', 'var_val'))

        for r in cursor.fetchall():
            setattr(self, r['var_name'], r['var_val'])

