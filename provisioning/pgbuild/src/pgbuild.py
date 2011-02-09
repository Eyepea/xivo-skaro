#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""A tool for managing prov plugins. 

This tool can do the following:
- build plugins from bplugins
- package plugins
- generate defs.db file from plugin packages or plugins

"""

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

import ConfigParser
import glob
import os
import shutil
import tarfile
from optparse import OptionParser
from subprocess import check_call, Popen, PIPE
from sys import exit, stderr

BUILD_FILENAME = 'build.py'
DB_FILENAME    = 'plugins.db'
INFO_FILENAME  = 'plugin-info'
PACKAGE_SUFFIX = '.tar.bz2'


def count(iterable, function=bool):
    """Return the number of element 'e' in iterable for which function(e) is
    true.
    
    If function is not specified, return the number of element 'e' in iterable
    which evaluates to true in a boolean context.
    
    """
    return len(filter(function, iterable))


def _is_bplugin(path):
    """Check if path is a bplugin.
    
    A path is a bplugin if it's a directory and has a file named BUILD_FILENAME
    inside it.
    
    """
    return os.path.isfile(os.path.join(path, BUILD_FILENAME))


def _list_bplugins(directory):
    def aux():
        for file in os.listdir(directory):
            file = os.path.join(directory, file)
            if _is_bplugin(file):
                yield file
    return list(aux())


class Bplugin(object):
    def __init__(self, path):
        """Create a new Bplugin object.
        
        path -- the path to a bplugin [directory]
        
        """
        self._load_bplugin(path)
        self._bplugin_path = path
        self.name = os.path.basename(path)
    
    def _load_bplugin(self, path):
        targets = {}
        def _target(target_id, pg_id):
            def aux(fun):
                if target_id in targets:
                    raise Exception("in bplugin '%s': target redefinition for '%s'" %
                                    (self.name, target_id))
                targets[target_id] = {'fun': fun, 'pg_id': pg_id}
                return fun
            return aux
        build_file = os.path.join(path, BUILD_FILENAME)
        execfile(build_file, {'target': _target})
        self.targets = targets
    
    def build(self, target_id, pgdir):
        """Build the target plugin in pgdir.
        
        Note: pgdir is the base directory where plugins are created. The
        plugin will be created in a sub-directory.
        
        Raise a KeyError if target_id is not a valid target id.
        
        """
        target = self.targets[target_id]
        path = os.path.join(pgdir, target['pg_id'])
        os.mkdir(path)
        # assert: path is empty
        old_cwd = os.getcwd()
        try:
            abs_path = os.path.abspath(path)
            os.chdir(self._bplugin_path)
            # assert: current directory is the one of the bplugin
            target['fun'](abs_path)
        finally:
            os.chdir(old_cwd)


def build_op(opts, args, src_dir, dest_dir):
    # Pre: src_dir is a directory
    # Pre: dest_dir is a directory
    bdir = src_dir
    pgdir = dest_dir
    
    # parse bplugins and target to build
    if args:
        bplugin_path = os.path.join(bdir, args[0])
        bplugins_target = {bplugin_path: args[1:]}
    else:
        # build all plugins from all bplugins
        bplugins_target = {}
        for bplugin_path in _list_bplugins(bdir):
            bplugins_target[bplugin_path] = None
    
    # create bplugins object and check targets
    bplugins_obj = {}
    for bplugin_path, targets in bplugins_target.iteritems():
        try:
            bplugin = Bplugin(bplugin_path)
        except Exception, e:
            print >>stderr, "error: while loading bplugin '%s': %s" % (bplugin_path, e)
            exit(1)
        else:
            bplugins_obj[bplugin_path] = bplugin
            if not targets:
                bplugins_target[bplugin_path] = bplugin.targets.keys()
            else:
                for target_id in targets:
                    if target_id not in bplugin.targets:
                        print >>stderr, "error: target '%s' not in bplugin '%s'" % \
                              (target_id, bplugin_path)
                        exit(1)
    
    # build bplugins
    for bplugin_path, targets in bplugins_target.iteritems():
        print "Processing targets for bplugin '%s'..." % bplugin_path
        bplugin = bplugins_obj[bplugin_path]
        for target_id in targets:
            path = os.path.join(pgdir, bplugin.targets[target_id]['pg_id'])
            if opts.force and os.path.exists(path):
                shutil.rmtree(path, True)
            print "  - Building target '%s' in directory '%s'..." % \
                  (target_id, path)
            bplugin.build(target_id, pgdir)


def _is_plugin(path):
    return os.path.isfile(os.path.join(path, INFO_FILENAME))


def _list_plugins(directory):
    def aux():
        for file in os.listdir(directory):
            file = os.path.join(directory, file)
            if _is_plugin(file):
                yield file
    return list(aux())


def _get_plugin_version(plugin):
    # Pre: plugin is a directory with an INFO_FILENAME file
    fobj = open(os.path.join(plugin, INFO_FILENAME))
    try:
        config = ConfigParser.RawConfigParser()
        config.readfp(fobj)
        return config.get('general', 'version')
    except ConfigParser.Error:
        print >>stderr, "error: plugin '%s' has invalid plugin info file" % plugin
        exit(1)
    finally:
        fobj.close()


def package_op(opts, args, src_dir, dest_dir):
    pg_dir = src_dir
    pkg_dir = dest_dir
    
    # parse plugins to package
    if args:
        plugins = [os.path.join(pg_dir, arg) for arg in args]
        # make sure plugins are plugins...
        for plugin in plugins:
            if not _is_plugin(plugin):
                print >>stderr, "error: plugin '%s' is missing info file" % plugin
                exit(1)
    else:
        plugins = _list_plugins(pg_dir)
    
    # build packages
    for plugin in plugins:
        plugin_version = _get_plugin_version(plugin)
        package = "%s-%s%s" % (os.path.join(pkg_dir, os.path.basename(plugin)),
                               plugin_version, PACKAGE_SUFFIX)
        print "Packaging plugin '%s' into '%s'..." % (plugin, package)
        check_call(['tar', 'caf', package,
                    '-C', os.path.dirname(plugin) or os.curdir,
                    os.path.basename(plugin)])


def _list_packages(directory):
    return glob.glob(os.path.join(directory, '*' + PACKAGE_SUFFIX))


def _get_package_filename(package):
    return os.path.basename(package)


def _get_package_name(package):
    tar_package = tarfile.open(package)
    try:
        shortest_name = min(tar_package.getnames())
        if tar_package.getmember(shortest_name).isdir():
            return shortest_name
        else:
            print >>stderr, "error: package '%s' should have only 1 directory at depth 0" % package
            exit(1)
    finally:
        tar_package.close()


def _get_package_description_and_version(package, package_name):
    # Return a tuple (version, description)
    tar_package = tarfile.open(package)
    try:
        plugin_info_name = os.path.join(package_name, INFO_FILENAME)
        if plugin_info_name not in tar_package.getnames():
            print >>stderr, "error: package '%s' has no file '%s'" % (package, plugin_info_name)
            exit(1)
        
        fobj = tar_package.extractfile(plugin_info_name)
        try:
            config = ConfigParser.RawConfigParser()
            config.readfp(fobj, plugin_info_name)
            description = config.get('general', 'description')
            version = config.get('general', 'version')
            return description.replace('\n', ' '), version 
        except ConfigParser.Error:
            print >>stderr, "error: package '%s' has invalid plugin-info file" % package
            exit(1)
        finally:
            fobj.close()
    finally:
        tar_package.close()


def _get_package_info(package):
    result = {}
    result['filename'] = _get_package_filename(package)
    result['name'] = _get_package_name(package)
    result['description'], result['version'] = \
        _get_package_description_and_version(package, result['name'])
    return result


def create_db_op(opts, args, src_dir, dest_dir):
    pkg_dir = src_dir
    db_file = os.path.join(dest_dir, DB_FILENAME)
    
    # parse packages to use to build db file
    if args:
        packages = [os.path.join(pkg_dir, arg) for arg in args]
    else:
        packages = _list_packages(pkg_dir)
    
    # create db file
    fobj = open(db_file, 'w')
    try:
        print "Creating DB file '%s'..." % db_file
        fobj.write("# This file has been automatically generated\n")
        for package in packages:
            print "  Adding package '%s' to db file..." % package
            package_info = _get_package_info(package)
            fobj.write('\n')
            fobj.write('[plugin_%s]\n' % package_info['name'])
            fobj.write('description: %s\n' % package_info['description'])
            fobj.write('filename: %s\n' % package_info['filename'])
            fobj.write('version: %s\n' % package_info['version'])
    finally:
        fobj.close()
    

def _get_directory(opt_value):
    # Return current dir if opt_value is none, else check if opt_value is
    # a directory and return it if it is, else write a message and exit
    if not opt_value:
        return os.curdir
    else:
        if not os.path.isdir(opt_value):
            print >>stderr, "error: '%s' is not a directory" % opt_value
            exit(1)
        return opt_value


def _get_directories(opts):
    # Return a tuple (source_dir, destination_dir)
    return _get_directory(opts.source), _get_directory(opts.destination)


def main():
    parser = OptionParser()
    parser.add_option('-B', '--build', action='store_true', dest='build',
                      help='create plugins from bplugins')
    parser.add_option('-P', '--package', action='store_true', dest='package',
                      help='create packages from plugins')
    parser.add_option('-D', '--db', action='store_true', dest='create_db',
                      help='create DB file from packages')
    parser.add_option('-s', '--source', dest='source',
                      help='source directory')
    parser.add_option('-d', '--destination', dest='destination',
                      help='destination directory')
    # Note: -f is only useful for the 'build' operation, other operation will
    #       overwrite destination files anyway
    parser.add_option('-f', action='store_true', dest='force',
                      help='overwrite file/dir if they exist')
    # XXX verbose not used
    parser.add_option('-v', action='store_true', dest='verbose')
    
    opts, args = parser.parse_args()
    nb_op = count(getattr(opts, name) for name in ('build', 'package', 'create_db'))
    if nb_op != 1:
        print >>stderr, "error: only one operation may be used at a time (%s given)" % nb_op
        exit(1)
    # assert: only one operation is specified
    
    src_dir, dest_dir = _get_directories(opts)
    if opts.build:
        build_op(opts, args, src_dir, dest_dir)
    elif opts.package:
        package_op(opts, args, src_dir, dest_dir)
    elif opts.create_db:
        create_db_op(opts, args, src_dir, dest_dir)
    else:
        raise AssertionError('unknown operation... this is a bug')

main()
