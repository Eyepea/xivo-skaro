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

import ConfigParser
import logging
import os
import re
from binascii import a2b_hex
from fetchfw import download, install, package, util

logger = logging.getLogger(__name__)


class StorageError(util.FetchfwError):
    pass


class ParsingError(StorageError):
    pass


class NodeBuilder(object):
    """A node builder takes a series of tokens and returns one node object
    (either a 'filter' or 'installer' node) for an installation manager.
    
    """
    def _build_unzip(self, args, tokens):
        if len(args) != 1:
            raise ParsingError("invalid number of arguments for unzip: '%s'"
                               % ' '.join(tokens))
        return 'filters', install.ZipFilter(args[0])
    
    def _build_untar(self, args, tokens):
        if len(args) != 1:
            raise ParsingError("invalid number of arguments for untar: '%s'"
                               % ' '.join(tokens))
        return 'filters', install.TarFilter(args[0])
    
    def _build_unrar(self, args, tokens):
        if len(args) != 1:
            raise ParsingError("invalid number of arguments for unrar: '%s'"
                               % ' '.join(tokens))
        return 'filters', install.RarFilter(args[0])
    
    def _build_unsign(self, args, tokens):
        if len(args) != 2:
            raise ParsingError("invalid number of arguments for unsign: '%s'"
                               % ' '.join(tokens))
        return 'filters', install.CiscoUnsignFilter(args[0], args[1])
    
    def _build_exclude(self, args, tokens):
        if not args:
            raise ParsingError("invalid number of arguments for exclude: '%s'"
                               % ' '.join(tokens))
        return 'filters', install.ExcludeFilter(args)
    
    def _build_cp(self, args, tokens):
        if len(args) < 2:
            raise ParsingError("invalid number of arguments for cp: '%s'"
                               % ' '.join(tokens))
        return 'installers', install.StandardInstaller(args[:-1], args[-1])
    
    def build_node(self, tokens):
        """Return a pair (node_type, node_object) from a string arguments.
        
        node_type can be one of the following: 'filters', 'installers'.
          If 'filters' is returned, then node_object provides the 'filter' interface.
          If 'installers' is returned, then node_object provides the 'installer' interface.
        
        Raise an Exception if arguments are not in the right number or invalid.
        
        Pre: len(tokens) >= 1
        
        """
        type, args = tokens[0], tokens[1:]
        method_name = '_build_' + type
        try:
            fun = getattr(self, method_name)
        except AttributeError:
            raise ParsingError("unknown type '%s': '%s'"
                               % (type, ' '.join(tokens)))
        else:
            return fun(args, tokens)


class InstallationMgrBuilder(object):
    """An installation manager builder takes a config object (RawConfigParser)
    and a section and builds an installation manager from it.
    
    """
    def __init__(self, node_builder=NodeBuilder()):
        self._node_builder = node_builder
        
    def _get_src_and_dst(self, name, section):
        try:
            src, dst = name.split('-')
        except ValueError:
            raise ParsingError("'%s' is not a valid key in install definition '%s'" %
                               (name, section))
        else:
            if src == 'a':
                src = None
            return src, dst
    
    def _tokenize(self, value, section):
        tokens = value.split()
        if not tokens:
            raise ParsingError("'%s' is not a valid value in install definition '%s'" %
                               (value, section))
        return tokens
    
    def _substitute(self, raw_tokens, variables):
        return [util.apply_subs(token, variables) for token in raw_tokens]
    
    def build_installation_mgr(self, config, section, variables, cache_dir):
        graph = {'installers': {}, 'filters': {}}
        for name, value in config.items(section):
            src, dst = self._get_src_and_dst(name, section)
            raw_tokens = self._tokenize(value, section)
            tokens = self._substitute(raw_tokens, variables)
            
            node_type, node_obj = self._node_builder.build_node(tokens)
            try:
                graph[node_type][dst] = (node_obj, src)
            except KeyError:
                raise Exception("node_builder returned an unknown node_type '%s'" % node_type)
        return install.InstallationManager(graph, cache_dir)


