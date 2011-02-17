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
from fetchfw.install import InstallationError
from fetchfw.util import FetchfwError, remove_paths

logger = logging.getLogger(__name__)


class PackageError(FetchfwError):
    pass


class Package(object):
    def __init__(self, name, version, description, hidden, dependencies):
        """- dependencies is a list of package name, or can be None
        """
        self.name = name
        self.version = version
        self.description = description
        self.hidden = hidden
        self.dependencies = [] if dependencies is None else dependencies

    def __str__(self):
        return "%s %s" % (self.name, self.version)


class InstallablePackage(Package):
    """Represent a package that can be installed."""
    def __init__(self, name, version, description, hidden, dependencies, remote_files,
                 install_manager):
        """- remote_files is a list of RemoteFile object, or None
           - install_manager is an InstallationManager object, or None
        """
        Package.__init__(self, name, version, description, hidden, dependencies)
        self.remote_files = [] if remote_files is None else remote_files
        self.install_manager = install_manager


class ToInstallPackage(InstallablePackage):
    """Represent a package that is going to be installed. The difference between this
       and InstallablePackage is that this hold information about the context of the
       installation.
    """
    def __init__(self, installable_pkg, explicit_install):
        """- explicit_install is False if the package will be installed as a
             dependency, else True
        """
        self.__dict__ = installable_pkg.__dict__.copy()
        self.explicilt_install = explicit_install
        
    def install(self):
        """Install this package on this system. This function does not install
           any dependency of this package, nor download any remote files; this
           has to be done before this method is called. This method only
           execute the installation manager and return an InstalledPackage object.
        """
        logger.debug("Installing package '%s'", self.name)
        if self.install_manager:
            installed_files = self.install_manager.execute()
        else:
            installed_files = () 
        return InstalledPackage(self.name, self.version,
                                self.description, self.hidden,
                                self.dependencies, self.explicilt_install,
                                installed_files)


class InstalledPackage(Package):
    """Represent a package that has been installed."""
    def __init__(self, name, version, description, hidden, dependencies,
                 explicitly_installed, installed_files):
        Package.__init__(self, name, version, description, hidden, dependencies)
        self.explicitly_installed = explicitly_installed
        self.installed_files = installed_files
        
    def uninstall(self):
        logger.info("Uninstalling package '%s'", self.name)
        remove_paths(self.installed_files)
    

class PackageManager(object):
    """Simple and modular packager manager."""
    def __init__(self, pkg_storage):
        self._pkg_storage = pkg_storage
        self._installable_pkgs = pkg_storage.installable_dict
        self._installed_pkgs = pkg_storage.installed_dict

    def install(self, pkg_names, installer=None):
        installer = DefaultInstaller() if installer is None else installer
        new_pkgs = installer(pkg_names, self._installable_pkgs, self._installed_pkgs)
        for new_pkg in new_pkgs:
            self._installed_pkgs[new_pkg.name] = new_pkg
        self._installed_pkgs.flush()

    def uninstall(self, pkg_names, uninstaller=None):
        uninstaller = DefaultUninstaller() if uninstaller is None else uninstaller
        removed_pkg_names = uninstaller(pkg_names, self._installable_pkgs, self._installed_pkgs)
        for pkg_name in removed_pkg_names:
            del self._installed_pkgs[pkg_name]
        self._installed_pkgs.flush()
        
    def upgrade(self, upgrader=None):
        upgrader = DefaultUpgrader() if upgrader is None else upgrader
        new_pkgs, removed_pkgs = upgrader(self._installable_pkgs, self._installed_pkgs)
        for removed_pkg in removed_pkgs:
            del self._installed_pkgs[removed_pkg.name]
        for new_pkg in new_pkgs:
            self._installed_pkgs[new_pkg.name] = new_pkg
        self._installed_pkgs.flush()
        
    @property
    def installable_pkgs(self):
        """A dictionary where keys are package id/name and values are
        installable package objects.
        
        This objects has also a few non-dictionary methods since it's in fact
        an InstallablePkgStorage object.
        
        """
        return self._installable_pkgs
    
    @property
    def installed_pkgs(self):
        """A dictionary where keys are package id/name and values are
        installed package objects.
        
        This objects has also a few non-dictionary methods since it's in fact
        an InstalledPkgStorage object.
        
        """
        return self._installed_pkgs
        

class DaemonPackageManager(PackageManager):
    # XXX this is just an (incomplete) example of a package manager with a slightly
    # different behaviour
    def install(self, *args, **kwargs):
        if self._needs_refresh():
            self._refresh()
        # ...
        
    def _needs_refresh(self):
        return True
    
    def _refresh(self):
        self._installable_pkgs.reload()
        self._installed_pkgs.reload()


