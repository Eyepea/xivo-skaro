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

import contextlib
import glob
import itertools
import logging
import os
import shutil
import tarfile
import tempfile
import zipfile
from fetchfw.util import FetchfwError, explode_path, wrap_exception, ends_with, remove_paths

logger = logging.getLogger(__name__)


class InstallationError(FetchfwError):
    pass


class InvalidInstallationGraphError(InstallationError):
    pass


class InstallationManager(object):
    """An installation manager.
    
    Has the following attributes:
      init_directory -- the directory in which nodes that doesn't depend on
        previous node will be run into
    """
    
    def __init__(self, installation_graph, init_directory=None):
        """Build an InstallationManager. installation_graph is a dictionary, for example:
             {'installers':
                 {'Installer1': (<StandardInstaller object>, 'ZipFilter1'),
                 },
              'filters':
                 {'ZipFilter1': (<ZipFilter object>, 'TarFilter1'),
                  'TarFilter1': (<TarFilter object>, None),
                 },
             }
             
           Raise an InvalidInstallationGraphError if the installation graph is invalid.
        """
        self._installation_graph = installation_graph
        self.init_directory = init_directory
        self._check_installation_graph_validity()

    def execute(self):
        """Launch the installation process and return a list of files and folders that have been
           installed.
        
        Raise an Exception if init_directory is not defined.
        
        """
        if self.init_directory is None:
            raise Exception('init_directory is not defined')
        installers = self._installation_graph['installers']
        filters = self._installation_graph['filters']
        input_dirs, output_dirs = self._create_directories_map()
        installed_files = set()
        try:
            for node_id in self._create_execution_plan():
                if node_id in filters:
                    filter = filters[node_id][0]
                    input_dir = input_dirs[node_id]
                    output_dir = output_dirs[node_id]
                    logger.debug("Executing filter '%s' - input '%s' - ouput '%s'",
                                 node_id, input_dir, output_dir)
                    filter.apply(input_dir, output_dir)
                else:
                    assert node_id in installers
                    installer = installers[node_id][0]
                    input_dir = input_dirs[node_id]
                    logger.debug("Executing installer '%s' - input '%s'", node_id, input_dir)
                    installed_files.update(installer.install(input_dir))
        except:
            logger.exception("Error during execution of installation manager")
            try:
                raise
            finally:
                remove_paths(installed_files)
        finally:
            logger.debug('Executing installation cleanup')
            for temp_dir in output_dirs.itervalues():
                logger.debug("Deleting temp directory '%s'" % temp_dir)
                shutil.rmtree(temp_dir, True)
        return sorted(installed_files)
    
    def _check_installation_graph_validity(self):
        """Check if the installation graph is valid, if not, raise an InstallationError."""
        self._check_nodes_id_are_unique()
        self._check_nodes_depend_on_filters_or_none()
        self._check_is_acyclic()
        self._check_no_useless_filter()
    
    def _check_nodes_id_are_unique(self):
        installer_ids = set(self._installation_graph['installers'])
        common_ids = installer_ids.intersection(self._installation_graph['filters'])
        if common_ids:
            raise InvalidInstallationGraphError("these IDs are shared by both an installer and a filter: %s" % common_ids)
        
    def _check_nodes_depend_on_filters_or_none(self):
        """Check that there's no unknown identifier in the installation graph, i.e. raise an
           exception if there's a node such that it depends on an unknown node.
        """
        installers = self._installation_graph['installers']
        filters = self._installation_graph['filters']
        for node_id, node_value in itertools.chain(installers.iteritems(), filters.iteritems()):
            node_dependency = node_value[1]
            if node_dependency is not None and node_dependency not in filters:
                raise InvalidInstallationGraphError("node '%s' depends on unknown filter '%s'" %
                                                    (node_id, node_dependency))
    
    def _check_no_useless_filter(self):
        """Check if every filters participate in the installation process, i.e. raise an exception
           if there's a filter such that no other filter or installer depend on it.
        """
        installers = self._installation_graph['installers']
        filters = self._installation_graph['filters']
        dependencies = set(v[1] for v in itertools.chain(installers.itervalues(), filters.itervalues()) if v is not None)
        for filter_id in filters:
            if filter_id not in dependencies:
                raise InvalidInstallationGraphError("filter '%s' is used by no filters nor installers" % filter_id)
    
    def _check_is_acyclic(self):
        """Check that the installation graph is acyclic."""
        filters = self._installation_graph['filters']
        visited = set()
        for node_id in filters:
            if node_id not in visited:
                currently_visited = set((node_id,))
                while True:
                    next_node_id = filters[node_id][1]
                    if next_node_id is None:
                        break
                    if next_node_id in currently_visited:
                        raise InvalidInstallationGraphError("a cycle in the installation graph has been detected")
                    currently_visited.add(next_node_id)
                    node_id = next_node_id
                visited.update(currently_visited)
    
    def _create_execution_plan(self):
        installers = self._installation_graph['installers']
        filters = self._installation_graph['filters']
        executed = set()
        def create_subplan(filter_id):
            if filter_id in executed:
                return ()
            # We can add filter_id to the executed set here since we suppose we have no cycle,
            # i.e. that means the subplan will never visit a node twice
            executed.add(filter_id)
            next_filter_id = filters[filter_id][1]
            if next_filter_id is None:
                return (filter_id,)
            else:
                return create_subplan(next_filter_id) + (filter_id,)
        result = []
        for installer_id, installer_val in installers.iteritems():
            filter_id = installer_val[1]
            if filter_id is not None:
                result.extend(create_subplan(filter_id))
            result.append(installer_id)
        return result 
    
    def _create_directories_map(self):
        installers = self._installation_graph['installers']
        filters = self._installation_graph['filters']
        output_map = dict((filter_id, tempfile.mkdtemp()) for filter_id in filters)
        input_map = {}
        for node_id, node_val in itertools.chain(filters.iteritems(), installers.iteritems()):
            dependency_id = node_val[1]
            if dependency_id is None:
                input_map[node_id] = self.init_directory
            else:
                input_map[node_id] = output_map[dependency_id]
        return input_map, output_map


