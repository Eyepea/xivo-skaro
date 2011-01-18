# -*- coding: UTF-8 -*-

from __future__ import with_statement

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
import logging.handlers
import os.path
import prov2.config
import prov2.devices.ident
import prov2.devices.pgasso
from prov2.servers.tftp.proto import TFTPProtocol
from prov2.servers.http_site import Site
from prov2.devices.config import ConfigManager
from prov2.devices.device import DeviceManager
from prov2.devices.util import NumericIdGenerator
from prov2.plugins import PluginManager
from prov2.rest.server import new_root_resource
from twisted.application.service import IServiceMaker, Service, MultiService
from twisted.application import internet
from twisted.plugin import IPlugin
from twisted.python import log
from twisted.web.resource import Resource
from zope.interface.declarations import implements

logger = logging.getLogger('main')


class InvalidIdError(Exception):
    """Raised when a passed ID is invalid, not necessary because of its type,
    but because of its semantic.
    
    """
    pass


class UsedIdError(InvalidIdError):
    """Raised if we try setting/adding a new device with an ID already in
    used.
    
    """
    pass


class UnusedIdError(InvalidIdError):
    pass


class Application(object):
    """
    Device objects in the device manager used by an application instance
    have the following restrictions:
    
    - 'config' is either absent, or dev['config'] in self.cfg_mgr
    - 'plugin' is either absent, or dev['plugin'] in self.pg_mgr
    
    Config objects (tuple) in the config manager used by an application
    instance have the following restrictions:
    
    - every base config of a config must be in self.cfg_mgr
    - len(bases) == len(set(bases))
    
    """
    
    def _split_config(self, config):
        splitted_config = {}
        for k, v in config.iteritems():
            current_dict = splitted_config
            key_tokens = k.split('.')
            for key_token in key_tokens[:-1]:
                current_dict = current_dict.setdefault(key_token, {})
            current_dict[key_tokens[-1]] = v
        return splitted_config
    
    def __init__(self, config):
        logger.info('Creating application...')
        self.cfg_mgr = ConfigManager()
        self.dev_mgr = DeviceManager()
        self.pg_mgr = PluginManager(self,
                                    config['general.plugins_dir'],
                                    config['general.cache_dir'])
        if 'general.plugin_server' in config:
            self.pg_mgr.server = config['general.plugin_server']
        self._dev_id_gen = NumericIdGenerator()
        self._cfg_id_gen = NumericIdGenerator()
        self._splitted_config = self._split_config(config)
        
        self._load_all_pg()
        
    def close(self):
        logger.info('Closing application...')
        self.pg_mgr.close()
    
    # Device operations
        
    def _check_valid_dev(self, dev):
        if 'config' in dev:
            if dev['config'] not in self.cfg_mgr:
                raise ValueError('device has invalid config value')
        if 'plugin' in dev:
            if dev['plugin'] in self.cfg_mgr:
                raise ValueError('device has invalid plugin value')
    
    def _get_plugin(self, dev):
        """Return the plugin of dev, or None."""
        if 'plugin' in dev:
            pg_id = dev['plugin']
            if pg_id in self.pg_mgr:
                return self.pg_mgr[pg_id]
        return None
    
    def _get_config(self, dev):
        """Return the flattened config of dev augmented with parameters from
        the common config, or None.
        
        """
        if 'config' in dev:
            cfg_id = dev['config']
            if cfg_id in self.cfg_mgr:
                config = self.cfg_mgr.flatten(cfg_id)
                # Non overwriting update of the config with the common config
                for k, v in self._splitted_config['common_config'].iteritems():
                    if k not in config:
                        config[k] = v
                return config
        return None
    
    def _get_plugin_and_config(self, dev):
        """Return either a tuple (plugin object, config object) or either
        a tuple (None, None) if one of the two object is not available.
        
        """
        plugin = self._get_plugin(dev)
        if plugin is not None:
            config = self._get_config(dev)
            if config is not None:
                return plugin, config
        return None, None
    
    def _configure_dev(self, dev):
        """Call plugin.configure(dev, config) if possible.
        
        Its possible if dev has a config ID and a plugin ID which refer to
        valid config and plugin respectively. 
        
        """
        plugin, config = self._get_plugin_and_config(dev)
        if plugin is not None:
            logger.info('Calling plugin.configure for plugin "%s"', plugin.name)
            plugin.configure(dev, config)
    
    def _deconfigure_dev(self, dev):
        """Call plugin.deconfigure(dev) if possible.
        
        Its possible if dev has a plugin ID which refer to a valid plugin.
        
        """
        plugin = self._get_plugin(dev)
        if plugin is not None:
            logger.info('Calling plugin.deconfigure for plugin "%s"', plugin.name)
            plugin.deconfigure(dev)
    
    def _synchronize_dev(self, dev):
        """Call plugin.synchronize(dev, config) if possible."""
        plugin, config = self._get_plugin_and_config(dev)
        if plugin is not None:
            logger.info('Calling plugin.synchronize for plugin "%s"', plugin.name)
            return plugin.synchronize(dev, config)
    
    def create_dev(self, dev, dev_id=None):
        """Add a new device to the device manager and return the device ID.
        
        dev_id -- a device ID or None
        
        Pre:  -dev_id not in self.dev_mgr
        Post: -dev has been added to the device manager
              -if dev.get('plugin') in self.pg_mgr \
                 and dev.get('config') in self.cfg_mgr ->
                 self.pg_mgr[dev['plugin']].configure(dev, cfg_mgr[dev['config']])
        """
        logger.info('Creating device')
        self._check_valid_dev(dev)
        if dev_id is None:
            dev_id = self._dev_id_gen.next_id(self.dev_mgr)
            assert dev_id not in self.dev_mgr
        elif dev_id in self.dev_mgr:
            raise UsedIdError(dev_id)
        self.dev_mgr[dev_id] = dev
        logger.info('Created device "%s"', dev_id)
        self._configure_dev(dev)
        return dev_id
    
    def retrieve_dev(self, dev_id):
        """Equivalent to 'self.dev_mgr[dev_id]'. This is only done so that
        we have the 4 CRUD operation available (i.e. only for symmetry).
        
        """
        try:
            return self.dev_mgr[dev_id]
        except KeyError:
            raise UnusedIdError(dev_id)
    
    def update_dev(self, dev_id, new_dev):
        """Update the device with dev_id to new_dev. This is a 'replace'
        operation. If you want only to update some of it's element, you need
        to first retrieve the device, create a new one from it and update the
        new device, then call this method.
        
        Pre:  - dev_id in self.dev_mgr
        Post: - deconfigure and configure might have been called... you should
                look at the source code...
        
        """
        logger.info('Updating device "%s"', dev_id)
        self._check_valid_dev(new_dev)
        try:
            old_dev = self.dev_mgr[dev_id]
        except KeyError:
            raise UnusedIdError(dev_id)
        else:
            self.dev_mgr[dev_id] = new_dev
            
            old_cfg_id = old_dev.get('config')
            new_cfg_id = new_dev.get('config')
            old_pg_id = old_dev.get('plugin')
            new_pg_id = new_dev.get('plugin')
            cfg_diff = old_cfg_id != new_cfg_id
            pg_diff = old_pg_id != new_pg_id
            if pg_diff:
                # next lines use the fact that these call might be no-op
                self._deconfigure_dev(old_dev)
                self._configure_dev(new_dev)
            elif cfg_diff:
                assert not pg_diff
                self._configure_dev(new_dev)
    
    def delete_dev(self, dev_id):
        """Remove a device from a device manager.
        
        Pre:  - dev_id in self.dev_mgr
        Post: - deconfigure has been called if the device has been configured
        
        """
        logger.info('Deleting device "%s"', dev_id)
        try:
            dev = self.dev_mgr[dev_id]
        except KeyError:
            raise UnusedIdError(dev_id)
        else:
            self._deconfigure_dev(dev)
            
    def synchronize_dev(self, dev_id):
        """Force the device to synchronize it's configuration."""
        logger.info('Synchronizing device "%s"', dev_id)
        try:
            dev = self.dev_mgr[dev_id]
        except KeyError:
            raise UnusedIdError(dev_id)
        else:
            # XXX what do we do with the callback...
            return self._synchronize_dev(dev)
    
    # Config operations
    
    def _check_valid_cfg(self, cfg):
        bases = cfg[1]
        for i, base in enumerate(bases):
            if base not in self.cfg_mgr or base in bases[:i]:
                raise ValueError('config has invalid bases value')
    
    def _configure_dev_from_cfgs(self, cfg_ids):
        """Update every devices for which dev.get('config') in cfg_ids.""" 
        for dev in self.dev_mgr.itervalues():
            if dev.get('config') in cfg_ids:
                self._configure_dev(dev)
    
    def create_cfg(self, cfg, cfg_id=None):
        """Add a new config to the config manager and return the config ID.
        
        """
        logger.info('Creating config')
        self._check_valid_cfg(cfg)
        if cfg_id is None:
            cfg_id = self._cfg_id_gen.next_id(self.cfg_mgr)
            assert cfg_id not in self.cfg_mgr
        elif cfg_id in self.cfg_mgr:
            raise UsedIdError(cfg_id)
        self.cfg_mgr[cfg_id] = cfg
        logger.info('Created config "%s"', cfg_id)
        return cfg_id
    
    def retrieve_cfg(self, cfg_id):
        try:
            return self.cfg_mgr[cfg_id]
        except KeyError:
            raise UnusedIdError(cfg_id)
    
    def update_cfg(self, cfg_id, new_cfg):
        """Update the config with cfg_id to new_cfg.
        
        Every device that depends directly or indirectly on this config will
        be passed as an argument to the configure method of their plugin. 
        
        """
        logger.info('Updating config "%s"', cfg_id)
        self._check_valid_cfg(new_cfg)
        if cfg_id not in self.cfg_mgr:
            raise UnusedIdError(cfg_id)
        self.cfg_mgr[cfg_id] = new_cfg
        
        # Note that it's possible for a config in the required_by set
        # not to have been 'modified' by the fact that a config has
        # been updated. Most common case is if the config override every
        # parameters that the config cfg_id had/has. 
        required_by = self.cfg_mgr.required_by(cfg_id)
        self._configure_dev_from_cfgs(required_by)
    
    def delete_cfg(self, cfg_id, force=False):
        logger.info('Deleting config "%s"', cfg_id)
        if cfg_id not in self.cfg_mgr:
            raise UnusedIdError(cfg_id)
        if self.cfg_mgr.is_required(cfg_id):
            if not force:
                raise ValueError('config is required by other configs')
            else:
                required_by = self.cfg_mgr.required_by(cfg_id)
                self.cfg_mgr.remove(cfg_id)