class DefaultInstaller(object):
    def __init__(self, **kwargs):
        # XXX don't know if it's a great idea to use **kwargs
        self._nodeps = kwargs.get('nodeps', False)
    
    def __call__(self, pkg_names, installable_pkgs, installed_pkgs):
        # 1. Process package names
        clean_pkg_names = self._clean_pkg_names(pkg_names, installable_pkgs, installed_pkgs)
        to_install_pkgs = self._get_pkgs_to_install(clean_pkg_names, installable_pkgs, installed_pkgs)
        # 2. Download the files
        self._pre_download(to_install_pkgs)
        self._download(to_install_pkgs)
        # 3. Install packages
        self._pre_install(to_install_pkgs)
        new_pkgs = self._install(to_install_pkgs)
        self._post_install(new_pkgs)
        return new_pkgs
    
    def _clean_pkg_names(self, pkg_names, installable_pkgs, installed_pkgs):
        """Return a cleaned up version of the package names to install
           Input: the package names at the start of the process
           Output: the package names after clean up
           Post: -for name in returned_value: name in installable_pkgs
                 -for name in returned_value: name in pkg_names
           
           Some example: 
             -cancel the installation if a package name is invalid
             -silently remove invalid package names
             -raise a warning if a package is already installed
             -ask for the user confirmation (if interactive)
           
           In this case, an exception is raised if a package name is not in installable_pkgs.
        """
        for pkg_name in pkg_names:
            if pkg_name not in installable_pkgs:
                raise PackageError("could not find package '%s'" % pkg_name)
        return pkg_names
    
    def _get_pkgs_to_install(self, pkg_names, installable_pkgs, installed_pkgs):
        """Return the list of package that will be installed.
           Input: the package names to install
           Output: the package that will be installed
           Pre: for name in pkg_names: name in installable_pkgs
           Post: for pkg in returned_value: pkg.name in installable_pkgs
           
           Some example:
             - add (or not) the uninstalled dependencies
             - remove the packages that are already installed
        """
        to_install_pkgs = [ToInstallPackage(installable_pkgs[pkg_name], True) for pkg_name in pkg_names]
        if not self._nodeps:
            to_install_pkg_names = set(pkg_names)
            def add_dependency(pkg_name):
                if pkg_name in to_install_pkg_names or pkg_name in installed_pkgs:
                    return
                else:
                    to_install_pkg_names.add(pkg_name)
                    to_install_pkgs.append(ToInstallPackage(installable_pkgs[pkg_name], False))
                    for dependency in installable_pkgs[pkg_name].dependencies:
                        add_dependency(dependency)
            for pkg_name in pkg_names:
                for dependency in installable_pkgs[pkg_name].dependencies: 
                    add_dependency(dependency)
        return to_install_pkgs
    
    def _pre_download(self, to_install_pkgs):
        pass
    
    def _download(self, to_install_pkgs):
        """Make sure all the files needed to install the packages are downloaded,
           else raise an exception.
           
           Post: remote_file.exists() for pkg in to_install_pkgs for remote_file in pkg.remote_files
        """
        for to_install_pkg in to_install_pkgs:
            for remote_file in to_install_pkg.remote_files:
                if not remote_file.exists():
                    remote_file.download()
    
    def _pre_install(self, to_install_pkgs):
        pass
    
    def _install(self, to_install_pkgs):
        """Install every package in to_install_pkgs and return a list of InstalledPackage objects.
        """
        installed_pkgs = []
        try:
            for to_install_pkg in to_install_pkgs:
                installed_pkgs.append(to_install_pkg.install())
        except InstallationError:
            logger.exception("error during installation of package '%s'", to_install_pkg.name)
            # TODO error handling - what should we do with package that
            # have just been installed ?
        return installed_pkgs
    
    def _post_install(self, new_pkgs):
        pass


