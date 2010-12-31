#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement

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

import logging
import optparse
import os
import sys

import fetchfw2.cli as cli
import fetchfw2.config as config
import fetchfw2.util as util


def install(pkg_manager, opt, args):
    if not args:
        print >>sys.stderr, "error: no targets specified"
        sys.exit(1)
    installer = cli.CliInstaller(nodeps=opt.nodeps)
    pkg_manager.install(args, installer)


def list_installable(pkg_manager, opt, args):
    for installable_pkg in sorted_itervalues(pkg_manager.installable_pkgs):
        if not installable_pkg.hidden or not opt.hide:
            if installable_pkg.name in pkg_manager.installed_pkgs:
                installed_pkg = pkg_manager.installed_pkgs[installable_pkg.name]
                if installed_pkg.version != installable_pkg.version:
                    print installable_pkg, "[installed: %s]" % installed_pkg.version
                else:
                    print installable_pkg, "[installed]"
            else:
                print installable_pkg


def upgrade(pkg_manager, opt, args):
    if args:
        print >>sys.stderr, "error: upgrade doesn't accept arguments"
        sys.exit(1)
    if opt.ignore:
        upgrader = cli.CliUpgrader(nodeps=opt.nodeps, ignore=opt.ignore)
    else:
        upgrader = cli.CliUpgrader(nodeps=opt.nodeps)
    pkg_manager.upgrade(upgrader)


def search_installable(pkg_manager, opt, args):
    if len(args) > 1:
        print >>sys.stderr, "warning: ignoring search words after the first space"
    word = args[0]
    for installable_pkg in sorted_itervalues(pkg_manager.installable_pkgs):
        if not installable_pkg.hidden or not opt.hide:
            if word in installable_pkg.name:
                if installable_pkg.name in pkg_manager.installed_pkgs:
                    installed_pkg = pkg_manager.installed_pkgs[installable_pkg.name]
                    if installed_pkg.version != installable_pkg.version:
                        print installable_pkg, "[installed: %s]" % installed_pkg.version
                    else:
                        print installable_pkg, "[installed]"
                else:
                    print installable_pkg
                print '   ', installable_pkg.description


def info_installable(pkg_manager, opt, args):
    if not args:
        print >>sys.stderr, "error: no targets specified"
        sys.exit(1)
    for pkg_name in args:
        if pkg_name not in pkg_manager.installable_pkgs:
            print >>sys.stderr, "error: package '%s' was not found" % pkg_name
        else:
            pkg = pkg_manager.installable_pkgs[pkg_name]
            print 'Name\t\t:', pkg.name
            print 'Version\t\t:', pkg.version
            print 'Hidden\t\t:', pkg.hidden
            if pkg.dependencies:
                depends_on = ' '.join(pkg.dependencies)
            else:
                depends_on = 'None'
            print 'Depends On\t:', depends_on
            print 'Description\t:', pkg.description
            print


def update(pkg_manager, opt, args):
    pass


def list_installed(pkg_manager, opt, args):
    if args:
        for pkg_name in args:
            if pkg_name in pkg_manager.installed_pkgs:
                installed_pkg = pkg_manager.installed_pkgs[pkg_name]
                print installed_pkg
            else:
                print >>sys.stderr, "error: package '%s' not found" % pkg_name
    else:
        for installed_pkg in sorted_itervalues(pkg_manager.installed_pkgs):
            if not installed_pkg.hidden or not opt.hide:
                print installed_pkg


def info_installed(pkg_manager, opt, args):
    if not args:
        print >>sys.stderr, "error: no targets specified"
        sys.exit(1)
    for pkg_name in args:
        if pkg_name not in pkg_manager.installed_pkgs:
            print >>sys.stderr, "error: package '%s' not found" % pkg_name
        else:
            pkg = pkg_manager.installed_pkgs[pkg_name]
            print 'Name\t\t:', pkg.name
            print 'Version\t\t:', pkg.version
            print 'Hidden\t\t:', pkg.hidden
            if pkg.dependencies:
                depends_on = ' '.join(pkg.dependencies)
            else:
                depends_on = 'None'
            print 'Depends On\t:', depends_on
            print 'Required By\t:', "TODO"
            print 'Install Reason\t:', 'Explicitly installed' if pkg.explicitly_installed else 'Installed as a dependency for another package'
            print 'Description\t:', pkg.description
            print