#                for cfg_id in required_by:
#                    cfg = self.cfg_mgr[cfg_id]
#                    bases = cfg[1]
#                    if cfg_id in bases:
#                        bases.remove(cfg_id)
                self._configure_dev_from_cfgs(required_by)
        else:
            del self.cfg_mgr[cfg_id]
    
    # Plugin operations
    
    def _load_all_pg(self):
        logger.info('Loading all plugins')
        for pg_info in self.pg_mgr.list_installed():
            pg_id = pg_info['name']
            self._load_pg(pg_id)
        
    def _load_pg(self, pg_id):
        gen_cfg = self._splitted_config['general']
        spec_cfg = self._splitted_config.get('plugin_config', {}).get(pg_id, {})
        logger.info('Loading plugin "%s', pg_id)
        self.pg_mgr.load(pg_id, gen_cfg, spec_cfg)
        self._common_configure(pg_id)
    
    def _common_configure(self, pg_id):
        # Pre: pg_id in self.pg_mgr
        pg = self.pg_mgr[pg_id]
        logger.info('Calling plugin.configure_common for plugin "%s"', pg_id)
        pg.configure_common(self._splitted_config['common_config'])
    
    def _configure_dev_from_plugin(self, pg_id):
        """Call plugin(dev, config) for every devices for which
        dev.get('plugin') is pg_id.
        
        """
        for dev in self.dev_mgr.itervalues():
            if dev.get('plugin') == pg_id:
                self._configure_dev(dev)
    
    def install_pg(self, pg_id):
        """Install the plugin with pg_id.
        
        Return an object providing the IProgressOperation interface.
        
        Raise an Exception if the plugin is already installed.
        
        Raise an Exception if there's no installable plugin with the specified
        name.
        
        Raise an Exception if there's already an install/upgrade operation
        in progress for the plugin.
        
        Raise an InvalidParameterError if the plugin package is not in cache
        and no 'server' param has been set.
        
        """
        logger.info('Installing plugin "%s"', pg_id)
        if self.pg_mgr.is_installed(pg_id):
            raise Exception("plugin '%s' is already installed" % pg_id)
        
        pop = self.pg_mgr.install(pg_id)
        def on_success(_):
            self._load_pg(pg_id)
        pop.deferred.addCallback(on_success)
        return pop

    def upgrade_pg(self, pg_id):
        """Upgrade the plugin with pg_id.
        
        Same contract as install_pg, except that the plugin must already be
        installed. 
        
        """
        logger.info('Upgrading plugin "%s"', pg_id)
        if not self.pg_mgr.is_installed(pg_id):
            raise Exception("plugin '%s' is not already installed" % pg_id)
        
        # XXX we probably want to check that the plugin is 'really' upgradeable
        pop = self.pg_mgr.upgrade(pg_id)
        def on_success(_):
            if pg_id in self.pg_mgr:
                self.pg_mgr.unload(pg_id)
            self._load_pg(pg_id)
            self._configure_dev_from_plugin(pg_id)
        pop.deferred.addCallback(on_success)
        return pop
    
    def _is_plugin_unused(self, pg_id):
        for dev in self.dev_mgr.itervalues():
            if dev.get('plugin') == pg_id:
                return False
        return True
    
    def uninstall_pg(self, pg_id):
        """Uninstall the plugin with pg_id.

        Contraty to install and upgrade, this is a synchronous operation. It
        returns nothing.
        
        Raise an Exception if the plugin is not already installed.
        
        Raise an Exception if at least one device depends on this plugin.
        
        """
        logger.info('Uninstallating plugin "%s"', pg_id)
        if not self.pg_mgr.is_installed(pg_id):
            raise Exception("plugin '%s' is not already installed" % pg_id)
        if not self._is_plugin_unused(pg_id):
            raise Exception("plugin '%s' is used by at least a device" % pg_id)
        
        self.pg_mgr.uninstall(pg_id)
        self.pg_mgr.unload(pg_id)


