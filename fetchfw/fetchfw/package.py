# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2010-2011  Avencall

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

import copy
import logging
from fetchfw.util import FetchfwError, install_paths, remove_paths, cmp_version

logger = logging.getLogger(__name__)


class PackageError(FetchfwError):
    pass


_COMMON_MANDATORY_KEYS = ['id', 'version', 'description']

def _check_pkg_info(pkg_info, mandatory_keys):
    for key in mandatory_keys:
        if key not in pkg_info:
            raise Exception("missing mandatory key %s" % key)


def _add_pkg_info_defaults(pkg_info):
    pkg_info.setdefault('depends', [])


class InstallablePackage(object):
    _MANDATORY_KEYS = _COMMON_MANDATORY_KEYS

    def __init__(self, pkg_info, remote_files, install_mgr):
        """Create a new installable package.
        
        pkg_info -- a dictionary with the following standardised keys:
          id -- id of the package (mandatory)
          version -- version of the package. See util.cmp_version for valid
            version examples (mandatory)
          description -- the description of the package (mandatory)
          description_<locale> -- the localized description of the package
            (optional)
          depends -- a list of package IDs on which this package depends
            (optional, default [])
        remotes_files -- a list of remote file
        install_mgr -- an installer manager or None
        
        Note that pkg_info values must be only of these type:
        - int
        - float
        - boolean
        - unicode string
        - list
        - dict
        
        All pkg_info keys must match \w+ and contains only character from the ASCII set.
        
        """
        _check_pkg_info(pkg_info, self._MANDATORY_KEYS)
        _add_pkg_info_defaults(pkg_info)
        self.pkg_info = pkg_info
        self.remote_files = remote_files
        self.install_mgr = install_mgr

    def clone(self):
        new_pkg_info = copy.deepcopy(self.pkg_info)
        return InstallablePackage(new_pkg_info, self.remote_files, self.install_mgr)

    def new_installed_package(self):
        # Note that for this to works, self must already have all mandatory keys
        # in it's info 
        new_pkg_info = copy.deepcopy(self.pkg_info)
        return InstalledPackage(new_pkg_info)

    def __str__(self):
        return "%s %s" % (self.pkg_info['id'], self.pkg_info['version'])


class InstalledPackage(object):
    _MANDATORY_KEYS = _COMMON_MANDATORY_KEYS + ['files', 'explicit_install']

    def __init__(self, pkg_info):
        """Create a new installed package.
        
        pkg_info -- same as pkg_info for installable package but adds the
          following standardized keys:
          explicit_install -- a boolean, true if the package was explictly
            installed (mandatory)
          files -- a list of files that were created on the host filesysmtem
            during installation (mandatory)
          
        """
        _check_pkg_info(pkg_info, self._MANDATORY_KEYS)
        _add_pkg_info_defaults(pkg_info)
        self.pkg_info = pkg_info

    def __str__(self):
        return "%s %s" % (self.pkg_info['id'], self.pkg_info['version'])