class _GlobHelper(object):
    """The python glob module works only with the notion of the current directory.
       This class is used to facilitate the application of one or more glob patterns
       inside arbitrary directories.
    """
    def __init__(self, pathnames, error_on_no_matches=True):
        """pathnames can be either a single path name or an iterable of path names.
        """
        if isinstance(pathnames, basestring):
            self._pathnames = [os.path.normpath(pathnames)]
        else:
            self._pathnames = [os.path.normpath(pathname) for pathname in pathnames]
        if not self._pathnames:
            # XXX should we accept the case where self._pathnames is empty ?
            raise ValueError("no path names")
        for pathname in self._pathnames:
            if os.path.isabs(pathname):
                raise ValueError("path name '%s' is an absolute path" % pathname)
            if pathname.startswith(os.pardir):
                raise ValueError("path name '%s' makes reference to the parent directory" % pathname)
        self._error_on_no_matches = error_on_no_matches

    def glob_in_dir(self, src_directory):
        return list(self.iglob_in_dir(src_directory))
    
    def iglob_in_dir(self, src_directory):
        """Apply the glob patterns in src_directory and return each file matched."""
        no_matches = True
        for rel_pathname in self._pathnames:
            abs_pathname = os.path.join(src_directory, rel_pathname)
            for globbed_abs_pathname in glob.iglob(abs_pathname):
                no_matches = False
                yield globbed_abs_pathname
        if no_matches and self._error_on_no_matches:
            raise InstallationError("the glob patterns %s did not match anything in directory '%s'"
                                    % (self._pathnames, src_directory))


class StandardInstaller(object):
    """An installer instance if an object taking a source directory containing files
       and folders and copying the ones it's interested in into a destination
       directory (or sub-directory), returning the list of files it has added to the
       destination directory. 
    """
    
    def __init__(self, pathnames, dst, error_handler=None):
        """-pathnames can be either a single glob pattern or an iterator over multiple
            glob patterns.
           -dst is either a directory name, if it ends with '/', or else a file name.
            This must be explicit because the installer create any missing directory
            when copying files.
        """
        self._glob_helper = _GlobHelper(pathnames)
        self._dst = dst
        self._error_handler = error_handler
        
    def install(self, src_directory):
        dst_is_dir = self._dst.endswith('/')
        installed_files = set()
        try:
            if os.path.exists(self._dst):
                if os.path.isdir(self._dst) != dst_is_dir:
                    if dst_is_dir:
                        raise InstallationError("destination exists and is a file but should be a directory")
                    else:
                        raise InstallationError("destination exists and is a directory but should be a file")
            else:
                dirname = os.path.dirname(self._dst)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            installed_files.update(ends_with(path, '/') for path in explode_path(os.path.dirname(self._dst)) if path != '/')
            if dst_is_dir:
                self._install_dir(src_directory, installed_files)
            else:
                self._install_file(src_directory, installed_files)
            return installed_files
        except EnvironmentError, e:
            logger.exception("Error during execution of installer")
            remove_paths(installed_files)
            raise InstallationError(e)
        
    def _install_dir(self, src_directory, installed_files):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            if os.path.isdir(pathname):
                src_dir_name = os.path.basename(pathname)
                shutil.copytree(pathname, os.path.join(self._dst, src_dir_name), True)
                for root, _, files in os.walk(os.path.join(self._dst, src_dir_name)):
                    installed_files.add(ends_with(root, '/'))
                    for file in files:
                        installed_files.add(os.path.join(root, file))
            else:
                shutil.copy(pathname, self._dst)
                installed_files.add(os.path.join(self._dst, os.path.basename(pathname)))
    
    def _install_file(self, src_directory, installed_files):
        pathnames = self._glob_helper.glob_in_dir(src_directory)
        if len(pathnames) > 1:
            raise InstallationError("glob pattern matched %d files" % len(pathnames))
        pathname = pathnames[0]
        shutil.copy(pathname, self._dst)
        installed_files.add(self._dst)
    


