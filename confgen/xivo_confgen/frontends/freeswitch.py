# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""
import re
import xml.etree.ElementTree as et
from confgen.frontend  import Frontend

class FreeSwitchFrontend(Frontend):
    def directory(self):
        """
            Users directory
        """
        root = et.Element('include')

        users = self.backend.users.list()
        if users is None:
            # error
            return None

        users = filter(lambda u: u['protocol'] == 'sip', users)

        print 'yop'
        for user in users:
            user = self.backend.users.view(user['id'])
            if user is None:
                continue
            user = user.get('protocol', {})

            xuser    = et.SubElement(root, 'user')
            xuser.set('id', user['name'])
            params   = et.SubElement(xuser, 'params')

            if 'secret' in user:
                p = et.SubElement(params, 'param',
                    name='password',
                    value=user['secret'])

        #return self.indent(et.tostring(root))
        self.indent(root)
        return et.tostring(root)

    #def indent(self, raw):
    #	xre = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
    #	return xre.sub('>\g<1></', raw)

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
                for e in elem:
                    self.indent(e, level+1)
                if not e.tail or not e.tail.strip():
                    e.tail = i
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