class PackageManager(object):
    def __init__(self, installable_pkg_sto, installed_pkg_sto):
        self.installable_pkg_sto = installable_pkg_sto
        self.installed_pkg_sto = installed_pkg_sto

    def _remove_installed_paths(self, installed_paths, root_dir):
        # This method never raise an error
        removed_paths = []
        try:
            # this rely on the fact that remove_paths is a generator
            for removed_path in remove_paths(installed_paths, root_dir):
                removed_paths.append(removed_path)
        except Exception, e:
            # error while removing files we were succesfull at installating
            non_removed_paths = list(set(installed_paths).difference(removed_paths))
            logger.warning('Error while removing already installed files: %s' %
                           e, exc_info=True)
            logger.warning('The following files have been left in %s: %s' %
                           (root_dir, non_removed_paths))

    def _install_pkg_from_install_mgr(self, install_mgr, root_dir, pkg_id):
        install_process = install_mgr.new_installation_process()
        result_dir = install_process.execute()

        installed_paths = []
        # this rely on the fact that install_paths is a generator (see doc)
        try:
            for installed_path in install_paths(result_dir, root_dir):
                installed_paths.append(installed_path)
        except Exception, e:
            logger.error('Error during installation of pkg %s in %s: %s' %
                         (pkg_id, root_dir, e))
            # preserve stack trace while removing installed files
            try:
                raise
            finally:
                self._remove_installed_paths(installed_paths, root_dir)
        else:
            return installed_paths
        finally:
            install_process.cleanup()

    def _install_pkg(self, installable_pkg, root_dir):
        # install the installable pkg and update the installed pkg sto
        pkg_id = installable_pkg.pkg_info['id']

        # install files
        install_mgr = installable_pkg.install_mgr
        if install_mgr is None:
            logger.debug("No install mgr for pkg %s" % pkg_id)
            files = []
        else:
            files = self._install_pkg_from_install_mgr(install_mgr, root_dir, pkg_id)

        # commit to installed database
        try:
            installable_pkg.pkg_info['files'] = files
            installed_pkg = installable_pkg.new_installed_package()

            self.installed_pkg_sto.upsert_pkg(installed_pkg)
        except Exception, e:
            logger.error("Error while commiting pkg %s to storage: %s" %
                         (pkg_id, e))
            # preserve stack trace while removing installed files
            try:
                raise
            finally:
                self._remove_installed_paths(files, root_dir)
        else:
            return installed_pkg

    def install(self, raw_pkg_ids, root_dir, installer_ctrl_factory):
        # 1. do some preparation
        installable_pkg_sto = self.installable_pkg_sto
        installed_pkg_sto = self.installed_pkg_sto
        # 1.1. instantiate an installer controller
        installer_ctrl = installer_ctrl_factory(installable_pkg_sto,
                                                installed_pkg_sto)
        installer_ctrl.pre_installation()

        try:
            # 2. preprocessing
            # 2.1. get the list of package ids to install
            pkg_ids = installer_ctrl.preprocess_raw_pkg_ids(raw_pkg_ids)

            # 2.2. get the list of packages to install
            # next line raise an error if one of pkg id is invalid, which is what we want
            raw_pkgs = [installable_pkg_sto[pkg_id].clone() for pkg_id in pkg_ids]
            pkgs = installer_ctrl.preprocess_raw_pkgs(raw_pkgs)

            # 2.3. get the list of remote files to download
            # this is a quick way to get the list of unique remote files
            raw_remote_files = dict((remote_file.path, remote_file) for pkg in pkgs
                                    for remote_file in pkg.remote_files).values()
            remote_files = installer_ctrl.preprocess_raw_remote_files(raw_remote_files)

            # 3. download remote files
            installer_ctrl.pre_download(remote_files)
            for remote_file in remote_files:
                installer_ctrl.download_file(remote_file)
            installer_ctrl.post_download(remote_files)

            # 4. install package
            installer_ctrl.pre_install(pkgs)
            for pkg in pkgs:
                installer_ctrl.pre_install_pkg(pkg)
                self._install_pkg(pkg, root_dir)
                installer_ctrl.post_install_pkg(pkg)
            installer_ctrl.post_install(pkgs)
        except Exception, e:
            # preserve stack trace
            try:
                raise
            finally:
                try:
                    installer_ctrl.post_installation(e)
                except Exception, e:
                    logger.error("Error during installer post installation: %s",
                                 e, exc_info=True)
        else:
            installer_ctrl.post_installation(None)

    def _uninstall_pkg(self, installed_pkg, root_dir):
        # uninstall the installed pkg and update the installed pkg sto
        pkg_id = installed_pkg.pkg_info['id']
        installed_paths = installed_pkg.pkg_info['files']

        removed_paths = []
        try:
            for removed_path in remove_paths(installed_paths, root_dir):
                removed_paths.append(removed_path)
        except Exception, e:
            logger.error("Error while removing files of pkg %s: %s" % (pkg_id, e))
            if removed_paths:
                logger.error("These files have been removed from %s although the"
                                 "package will still be shown as installed: %s" %
                                 (root_dir, removed_path))
            raise
        else:
            try:
                self.installed_pkg_sto.delete_pkg(pkg_id)
            except Exception, e:
                logger.error("Error while commiting pkg %s to storage: %s" %
                             (pkg_id, e))
                if removed_paths:
                    logger.error("These files have been removed from %s although the"
                                 "package will still be shown as installed: %s" %
                                 (root_dir, removed_path))
                raise

    def uninstall(self, raw_pkg_ids, root_dir, uninstaller_ctrl_factory):
        # 1. do some preparation
        installable_pkg_sto = self.installable_pkg_sto
        installed_pkg_sto = self.installed_pkg_sto
        # 1.1. instantiate an installer controller
        uninstaller_ctrl = uninstaller_ctrl_factory(installable_pkg_sto,
                                                    installed_pkg_sto)
        uninstaller_ctrl.pre_uninstallation()

        try:
            # 2. preprocessing
            # 2.1. get the list of package ids to uninstall
            pkg_ids = uninstaller_ctrl.preprocess_raw_pkg_ids(raw_pkg_ids)

            # 2.2. get the list of packages to install
            # next line raise an error if one of pkg id is invalid, which is what we want
            raw_pkgs = [installed_pkg_sto[pkg_id] for pkg_id in pkg_ids]
            pkgs = uninstaller_ctrl.preprocess_raw_pkgs(raw_pkgs)

            # 3. uninstall package
            uninstaller_ctrl.pre_uninstall(pkgs)
            for pkg in pkgs:
                uninstaller_ctrl.pre_uninstall_pkg(pkg)
                self._uninstall_pkg(pkg, root_dir)
                uninstaller_ctrl.post_uninstall_pkg(pkg)
            uninstaller_ctrl.post_uninstall(pkgs)
        except Exception, e:
            # preserve stack trace
            try:
                raise
            finally:
                try:
                    uninstaller_ctrl.post_uninstallation(e)
                except Exception, e:
                    logger.error('Error during uninstaller post uninstallation: %s',
                                 e, exc_info=True)
        else:
            uninstaller_ctrl.post_uninstallation(None)

    def _get_raw_upgrade_list(self):
        # Return a list of tuple (<installed package>, <installable_pkg>) for
        # which the version differs
        raw_upgrade_list = []
        for installed_pkg in self.installed_pkg_sto.itervalues():
            pkg_id = installed_pkg.pkg_info['id']
            if pkg_id in self.installable_pkg_sto:
                installable_pkg = self.installable_pkg_sto[pkg_id]
                if installable_pkg.pkg_info['version'] != installed_pkg.pkg_info['version']:
                    installable_pkg = self.installable_pkg_sto[pkg_id].clone()
                    installable_pkg.pkg_info['explicit_install'] = \
                        installed_pkg.pkg_info['explicit_install']
                    raw_upgrade_list.append((installed_pkg, installable_pkg))
        return raw_upgrade_list

    def upgrade(self, root_dir, upgrader_ctrl_factory):
        # 1. do some preparation
        installable_pkg_sto = self.installable_pkg_sto
        installed_pkg_sto = self.installed_pkg_sto
        # 1.1. instantiate an installer controller
        upgrader_ctrl = upgrader_ctrl_factory(installable_pkg_sto,
                                              installed_pkg_sto)
        upgrader_ctrl.pre_upgradation()

        try:
            raw_upgrade_list = self._get_raw_upgrade_list()

            # 2. preprocess stuff
            # 2.1. 
            upgrade_list = upgrader_ctrl.preprocess_raw_upgrade_list(raw_upgrade_list)

            # 2.2. from this list, get any package that should be 
            #      uninstalled/installed at the same time
            upgrade_specs = upgrader_ctrl.preprocess_upgrade_list(upgrade_list)

            # 2.3. get the list of remote files to download
            raw_remote_files_dict = {}
            for _, installable_pkg, install_list, _ in upgrade_specs:
                for pkg in [installable_pkg] + install_list:
                    for remote_file in pkg.remote_files:
                        raw_remote_files_dict[remote_file.path] = remote_file
            raw_remote_files = raw_remote_files_dict.values()
            remote_files = upgrader_ctrl.preprocess_raw_remote_files(raw_remote_files)

            # 3. download remote files
            upgrader_ctrl.pre_download(remote_files)
            for remote_file in remote_files:
                upgrader_ctrl.download(remote_file)
            upgrader_ctrl.post_download(remote_files)

            # 4. upgrade packages
            upgrader_ctrl.pre_upgrade(upgrade_specs)
            for installed_pkg, installable_pkg, install_list, uninstall_list in upgrade_specs:
                # 4.1 first uninstall pkg from the list
                for cur_installed_pkg in uninstall_list:
                    upgrader_ctrl.pre_upgrade_uninstall_pkg(cur_installed_pkg)
                    self._uninstall_pkg(cur_installed_pkg, root_dir)
                    upgrader_ctrl.post_upgrade_uninstall_pkg(cur_installed_pkg)
                # 4.2 then install pkg from the list
                for cur_installable_pkg in install_list:
                    upgrader_ctrl.pre_upgrade_install_pkg(cur_installable_pkg)
                    self._install_pkg(pkg, root_dir)
                    upgrader_ctrl.post_upgrade_install_pkg(cur_installable_pkg)
                # 4.3 then "upgrade" installed pkg, i.e. uninstall and install
                upgrader_ctrl.pre_upgrade_pkg(installed_pkg)
                self._uninstall_pkg(installed_pkg, root_dir)
                self._install_pkg(installable_pkg, root_dir)
                upgrader_ctrl.post_upgrade_pkg(installed_pkg)
            upgrader_ctrl.post_upgrade(upgrade_specs)
        except Exception, e:
            # preserve stack trace
            try:
                raise
            finally:
                try:
                    upgrader_ctrl.post_upgradation(e)
                except Exception, e:
                    logger.error('Error during upgrader post upgradation: %s',
                                 e, exc_info=True)
        else:
            upgrader_ctrl.post_upgradation(None)


