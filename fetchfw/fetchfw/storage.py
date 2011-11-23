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

import collections
import ConfigParser
import logging
import json
import os
from binascii import a2b_hex
from fetchfw import download, install, util
from fetchfw.package import InstallablePackage, InstalledPackage

logger = logging.getLogger(__name__)


class StorageError(util.FetchfwError):
    pass


class ParsingError(StorageError):
    pass


class DefaultRemoteFileBuilder(object):
    """A remote file builder takes a config object (RawConfigParser) and a
    file section and builds a remote file (RemoteFile) from it.
    
    Here's an example section:
    
    [some_section_name]
    filename: foo.gz    ; optional
    url: http://example.org/foo.gz
    size: 29252
    sha1sum: 56c59081b1bd29c97f352b62c9667c409ca99f69
    downloader: default      ; optional
    
    """
    def __init__(self, cache_dir, downloaders):
        """Initialize a new remote file builder.
        
        cache_dir -- the directory where downloaded files are going to be
          saved
        downloaders -- a dictionary where keys are strings and values are
          downloaders (see fetchfw.download).
        
        When a remote file is built, if no downloader is specified in the
        section, the builder will look for the key 'default' in the
        downloaders dictionary.
        
        """
        self._cache_dir = cache_dir
        self._downloaders = downloaders

    def build_remote_file(self, config, section):
        url = config.get(section, 'url')
        size = config.getint(section, 'size')
        sha1sum = a2b_hex(config.get(section, 'sha1sum'))
        if config.has_option(section, 'filename'):
            filename = config.get(section, 'filename')
        else:
            filename = os.path.basename(url)
        path = os.path.join(self._cache_dir, filename)
        if config.has_option(section, 'downloader'):
            downloader_name = config.get(section, 'downloader')
        else:
            downloader_name = 'default'
        try:
            downloader = self._downloaders[downloader_name]
        except KeyError:
            raise ParsingError("'%s' is not a valid downloader name in file definition '%s'" %
                               (downloader_name, section))
        return download.RemoteFile.new_remote_file(path, size, url, downloader,
                                                   [download.SHA1Hook.create_factory(sha1sum)])


class DefaultFilterBuilder(object):
    """A filter builder takes a list of string tokens and returns a filter object.
    
    For example, if 'fb' is a DefaultFilterBuilder object, then:
      fb.build_node(['untar', 'test.tar'])
    will return a <TarFilter('test.tar')> object.
    
    """
    def _build_unzip(self, args):
        if len(args) != 1:
            raise ValueError("unzip takes 1 arguments: has %d" % len(args))
        return install.ZipFilter(args[0])

    def _build_untar(self, args):
        if len(args) != 1:
            raise ValueError("untar takes 1 arguments: has %d" % len(args))
        return install.TarFilter(args[0])

    def _build_unrar(self, args):
        if len(args) != 1:
            raise ValueError("unrar takes 1 arguments: has %d" % len(args))
        return install.RarFilter(args[0])

    def _build_7z(self, args):
        if len(args) != 1:
            raise ValueError("7z takes 1 arguments: has %d" % len(args))
        return install.Filter7z(args[0])

    def _build_unsign(self, args):
        if len(args) != 2:
            raise ValueError("unsign takes 1 arguments: has %d" % len(args))
        return install.CiscoUnsignFilter(args[0], args[1])

    def _build_exclude(self, args):
        if not args:
            raise ValueError("exclude takes at least 1 arguments")
        return install.ExcludeFilter(args)

    def _build_include(self, args):
        if not args:
            raise ValueError("include takes at least 1 arguments")
        return install.IncludeFilter(args)

    def _build_cp(self, args):
        if len(args) < 2:
            raise ValueError("cp takes at least 2 arguments: has %d" % len(args))
        return install.CopyFilter(args[:-1], args[-1])

    def _build_null(self, args):
        if args:
            raise ValueError("null takes no arguments: has %d" % len(args))
        return install.NullFilter()

    def build_node(self, tokens):
        """
        Raise a ValueError if arguments are not in the right number or invalid.
        
        Pre: len(tokens) >= 1
        
        """
        type, args = tokens[0], tokens[1:]
        method_name = '_build_' + type
        try:
            fun = getattr(self, method_name)
        except AttributeError:
            raise ValueError("unknown node type %s" % type)
        else:
            return fun(args)


