#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""Small script to upgrade installable package database files from the
old format (pre 2011-07) to the newer (post 2011-07).

"""

from __future__ import print_function

__license__ = """
    Copyright (C) 2011  Avencall

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

import optparse
import os
import re
import sys


SECTION = '['
PKG_SECTION = '[pkg_'


def update_file(src_fobj, dst_fobj):
    in_pkg_section = False
    for line in src_fobj:
        line = line.rstrip()
        if not in_pkg_section:
            if line.startswith(PKG_SECTION):
                in_pkg_section = True
            print(line, file=dst_fobj)
        else:
            if line.startswith(SECTION) and not line.startswith(PKG_SECTION):
                in_pkg_section = False
                print(line, file=dst_fobj)
            elif line.startswith('desc'):
                print('description', line[4:], sep='', file=dst_fobj)
            elif line.startswith('files:'):
                print('files:', line[6:].replace('file_', ''), sep='',
                      file=dst_fobj)
            elif line.startswith('install_proc:'):
                print('install:', line[13:].replace('install_', ''), sep='',
                      file=dst_fobj)
            elif line.startswith('depends:'):
                print('depends:', line[8:].replace('pkg_', ''), sep='',
                      file=dst_fobj)
            else:
                print(line, file=dst_fobj)


if __name__ == '__main__':
    parser = optparse.OptionParser(usage='usage: %prog [options] <db_file>')
    parser.add_option('-i', '--inplace', action='store_true')

    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit(1)

    src_filename = args[0]
    if opts.inplace:
        dst_filename = src_filename + '.newdb-tmp'
        with open(src_filename) as src_fobj:
            with open(dst_filename, 'w') as dst_fobj:
                update_file(src_fobj, dst_fobj)
        os.rename(dst_filename, src_filename)
    else:
        with open(src_filename) as src_fobj:
            update_file(src_fobj, sys.stdout)