class InstallerController(object):
    """The method are shown in the order they are called.
    
    All installer controller should inherit from this one. Although this class
    is a valid installer controller, it's so basic that you mostly do not want
    to use it directly.
    
    """

    def __init__(self, installable_pkg_sto, installed_pkg_sto):
        pass

    def pre_installation(self):
        """Called before anything else, i.e. just after installer controller
        creation.
        
        Return value is ignored. 
        
        """
        pass

    def preprocess_raw_pkg_ids(self, raw_pkg_ids):
        """Return a list of package IDs from the given list of package IDs.
        
        Every returned package ID must be in the installable package storage.
        
        In this function, you could do things like:
        - remove package from the ignore list (?)
        - print a warning message and raise an exception if a pkg id is
          invalid
        
        """
        return raw_pkg_ids

    def preprocess_raw_pkgs(self, raw_installable_pkgs):
        """Return a list of package from the given list of packages.
        
        In this function, you could do things like:
        - add dependencies
        - remove the package that are already installed
        - print a warning if a package to be installed is older than an
          already installed package
        
        Note that you can modify the list and the packages given in arguments.
        
        """
        for installable_pkg in raw_installable_pkgs:
            installable_pkg.pkg_info['explicit_install'] = True
        return raw_installable_pkgs

    def preprocess_raw_remote_files(self, raw_remote_files):
        """Return a list of remote file from the given list of remote files.
        
        In this function, you could do things like:
        - remove already downloaded remote files
        
        """
        return [xfile for xfile in raw_remote_files if not xfile.exists()]

    def pre_download(self, remote_files):
        """Called before any files have downloaded."""
        pass

    def download_file(self, remote_file):
        """Called to download the next file."""
        remote_file.download()

    def post_download(self, remote_files):
        """Called after every files have been downloaded."""
        pass

    def pre_install(self, installable_pkgs):
        """Called before the installation of any pkg."""
        pass

    def pre_install_pkg(self, installable_pkg):
        """Called before the installation of the given installable pkg."""
        pass

    def post_install_pkg(self, installable_pkg):
        """Called after the successful installation of the given installable pkg."""
        pass

    def post_install(self, installable_pkgs):
        """Called after the successful installation of all pkg."""
        pass

    def post_installation(self, exc_value):
        """Called after anything else (will be called if pre_installation returned successfully)
        exc_value is None if no error, else the exception value
        
        """
        pass

    @classmethod
    def new_factory(cls, *args, **kwargs):
        def aux(installable_pkg_sto, installed_pkg_sto):
            return cls(installable_pkg_sto, installed_pkg_sto, *args, **kwargs)
        return aux


