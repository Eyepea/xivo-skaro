# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

import binascii
import uuid


def numeric_id_generator(prefix=u'', start=0):
    n = start
    while True:
        yield prefix + unicode(n)
        n += 1 


def uuid_id_generator():
    while True:
        yield unicode(uuid.uuid4().hex)


def urandom_id_generator(length=12):
    while True:
        f = open('/dev/urandom')
        try:
            id = unicode(binascii.hexlify(f.read(length)))
        finally:
            f.close() 
        yield id
