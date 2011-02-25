# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

from provd.rest.client.base import new_server_resource
from provd.rest.client.util import once_per_instance


class ServiceNotAvailableError(Exception):
    pass


class OperationInProgress(object):
    # This class has the same interface as the resource it wraps, yet it
    # might eventually evolve (catching exception, etc)
    def __init__(self, op_in_progress_res):
        self._res = op_in_progress_res
    
    def status(self):
        return self._res.status()
    
    def delete(self):
        self._res.delete()
    

class ProvisioningClient(object):
    def __init__(self, server_res):
        self._server_res = server_res

    @once_per_instance
    def config_manager(self):
        cfg_mgr_res = self._server_res.cfg_mgr_res() 
        return ConfigManager(cfg_mgr_res)
    
    @once_per_instance
    def device_manager(self):
        dev_mgr_res = self._server_res.dev_mgr_res() 
        return DeviceManager(dev_mgr_res)
    
    @once_per_instance
    def plugin_manager(self):
        pg_mgr_res = self._server_res.pg_mgr_res()
        return PluginManager(pg_mgr_res)
    
    def test_connectivity(self):
        # raise an exception if there seems to be connectivity issues
        self._server_res.test_connectivity()


class ConfigManager(object):
    def __init__(self, cfg_mgr_res):
        self._cfg_mgr_res = cfg_mgr_res
    
    @once_per_instance
    def _get_configs_res(self):
        return self._cfg_mgr_res.configs_res()
    
    def add(self, config):
        """Add a config and return its ID."""
        configs_res = self._get_configs_res()
        return configs_res.add(config)
    
    def _get_config_res(self, id):
        configs_res = self._get_configs_res()
        return configs_res.config_res(id)
    
    def get(self, id):
        """Return a config object with the given ID."""
        config_res = self._get_config_res(id)
        return config_res.get()
    
    def _get_raw_config_res(self, id):    
        configs_res = self._get_configs_res()
        return configs_res.raw_config_res(id)
    
    def get_raw(self, id):
        """Return a raw config object, i.e. the 'raw_config' part of a config
        object, with the raw_config of all it's ancestor. This is the same
        thing as what a plugin will receive when told to configure a device
        with this config.
        
        """
        raw_config_res = self._get_raw_config_res(id)
        return raw_config_res.get()
    
    def update(self, config):
        """Update the given config."""
        id = config[u'id']
        config_res = self._get_config_res(id)
        config_res.update(config)
    
    def remove(self, id):
        """Remove the config with the given ID."""
        config_res = self._get_config_res(id)
        config_res.delete()
    
    def find(self, selector):
        """Return a list of configs ID that match the given selector.
        
        The selector is a dictionary where keys and values are [unicode]
        string. If you want to list every config, pass an empty dictionary.
        
        """
        configs_res = self._get_configs_res()
        return configs_res.find(selector)
    
    def rename(self, id, new_id):
        raise NotImplementedError('not supported by client and server yet')


class DeviceManager(object):
    def __init__(self, dev_mgr_res):
        self._dev_mgr_res = dev_mgr_res
    
    @once_per_instance
    def _get_sync_res(self):
        return self._dev_mgr_res.resync_res()
    
    def synchronize(self, id):
        """Synchronize the device with the given ID and return something..."""
        sync_res = self._get_sync_res()
        return OperationInProgress(sync_res.resync(id))
    
    @once_per_instance
    def _get_reconfigure_res(self):
        return self._dev_mgr_res.reconfigure_res() 
        
    def reconfigure(self, id):
        """Reconfigure the device with the given ID."""
        reconfigure_res = self._get_reconfigure_res()
        reconfigure_res.reconfigure(id)
    
    @once_per_instance
    def _get_devices_res(self):
        return self._dev_mgr_res.devices_res()
    
    def add(self, device):
        """Add a device and return it's ID."""
        devices_res = self._get_devices_res()
        return devices_res.add(device)

    def _get_device_res(self, id):    
        devices_res = self._get_devices_res()
        return devices_res.device_res(id)
    
    def get(self, id):
        """Return a device object with the given ID."""
        device_res = self._get_device_res(id)
        return device_res.get()
    
    def update(self, device):
        """Update the given device."""
        id = device[u'id']
        device_res = self._get_device_res(id)
        device_res.update(device)
    
    def remove(self, id):
        """Delete the device with the given ID."""
        device_res = self._get_device_res(id)
        device_res.delete()
    
    def find(self, selector):
        """Return a list of device ID that match the given selector."""
        devices_res = self._get_devices_res()
        return devices_res.find(selector)
    
    def rename(self, id, new_id):
        raise NotImplementedError('not supported by client and server yet')


