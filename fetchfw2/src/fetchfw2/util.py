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

import functools
import logging
import os
import re

logger = logging.getLogger(__name__)


class FetchfwError(Exception):
    pass


def func_once(fun):
    result = []
    @functools.wraps(fun)
    def aux(*args, **kwargs):
        try:
            return result[0]
        except IndexError:
            result.append(fun(*args, **kwargs))
            return result[0] 
    return aux


def method_once(method):
    attrname = "_%s_once_result" % id(method)
    @functools.wraps(method)
    def aux(self, *args, **kwargs):
        try:
            return getattr(self, attrname)
        except AttributeError:
            setattr(self, attrname, method(self, *args, **kwargs))
            return getattr(self, attrname)
    return aux


def explode_path(path):
    """Explode path into all it's subcomponents. This is a generator function.

       >>> list(explode_path('tmp/test/dir'))
       ['tmp', 'tmp/test', 'tmp/test/dir']
       >>> list(explode_path('/tmp/test'))
       ['/', '/tmp', '/tmp/test']
       >>> list(explode_path('tmp/'))
       ['tmp']
       >>> list(explode_path('tmp'))
       ['tmp']
    """
    start = 0
    while True:
        idx = path.find(os.sep, start)
        if idx == -1:
            break
        if idx == 0:
            idx += 1
        yield path[:idx] 
        start = idx + 1
    if start < len(path):
        yield path


def wrap_exception(wrapped, wrapper, logger=None):
    """Decorator used so that every exception of type 'wrapped' raised in a
       function body will be re-raised as exception of type 'wrapper'. The
       original exception is passed as the argument of the wrapper exception.
    """
    # XXX in fact, in python2, it might not be such a good idea to do exception
    # chaining since we lose the traceback, which is useful for debugging....
    def aux(fun):
        @functools.wraps(fun)
        def aux1(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            except wrapped, e:
                if logger:
                    logger.exception("exception raised in wrapped function")
                raise wrapper(e)
        return aux1
    return aux


def ends_with(str, end):
    """
       >>> ends_with('a', '/')
       'a/'
       >>> ends_with('a/', '/')
       'a/'
       >>> ends_with('a//', '/')
       'a//'
    """
    if str.endswith('/'):
        return str
    else:
        return str + '/'


def is_forward_path(path):
    # XXX le nom n'est pas très evocateur
    # XXX n'est pas utilisé présentement
    """Check that the path is not absolute and is not making reference to a parent directory.
    
       >>> is_forward_path('/root')
       False
       >>> is_forward_path('..')
       False
       >>> is_forward_path('../boot')
       False
       >>> is_forward_path('foo/../..')
       False
       >>> is_forward_path('foo/..')
       True
       >>> is_forward_path('foo')
       True
       >>> is_forward_path('foo/bar')
       True
    """
    if os.path.isabs(path):
        return False
    if os.path.normpath(path).startswith(os.pardir):
        return False
    return True

# XXX n'est pas utilisé présentement
def _human_readable(step, words):
    step = float(step)
    max_idx = len(words) - 1
    def aux(nb_bytes):
        idx = 0
        while nb_bytes >= step and idx < max_idx:
            nb_bytes = nb_bytes / step
            idx += 1
        if idx == 0:
            format_string = "%d %s"
        else:
            format_string = "%.2f %s"
        return format_string % (nb_bytes, words[idx])
    return aux

human_readable_bin = _human_readable(1024, ('B', 'KiB', 'MiB', 'GiB', 'TiB'))

human_readable_dec = _human_readable(1000, ('B', 'KB', 'MB', 'GB', 'TB'))


def apply_subs(string, variables):
    """Apply and return string with variable substitution applied.
    
    >>> apply_subs('$FOO', {'FOO': 'foo'})
    'foo'
    >>> apply_subs('${FOO}bar', {'FOO': 'foo'})
    'foobar'
    >>> apply_subs('${FOO}${BAR}', {'FOO': 'foo', 'BAR': 'bar'})
    'foobar'
    >>> apply_subs('$FOO/$BAR', {'FOO': 'foo', 'BAR': 'bar'})
    'foo/bar'
    >>> apply_subs('$N\$', {'N': '20'})
    '20$'
    
    Raise a KeyError if a substitution is not defined in variables.
    
    """
    def aux(m):
        var_name = m.group(1)
        if var_name is None:
            var_name = m.group(2)
        try:
            return variables[var_name]
        except KeyError:
            raise KeyError("undefined substitution '%s'" % var_name)
    interm = re.sub(r'(?<!\\)\$(?:{(\w+)}|(\w+))', aux, string) 
    return interm.replace(r'\$', '$')


def ReadOnlyForwardingDictMixin(attr_name):
    class ReadOnlyForwardingDictMixin_aux(object):
            def __getitem__(self, key):
                return getattr(self, attr_name)[key]
        
            def __len__(self):
                return len(getattr(self, attr_name))
            
            def __iter__(self):
                return iter(getattr(self, attr_name))
            
            def __contains__(self, item):
                return item in getattr(self, attr_name)
            
            def get(self, key, *args):
                return getattr(self, attr_name).get(key, *args)
            
            def items(self):
                return list(self.iteritems())
            
            def iterkeys(self):
                return getattr(self, attr_name).iterkeys()
            
            def itervalues(self):
                return getattr(self, attr_name).itervalues()
            
            def iteritems(self):
                return getattr(self, attr_name).iteritems()
            
            def keys(self):
                return list(self.iterkeys())
            
            def values(self):
                return list(self.values())
    return ReadOnlyForwardingDictMixin_aux

# XXX not used right now - in fact, used by the 2 methods are overriden, so its useless
def ReadWriteForwardingDictMixin(attr_name):
    class ReadWriteForwardingDictMixin_aux(ReadOnlyForwardingDictMixin(attr_name)):
        def __setitem__(self, key, value):
            getattr(self, attr_name)[key] = value
            
        def __delitem__(self, key):
            del getattr(self, attr_name)[key]
    return ReadWriteForwardingDictMixin_aux


def remove_paths(paths):
    """Remove all file/directory in paths from the filesystem.
       Takes care of removing the files inside a directory before
       trying to remove the directory.
       Never throws an exception.
    """
    for path in sorted(paths, reverse=True):
        if path.endswith('/'):
            logger.debug("Deleting '%s' as directory", path)
            try:
                os.rmdir(path)
            except OSError, e:
                logger.debug("Could not delete directory '%s' - %s", path, e)
        else:
            logger.debug("Deleting '%s' as file", path)
            try:
                os.remove(path)
            except OSError, e:
                logger.error("Could not delete file '%s'", path, exc_info=True)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