class ZipFilter(object):
    """A filter who transform a directory containing zip files to a directory containing
       the content of these zip files.
    """
    def __init__(self, pathnames):
        self._glob_helper = _GlobHelper(pathnames)
        
    @wrap_exception((EnvironmentError, zipfile.BadZipfile), InstallationError, logger)
    def apply(self, src_directory, dst_directory):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            with contextlib.closing(zipfile.ZipFile(pathname, 'r')) as zf:
                zf.extractall(dst_directory)


class TarFilter(object):
    """A filter who transform a directory containing tar files to a directory containing
       the content of these tar files. The tar files can be either uncompressed, gzipped
       or bz2-ipped.
    """
    def __init__(self, pathnames):
        self._glob_helper = _GlobHelper(pathnames)
    
    @wrap_exception((EnvironmentError, tarfile.TarError), InstallationError, logger)
    def apply(self, src_directory, dst_directory):
        for pathname in self._glob_helper.iglob_in_dir(src_directory):
            with contextlib.closing(tarfile.open(pathname)) as tf:
                tf.extractall(dst_directory)


class CiscoUnsignFilter(object):
    """A filter who transform a directory containing a Cisco-signed gzip file to a directory
       containing the gzipped file inside the signed file.
    """
    _BUF_SIZE = 512
    _GZIP_MAGIC_NUMBER = '\x1f\x8b'  # see http://www.gzip.org/zlib/rfc-gzip.html#file-format
    
    def __init__(self, signed_pathname, unsigned_pathname):
        """Note: signed_pathname can be a glob pattern, but when the pattern is expanded,
           it must match only ONE file or an error will be raised. This is for convenience, so
           that if you don't know the exact name of a file, you can still use a glob pattern to
           match it.
        """
        self._glob_helper = _GlobHelper(signed_pathname)
        self._unsigned_pathname = os.path.normpath(unsigned_pathname)
        if os.path.isabs(self._unsigned_pathname):
            raise ValueError("unsigned path name '%s' is an absolute path" % self._unsigned_pathname)
        if self._unsigned_pathname.startswith(os.pardir):
            raise ValueError("unsigned path name '%s' makes reference to the parent directory" % self._unsigned_pathname)
    
    @wrap_exception(EnvironmentError, InstallationError, logger)
    def apply(self, src_directory, dst_directory):
        signed_pathnames = self._glob_helper.glob_in_dir(src_directory)
        if len(signed_pathnames) > 1:
            raise InstallationError("glob pattern matched %d files" % len(signed_pathnames))
        signed_pathname = signed_pathnames[0]
        with open(signed_pathname, 'rb') as sf:
            buf = sf.read(CiscoUnsignFilter._BUF_SIZE)
            index = buf.find(CiscoUnsignFilter._GZIP_MAGIC_NUMBER)
            if index == -1:
                raise InstallationError("Couldn't find gzip magic number in the signed file.")
            unsigned_filename = os.path.join(dst_directory, self._unsigned_pathname)
            with open(unsigned_filename, 'wb') as f:
                f.write(buf[index:])
                shutil.copyfileobj(sf, f)


class ExcludeFilter(object):
    """A filter who excludes some files of the source directory from the destination
       directory. Excluded files can be either files, directories or both.
    """
    def __init__(self, pathnames):
        self._glob_helper = _GlobHelper(pathnames, False)
        
    @wrap_exception(EnvironmentError, InstallationError, logger)
    def apply(self, src_directory, dst_directory):
        abs_excluded_paths = set(self._glob_helper.iglob_in_dir(src_directory))
        rel_dir_stack = [os.curdir]
        while rel_dir_stack:
            rel_current_dir = rel_dir_stack.pop()
            abs_current_dir = os.path.join(src_directory, rel_current_dir)
            for file in os.listdir(abs_current_dir):
                rel_file = os.path.normpath(os.path.join(rel_current_dir, file))
                abs_file = os.path.join(src_directory, rel_file)
                if abs_file not in abs_excluded_paths:
                    if os.path.isdir(abs_file):
                        os.mkdir(os.path.join(dst_directory, rel_file))
                        rel_dir_stack.append(rel_file)
                    elif os.path.isfile(abs_file):
                        shutil.copy(abs_file, os.path.join(dst_directory, rel_file))
