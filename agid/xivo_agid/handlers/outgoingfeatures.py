# -*- coding: utf-8 -*-

__license__ = """
    Copyright (C) 2006-2010  Avencall

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

from xivo_agid import dialplan_variables
from xivo_agid.handlers.Handler import Handler
from xivo_agid import objects
import time

class OutgoingFeatures(Handler):
    
    PATH_TYPE = 'outcall'
    
    def __init__(self, agi, cursor, args):
        Handler.__init__(self, agi, cursor, args)
        self.userid = None
        self.callerid = None
        self.callrecord = False
        self.options = ""
        self.outcall = objects.Outcall(self._agi, self._cursor)
    

    def _retrieve_outcall(self):
        try:
            self.outcall.retrieve_values(self.dstid)
        except (ValueError, LookupError) as e:
            self._agi.dp_break(str(e))


    def _set_destination_number(self):
        if self.outcall.stripnum > 0:
            self.dstnum = self.dstnum[self.outcall.stripnum:]
        if self.outcall.externprefix:
            self.dstnum = self.outcall.externprefix + self.dstnum


    def _retrieve_user(self):
        try:
            self.user = objects.User(self._agi, self._cursor, int(self.userid))
            if self.user.enablexfer:
                self.options += 'T'
                
            if not self.outcall.internal:
                self.callerid = self.user.outcallerid
                if self.user.enableautomon:
                    self.options += "W"
                self.callrecord = self.user.callrecord
        except (ValueError, LookupError):
            pass
        self._agi.set_variable(dialplan_variables.CALL_OPTIONS, self.options)


    def _set_caller_id(self):
        if not self.outcall.internal:
            if self.callerid in (None, '', 'default') and self.outcall.callerid:
                self.callerid = self.outcall.callerid
        if self.callerid and self.callerid != 'default':
            objects.CallerID.set(self._agi, self.callerid)
            if self.callerid == 'anonymous':
                self._agi.appexec('SetCallerPres', 'prohib')


    def _set_trunk_info(self):
        for i, trunk in enumerate(self.outcall.trunks):
            self._agi.set_variable('%s%d' % (dialplan_variables.INTERFACE, i), trunk.interface)
            self._agi.set_variable('%s%d' % (dialplan_variables.TRUNK_EXTEN, i), self.dstnum)
            if trunk.intfsuffix:
                intfsuffix = trunk.intfsuffix
            else:
                intfsuffix = ""
            self._agi.set_variable('%s%d' % (dialplan_variables.TRUNK_SUFFIX, i), intfsuffix)


    def _set_record_file_name(self):
        if self.callrecord and objects.ExtenFeatures(self._agi, self._cursor).callrecord: # BUGBUG the context is missing in the filename TODO use ids
            callrecordfile = "user-%s-%s-%s.wav" % (self.srcnum, self.orig_dstnum, int(time.time()))
        else:
            callrecordfile = ""
        self._agi.set_variable(dialplan_variables.CALL_RECORD_FILE_NAME, callrecordfile)


    def _set_preprocess_subroutine(self):
        if self.outcall.preprocess_subroutine:
            preprocess_subroutine = self.outcall.preprocess_subroutine
        else:
            preprocess_subroutine = ""
        self._agi.set_variable(dialplan_variables.OUTCALL_PREPROCESS_SUBROUTINE, preprocess_subroutine)


    def _set_hangup_ring_time(self):
        if self.outcall.hangupringtime:
            hangupringtime = self.outcall.hangupringtime
        else:
            hangupringtime = ""
        self._agi.set_variable(dialplan_variables.HANGUP_RING_TIME, hangupringtime)



    def _extract_dialplan_variables(self):
        self.userid = self._agi.get_variable(dialplan_variables.USERID)
        self.dstid = self._agi.get_variable(dialplan_variables.DESTINATION_ID)
        self.dstnum = self._agi.get_variable(dialplan_variables.DESTINATION_NUMBER)
        self.srcnum = self._agi.get_variable(dialplan_variables.SOURCE_NUMBER)
        self.orig_dstnum = self.dstnum

    def execute(self):
        self._extract_dialplan_variables()

        self._retrieve_outcall()

        self._set_destination_number()

        self._retrieve_user()

        self._set_caller_id()

        self._set_trunk_info()

        self._set_record_file_name()

        self._set_preprocess_subroutine()

        self._set_hangup_ring_time()

        self._agi.set_variable(dialplan_variables.OUTCALL_ID, self.outcall.id)

        self._set_path(OutgoingFeatures.PATH_TYPE, self.outcall.id)