class DefaultInstallMgrFactory(object):
    """
    
    Note that unless you really know what you're doing, you probably don't
    want to instantiate this class directly, but instead create instances
    of this class via a DefaultInstallMgrFactoryBuilder.
    
    Here's an example section (we suppose a DefaultFilterBuilder):
    
    [some_section_name]
    a-b: untar $FILE1
    b-c: exclude $ARG1
    c-d: cp */*.txt var/lib/foo/
    
    """
    def __init__(self, config, section, filter_builder, global_vars):
        # XXX it could be "better" if we could create an intermediate representation
        #     with the info we have so that creating a new install manager would
        #     be faster and we would already have checked the validity of the section
        self._config = config
        self._section = section
        self._filter_builder = filter_builder
        self._global_vars = global_vars

    def new_install_mgr(self, src_node, local_vars):
        vars = dict(self._global_vars)
        vars.update(local_vars)
        filters = {}
        graph = {'sources': {'a': src_node}, 'filters': filters}
        for name, value in self._config.items(self._section):
            src, dst = self._get_src_and_dst(name, self._section)
            if dst == 'a':
                raise ParsingError("usage of reserved dst 'a' in install definition '%s'" %
                                   self._section)
            if dst in filters:
                raise ParsingError("at least two filter with dst '%s' in install definition '%s'" %
                                   (dst, self._section))
            raw_tokens = self._tokenize(value, self._section)
            tokens = self._substitute(raw_tokens, vars)
            filter_obj = self._filter_builder.build_node(tokens)
            filters[dst] = (filter_obj, src)
        return install.InstallationManager(graph)

    def _get_src_and_dst(self, name, section):
        try:
            src, dst = name.split('-')
        except ValueError:
            raise ParsingError("'%s' is not a valid key in install definition '%s'" %
                               (name, section))
        else:
            return src, dst

    def _tokenize(self, value, section):
        tokens = value.split()
        if not tokens:
            raise ParsingError("'%s' is not a valid value in install definition '%s'" %
                               (value, section))
        return tokens

    def _substitute(self, raw_tokens, local_vars):
        vars = dict(self._global_vars)
        vars.update(local_vars)
        return [util.apply_subs(token, vars) for token in raw_tokens]


class DefaultInstallMgrFactoryBuilder(object):
    """A factory that creates DefaultInstallMgrFactory instances."""
    def __init__(self, filter_builder, global_vars):
        self._filter_builder = filter_builder
        self._global_vars = global_vars

    def build_install_mgr_factory(self, config, section):
        return DefaultInstallMgrFactory(config, section, self._filter_builder,
                                        self._global_vars)