class RemoteFileBuilder(object):
    """A remote file builder takes a config object (RawConfigParser) and a
    section and builds a remote file (RemoteFile) from it.
    
    """
    def __init__(self, downloaders):
        self._downloaders = downloaders
    
    def build_remote_file(self, config, section, cache_dir):
        url = config.get(section, 'url')
        size = config.getint(section, 'size')
        sha1sum = a2b_hex(config.get(section, 'sha1sum'))
        if config.has_option(section, 'filename'):
            filename = config.get(section, 'filename')
        else:
            filename = os.path.basename(url)
        path = os.path.join(cache_dir, filename)
        if config.has_option(section, 'downloader'):
            downloader_name = config.get(section, 'downloader')
        else:
            downloader_name = 'default'
        try:
            downloader = self._downloaders[downloader_name]
        except KeyError:
            raise ParsingError("'%s' is not a valid downloader name in filedef '%s'"
                               % (downloader_name, section))
        return download.RemoteFile(path, url, downloader, size, [download.SHA1Hook.create_factory(sha1sum)])


class DefaultInstallablePkgStorage(util.ReadOnlyForwardingDictMixin('_pkgs')):
    def __init__(self, installable_dir, cache_dir, rfile_builder, install_mgr_builder, variables):
        self._installable_dir = installable_dir
        self._cache_dir = cache_dir
        self._rfile_builder = rfile_builder
        self._install_mgr_builder = install_mgr_builder
        self._variables = dict(variables)
        self._pkgs = {}
        self._load_pkgs()
    
    def _load_pkgs(self):
        self._pkgs.clear()
        config = self._read_config_files()
        remote_files = self._create_remote_files_from_config(config)
        self._pkgs = self._create_installable_pkgs_from_config(config, remote_files)
    
    def _read_config_files(self):
        dir = self._installable_dir
        config = ConfigParser.RawConfigParser()
        try:
            for path in (os.path.join(dir, path) for path in os.listdir(dir) if not path.startswith('.')):
                with open(path, 'r') as f:
                    config.readfp(f)
        except IOError, e:
            raise StorageError("could not open/read file '%s': %s" % (path, e))
        except ConfigParser.ParsingError, e:
            raise StorageError("could not parse file '%s': %s" % (path, e))
        return config
    
    def _create_remote_files_from_config(self, config):
        res = {}
        for section in config.sections():
            if section.startswith('file_'):
                res[section] = self._rfile_builder.build_remote_file(config, section, self._cache_dir)
        return res
    
    def _create_installable_pkgs_from_config(self, config, remote_files):
        # TODO sensible error handling...
        pkgs = {}
        for section in config.sections():
            if section.startswith('pkg_'):
                assert section[:4] == 'pkg_'
                name = section[4:]  # name of the package definition
                desc = config.get(section, 'desc')
                version = config.get(section, 'version')
                if config.has_option(section, 'hidden'):
                    hidden_raw = config.get(section, 'hidden')
                    if hidden_raw not in ('yes', 'no'):
                        raise ParsingError("'%s' is not a valid hidden value in pkgdef '%s'"
                                           % (hidden_raw, section))
                    hidden = True if hidden_raw == 'yes' else False
                else:
                    hidden = False
                if config.has_option(section, 'depends'):
                    depends_raw = config.get(section, 'depends')
                    depends = []
                    for token in depends_raw.split():
                        if not token.startswith('pkg_'):
                            raise ParsingError("pkgdef '%s' depends on non-pkg '%s'"
                                               % (section, token))
                        if not config.has_section(token):
                            raise ParsingError("pkgdef '%s' depends on unknown pkgdef '%s'"
                                               % (section, token))
                        assert token[:4] == 'pkg_'
                        depends.append(token[4:])
                else:
                    depends = []
                if config.has_option(section, 'files'):
                    files_raw = config.get(section, 'files')
                    cur_remote_files = []
                    for token in files_raw.split():
                        if token not in remote_files:
                            raise ParsingError("pkgdef '%s' uses unknown file '%s'"
                                               % (section, token)) 
                        cur_remote_files.append(remote_files[token])
                else:
                    cur_remote_files = []
                if not config.has_option(section, 'install_proc'):
                    if cur_remote_files:
                        raise ParsingError("pkgdef '%s' uses at least one remote file but has no install_proc"
                                           % section)
                    install_mgr = None
                else:
                    install_proc_tokens = config.get(section, 'install_proc').split()
                    install_proc_name = install_proc_tokens[0]
                    if not install_proc_name.startswith('install_') or not config.has_section(install_proc_name):
                        raise ParsingError("'%s' is not a valid install_proc value in pkgdef '%s'"
                                           % (install_proc_name, section))
                    # we generate the variable that could be used by the installation manager
                    variables = dict(self._variables)
                    for i, remote_file in enumerate(cur_remote_files):
                        variables['FILE%d' % (i + 1)] = remote_file.filename
                    for i, install_arg in enumerate(install_proc_tokens[1:]):
                        variables['ARG%d' % (i + 1)] = install_arg
                    install_mgr = self._install_mgr_builder.build_installation_mgr(config, install_proc_name, variables, self._cache_dir)
                pkgs[name] = package.InstallablePackage(name, version, desc, hidden, depends,
                                                        cur_remote_files, install_mgr)
        return pkgs
    
    def reload(self):
        self._load_pkgs()
        
    def update(self):
        # TODO
        pass


