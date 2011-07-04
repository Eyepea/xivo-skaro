# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010-2011  Proformatique <technique@proformatique.com>

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

import errno
import itertools
import logging
import operator
import os
import re
import shutil

logger = logging.getLogger(__name__)


class FetchfwError(Exception):
    pass


_APPLY_SUBS_REGEX = re.compile(r'(?<!\\)\$(?:{(\w*)}|(\w*))')

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
    
    Raise a ValueError if the substitution string is invalid, like
    using zero-length substitution variables ("a$." for example).
    
    """
    def aux(m):
        var_name = m.group(1)
        if var_name is None:
            var_name = m.group(2)
        if not var_name:
            raise ValueError("invalid zero-length variable: %s" % string)
        try:
            var_value = variables[var_name]
        except KeyError:
            raise KeyError("undefined substitution '%s'" % var_name)
        else:
            # This treat a special case where var_value has the string
            # "\$" in it, we don't want it to get unescaped at the end
            return var_value.replace(r'\$', r'\\$')
    interm = _APPLY_SUBS_REGEX.sub(aux, string) 
    return interm.replace(r'\$', '$')


def _split_version(raw_version):
    # Return a tuple (epoch, version_tokens, release) from a version string
    if ':' in raw_version:
        epoch, rest = raw_version.split(':', 1)
        epoch = int(epoch)
    else:
        epoch = 0
        rest = raw_version
    if '-' in rest:
        rest, rel = rest.rsplit('-', 1)
        rel = int(rel)
    else:
        rel = 0
    return epoch, rest.split('.'), rel


def cmp_version(version1, version2):
    """Compare version1 with version2 and return an integer according to the
    outcome.
    
    The return value is negative if version1 < version2, zero if
    version1 == version2 or positive if version1 > version2. 
    
    The version string must match the following regex, else the behaviour
    is not defined:
      ^(\d+:)?(\w+(?:\.\w+)*)(-\d+)?$
    where
      the first group is the epoch (missing is equivalent to "0:")
      the second group is the version
      the last group is the release (missing is equivalent to "-0")
    
    """
    # common case optimization
    if version1 == version2:
        return 0
    v1_epoch, v1_tokens, v1_rel = _split_version(version1)
    v2_epoch, v2_tokens, v2_rel = _split_version(version2)
    # compare epoch
    if v1_epoch != v2_epoch:
        return v1_epoch - v2_epoch
    # compare version
    for v1_token, v2_token in zip(v1_tokens, v2_tokens):
        v1_is_digit = v1_token.isdigit()
        v2_is_digit = v2_token.isdigit()
        if v1_is_digit and v2_is_digit:
            v1_int_token = int(v1_token)
            v2_int_token = int(v2_token)
            if v1_int_token != v2_int_token:
                return v1_int_token - v2_int_token
        elif v1_is_digit:
            assert not v2_is_digit
            return 1
        elif v2_is_digit:
            assert not v1_is_digit
            return -1
        else:
            token_cmp = cmp(v1_token, v2_token)
            if token_cmp:
                return token_cmp
    # check tokens length
    tokens_len_diff = len(v1_tokens) - len(v2_tokens)
    if tokens_len_diff:
        return tokens_len_diff
    # compare release
    if v1_rel != v2_rel:
        return v1_rel - v2_rel
    # we reach this if we compare "1.0" with "1.00" for example
    return 0


def _recursive_listdir_tuple(directory):
    # recursive_listdir that yield tuple (abs_path, path) instead
    # XXX we might want to yield stat.st_mode also...
    directories_stack = []
    for path in os.listdir(directory):
        abs_path = os.path.join(directory, path)
        if os.path.isdir(abs_path):
            directories_stack.append(path)
        yield abs_path, path
    while directories_stack:
        cur_directory = directories_stack.pop()
        cur_abs_directory = os.path.join(directory, cur_directory)
        for path in os.listdir(cur_abs_directory):
            rel_path = os.path.join(cur_directory, path)
            abs_path = os.path.join(directory, rel_path)
            if os.path.isdir(abs_path):
                directories_stack.append(rel_path)
            yield abs_path, rel_path


def recursive_listdir(directory):
    """Return an iterator that yield recursively all the files and directories
    inside the given directory.
    
    The directories are visited a bit more every time a new element is yielded
    from the iterator.
    
    Note that if the given directory doesn't exist, an error will be raised
    only on the first iteration and not during the function call.
    
    For example, if:
    $ mkdir test-dir
    $ touch test-dir/file1
    $ mkdir test-dir/dir2
    $ touch test-dir/dir2/file2
    
    then:
    > sorted(recursive_listdir('test-dir'))
    ['dir2', 'dir2/file2', 'file1']
    
    """
    return itertools.imap(operator.itemgetter(1), _recursive_listdir_tuple(directory))


def list_paths(directory):
    """Return an iterator that yield recursively all the files and directories
    inside the given directory, adding a one character tag at the end of
    non-regular files.
    
    Directories are returned with a '/' character appended.
    
    Be careful if your directories contains files other than regular files
    and directories (i.e. symbolic links, block device, etc) i.e. any non
    "regular files" or directories, since the behaviour is not defined.
    
    Except than that, the behaviour is the same as recursive_listdir.
    
    """
    for abs_path, path in _recursive_listdir_tuple(directory):
        if os.path.isdir(abs_path):
            yield path + '/'
        else:
            yield path


def install_paths(src_directory, dst_directory):
    """Copy recursively all the files from src_directory to dst_directory,
    yielding the copied files/directories at the same rate the files are
    copied.
    
    Directories are returned with a '/' character appended at the end.
    
    Note that if directories already exist in dst_directory, no error are
    raised and the directory is yielded like if it would have been created.
    Existing files are overriden without warning, so be careful.
    
    Also, note that both src_directory and dst_directory must already exist or
    an error will be raised on the first iteration.
    
    For example, if:
    $ mkdir test-dir
    $ touch test-dir/file1
    $ mkdir test-dir/dir2
    $ touch test-dir/dir2/file2
    
    then:
    > sorted(install_paths('test-dir', 'test-dir2'))
    ['file1', 'dir2/', 'dir2/file2']
    > sorted(list_paths('test-dir2'))
    ['dir2/', 'dir2/file2', 'file1']
    
    Note that you are looking for trouble if src_directory is the same as
    dst_directory or if both directories share a same subtree (i.e. one is
    the parent of the other).
    
    """
    for src_abs_path, path in _recursive_listdir_tuple(src_directory):
        dst_abs_path = os.path.join(dst_directory, path)
        if os.path.isdir(src_abs_path):
            try:
                os.mkdir(dst_abs_path)
            except OSError, e:
                if e.errno == errno.EEXIST and os.path.isdir(dst_abs_path):
                    # dst_abs_path already exist and is a dictionary
                    pass
                else:
                    raise
            yield path + '/'
        else:
            # Do not use shutil.copy since dst must not be a directory
            shutil.copyfile(src_abs_path, dst_abs_path)
            shutil.copymode(src_abs_path, dst_abs_path)
            yield path


def remove_paths(paths, directory):
    """Remove all the given paths from directory, yielding the removed paths
    at the same rate they are removed.
    
    paths must be an iterable of relative paths, with directories ending with '/'.
    
    Note that the function takes care of removing the files inside a directory
    before trying to remove the directory.
    
    An exception is not thrown in the following cases and in fact the path
    will be returned as if the removing was succesful:
    - removing a non-empty directory
    - removing a file/directory that doesn't exist
    
    In any other error case, an exception will be raised.
    
    For example, if:
    $ mkdir test-dir
    $ touch test-dir/file1
    $ mkdir test-dir/dir2
    $ touch test-dir/dir2/file2
    
    then:
    > sorted(remove_paths(['file1', 'dir2/', 'dir2/file2'], 'test-dir'))
    ['file1', 'dir2/', 'dir2/file2']
    > list(list_paths('test-dir'))
    []
    
    """
    non_empty_directories = []
    for path in sorted(paths, reverse=True):
        abs_path = os.path.join(directory, path)
        if abs_path.endswith('/'):
            # test if 'os.rmdir' will fail, i.e. if removing a child path that
            # previously failed.
            for non_empty_directory in non_empty_directories:
                if non_empty_directory.startswith(abs_path):
                    logger.debug("Not trying to remove '%s' since removing '%s' failed",
                                 abs_path, non_empty_directory)
                    break
            else:
                logger.debug("Deleting '%s' as directory", abs_path)
                try:
                    os.rmdir(abs_path)
                except OSError, e:
                    if e.errno == errno.ENOTEMPTY:
                        logger.debug("Could not delete directory '%s' because it is not empty", path)
                        non_empty_directories.append(abs_path)
                    elif e.errno == errno.ENOENT:
                        logger.warning("Could not delete directory '%s' because it does not exist", path)
                    else:
                        raise
        else:
            logger.debug("Deleting '%s' as file", abs_path)
            try:
                os.remove(abs_path)
            except OSError, e:
                if e.errno == errno.ENOENT:
                    logger.warning("Could not delete file '%s' because it does not exist", abs_path)
                else:
                    raise
        yield path


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