def search_installed(pkg_manager, opt, args):
    if not args:
        print >>sys.stderr, "error: no search pattern specified"
        sys.exit(1)
    if len(args) > 1:
        print >>sys.stderr, "warning: ignoring search words after the first space"
    word = args[0]
    for installed_pkg in sorted_itervalues(pkg_manager.installed_pkgs):
        if not installed_pkg.hidden or not opt.hide:
            if word in installed_pkg.name:
                print installed_pkg
                print '   ', installed_pkg.description


def list_files_installed(pkg_manager, opt, args):
    if not args:
        print >>sys.stderr, "error: no targets specified"
        sys.exit(1)
    for pkg_name in args:
        if pkg_name not in pkg_manager.installed_pkgs:
            print >>sys.stderr, "error: package '%s' not found" % pkg_name
        else:
            installed_pkg = pkg_manager.installed_pkgs[pkg_name]
            if not installed_pkg.installed_files:
                print pkg_name, "-- no installed files"
            else:
                for file in installed_pkg.installed_files:
                    print pkg_name, file


def remove(pkg_manager, opt, args):
    if not args:
        print >>sys.stderr, "error: no targets specified"
        sys.exit(1)
    uninstaller = cli.CliUninstaller(recursive=opt.s)
    pkg_manager.uninstall(args, uninstaller)


def check_is_root():
    if os.geteuid() != 0:
        print >>sys.stderr, "error: you cannot perform this operation unless you are root"
        sys.exit(1)
        

def sorted_itervalues(dict):
    for key in sorted(dict):
        yield dict[key]


def sorted_iterkeys(dict):
    return sorted(dict)


def sorted_iteritems(dict):
    for key in sorted(dict):
        yield key, dict[key]


p = optparse.OptionParser()
p.add_option('--config', action='store', dest='config')
p.add_option('--debug', action='store_true', dest='debug')
p.add_option('--hide', action='store_true', dest='hide')
p.add_option('-d', '--nodeps', action='store_true', dest='nodeps', default=False)
p.add_option('-S', '--sync', action='store_true', dest='sync')
p.add_option('-Q', '--query', action='store_true', dest='query')
p.add_option('-R', '--remove', action='store_true', dest='remove')
p.add_option('-i', action='store_true', dest='i', default=False)
p.add_option('-l', action='store_true', dest='l', default=False)
p.add_option('-s', action='store_true', dest='s', default=False)
p.add_option('-u', action='store_true', dest='u', default=False)
p.add_option('--ignore', action='store', dest='ignore')

opt, args = p.parse_args()
if opt.debug:
    logger = logging.getLogger('fetchfw2')
    logger.setLevel(logging.DEBUG)
operations = set(name for name in ('sync', 'query', 'remove') if getattr(opt, name))
if not operations:
    print >>sys.stderr, "error: no operation specified"
    sys.exit(1)
elif len(operations) > 1:
    print >>sys.stderr, "error: only one operation may be used at a time"
    sys.exit(1)
assert len(operations) == 1
op = operations.pop()

cfg_filename = opt.config if opt.config else config.DEF_CFG_FILENAME
try:
    pkg_manager = config.new_package_manager(cfg_filename)
except config.ConfigError, e:
    print >>sys.stderr, "error: config file '%s': %s" % (cfg_filename, e)
    sys.exit(1)

try:
    if op == 'sync':
        sub_op = (opt.i, opt.l, opt.s, opt.u)
        if (False, False, False, False) == sub_op:
            check_is_root()
            install(pkg_manager, opt, args)
        elif (True, False, False, False) == sub_op:
            info_installable(pkg_manager, opt, args)
        elif (False, True, False, False) == sub_op:
            list_installable(pkg_manager, opt, args)
        elif (False, False, True, False) == sub_op:
            search_installable(pkg_manager, opt, args)
        elif (False, False, False, True) == sub_op:
            check_is_root()
            upgrade(pkg_manager, opt, args)
        else:
            print >>sys.stderr, "error: no valid option combination for sync operation"
    elif op == 'query':
        sub_op = (opt.i, opt.l, opt.s)
        if (False, False, False) == sub_op:
            list_installed(pkg_manager, opt, args)
        elif (True, False, False) == sub_op:
            info_installed(pkg_manager, opt, args)
        elif (False, True, False) == sub_op:
            list_files_installed(pkg_manager, opt, args)
        elif (False, False, True) == sub_op:
            search_installed(pkg_manager, opt, args)
        else:
            print >>sys.stderr, "error: no valid option combination for query operation"
    elif op == 'remove':
        check_is_root()
        remove(pkg_manager, opt, args)
except cli.UserCancellationError:
    pass
except util.FetchfwError, e:
    print >>sys.stderr, "error:", e
    if opt.debug:
        import traceback
        traceback.print_exc()
    sys.exit(1)