#!/usr/bin/python2
# -*- coding: UTF-8 -*-

"""A tool for managing prov2 plugins. 

This tool can do the following:
- build plugins from bplugins
- package plugins
- generate defs.db file from plugin packages or plugins

"""

import os
import shutil
from optparse import OptionParser
from sys import exit, stderr


BUILD_FILENAME='build.py'


def count(iterable, function=bool):
    """Return the number of element 'e' in iterable for which function(e) is
    true.
    
    If function is not specified, return the number of element 'e' in iterable
    which evaluates to true in a boolean context.
    
    """
    return len(filter(function, iterable))


def is_bplugin(path):
    """Check if path is a bplugin.
    
    A path is a bplugin if it's a directory and has a file named BUILD_FILENAME
    inside it.
    
    """
    if os.path.isfile(os.path.join(path, BUILD_FILENAME)):
        return True
    else:
        return False


def list_bplugins(path):
    def aux():
        for name in os.listdir(path):
            bplugin = os.path.join(path, name)
            if is_bplugin(bplugin):
                yield bplugin
#    return list(aux())
    return aux()


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


def build_op(opt, args):
    # parse 'bdir' option
    if opt.bdir:
        bdir = opt.bdir
        if not os.path.isdir(bdir):
            print >>stderr, "error: bdir must be a directory ('%s' is not)" % bdir
            exit(1)
    else:
        bdir = os.curdir
    assert os.path.isdir(bdir)
    
    # parse 'pgdir' option
    if opt.pgdir:
        pgdir = opt.pgdir
        if not os.path.isdir(pgdir):
            print >>stderr, "error: pgdir must be a directory ('%s' is not)" % pgdir
            exit(1)
    else:
        pgdir = os.curdir
    
    # parse bplugins and target to build
    if args:
        bplugin_path = os.path.join(bdir, args[0])
        bplugins_target = {bplugin_path: args[1:]}
    else:
        # build all plugins from all bplugins
        bplugins_target = {}
        for bplugin_path in list_bplugins(bdir):
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
        print >>stderr, "Processing targets for bplugin '%s'..." % bplugin_path
        bplugin = bplugins_obj[bplugin_path]
        for target_id in targets:
            path = os.path.join(pgdir, bplugin.targets[target_id]['pg_id'])
            if opt.force and os.path.exists(path):
                shutil.rmtree(path, True)
            print >>stderr, "  - Building target '%s' in directory '%s'..." % \
                  (target_id, path)
            bplugin.build(target_id, pgdir)


def package_op(opt, args):
    raise NotImplementedError('not yet')


parser = OptionParser()
parser.add_option('-B', action='store_true', dest='build', help='build plugins from bplugins')
parser.add_option('-P', action='store_true', dest='package', help='package plugins')
parser.add_option('--bdir', dest='bdir', help='bplugins directory')
parser.add_option('--pgdir', dest='pgdir', help='plugins directory')
parser.add_option('--pkdir', dest='pkdir', help='packages directory')
parser.add_option('-f', action='store_true', dest='force', help='overwrite file/dir if they exist')
# XXX verbose not used
parser.add_option('-v', action='store_true', dest='verbose')

opt, args = parser.parse_args()
nb_op = count(getattr(opt, name) for name in ('build', 'package'))
if nb_op != 1:
    print >>stderr, "error: only one operation may be used at a time (%s given)" % nb_op
    exit(1)
# assert: only one operation is used

if opt.build:
    build_op(opt, args)
elif opt.package:
    package_op(opt, args)
else:
    raise AssertionError('unknown operation... this is a bug')
