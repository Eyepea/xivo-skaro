# -*- coding: utf-8 -*-

__license__ = """
    Copyright (C) 2009-2010  Avencall

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

from xivo_agid import agid
from xivo_agid import objects

from xivo.xivo_helpers import split_extension

def phone_progfunckey(agi, cursor, args):
    userid  = agi.get_variable('XIVO_USERID')
    xlen    = len(args)

    if xlen < 1:
        agi.dp_break("Invalid number of arguments (args: %r)" % args)

    if xlen > 1 and args[1] != '':
        try:
            if xlen == 2:
                context = objects.MasterLineUser(agi, cursor, xid=int(userid)).line['context']
            else:
                context = args[2]

        except (ValueError, LookupError), e:
            agi.dp_break(str(e))
    else:
        try:
            context = objects.MasterLineUser(agi, cursor, xid=int(userid)).line['context']
        except (ValueError, LookupError), e:
            agi.dp_break(str(e))

    try:
        fklist = split_extension(args[0])
    except ValueError, e:
        agi.dp_break(str(e))

    if userid != fklist[0]:
        agi.dp_break("Wrong userid. (userid: %r, excepted: %r)" % (fklist[0], userid))

    feature = ""

    try:
        extenfeatures = objects.ExtenFeatures(agi, cursor)
        feature = extenfeatures.get_name_by_exten(fklist[1])
    except LookupError, e:
        feature = ""
        agi.verbose(str(e))

    agi.set_variable('XIVO_PHONE_CONTEXT', context)
    agi.set_variable('XIVO_PHONE_PROGFUNCKEY', ''.join(fklist[1:]))
    agi.set_variable('XIVO_PHONE_PROGFUNCKEY_FEATURE', feature)

agid.register(phone_progfunckey)