# configure logging...
def _configure_root_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(filename)s:%(lineno)d - %(name)s: %(message)s"))
    root_logger.addHandler(handler)


_configure_root_logger()
observer = log.PythonLoggingObserver()
observer.start()


# Create some config -- testing purpose only
# a 'base' configuration
xivo_ip = '192.168.33.4'
base_cfg = {
    'locale': 'fr_CA',
    'timezone': 'America/Montreal',
    'subscribe_mwi': False,
    'ntp_server': xivo_ip,
    'vlan': {
        'enabled': False,
    },
    'sip': {
        'lines': {
            1: {
                'proxy_ip': xivo_ip,
                'registrar_ip': xivo_ip,
            },
        }
    },
    'exten': {
        'voicemail': '*98',
        'pickup_prefix': '*8',
        'fwdunc': '*21',
        'dnd': '*25'
    },
    'funckey': {},
}

# a 'guest' configuration
guest_cfg = {
    'sip': {
        'lines': {
            1: {
                'display_name': 'guest',
                'user_id': 'guest',
                'auth_id': 'guest',
                'passwd': 'guest',
            }
        }
    }
}

# a configuration for a device
dev1_cfg = {
    'sip': {
        'lines': {
            1: {
                'display_name': 'ProV2',
                'user_id': '3900',
                'auth_id': '3900',
                'passwd': '3900',
            },
            2: {
                'proxy_ip': xivo_ip,
                'registrar_ip': xivo_ip,
                'display_name': 'V2pro',
                'user_id': '3901',
                'auth_id': '3901',
                'passwd': '3901',
            }
        }
    }
}


