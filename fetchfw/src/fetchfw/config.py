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
import re
from fetchfw import download, package, storage, util

logger = logging.getLogger(__name__)

DEF_CFG_FILENAME = '/etc/pf-xivo/fetchfw.conf'
DEF_CFG = {
   'cache_dir': '/var/cache/pf-xivo/fetchfw',
   'storage_dir': '/var/lib/pf-xivo/fetchfw',
   'auth_sections': [],
}


class ConfigError(util.FetchfwError):
    pass


def new_package_manager(config_filename=DEF_CFG_FILENAME):
    cfg_dict = dict(DEF_CFG)
    cfg_parser = ConfigParser.RawConfigParser()
    cfg_parser.optionxform=str
    with open(config_filename, 'r') as f:
        try:
            cfg_parser.readfp(f)
        except ConfigParser.ParsingError:
            logger.exception("error while parsing configuration file")
            raise ConfigError('error while parsing configuration file')
    def set_if(section, option, fun=lambda x: x):
        if cfg_parser.has_option(section, option):
            cfg_dict[option] = fun(cfg_parser.get(section, option))
    def ret_or_raise(section, option, fun=lambda x: x):
        if cfg_parser.has_option(section, option):
            return fun(cfg_parser.get(section, option))
        else:
            raise ConfigError("missing mandatory option '%s' in section '%s'"
                              % (option, section))
    if cfg_parser.has_section('general'):
        set_if('general', 'cache_dir')
        set_if('general', 'storage_dir')
        set_if('general', 'http_proxy_url')
        set_if('general', 'auth_sections', lambda x: x.split())
    downloaders = _create_downloaders(cfg_dict.get('http_proxy_url'))
    # add credentials to auth downloader
    for section in cfg_dict['auth_sections']:
        if not cfg_parser.has_section(section):
            raise ConfigError("auth_sections line makes reference to inexistant section '%s'"
                              % section)
        uri = ret_or_raise(section, 'uri')
        user = ret_or_raise(section, 'username')
        pwd = ret_or_raise(section, 'password')
        if cfg_parser.has_option(section, 'realm'):
            realm = cfg_parser.get(section, 'realm')
        else:
            realm = None
        downloaders['auth'].add_password(realm, uri, user, pwd)
    # read variables definition
    variables = {}
    if cfg_parser.has_section('variables'):
        for name, value in cfg_parser.items('variables'):
            if re.match(r'\W|^(?:FILE|ARG)\d+$', name):
                raise ConfigError("'%s' is not a valid variable name" % name)
            variables[name] = value
    rfile_builder = storage.RemoteFileBuilder(downloaders)
    installation_mgr_builder = storage.InstallationMgrBuilder()
    res_storage = storage.DefaultPackageStorage.new_storage(cfg_dict['cache_dir'],
                                                            cfg_dict['storage_dir'],
                                                            rfile_builder,
                                                            installation_mgr_builder,
                                                            variables)
    manager = package.PackageManager(res_storage)
    return manager


def _create_downloaders(http_proxy_url=None):
    handlers = download.new_handlers(http_proxy_url)
    return download.new_downloaders(handlers)