class PluginManager(object):
    def __init__(self, pg_mgr_res):
        self._pg_mgr_res = pg_mgr_res

    @once_per_instance
    def configure_service(self):
        """Return a configure object for the plugin manager."""
        config_srv_res = self._pg_mgr_res.config_srv_res()
        return ConfigureService(config_srv_res)
    
    @once_per_instance
    def install_service(self):
        """Return an install object for the plugin manager."""
        install_srv_res = self._pg_mgr_res.install_srv_res()
        return InstallService(install_srv_res)
    
    @once_per_instance
    def _get_plugins_res(self):
        return self._pg_mgr_res.plugins_res()
    
    def plugins(self):
        """Return a list of [loaded] plugin ID."""
        plugins_res = self._get_plugins_res()
        return plugins_res.list()
    
    def plugin(self, id):
        """Return the [loaded] plugin with the given ID."""
        plugins_res = self._get_plugins_res()
        return Plugin(plugins_res.get(id))


class Plugin(object):
    def __init__(self, pg_res):
        self._pg_res = pg_res
    
    @once_per_instance
    def _get_services(self):
        return self._pg_res.services()
    
    @once_per_instance
    def configure_service(self):
        services = self._get_services()
        try:
            config_srv_res = services[u'srv.configure'] 
        except KeyError:
            raise ServiceNotAvailableError('no configure service')
        else:
            return ConfigureService(config_srv_res)
    
    @once_per_instance
    def install_service(self):
        services = self._get_services()
        try:
            install_srv_res = services[u'srv.install']
        except KeyError:
            raise ServiceNotAvailableError('no install service')
        else:
            return InstallService(install_srv_res)
    

class ConfigureService(object):
    def __init__(self, config_srv_res):
        self._config_srv_res = config_srv_res
    
    def _get_config_param_res(self, key):
        return self._config_srv_res.get(key)
    
    def get(self, key):
        config_param_res = self._get_config_param_res(key)
        return config_param_res.get()
    
    def set(self, key, value):
        config_param_res = self._get_config_param_res(key)
        config_param_res.set(value)
    
    @once_per_instance
    def description(self):
        """Return a dictionary where keys are configuration key and values
        are short description of the configuration key.
        
        """
        return self._config_srv_res.parameters()


class InstallService(object):
    def __init__(self, install_srv_res):
        self._install_srv_res = install_srv_res
    
    @once_per_instance
    def _get_install_res(self):
        return self._install_srv_res.install_res()
    
    def install(self, id):
        """Install the package with the given ID."""
        install_res = self._get_install_res()
        return OperationInProgress(install_res.install(id))
    
    @once_per_instance
    def _get_uninstall_res(self):
        return self._install_srv_res.uninstall_res()
    
    def uninstall(self, id):
        """Uninstall the package with the given ID."""
        uninstall_res = self._get_uninstall_res()
        uninstall_res.uninstall(id)
    
    @once_per_instance
    def _get_upgrade_res(self):
        return self._install_srv_res.upgrade_res()
    
    def upgrade(self, id):
        """Upgrade the package with the given ID."""
        upgrade_res = self._get_upgrade_res()
        return OperationInProgress(upgrade_res.upgrade(id))
    
    @once_per_instance
    def _get_update_res(self):
        return self._install_srv_res.update_res()
    
    def update(self):
        """Update the list of installable packages."""
        update_res = self._get_update_res()
        return OperationInProgress(update_res.update())
    
    @once_per_instance
    def _get_installed_res(self):
        return self._install_srv_res.installed_res()
    
    def installed(self):
        installed_res = self._get_installed_res()
        return installed_res.installed()
    
    @once_per_instance
    def _get_installable_res(self):
        return self._install_srv_res.installable_res()
    
    def installable(self):
        installable_res = self._get_installable_res()
        return installable_res.installable()


def new_provisioning_client(server_uri, credentials=None):
    server_res = new_server_resource(server_uri, credentials)
    return ProvisioningClient(server_res)