class DefaultInstallerController(InstallerController):
    def __init__(self, installable_pkg_sto, installed_pkg_sto,
                 nodeps=False):
        self._installable_pkg_sto = installable_pkg_sto
        self._installed_pkg_sto = installed_pkg_sto
        self._nodeps = nodeps

    def preprocess_raw_pkg_ids(self, raw_pkg_ids):
        # check that all package are installable and raise our own
        # error even though this job is redone indirectly by the
        # package manager
        for pkg_id in raw_pkg_ids:
            if pkg_id not in self._installable_pkg_sto:
                raise PackageError("could not find package '%s'" % pkg_id)
        return raw_pkg_ids

    def preprocess_raw_pkgs(self, raw_installable_pkgs):
        installable_pkgs = list(raw_installable_pkgs)
        for installable_pkg in installable_pkgs:
            installable_pkg.pkg_info['explicit_install'] = True
        if not self._nodeps:
            pkg_ids = set(pkg.pkg_info['id'] for pkg in installable_pkgs)
            def filter_fun(dep_pkg_id):
                return dep_pkg_id not in self._installed_pkg_sto and \
                       dep_pkg_id not in pkg_ids
            dependencies = self._installable_pkg_sto.get_dependencies_many(
                    pkg_ids, filter_fun=filter_fun)
            for dep_pkg_id in dependencies:
                dep_pkg = self._installable_pkg_sto[dep_pkg_id].clone()
                dep_pkg.pkg_info['explicit_install'] = False
                installable_pkgs.append(dep_pkg)
        return installable_pkgs