class DefaultPkgBuilder(object):
    """A package builder takes a config object (RawConfigParser) and a
    pkg section and builds an installable package (InstallablePackage) from it.
    
    It also takes a package id, a dict of available remotes files and a dict
    of installation manager factories to build a package.
    
    Here's an example section:
    
    [some_section_name]
    description: Firmware for Digium HX8.
    version: 2.06
    files: digium-hx8fw
    install: digium-fw
    depends: base-digium        ; optional

    """
    def build_installable_pkg(self, config, section, pkg_id, remotes_files, install_mgr_factories):
        # remote files -- a map where keys are remote file ids and values are remote files
        # install_mgr_factories -- a map where keys are install manager ids and values are
        #   install manager factories
        pkg_info = {'id': pkg_id}
        raw_pkg_info = dict(config.items(section))

        if 'id' in raw_pkg_info:
            raise ParsingError("found invalid option 'id' in pkg def '%s'" % section)

        if 'depends' in raw_pkg_info:
            pkg_info['depends'] = raw_pkg_info.pop('depends').split()

        pkg_remote_files = []
        if 'files' in raw_pkg_info:
            for remote_file_id in raw_pkg_info.pop('files').split():
                try:
                    pkg_remote_files.append(remotes_files[remote_file_id])
                except KeyError:
                    raise ParsingError("unknown file '%s' in pkg def '%s'" %
                                       (remote_file_id, section))

        if 'install' in raw_pkg_info:
            tokens = raw_pkg_info.pop('install').split()
            install_mgr_id = tokens[0]
            install_mgr_args = tokens[1:]
            try:
                install_mgr_factory = install_mgr_factories[install_mgr_id]
            except KeyError:
                raise ParsingError("unknown install '%s' in pkg def '%s'" %
                                   (remote_file_id, section))
            else:
                src_node = install.NonGlobbingFilesystemLinkSource(f.path for f in pkg_remote_files)
                local_vars = {}
                for i, remote_file in enumerate(pkg_remote_files):
                    local_vars['FILE%d' % (i + 1)] = remote_file.filename
                for i, arg in enumerate(install_mgr_args):
                    local_vars['ARG%d' % (i + 1)] = arg
                pkg_install_mgr = install_mgr_factory.new_install_mgr(src_node, local_vars)
        else:
            pkg_install_mgr = None

        pkg_info.update(raw_pkg_info)

        return InstallablePackage(pkg_info, pkg_remote_files, pkg_install_mgr)


class BasePkgStorage(object):
    """Note to be instantiated directly but to serve as a base class for
    package storage classes.
    
    If you derive from this class, instances must haves a '_pkgs' attribute
    which is a dictionary where keys are package ids and values are package. 
    
    """
    def __getitem__(self, key):
        return self._pkgs[key]

    def __len__(self):
        return len(self._pkgs)

    def __iter__(self):
        return iter(self._pkgs)

    def __contains__(self, item):
        return item in self._pkgs

    def get(self, key, *args):
        return self._pkgs.get(key, *args)

    def items(self):
        return self._pkgs.items()

    def iterkeys(self):
        return self._pkgs.iterkeys()

    def itervalues(self):
        return self._pkgs.itervalues()

    def iteritems(self):
        return self._pkgs.iteritems()

    def keys(self):
        return self._pkgs.keys()

    def values(self):
        return self._pkgs.values()

    def get_dependencies(self, pkg_id, maxdepth=-1, filter_fun=None,
                         ignore_missing=False):
        """Return the set of direct and indirect dependencies of pkg_id.
        
        maxdepth -- -1 to get recursively all the dependencies, 0 to return an
          empty set or a positive number to get the dependencies up to this
          depth
        filter_fun -- a function taking a package id and returning true if the
          package is to be added as a dependencies (and its child, up to maxdepth)
        
        """
        return self.get_dependencies_many([pkg_id], maxdepth, filter_fun,
                                          ignore_missing)

    def get_dependencies_many(self, pkg_ids, maxdepth=-1, filter_fun=None,
                              ignore_missing=False):
        """Similar to get_depencies but accept a list of package IDs instead
        of only one package ID.
        
        """
        # return immediately if maxdepth is 0, this simplify the implementation
        if maxdepth == 0:
            return set()
        stack = [(pkg_id, maxdepth) for pkg_id in pkg_ids]
        dependencies = set()
        # dictionary of pkg_id -> maxdepth to prevent infinite loop
        visited = {}
        while stack:
            # note that depth is not a real depth value
            pkg_id, depth = stack.pop()
            try:
                pkg = self._pkgs[pkg_id]
            except KeyError:
                if not ignore_missing:
                    raise
            else:
                next_depth = depth - 1
                for dep_pkg_id in pkg.pkg_info['depends']:
                    if dep_pkg_id in visited:
                        visit_depth = visited[dep_pkg_id]
                        if visit_depth >= next_depth:
                            continue
                    visited[dep_pkg_id] = next_depth
                    if filter_fun is None or filter_fun(dep_pkg_id):
                        dependencies.add(dep_pkg_id)
                        if next_depth:
                            stack.append((dep_pkg_id, next_depth))
        return dependencies


