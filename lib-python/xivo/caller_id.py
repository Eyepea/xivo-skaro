# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import re

COMPLETE_CALLER_ID_PATTERN = re.compile('\"(.*)\" \<(\d+)\>')


def build_caller_id(caller_id, name, number):
    if _complete_caller_id(caller_id):
        cid_name, cid_number = COMPLETE_CALLER_ID_PATTERN.search(caller_id).groups()
        return caller_id, cid_name, cid_number
    else:
        return '"%s" <%s>' % (name, number), name, number


def _complete_caller_id(caller_id):
    return True if COMPLETE_CALLER_ID_PATTERN.match(caller_id) else False


def extract_number(caller_id):
    result = COMPLETE_CALLER_ID_PATTERN.search(caller_id)
    if result:
        return result.groups()[1]
    else:
        raise ValueError('Not a valid Caller ID: %s', caller_id)
