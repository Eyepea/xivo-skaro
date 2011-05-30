# -*- coding: UTF-8 -*-

"""Extension to the jinja2.loaders module.

"""

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

from os import walk
from os.path import join, getmtime, sep
from itertools import chain
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import split_template_path, BaseLoader
from jinja2.utils import open_if_exists


def _new_mtime_map(directories):
    # Return a dictionary where keys are pathname and values are last
    # modification times
    if isinstance(directories, basestring):
        directories = [directories]
    mtime_map = {}
    for directory in directories:
        for dirpath, dirnames, filenames in walk(directory):
            for pathname in chain(dirnames, filenames):
                abs_pathname = join(dirpath, pathname)
                try:
                    mtime_map[abs_pathname] = getmtime(abs_pathname)
                except OSError:
                    pass
    return mtime_map


class ProvdFileSystemLoader(BaseLoader):
    """A custom file system loader that does some extra check to templates
    'up to date' status to make sure that a custom template will always
    override a base template.
    
    """
    
    def __init__(self, searchpath, encoding='utf-8'):
        if isinstance(searchpath, basestring):
            searchpath = [searchpath]
        self._searchpath = list(searchpath)
        self._encoding = encoding
    
    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self._searchpath:
            filename = join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self._encoding)
            finally:
                f.close()
            
            mtime_map = _new_mtime_map(self._searchpath)
            def uptodate():
                return mtime_map == _new_mtime_map(self._searchpath)
            return contents, filename, uptodate
        raise TemplateNotFound(template)
    
    def list_templates(self):
        found = set()
        for searchpath in self._searchpath:
            for dirpath, _, filenames in walk(searchpath):
                for filename in filenames:
                    template = join(dirpath, filename)[len(searchpath):].strip(sep).replace(sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)
