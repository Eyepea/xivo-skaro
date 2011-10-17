# -*- coding: utf8 -*-
from __future__ import with_statement
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Proformatique, Guillaume Bour <gbour@proformatique.com>

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
import os.path

class Cache(object):
    def __init__(self):
        pass

    def get(self, key):
        raise NotImplementedError()

    def put(self, key):
        # cache miss
        raise NotImplementedError()

class FileCache(Cache):
    def __init__(self, basedir):
        super(FileCache, self).__init__()
        self.basedir = basedir

    def get(self, key):
        path = os.path.join(self.basedir, key)

        if not os.path.exists(path):
            return None

        with open(path, 'r') as f:
            content = f.read()

        return content

    def put(self, key, value):
        path = os.path.join(self.basedir, key)
        dir  = os.path.dirname(path)

        if not os.path.exists(dir):
            try:
                os.makedirs(dir)	
            except Exception:
                return False

        with open(path, 'w') as f:
            f.write(value)
        
        return True
    
    		

    


