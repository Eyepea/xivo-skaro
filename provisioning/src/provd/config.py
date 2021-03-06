# -*- coding: UTF-8 -*-

"""Provisioning server configuration module.

Read raw parameter values from different sources and return a dictionary
with well defined values.

The following parameters are defined (parameters that can be set in the
configuration file are documented in provd.conf):
    general.config_file
    general.base_raw_config_file
    general.base_raw_config
        The dictionary holding the base raw config.
    general.request_config_dir 
    general.cache_dir
    general.cache_plugin
    general.check_compat_min
    general.check_compat_max
    general.base_storage_dir
    general.plugin_server
    general.info_extractor
    general.retriever
    general.updater
    general.router
    general.external_ip
    general.http_port
    general.tftp_port
    general.rest_port
    general.rest_ip
    general.rest_username
    general.rest_password
    general.rest_authentication
    general.rest_ssl
    general.rest_ssl_certfile
    general.rest_ssl_keyfile
    general.verbose
    general.sync_service_type
    general.asterisk_ami_servers
    database.type
    database.generator
    database.ensure_common_indexes
    database.json_db_dir
    database.shelve_db_dir
    plugin_config.*.*
        where the first * is a plugin ID and the second * is a parameter
        name for the plugin with the given ID
    proxy.http
    proxy.ftp
    proxy.https
    proxy.*
        The proxy for * protocol requests.

"""

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

# XXX there's is some naming confusion between application configuration
#     and device configuration, since both used the word 'config' and
#     raw config yet it means different thing

import ConfigParser
import logging
import json
import os.path
import socket
from provd.util import norm_ip
from twisted.python import usage

logger = logging.getLogger(__name__)


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

    _DEFAULT_RAW_PARAMETERS = [
        # (parameter name, parameter value)
        ('general.config_file', '/etc/pf-xivo/provd/provd.conf'),
        ('general.base_raw_config_file', '/etc/pf-xivo/provd/base_raw_config.json'),
        ('general.request_config_dir', '/etc/pf-xivo/provd'),
        ('general.cache_dir', '/var/cache/pf-xivo-provd'),
        ('general.cache_plugin', 'True'),
        ('general.check_compat_min', 'True'),
        ('general.check_compat_max', 'True'),
        ('general.base_storage_dir', '/var/lib/pf-xivo-provd'),
        ('general.plugin_server', 'http://provd.xivo.fr/plugins/1/stable/'),
        ('general.info_extractor', 'default'),
        ('general.retriever', 'default'),
        ('general.updater', 'default'),
        ('general.router', 'default'),
        ('general.http_port', '8667'),
        ('general.tftp_port', '69'),
        ('general.rest_ip', '127.0.0.1'),
        ('general.rest_port', '8666'),
        ('general.rest_username', 'admin'),
        ('general.rest_password', 'admin'),
        ('general.rest_authentication', 'False'),
        ('general.rest_ssl', 'False'),
        ('general.rest_ssl_certfile', '/etc/pf-xivo/provd/keys/cert.pem'),
        ('general.rest_ssl_keyfile', '/etc/pf-xivo/provd/keys/key.pem'),
        ('general.verbose', 'False'),
        ('general.sync_service_type', 'none'),
        ('general.asterisk_ami_servers', '[("127.0.0.1", 5038, False, "provd", "provd")]'),
        ('database.type', 'json'),
        ('database.generator', 'default'),
        ('database.ensure_common_indexes', 'False'),
        ('database.json_db_dir', 'jsondb'),
        ('database.shelve_db_dir', 'shelvedb'),
    ]

    def pull(self):
        return dict(self._DEFAULT_RAW_PARAMETERS)


