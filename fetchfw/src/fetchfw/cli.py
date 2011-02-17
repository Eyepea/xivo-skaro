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

import logging
import progressbar
from fetchfw import package
from fetchfw.download import ProgressBarHook

logger = logging.getLogger(__name__)


class UserCancellationError(package.PackageError):
    # XXX not an error per se, but raised when the user didn't want to proceed
    pass


class CliInstaller(package.DefaultInstaller):
    # TODO better formatting, etc
    def __init__(self, **kwargs):
        # XXX don't know if it's a good idea to use **kwargs
        package.DefaultInstaller.__init__(self, **kwargs)
        #self._verbose = kwargs.get('verbose', False)
    
    def _get_pkgs_to_install(self, pkg_names, installable_pkgs, installed_pkgs):
        if not self._nodeps:
            print "resolving dependencies..."
        return package.DefaultInstaller._get_pkgs_to_install(self, pkg_names, installable_pkgs, installed_pkgs)
    
    def _pre_download(self, to_install_pkgs):
        print "Targets (%d):" % len(to_install_pkgs)
        for pkg in to_install_pkgs:
            print "    ", pkg
        print
        total_dl_size = sum(remote_file.size
                            for pkg in to_install_pkgs
                            for remote_file in pkg.remote_files if not remote_file.exists())
        print "Total Download Size:    %.2f MB" % (float(total_dl_size) / 1000 ** 2)
        print
        rep = raw_input("Proceed with installation? [Y/n] ")
        if rep and rep not in ('Y', 'y'):
            raise UserCancellationError() 
        
    def _download(self, to_install_pkgs):
        for to_install_pkg in to_install_pkgs:
            for remote_file in to_install_pkg.remote_files:
                if not remote_file.exists():
                    widgets = [remote_file.filename,
                               ':    ',
                               progressbar.FileTransferSpeed(),
                               ' ',
                               progressbar.ETA(),
                               ' ',
                               progressbar.Bar(),
                               ' ',
                               progressbar.Percentage(),
                               ]
                    # XXX some widgets would look better with customisation
                    remote_file.download([ProgressBarHook(progressbar.ProgressBar(widgets=widgets, maxval=remote_file.size))])

    def _pre_install(self, to_install_pkgs):
        print "Installing... "
    
    def _post_install(self, new_pkgs):
        print "Installation done."


class CliUninstaller(package.DefaultUninstaller):
    def _pre_uninstall(self, to_uninstall_pkgs):
        print "Remove (%d):" % len(to_uninstall_pkgs)
        for pkg in to_uninstall_pkgs:
            print "    ", pkg
        print
        rep = raw_input("Do you want to remove these packages? [Y/n] ")
        if rep and rep not in ('Y', 'y'):
            raise UserCancellationError() 


class CliUpgrader(package.DefaultUpgrader):
    def _get_pkgs_to_upgrade(self, installable_pkgs, installed_pkgs):
        if not self._nodeps:
            print "resolving dependencies..."
        return package.DefaultUpgrader._get_pkgs_to_upgrade(self, installable_pkgs, installed_pkgs)
    
    def _pre_download(self, upgrade_list):
        if not upgrade_list:
            print " there is nothing to do"
        else:
            to_install_pkgs = [to_install_pkg for elem in upgrade_list for to_install_pkg in elem[1]]
            print "Targets (%d):" % len(to_install_pkgs)
            for pkg in to_install_pkgs:
                print "    ", pkg
            print
            total_dl_size = sum(remote_file.size
                                for pkg in to_install_pkgs
                                for remote_file in pkg.remote_files if not remote_file.exists())
            print "Total Download Size:    %.2f MB" % (float(total_dl_size) / 1000 ** 2)
            print
            rep = raw_input("Proceed with installation? [Y/n] ")
            if rep and rep not in ('Y', 'y'):
                raise UserCancellationError() 

    def _download(self, upgrade_list):
        for to_install_pkg in (to_install_pkg for elem in upgrade_list for to_install_pkg in elem[1]):
            for remote_file in to_install_pkg.remote_files:
                if not remote_file.exists():
                    widgets = [remote_file.filename,
                               ':    ',
                               progressbar.FileTransferSpeed(),
                               ' ',
                               progressbar.ETA(),
                               ' ',
                               progressbar.Bar(),
                               ' ',
                               progressbar.Percentage(),
                               ]
                    # XXX some widgets would look better with customisation
                    remote_file.download([ProgressBarHook(progressbar.ProgressBar(widgets=widgets, maxval=remote_file.size))])