class DefaultInstallablePkgStorage(BasePkgStorage):
    def __init__(self, db_dir, remote_file_builder, install_mgr_factory_builder, pkg_builder):
        self._db_dir = db_dir
        self._remote_file_builder = remote_file_builder
        self._install_mgr_factory_builder = install_mgr_factory_builder
        self._pkg_builder = pkg_builder
        self._load_pkgs()

    def _load_pkgs(self):
        config = self._read_db_files()
        pkg_sections, file_sections, install_sections = self._split_sections(config)
        remote_files = self._create_remote_files(config, file_sections)
        install_mgr_factories = self._create_install_mgr_factories(config, install_sections)
        self._pkgs = self._create_pkg(config, pkg_sections, remote_files, install_mgr_factories)

    def _read_db_files(self):
        # Read the files in the db dir and return a config parser object
        db_dir = self._db_dir
        config = ConfigParser.RawConfigParser()
        try:
            for rel_path in os.listdir(db_dir):
                if not rel_path.startswith('.'):
                    path = os.path.join(db_dir, rel_path)
                    with open(path) as fobj:
                        config.readfp(fobj)
        except IOError, e:
            raise StorageError("could not open/read file '%s': %s" % (path, e))
        except ConfigParser.ParsingError, e:
            raise StorageError("could not parse file '%s': %s" % (path, e))
        return config

    def _split_sections(self, config):
        pkg_sections = []
        file_sections = []
        install_sections = []
        for section in config.sections():
            if section.startswith('pkg_'):
                pkg_sections.append(section)
            elif section.startswith('file_'):
                file_sections.append(section)
            elif section.startswith('install_'):
                install_sections.append(section)
            else:
                raise ParsingError("invalid section '%s'" % section)
        return pkg_sections, file_sections, install_sections

    def _create_remote_files(self, config, sections):
        # Return a map where keys are remote file ids and values are remote files
        remote_files = {}
        remote_file_paths = set()
        for section in sections:
            assert section.startswith('file_')
            remote_file_id = section[5:]
            remote_file = self._remote_file_builder.build_remote_file(config, section)
            if remote_file.path in remote_file_paths:
                raise ParsingError('two remote files use the same path: %s' %
                                   remote_file.path)
            remote_file_paths.add(remote_file.path)
            remote_files[remote_file_id] = remote_file
        return remote_files

    def _create_install_mgr_factories(self, config, sections):
        install_mgr_factories = {}
        for section in sections:
            assert section.startswith('install_')
            install_mgr_factory_id = section[8:]
            install_mgr_factory = self._install_mgr_factory_builder.build_install_mgr_factory(config, section)
            install_mgr_factories[install_mgr_factory_id] = install_mgr_factory
        return install_mgr_factories

    def _create_pkg(self, config, sections, remote_files, install_mgr_factories):
        pkgs = {}
        for section in sections:
            assert section.startswith('pkg_')
            pkg_id = section[4:]
            pkg = self._pkg_builder.build_installable_pkg(config, section, pkg_id, remote_files, install_mgr_factories)
            pkgs[pkg_id] = pkg
        return pkgs

    def reload(self):
        self._load_pkgs()