class DefaultUninstaller(object):
    def __init__(self, **kwargs):
        self._recursive = kwargs.get('recursive', False)
    
    def __call__(self, pkg_names, installable_pkgs, installed_pkgs):
        # 1. Process package names
        clean_pkg_names = self._clean_pkg_names(pkg_names, installable_pkgs, installed_pkgs)
        to_uninstall_pkgs = self._get_pkgs_to_uninstall(clean_pkg_names, installable_pkgs, installed_pkgs)
        # 2. Install packages
        self._pre_uninstall(to_uninstall_pkgs)
        return self._uninstall(to_uninstall_pkgs)
    
    def _clean_pkg_names(self, pkg_names, installable_pkgs, installed_pkgs):
        for pkg_name in pkg_names:
            # Check that each pkg_name in pkg_names is installed on this system
            if pkg_name not in installed_pkgs:
                raise PackageError("package '%s' not found" % pkg_name)
            # Check that there's no installed package that depends on one of the
            # package that we are about to uninstall
            for require_pkg_name in installed_pkgs.required_by(pkg_name):
                if require_pkg_name not in pkg_names: 
                    raise PackageError("'%s' depends on '%s'"
                                       % (pkg_name, require_pkg_name))
        return pkg_names

    def _get_pkgs_to_uninstall(self, pkg_names, installable_pkgs, installed_pkgs):
        """Return a list of InstalledPackage object that will be uninstalled.
        """
        to_uninstall_pkgs = [installed_pkgs[pkg_name] for pkg_name in pkg_names]
        if self._recursive:
            to_uninstall_pkg_names = set(pkg_names)
            def add_dependency(pkg_name):
                if pkg_name in to_uninstall_pkg_names:
                    # already processed
                    return
                if pkg_name not in installed_pkgs:
                    # rare case of a dependency that has been not been installed
                    return
                installed_pkg = installed_pkgs[pkg_name]
                if installed_pkg.explicitly_installed:
                    # we do not desinstall explicitly installed pkg
                    return
                if installed_pkgs.required_by(pkg_name, to_uninstall_pkg_names):
                    # dependency is required by some other installed packages
                    return
                to_uninstall_pkg_names.add(pkg_name)
                to_uninstall_pkgs.append(installed_pkg)
                for dependency in installed_pkg.dependencies:
                    add_dependency(dependency)
            for pkg_name in pkg_names:
                for dependency in installed_pkgs[pkg_name].dependencies:
                    add_dependency(dependency)
        return to_uninstall_pkgs
    
    def _pre_uninstall(self, to_uninstall_pkgs):
        pass
    
    def _uninstall(self, to_uninstall_pkgs):
        for installed_pkg in to_uninstall_pkgs:
            installed_pkg.uninstall()
        return [installed_pkg.name for installed_pkg in to_uninstall_pkgs]
        

class DefaultUpgrader(object):
    def __init__(self, **kwargs):
        self._nodeps = kwargs.get('nodeps', False)
        self._ignore = kwargs.get('ignore', ())

    def __call__(self, installable_pkgs, installed_pkgs):
        # 1. Find the package to upgrade (install/uninstall)
        # upgrade_list is a list of tuple which first element is the old
        # installed package and the second element is the list of new packages
        # to install
        upgrade_list = self._get_pkgs_to_upgrade(installable_pkgs, installed_pkgs)
        # 2. Download the files
        self._pre_download(upgrade_list)
        self._download(upgrade_list)
        # 3. Upgrade the packages
        self._pre_upgrade(upgrade_list)
        return self._upgrade(upgrade_list)
        
    def _get_pkgs_to_upgrade(self, installable_pkgs, installed_pkgs):
        upgrade_list = []
        for installed_pkg in installed_pkgs.itervalues():
            if installed_pkg.name not in self._ignore:
                if installed_pkg.name in installable_pkgs:
                    installable_pkg = installable_pkgs[installed_pkg.name]
                    if self._versioncmp(installable_pkg.version, installed_pkg.version) > 0:
                        to_install_pkgs = [ToInstallPackage(installable_pkg, True)]
                        if not self._nodeps:
                            to_install_pkg_names = set((installable_pkg.name,))
                            def add_dependency(pkg_name):
                                if pkg_name in to_install_pkg_names or pkg_name in installed_pkgs:
                                    return
                                to_install_pkg_names.add(pkg_name)
                                to_install_pkgs.append(ToInstallPackage(installable_pkgs[pkg_name], False))
                                for dependency in installable_pkgs[pkg_name].dependencies:
                                    add_dependency(dependency)
                            for dependency in installable_pkg.dependencies:
                                add_dependency(dependency)
                        upgrade_list.append((installed_pkg, to_install_pkgs))
        return upgrade_list

    @staticmethod
    def _versioncmp(version1, version2):
        """Compare the version version1 to version version2 and return an int:
           - 0 if they are the same
           - <0 if version1 < version2
           - >0 if version1 > version2
        """
        # XXX this might be a bit weak...
        for i1, i2 in zip(version1.split('.'), version2.split('.')):
            res_cmp = cmp(i1, i2)
            if res_cmp != 0:
                return res_cmp
        return len(version1) - len(version2)

    def _pre_download(self, upgrade_list):
        pass

    def _download(self, upgrade_list):
        for elem in upgrade_list:
            to_install_pkgs = elem[1]
            for to_install_pkg in to_install_pkgs:
                for remote_file in to_install_pkg.remote_files:
                    if not remote_file.exists():
                        remote_file.download()
    
    def _pre_upgrade(self, upgrade_list):
        pass
    
    def _upgrade(self, upgrade_list):
        # TODO error handling...
        new_pkgs = []
        removed_pkgs = []
        for old_installed_pkg, to_install_pkgs in upgrade_list:
            # uninstall old package first
            old_installed_pkg.uninstall()
            removed_pkgs.append(old_installed_pkg)
            # install new pkgs
            for to_install_pkg in to_install_pkgs:
                new_pkgs.append(to_install_pkg.install())
        return new_pkgs, removed_pkgs