class ProvisioningService(Service):
    def __init__(self, config):
        self._config = config
        
    def startService(self):
        Service.startService(self)
        self.app = Application(self._config)
        
        # XXX next lines are for testing purpose only
        cfg_mgr = self.app.cfg_mgr
        cfg_mgr['base'] = (base_cfg, [])
        cfg_mgr['guest'] = (guest_cfg, ['base'])
        cfg_mgr['dev1'] = (dev1_cfg, ['base'])
    
    def stopService(self):
        Service.stopService(self)
        self.app.close()


class ProcessService(Service):
    def __init__(self, prov_service, dhcp_infos, config):
        self._prov_service = prov_service
        self._dhcp_infos = dhcp_infos
        self._config = config
    
    def _get_conffile_globals(self):
        # Pre: hasattr(self._prov_service, 'app')
        conffile_globals = {}
        conffile_globals.update(prov2.devices.ident.__dict__)
        conffile_globals.update(prov2.devices.pgasso.__dict__)
        conffile_globals['app'] = self._prov_service.app
        conffile_globals['dhcp_infos'] = self._dhcp_infos
        return conffile_globals
    
    def _create_processor(self, config_dir, name, config_name):
        # name is the name of the processor, for example 'info_extractor'
        filename = os.path.join(config_dir, name + '.py.conf.' + config_name)
        conffile_globals = self._get_conffile_globals()
        try:
            execfile(filename, conffile_globals)
        except Exception, e:
            logger.error('error while executing process config file "%s": %s', filename, e)
            raise
        if name not in conffile_globals:
            raise Exception('process config file "%s" doesn\'t define a "%s" name',
                            filename, name)
        return conffile_globals[name]
    
    def startService(self):
        # Pre: hasattr(self._prov_service, 'app')
        Service.startService(self)
        self.request_processing = prov2.devices.ident.RequestProcessingService(self._prov_service.app)
        config_dir = self._config['general.config_dir']
        for name in ('info_extractor', 'retriever', 'updater', 'router'):
            setattr(self.request_processing, 'dev_' + name,
                    self._create_processor(config_dir, name, self._config['general.' + name]))