class DefaultInstalledPkgStorage(BasePkgStorage):
    def __init__(self, db_dir, pretty_printing=False):
        self._db_dir = db_dir
        self._json_indent = 4 if pretty_printing else None
        self._load_pkgs()

    def _add_requirements(self, pkg, pkg_id):
        for dep_pkg_id in pkg.pkg_info['depends']:
            self._requirement_map[dep_pkg_id].add(pkg_id)

    def _remove_requirements(self, pkg, pkg_id):
        for dep_pkg_id in pkg.pkg_info['depends']:
            self._requirement_map[dep_pkg_id].discard(pkg_id)

    def _load_pkgs(self):
        pkgs = {}
        self._requirement_map = collections.defaultdict(set)
        for pkg_id in os.listdir(self._db_dir):
            if not pkg_id.startswith('.'):
                pkg = InstalledPackage(self._load_pkg_info(pkg_id))
                self._add_requirements(pkg, pkg_id)
                pkgs[pkg_id] = pkg
        self._pkgs = pkgs

    def _load_pkg_info(self, pkg_id):
        filename = os.path.join(self._db_dir, pkg_id)
        with open(filename, 'r') as fobj:
            # XXX json.load returns string as unicode strings but we are using
            #     plain string in the rest of the code. Using unicode would be
            #     great but config parser, used for the installable storage,
            #     doens't support unicode...
            pkg_info = json.load(fobj)
            return pkg_info

    def insert_pkg(self, installed_pkg):
        pkg_info = installed_pkg.pkg_info
        pkg_id = pkg_info['id']
        if pkg_id in self._pkgs:
            raise ValueError('package is already installed: %s' % pkg_id)
        self._write_pkg_info(pkg_id, pkg_info)
        self._add_requirements(installed_pkg, pkg_id)
        self._pkgs[pkg_id] = installed_pkg

    def update_pkg(self, installed_pkg):
        # Note that this is a replace operation
        pkg_info = installed_pkg.pkg_info
        pkg_id = pkg_info['id']
        if pkg_id not in self._pkgs:
            raise ValueError('package is not installed: %s' % pkg_id)
        self._remove_requirements(installed_pkg, pkg_id)
        self._write_pkg_info(pkg_id, pkg_info)
        self._add_requirements(installed_pkg, pkg_id)
        self._pkgs[pkg_id] = installed_pkg

    def upsert_pkg(self, installed_pkg):
        pkg_info = installed_pkg.pkg_info
        pkg_id = pkg_info['id']
        if pkg_id in self._pkgs:
            self._remove_requirements(installed_pkg, pkg_id)
        self._write_pkg_info(pkg_id, pkg_info)
        self._add_requirements(installed_pkg, pkg_id)
        self._pkgs[pkg_id] = installed_pkg

    def _write_pkg_info(self, pkg_id, pkg_info):
        if os.sep in pkg_id:
            raise ValueError('invalid pkg id: %s' % pkg_id)
        filename = os.path.join(self._db_dir, pkg_id)
        with open(filename, 'w') as fobj:
            json.dump(pkg_info, fobj, indent=self._json_indent)

    def delete_pkg(self, pkg_id):
        if pkg_id not in self._pkgs:
            raise ValueError('package is not installed: %s' % pkg_id)
        self._remove_requirements(self._pkgs[pkg_id], pkg_id)
        filename = os.path.join(self._db_dir, pkg_id)
        os.remove(filename)
        del self._pkgs[pkg_id]

    def reload(self):
        self._load_pkgs()

    def get_requisites(self, pkg_id):
        """Return the set of direct requisites of pkg_id, i.e. the set of
        package IDs which depends directly on pkg_id.
        
        """
        # we check first since we are using a defaultdict and don't want to
        # create a new instance if pkg_id is not there
        if pkg_id not in self._pkgs:
            raise ValueError('package is not installed: %s' % pkg_id)
        return set(self._requirement_map[pkg_id])


def new_installable_pkg_storage(db_dir, cache_dir, downloaders, global_vars):
    remote_file_builder = DefaultRemoteFileBuilder(cache_dir, downloaders)
    filter_builder = DefaultFilterBuilder()
    install_mgr_factory_builder = DefaultInstallMgrFactoryBuilder(filter_builder, global_vars)
    pkg_builder = DefaultPkgBuilder()
    return DefaultInstallablePkgStorage(db_dir, remote_file_builder, install_mgr_factory_builder, pkg_builder)


def new_installed_pkg_storage(db_dir):
    return DefaultInstalledPkgStorage(db_dir)


def new_pkg_storages(base_db_dir, cache_dir, downloaders, global_vars):
    # Return a tuple (installable_pkg_storage, installed_pkg_storage) using
    # base_db_dir as a common base directory for both package storage
    able_db_dir = os.path.join(base_db_dir, 'installable')
    ed_db_dir = os.path.join(base_db_dir, 'installed')
    for dir in [able_db_dir, ed_db_dir]:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    able_storage = new_installable_pkg_storage(able_db_dir, cache_dir, downloaders, global_vars)
    ed_storage = new_installed_pkg_storage(ed_db_dir)
    return able_storage, ed_storage