class UninstallerController(object):
    # TODO add comments

    def __init__(self, installable_pkg_sto, installed_pkg_sto):
        pass

    def pre_uninstallation(self):
        pass

    def preprocess_raw_pkg_ids(self, raw_pkg_ids):
        return raw_pkg_ids

    def preprocess_raw_pkgs(self, raw_installed_pkgs):
        return raw_installed_pkgs

    def pre_uninstall(self, installed_pkgs):
        pass

    def pre_uninstall_pkg(self, installed_pkg):
        pass

    def post_uninstall_pkg(self, installed_pkg):
        pass

    def post_uninstall(self, installed_pkgs):
        pass

    def post_uninstallation(self, exc_value):
        pass

    @classmethod
    def new_factory(cls, *args, **kwargs):
        def aux(installable_pkg_sto, installed_pkg_sto):
            return cls(installable_pkg_sto, installed_pkg_sto, *args, **kwargs)
        return aux


class DefaultUninstallerController(UninstallerController):
    def __init__(self, installable_pkg_sto, installed_pkg_sto,
                 recursive=False):
        self._installable_pkg_sto = installable_pkg_sto
        self._installed_pkg_sto = installed_pkg_sto
        self._recursive = recursive

    def preprocess_raw_pkg_ids(self, raw_pkg_ids):
        for pkg_id in raw_pkg_ids:
            # Check that each pkg_id in pkg_ids is installed on this system
            if pkg_id not in self._installed_pkg_sto:
                raise PackageError("package '%s' not found" % pkg_id)
            # Check that there's no installed package that depends on one of the
            # package that we are about to uninstall
            requisite_ids = self._installed_pkg_sto.get_requisites(pkg_id)
            requisite_ids.difference_update(raw_pkg_ids)
            if requisite_ids:
                raise PackageError("%s is required by: %s" %
                                   (pkg_id, ' '.join(requisite_ids)))
        return raw_pkg_ids

    def preprocess_raw_pkgs(self, raw_installed_pkgs):
        installed_pkgs = list(raw_installed_pkgs)
        if self._recursive:
            # some cases are complex to handle, this is why this might
            # seems overly complex
            to_remove_ids = set(pkg.pkg_info['id'] for pkg in installed_pkgs)
            def filter_fun(dep_pkg_id):
                # next line should never raise a KeyError since we are asking
                # to ignore missing dependencies
                dep_pkg = self._installed_pkg_sto[dep_pkg_id]
                return not dep_pkg.pkg_info['explicit_install']
            candidate1_ids = self._installed_pkg_sto.get_dependencies_many(
                    to_remove_ids, filter_fun=filter_fun, ignore_missing=True)
            candidate2_ids = set(candidate1_ids)
            candidate2_ids.difference_update(to_remove_ids)
            augm_candidate1_ids = set(candidate1_ids)
            augm_candidate1_ids.update(to_remove_ids)
            for candidate_id in candidate1_ids:
                requisite_ids = self._installed_pkg_sto.get_requisites(candidate_id)
                if not requisite_ids.issubset(augm_candidate1_ids):
                    dependency_ids = self._installed_pkg_sto.get_dependencies(
                            candidate_id, ignore_missing=True)
                    candidate2_ids.discard(candidate_id)
                    candidate2_ids.difference_update(dependency_ids)
            for candidate_id in candidate2_ids:
                installed_pkgs.append(self._installed_pkg_sto[candidate_id])
        return installed_pkgs