class HTTPProcessService(Service):
    def __init__(self, prov_service, process_service, config):
        self._prov_service = prov_service
        self._process_service = process_service
        self._config = config
    
    def startService(self):
        Service.startService(self)
        
        app = self._prov_service.app
        process_service = self._process_service.request_processing
        http_process_service = prov2.devices.ident.HTTPRequestProcessingService(process_service,
                                                                                app.pg_mgr) 
        site = Site(http_process_service)
        port = self._config['general.http_port']
        interface = self._config['general.ip']
        if interface == '*':
            interface = ''
        self._tcp_server = internet.TCPServer(port, site, interface=interface)
        self._tcp_server.startService()

    def stopService(self):
        Service.stopService(self)
        return self._tcp_server.stopService()


class TFTPProcessService(Service):
    def __init__(self, prov_service, process_service, config):
        self._prov_service = prov_service
        self._process_service = process_service
        self._config = config
    
    def startService(self):
        Service.startService(self)
        
        app = self._prov_service.app
        process_service = self._process_service.request_processing
        tftp_process_service = prov2.devices.ident.TFTPRequestProcessingService(process_service,
                                                                                app.pg_mgr)
        tftp_protocol = TFTPProtocol(tftp_process_service)
        port = self._config['general.tftp_port']
        interface = self._config['general.ip']
        if interface == '*':
            interface = ''
        self._udp_server = internet.UDPServer(port, tftp_protocol, interface=interface)
        self._udp_server.startService()
    
    def stopService(self):
        Service.stopService(self)
        return self._udp_server.stopService()


class RemoteConfigurationService(Service):
    def __init__(self, prov_service, dhcp_infos, config):
        self._prov_service = prov_service
        self._dhcp_infos = dhcp_infos
        self._config = config
    
    def startService(self):
        Service.startService(self)
        app = self._prov_service.app
        root_resource = new_root_resource(app, self._dhcp_infos)
        rest_site = Site(root_resource)
        
        port = self._config['general.rest_port']
        interface = self._config['general.ip']
        if interface == '*':
            interface = ''
        self._tcp_server = internet.TCPServer(port, rest_site, interface=interface)
        self._tcp_server.startService()
    
    def stopService(self):
        Service.stopService(self)
        return self._tcp_server.stopService()


class _CompositeConfigSource(object):
    def __init__(self, options):
        self._options = options
        
    def pull(self):
        raw_config = {}
        
        default = prov2.config.DefaultConfigSource()
        raw_config.update(default.pull())
        
        command_line = prov2.config.CommandLineConfigSource(self._options)
        raw_config.update(command_line.pull())
        
        config_file = prov2.config.ConfigFileConfigSource(raw_config['general.config_file'])
        raw_config.update(config_file.pull())
        
        return raw_config


class ProvisioningServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    
    tapname = "prov2"
    description = "A provisioning server."
    options = prov2.config.Options
    
    def _read_config(self, options):
        config_sources = [_CompositeConfigSource(options)]
        return prov2.config.get_config(config_sources)
    
    def makeService(self, options):
        config = self._read_config(options)
        dhcp_infos = {}
        top_service = MultiService()
        
        prov_service = ProvisioningService(config)
        prov_service.setServiceParent(top_service)
        
        process_service = ProcessService(prov_service, dhcp_infos, config)
        process_service.setServiceParent(top_service)
        
        http_process_service = HTTPProcessService(prov_service, process_service, config)
        http_process_service.setServiceParent(top_service)
        
        tftp_process_service = TFTPProcessService(prov_service, process_service, config)
        tftp_process_service.setServiceParent(top_service)
        
        remote_config_service = RemoteConfigurationService(prov_service, dhcp_infos, config)
        remote_config_service.setServiceParent(top_service)

        return top_service