class Options(usage.Options):
    # The 'stderr' option should probably be defined somewhere else but
    # it's more practical to define it here. It SHOULD NOT be inserted
    # in the config though.
    optFlags = [
        ('stderr', 's', 'Log to standard error instead of syslog.'),
        ('verbose', 'v', 'Increase verbosity.'),
    ]

    optParameters = [
        ('config-file', 'f', None,
         'The configuration file'),
        ('config-dir', 'c', None,
         'The directory where request processing configuration file can be found'),
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

    _OPTION_TO_PARAM_LIST = [
        # (<option name, param name>)
        ('config-file', 'general.config_file'),
        ('config-dir', 'general.request_config_dir'),
        ('http-port', 'general.http_port'),
        ('tftp-port', 'general.tftp_port'),
        ('rest-port', 'general.rest_port'),
    ]

    def __init__(self, options):
        self.options = options

    def pull(self):
        raw_config = {}
        for option_name, param_name in self._OPTION_TO_PARAM_LIST:
            if self.options[option_name] is not None:
                raw_config[param_name] = self.options[option_name]
        if self.options['verbose']:
            raw_config['general.verbose'] = 'True'
        return raw_config


class ConfigFileConfigSource(object):
    """A source of raw parameter values coming from a configuration file.
    See the example file to see what is the syntax of the configuration file.
    
    """

    _BASE_SECTIONS = ['general', 'database', 'proxy']
    _PLUGIN_SECTION_PREFIX = 'pluginconfig_'

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
        # Pre: section.startswith(self._PLUGIN_SECTION_PREFIX)
        # Note: config is a [Raw]ConfigParser object
        raw_config = {}
        base_name = 'plugin_config.' + section[len(self._PLUGIN_SECTION_PREFIX):]
        for name, value in config.items(section):
            raw_config_name = base_name + '.' + name
            raw_config[raw_config_name] = value
        return raw_config

    def _get_pluginconfig(self, config):
        # Note: config is a [Raw]ConfigParser object
        raw_config = {}
        for section in config.sections():
            if section.startswith(self._PLUGIN_SECTION_PREFIX):
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
        for section in self._BASE_SECTIONS:
            raw_config.update(self._get_config_from_section(config, section))
        raw_config.update(self._get_pluginconfig(config))
        return raw_config

    def pull(self):
        try:
            return self._do_pull()
        except Exception, e:
            raise ConfigSourceError(e)


def _pull_config_from_sources(config_sources):
    raw_config = {}
    for config_source in config_sources:
        current_raw_config = config_source.pull()
        raw_config.update(current_raw_config)
    return raw_config


def _port_number(raw_value):
    port = int(raw_value)
    if not 1 <= port <= 65535:
        raise ValueError('invalid port number "%s"' % str)
    return port


def _ip_address(raw_value):
    return norm_ip(raw_value)


def _ip_address_or_star(raw_value):
    if raw_value == '*':
        return raw_value
    else:
        return _ip_address(raw_value)


_BOOL_TRUE = ['True', 'true', '1']
_BOOL_FALSE = ['False', 'false', '0']

def _bool(raw_value):
    if raw_value in _BOOL_TRUE:
        return True
    elif raw_value in _BOOL_FALSE:
        return False
    else:
        raise ValueError('invalid boolean raw value "%s"' % raw_value)


def _ast_ami_server(raw_value):
    try:
        value = eval(raw_value)
    except Exception, e:
        raise ValueError(e)
    else:
        if isinstance(value, list):
            for e in value:
                if isinstance(e, tuple) and len(e) == 5:
                    pass
                else:
                    break
            else:
                return value
        raise ValueError('invalid asterisk ami server: %s' % value)


def _load_json_file(raw_value):
    # Return a dictionary representing the JSON document contained in the
    # file pointed by raw value. The file must be encoded in UTF-8.
    fobj = open(raw_value)
    try:
        return json.load(fobj)
    finally:
        fobj.close()


def _process_aliases(raw_config):
    if 'general.ip' in raw_config and 'general.external_ip' not in raw_config:
        raw_config['general.external_ip'] = raw_config['general.ip']


_PARAMS_DEFINITION = [
    # list only the mandatory parameters or the parameters that need
    # transformation
    # (<param name>: (<transform/check function>, <is mandatory?>))
    ('general.base_raw_config_file', (str, True)),
    ('general.request_config_dir', (str, True)),
    ('general.cache_dir', (str, True)),
    ('general.cache_plugin', (_bool, True)),
    ('general.check_compat_min', (_bool, True)),
    ('general.check_compat_max', (_bool, True)),
    ('general.base_storage_dir', (str, True)),
    ('general.info_extractor', (str, True)),
    ('general.retriever', (str, True)),
    ('general.updater', (str, True)),
    ('general.router', (str, True)),
    ('general.external_ip', (_ip_address, False)),
    ('general.http_port', (_port_number, True)),
    ('general.tftp_port', (_port_number, True)),
    ('general.rest_ip', (_ip_address_or_star, True)),
    ('general.rest_port', (_port_number, True)),
    ('general.rest_username', (str, True)),
    ('general.rest_password', (str, True)),
    ('general.rest_authentication', (_bool, True)),
    ('general.rest_ssl', (_bool, True)),
    ('general.verbose', (_bool, True)),
    ('general.sync_service_type', (str, True)),
    ('general.asterisk_ami_servers', (_ast_ami_server, False)),
    ('database.type', (str, True)),
    ('database.generator', (str, True)),
    ('database.ensure_common_indexes', (_bool, True))
]

def _check_and_convert_parameters(raw_config):
    for param_name, (fun, mandatory) in _PARAMS_DEFINITION:
        # check if mandatory parameter is present
        if mandatory:
            if param_name not in raw_config:
                logger.warning('Mandatory parameter "%s" is missing', param_name)
                raise ConfigError('parameter "%s" is missing' % param_name)
        # convert parameter if present
        if param_name in raw_config:
            try:
                raw_config[param_name] = fun(raw_config[param_name])
            except Exception, e:
                raise ConfigError('parameter "%s" is invalid: %s' % (param_name, e))
    if raw_config['general.rest_ssl']:
        if 'general.rest_ssl_certfile' not in raw_config:
            raise ConfigError('Missing parameter "rest_ssl_certfile"')
        if 'general.rest_ssl_keyfile' not in raw_config:
            raise ConfigError('Missing parameter "rest_ssl_keyfile"')
    # load base_raw_config_file JSON document
    # XXX maybe we should put this in a separate method since it's more or less
    #     a check and not really a convert...
    raw_config['general.base_raw_config'] = _load_json_file(raw_config['general.base_raw_config_file'])


_BASE_RAW_CONFIG_UPDATE_LIST = [
    # (<dev raw config param name, app raw config param name>
    (u'http_port', 'general.http_port'),
    (u'tftp_port', 'general.tftp_port'),
]

def _get_ip_fallback():
    # This function might return an IP address of a loopback interface, but we
    # don't care since it's not possible to determine implicitly which IP address
    # we should use anyway.
    return socket.gethostbyname(socket.gethostname())


def _update_general_base_raw_config(app_raw_config):
    # warning: raw_config in the function name means device raw config and
    # the app_raw_config argument means application configuration.
    base_raw_config = app_raw_config['general.base_raw_config']
    for key, source_param_name in _BASE_RAW_CONFIG_UPDATE_LIST:
        if key not in base_raw_config:
            # currently, we only refer to always specified config parameters,
            # so next line will never raise a KeyError
            base_raw_config[key] = app_raw_config[source_param_name]
    if u'ip' not in base_raw_config:
        if 'general.external_ip' in app_raw_config:
            external_ip = app_raw_config['general.external_ip']
        else:
            external_ip = _get_ip_fallback()
            logger.warning('Using "%s" for base raw config ip parameter', external_ip)
        base_raw_config[u'ip'] = external_ip


def _post_update_raw_config(raw_config):
    # Update raw config after transformation/check
    _update_general_base_raw_config(raw_config)
    # update json_db_dir to absolute dir
    if 'database.json_db_dir' in raw_config:
        raw_config['database.json_db_dir'] = os.path.join(raw_config['general.base_storage_dir'],
                                                          raw_config['database.json_db_dir'])
    # update json_db_dir to absolute dir
    if 'database.shelve_db_dir' in raw_config:
        raw_config['database.shelve_db_dir'] = os.path.join(raw_config['general.base_storage_dir'],
                                                            raw_config['database.shelve_db_dir'])


def get_config(config_sources):
    """Pull the raw parameters values from the configuration sources and
    return a config dictionary.
    
    config_source is a sequence/iterable of objects with a pull method taking
    no arguments and returning a dictionary of raw parameter values.
    
    """
    raw_config = _pull_config_from_sources(config_sources)
    _process_aliases(raw_config)
    _check_and_convert_parameters(raw_config)
    _post_update_raw_config(raw_config)
    return raw_config