class UpgraderController(object):
    # TODO add comments
    def __init__(self, installable_pkg_sto, installed_pkg_sto):
        pass

    def pre_upgradation(self):
        pass

    def preprocess_raw_upgrade_list(self, raw_upgrade_list):
        """Return the list of tuple (installed pkg, installable pkg) to
        upgrade from the list of (installed pkg, installable pkg) tuple
        that have a different version than their installable counterpart.
        
        """
        # By default, upgrade all package that are not in sync, which is
        # not what you want to do for more evolved package management
        return raw_upgrade_list

    def preprocess_upgrade_list(self, upgrade_list):
        """From the list of known to be upgraded pkgs, return a list of tuple
        (installed_pkg, [<new_to_install_pkg>], [<to_uninstall_pkg>])) such
        that both list doesn't contains the pkg of the installed pkg.
        
        Also, if a new package to install is found in more than in one list, it
        will be discard in the later list.
        
        """
        return [(ed_pkg, able_pkg, [], []) for (ed_pkg, able_pkg) in upgrade_list]

    def preprocess_raw_remote_files(self, raw_remote_files):
        return [xfile for xfile in raw_remote_files if not xfile.exists()]

    def pre_download(self, remote_files):
        pass

    def download_file(self, remote_file):
        remote_file.download()

    def post_download(self, remote_files):
        pass

    def pre_upgrade(self, upgrade_specs):
        """Called before the installation of any pkg."""
        pass

    def pre_upgrade_uninstall_pkg(self, installed_pkg):
        pass

    def post_upgrade_uninstall_pkg(self, installed_pkg):
        pass

    def pre_upgrade_install_pkg(self, installable_pkg):
        pass

    def post_upgrade_install_pkg(self, installable_pkg):
        pass

    def pre_upgrade_pkg(self, installed_pkg):
        pass

    def post_upgrade_pkg(self, installed_pkg):
        pass

    def post_upgrade(self, upgrade_specs):
        pass

    def post_upgradation(self, exc_value):
        pass

    @classmethod
    def new_factory(cls, *args, **kwargs):
        def aux(installable_pkg_sto, installed_pkg_sto):
            return cls(installable_pkg_sto, installed_pkg_sto, *args, **kwargs)
        return aux


class DefaultUpgraderController(UpgraderController):
    def __init__(self, installable_pkg_sto, installed_pkg_sto,
                 ignore=None,
                 nodeps=False):
        self._installable_pkg_sto = installable_pkg_sto
        self._installed_pkg_sto = installed_pkg_sto
        self._ignore = [] if ignore is None else ignore
        self._nodeps = nodeps

    def _upgrade_list_filter_function(self, (installed_pkg, installable_pkg)):
        # Return true if installed_pkg is not in the ignore list and if 
        # installable_pkg version is higher than installed_pkg version
        pkg_id = installed_pkg.pkg_info['id']
        if pkg_id in self._ignore:
            return False

        installed_version = installed_pkg.pkg_info['version']
        installable_version = installable_pkg.pkg_info['version']
        return cmp_version(installable_version, installed_version)

    def preprocess_raw_upgrade_list(self, raw_upgrade_list):
        return filter(self._upgrade_list_filter_function, raw_upgrade_list)

    def preprocess_upgrade_list(self, upgrade_list):
        installed_specs = []
        scheduled_pkg_ids = set(elem[0].pkg_info['id'] for elem in upgrade_list)
        for installed_pkg, installable_pkg in upgrade_list:
            install_list = []
            if not self._nodeps:
                pkg_id = installed_pkg.pkg_info['id']
                def filter_fun(dep_pkg_id):
                    return dep_pkg_id not in self._installed_pkg_sto and \
                           dep_pkg_id not in scheduled_pkg_ids
                dependencies = self._installable_pkg_sto.get_dependencies(
                        pkg_id, filter_fun=filter_fun)
                for dep_pkg_id in dependencies:
                    scheduled_pkg_ids.add(dep_pkg_id)
                    dep_pkg = self._installable_pkg_sto[dep_pkg_id].clone()
                    dep_pkg.pkg_info['explicit_install'] = False
                    install_list.append(dep_pkg)
            installed_specs.append((installed_pkg, installable_pkg, install_list, []))
        return installed_specs
