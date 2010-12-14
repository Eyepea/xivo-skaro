# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010  Proformatique <technique@proformatique.com>

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

from zope.interface import Interface, implements


class IIdGenerator(Interface):
    def next_id(self, used):
        """Return a unique ID (a string). The returned ID must not be in
        used (i.e. 'new_id not in used' must be true).
        
        """


class NumericIdGenerator(object):
    implements(IIdGenerator)
    
    def __init__(self, prefix='', start=0):
        self.prefix = ''
        self.n = start
        
    def next_id(self, used):
        n = self.n
        prefix = self.prefix
        while prefix + str(n) in used:
            n += 1
        self.n = n + 1
        return prefix + str(n)
