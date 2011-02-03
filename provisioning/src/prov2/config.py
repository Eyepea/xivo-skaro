# -*- coding: UTF-8 -*-

"""Provisioning server configuration module.

Read raw parameter values from different sources and return a dictionary
with well defined values.

The following parameters are defined:
    general.config_file
    general.http_proxy
        HTTP proxy for plugin downloads, etc
    general.plugin_server
        URL of the plugin server (where plugins are downloaded)
    general.config_dir 
        Directory where request processing configuration files can be found
        # XXX should rename to something else
    general.cache_dir
    general.plugins_dir
    general.info_extractor
    general.retriever
    general.updater
    general.router
    general.ip
        The IP address to listen on, or '*' to listen on every address.
    general.http_port
    general.tftp_port
    general.rest_port
    common_config.ip
        The IP address the phone use to contact the provisioning server.
        Normally the same as general.ip when general.ip is not *.
    common_config.http_port
        The HTTP port the phone use to contact the provisioning server.
        Normally the same as general.http_port.
    common_config.tftp_port
        The TFTP port the phone use to contact the provisioning server.
        Normally the same as general.tftp_port.
    common_config.*
    database.type
        The type of the 'database' used for storing devices and configs.
    database.generator
        The kind of generator used to generate ID for devices and configs.
    database.shelve_dir
        For 'shelve' database, the directory where files are stored.
    database.mongo_uri
        For 'mongo' database, the URI of the database.
    plugin_config.*.*

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
from prov2.util import norm_ip
from twisted.python import usage

# XXX right now, bad parameter names will be silently ignored, and we might
#     want to raise an exception when we see a parameter that is invalid
# XXX better documentation...


class ConfigError(Exception):
    """Raise when an error occur while getting configuration."""
    pass


class ConfigSourceError(ConfigError):
    """Raise when an error occur while pulling raw parameter values from
    a config source.
    
    """
    pass


class DefaultConfigSource(object):
    """A source of raw parameter values that always return the same default
    values.
    
    """
    
    _DEFAULT_RAW_CONFIG = {
        'general.config_file': '/etc/pf-xivo/prov/prov.conf',
        'general.config_dir': '/etc/pf-xivo/prov',
        'general.cache_dir': '/var/cache/pf-xivo/prov',
        'general.plugins_dir': '/var/lib/pf-xivo/prov/plugins',
        'general.info_extractor': 'default',
        'general.retriever': 'default',
        'general.updater': 'default',
        'general.router': 'default',
        'general.ip': '*',
        'general.http_port': '80',
        'general.tftp_port': '69',
        'general.rest_port': '8081',
        'database.type': 'shelve',
        'database.generator': 'default',
        'database.shelve_dir': '/var/lib/pf-xivo/prov/shelvedb',
    }
    
    def pull(self):
        return dict(self._DEFAULT_RAW_CONFIG)


class Options(usage.Options):
    optParameters = [
        ('config-file', 'f', None,
         'The configuration file'),
        ('config-dir', 'c', None,
         'The directory where request processing configuration file can be found'),
        ('ip', None, None,
         'The IP address to listen on, or * to listen on every.'),
        ('http-port', None, None,
         'The HTTP port to listen on.'),
        ('tftp-port', None, None,
         'The TFTP port to listen on.'),
        ('rest-port', None, None,
         'The port to listen on.'),
    ]


class CommandLineConfigSource(object):
    """A source of raw parameter values coming from the an instance of the
    Options class defined above.
    
    """
    
    _PARAMS_MAP = {
        'config-file': 'general.config_file',
        'config-dir': 'general.config_dir',
        'ip': 'general.ip',
        'http-port': 'general.http_port',
        'tftp-port': 'general.tftp_port',
        'rest-port': 'general.rest_port',
    }
    
    def __init__(self, options):
        self.options = options
    
    def pull(self):
        raw_config = {}
        for option_name, param_name in self._PARAMS_MAP.iteritems():
            if self.options[option_name] is not None:
                raw_config[param_name] = self.options[option_name]
        return raw_config


class ConfigFileConfigSource(object):
    """A source of raw parameter values coming from a configuration file.
    See the example file to see what is the syntax of the configuration file.
    
    """
    
    _PLUGIN_CONFIG_PREFIX = 'pluginconfig_'
    
    def __init__(self, filename):
        self.filename = filename
    
    def _get_config_from_section(self, config, section):
        # Note: config is a [Raw]ConfigParser object
        raw_config = {}
        if config.has_section(section):
            for name, value in config.items(section):
                raw_config_name = section + '.' + name 
                raw_config[raw_config_name] = value
        return raw_config
    
    def _get_pluginconfig_from_section(self, config, section):
        # Pre: config.has_section(section)
        # Pre: section.startswith(self._PLUGIN_CONFIG_PREFIX)
        # Note: config is a [Raw]ConfigParser object
        raw_config = {}
        base_name = 'plugin_config.' + section[len(self._PLUGIN_CONFIG_PREFIX):]
        for name, value in config.items(section):
            raw_config_name = base_name + '.' + name
            raw_config[raw_config_name] = value
        return raw_config
    
    def _get_pluginconfig(self, config):
        # Note: config is a [Raw]ConfigParser object
        raw_config = {}
        for section in config.sections():
            if section.startswith(self._PLUGIN_CONFIG_PREFIX):
                raw_config.update(self._get_pluginconfig_from_section(config, section))
        return raw_config
    
    def _do_pull(self):
        config = ConfigParser.RawConfigParser()
        fobj = open(self.filename)
        try:
            config.readfp(fobj)
        finally:
            fobj.close()
        
        raw_config = {}
        raw_config.update(self._get_config_from_section(config, 'general'))
        raw_config.update(self._get_config_from_section(config, 'common_config'))
        raw_config.update(self._get_pluginconfig(config))
        return raw_config
    
    def pull(self):
        try:
            return self._do_pull()
        except Exception, e:
            raise ConfigSourceError(e)


def _port_number(raw_value):
    # Return a port number as an integer or raise a ValueError
    port = int(raw_value)
    if not 1 <= port <= 65535:
        raise ValueError('invalid port number "%s"' % str)
    return port


def _ip_address(raw_value):
    # Return an IP address as a string or raise a ValueError
    return norm_ip(raw_value)


def _ip_address_or_star(raw_value):
    if raw_value == '*':
        return raw_value
    else:
        return _ip_address(raw_value)


_PARAMS_DEFINITION = {
    # <config_name>: (<transform/check fonction>, <mandatory>)
    'general.config_file':      (str, False),
    'general.http_proxy':       (str, False),
    'general.plugin_server':    (str, False),
    'general.cache_dir':        (str, True),
    'general.plugins_dir':      (str, True),
    'general.config_dir':       (str, True),
    'general.info_extractor':   (str, True),
    'general.retriever':        (str, True),
    'general.updater':          (str, True),
    'general.router':           (str, True),
    'general.ip':               (_ip_address_or_star, True),
    'general.http_port':        (_port_number, True),
    'general.tftp_port':        (_port_number, True),
    'general.rest_port':        (_port_number, True),
    'common_config.ip':         (_ip_address, True),
    'common_config.http_port':  (_port_number, True),
    'common_config.tftp_port':  (_port_number, True),
    'database.type':            (str, True),
    'database.generator':       (str, True),
}


def _pull_config_from_sources(config_sources):
    raw_config = {}
    for config_source in config_sources:
        current_raw_config = config_source.pull()
        raw_config.update(current_raw_config)
    return raw_config


def _update_raw_config(raw_config):
    def _copy_if(src, dst):
        if src in raw_config and dst not in raw_config:
            raw_config[dst] = raw_config[src]
    for suffix in ('ip', 'http_port', 'tftp_port'):
        _copy_if('general.' + suffix, 'common_config.' + suffix)


def _check_and_convert_parameters(raw_config):
    config = {}
    for param_name, (fun, mandatory) in _PARAMS_DEFINITION.iteritems():
        # check if mandatory parameter is present
        if mandatory:
            if param_name not in raw_config:
                raise ConfigError('parameter "%s" is missing' % param_name)
        # convert parameter if present
        if param_name in raw_config:
            try:
                config[param_name] = fun(raw_config[param_name])
            except ValueError, e:
                raise ConfigError('parameter "%s" is invalid: %s' %
                                  param_name, e)
    return config


def get_config(config_sources):
    """Pull the raw parameters values from the configuration sources and
    return a config dictionary.
    
    config_source is a sequence/iterable of objects with a pull method taking
    no arguments and returning a dictionary of raw parameter values.
    
    """ 
    raw_config = _pull_config_from_sources(config_sources)
    _update_raw_config(raw_config)
    config = _check_and_convert_parameters(raw_config)
    return config