def _strip_line(lines):
    for line in lines:
        yield line.rstrip()

        
def _ignore_empty(lines):
    for line in lines:
        if line:
            yield line


class _SimpleFormatParser(object):
    # XXX name is not good
    _RE_SECTION = re.compile(r'^\[([^\]]+)\]$')
    
    def __init__(self, file):
        if isinstance(file, basestring):
            with open(file, 'r') as f:
                self._parse_fobj(f)
        else:
            self._parse_fobj(file)
    
    def _parse_fobj(self, fobj):
        self._dict = {}
        cur_list = None
        for line in _ignore_empty(_strip_line(fobj)):
            m = self._RE_SECTION.match(line)
            if m:
                # new section
                cur_list = []
                self._dict[m.group(1)] = cur_list
            else:
                if cur_list is None:
                    raise ParsingError("value line before section")
                cur_list.append(line)
    
    def get_as_list(self, name, default=None):
        return self._dict.get(name, default)
    
    def get_as_string(self, name, default=None):
        res = self._dict.get(name, default)
        if id(res) == id(default) or not res:
            # a section with no values
            return default
        return res[0]
    
    def __contains__(self, item):
        return item in self._dict


def _yes_no_to_bool(string):
    if string == 'yes':
        return True
    elif string == 'no':
        return False
    else:
        raise ParsingError("'%s' is not a valid yes/no value")


def _bool_to_yes_no(bool_):
    if bool_:
        return 'yes'
    else:
        return 'no'


