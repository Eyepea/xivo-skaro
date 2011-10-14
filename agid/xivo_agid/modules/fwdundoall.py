# -*- coding: utf-8 -*-

__license__ = """
    Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>

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

def fwdundoall(agi, cursor, args):
    userid = agi.get_variable('XIVO_USERID')

    try:
        user = objects.User(agi, cursor, int(userid))
    except (ValueError, LookupError), e:
        agi.dp_break(str(e))

    try:
        user.disable_forwards()
    except objects.DBUpdateException, e:
        agi.verbose(str(e))

agid.register(fwdundoall)