class DefaultInstalledPkgStorage(util.ReadWriteForwardingDictMixin('_pkgs')):
    def __init__(self, installed_dir):
        self._directory = installed_dir
        self._modified_pkgs = set()
        self._pkgs = {}
        self._load_pkgs()
        
    def _load_pkgs(self):
        self._pkgs.clear()
        self._modified_pkgs.clear()
        for filename in (path for path in os.listdir(self._directory) if not path.startswith('.')):
            installed_pkg = self._create_pkg_from_file(os.path.join(self._directory, filename))
            self._pkgs[installed_pkg.name] = installed_pkg
    
    def _create_pkg_from_file(self, filename):
        parser = _SimpleFormatParser(filename)
        for section in ['name', 'desc', 'version']:
            if section not in parser:
                raise ParsingError("no section '%s' in file '%s'" % (section, filename))
        name = parser.get_as_string('name')
        if name != os.path.basename(filename):
            raise ParsingError("the file name and the value of the name section must be the same")
        version = parser.get_as_string('version')
        description = parser.get_as_string('desc')
        explicitly_installed = _yes_no_to_bool(parser.get_as_string('explicitly_installed', 'yes'))
        hidden = _yes_no_to_bool(parser.get_as_string('hidden', 'no'))
        depends = parser.get_as_list('depends', [])
        files = parser.get_as_list('files', [])
        return package.InstalledPackage(name, version, description, hidden, depends, explicitly_installed, files)
        
    def flush(self):
        for pkg_name in self._modified_pkgs:
            if pkg_name in self._pkgs:
                self._write_pkg_to_file(self._pkgs[pkg_name])
        self._modified_pkgs.clear()
    
    def _write_pkg_to_file(self, pkg):
        with open(os.path.join(self._directory, pkg.name), 'w') as f:
            f.write('[name]\n%s\n\n' % pkg.name)
            f.write('[desc]\n%s\n\n' % pkg.description)
            f.write('[version]\n%s\n\n' % pkg.version)
            f.write('[hidden]\n%s\n\n' % _bool_to_yes_no(pkg.hidden))
            f.write('[explicitly_installed]\n%s\n\n' % _bool_to_yes_no(pkg.explicitly_installed))
            if pkg.dependencies:
                f.write('[depends]\n')
                for dependency in pkg.dependencies:
                    f.write('%s\n' % dependency)
                f.write('\n')
            if pkg.installed_files:
                f.write('[files]\n')
                for installed_file in pkg.installed_files:
                    f.write('%s\n' % installed_file)
    
    def reload(self):
        self._load_pkgs()

    def required_by(self, pkg_name, exclude=()):
        """Return every installed package name that depends on pkg_name such that
           pkg_name is an installed_pkg. The returned list exclude all package in
           exclude.
        """
        # TODO wiser solution using a 'map of requirements'
        res = set()
        for cur_pkg_name, cur_pkg_val in self._pkgs.iteritems():
            if cur_pkg_name not in exclude and pkg_name in cur_pkg_val.dependencies:
                res.add(cur_pkg_name)
        return res
        
    def __setitem__(self, key, value):
        if key in self._pkgs:
            self._delete_pkg_file(key)
        self._pkgs[key] = value
        self._modified_pkgs.add(key)

    def __delitem__(self, key):
        del self._pkgs[key]
        self._delete_pkg_file(key)
            
    def _delete_pkg_file(self, pkg_name):
        filename = os.path.join(self._directory, pkg_name)
        try:
            os.remove(filename)
        except OSError:
            logger.exception("could not delete installed package file '%s'", filename)


class DefaultPackageStorage(object):
    def __init__(self, cache_dir, installable_dir, installed_dir, rfile_builder, install_mgr_builder, variables):
        self._installable_dict = DefaultInstallablePkgStorage(installable_dir, cache_dir, rfile_builder, install_mgr_builder, variables)
        self._installed_dict = DefaultInstalledPkgStorage(installed_dir)
    
    @classmethod
    def new_storage(cls, cache_dir, storage_dir, rfile_builder, install_mgr_builder, variables):
        # storage-dir/
        # +--installable/
        # |  +--all files in here are installable package definition files
        # +--installed/ (must be writable)
        #    +--all files in here are installed package definition files
        installable_dir = os.path.join(storage_dir, 'installable')
        installed_dir = os.path.join(storage_dir, 'installed')
        return cls(cache_dir, installable_dir, installed_dir, rfile_builder, install_mgr_builder, variables)
    
    # XXX name could be better, it's more than a simple dict
    @property
    def installable_dict(self):
        return self._installable_dict
    
    # XXX name could be better, it's more than a simple dict
    @property
    def installed_dict(self):
        return self._installed_dict
