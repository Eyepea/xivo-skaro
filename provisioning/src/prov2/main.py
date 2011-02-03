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

# XXX right now, if we install a plugin that has a bug and can't be loaded,
#     the only way to uninstall it is manually...
# XXX incoherent handling of exceptions in ProvisioningApplication

import copy
import logging
import logging.handlers
import functools
import os.path
import prov2.config
import prov2.devices.ident
import prov2.devices.pgasso
from prov2.servers.tftp.proto import TFTPProtocol
from prov2.servers.http_site import Site
from prov2.synchro import DeferredRWLock
from prov2.persist.memory import MemoryDatabaseFactory
from prov2.persist.shelve import ShelveDatabaseFactory
from prov2.persist.common import ID_KEY
from prov2.plugins import PluginManager
from prov2.rest.server import new_root_resource
from twisted.application.service import IServiceMaker, Service, MultiService
from twisted.application import internet
from twisted.internet import defer
from twisted.plugin import IPlugin
from twisted.python import log
from zope.interface.declarations import implements

logger = logging.getLogger('main')


class InvalidIdError(Exception):
    """Raised when a passed ID is invalid, not necessary because of its type,
    but because of its semantic.
    
    """
    pass


def _rlock(fun):
    # Decorator for instance method of ProvisioningApplication that need to
    # acquire the read lock
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        d = self._rw_lock.read_lock.run(fun, self, *args, **kwargs)
        return d
    return aux

    
def _wlock(fun):
    # Decorator for instance method of ProvisioningApplicatio that need to
    # acquire the write lock
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        d = self._rw_lock.read_lock.run(fun, self, *args, **kwargs)
        return d
    return aux


class ProvisioningApplication(object):
    """Main logic used to provision devices.
    
    Here's the restrictions on the devices/configs/plugins stored by instances
    of this class:
    - device can make references to unknown configs or plugins
    - configs can make references to unknown configs
    - a plugin can be uninstalled even if some devices make references to it
    - a config can be removed even if some devices or other configs make
      reference to it
    
    This class enforce the plugin contract.
    
    """
    # Note that, seen from the outside, all method acquiring a lock return a
    # deferred.
    
    def _split_config(self, config):
        splitted_config = {}
        for k, v in config.iteritems():
            current_dict = splitted_config
            key_tokens = k.split('.')
            for key_token in key_tokens[:-1]:
                current_dict = current_dict.setdefault(key_token, {})
            current_dict[key_tokens[-1]] = v
        return splitted_config
    
    def __init__(self, database, config):
        logger.info('Creating application...')
        self._cfg_collection = database.collection('configs')
        self._dev_collection = database.collection('devices')
        self.pg_mgr = PluginManager(self,
                                    config['general.plugins_dir'],
                                    config['general.cache_dir'])
        if 'general.plugin_server' in config:
            self.pg_mgr.server = config['general.plugin_server']
        self._splitted_config = self._split_config(config)
        self._rw_lock = DeferredRWLock()
    
    @_wlock
    def close(self):
        self._cfg_collection.close()
        self._dev_collection.close()
        self.pg_mgr.close()
    
    # device methods
    
    def _dev_check_validity_std_keys(self, device):
        # TODO implement if useful... this might go below in device collection
        #      or above in the REST server
        pass
    
    def _dev_check_validity(self, device):
        self._dev_check_validity_std_keys(device)
    
    def _dev_get_plugin(self, device):
        # Return the plugin associated with the device, or None if there's
        # no such plugin
        if u'plugin' in device:
            return self.pg_mgr.get(device[u'plugin'])
        else:
            return None
    
    def _dev_get_raw_config(self, device):
        # Return a deferred that will fire with a raw config associated
        # with the device, or fire with None if there's no such raw config
        if u'config' in device:
            cfg_id = device[u'config']
            return self._cfg_collection.get_raw_config(cfg_id, self._splitted_config['common_config'])
        else:
            return defer.succeed(None)
    
    @defer.inlineCallbacks
    def _dev_get_plugin_and_raw_config(self, device):
        # Return a deferred that will fire with a tuple (plugin, raw_config)
        # associated with the device, or fire with the tuple (None, None) if
        # there's at least one without etc etc
        plugin = self._dev_get_plugin(device)
        if plugin is not None:
            raw_config = yield self._dev_get_raw_config(device)
            if raw_config is not None:
                defer.returnValue((plugin, raw_config))
        defer.returnValue((None, None))
    
    def _dev_configure(self, device, plugin, raw_config):
        # Return true if device has been updated, else false
        updated = False
        if None in (plugin, raw_config):
            logging.info('Not configuring device "%s" because one of plugin or raw_config is None',
                         device)
        else:
            logger.info('Configuring device "%s" with plugin "%s"', device, plugin.name)
            try:
                plugin.configure(device, raw_config)
            except Exception:
                logger.error('Error while configuring device "%s"', device, exc_info=True)
            else:
                if not device[u'configured']:
                    device[u'configured'] = True
                    updated = True
        return updated
    
    @defer.inlineCallbacks
    def _dev_configure_if_possible(self, device):
        # Return a deferred that will fire with true if device object has
        # been updated, else false
        plugin, raw_config = yield self._dev_get_plugin_and_raw_config(device)
        defer.returnValue(self._dev_configure(device, plugin, raw_config))
    
    def _dev_is_possibly_configurable(self, device):
        # Return true if device is possibly configurable, i.e. if it has a
        # u'plugin' and u'config' attribute
        return u'plugin' in device and u'config' in device
    
    def _dev_needs_configuration(self, old_device, new_device):
        # Return true if new_device need to be configured, else false
        if not self._dev_is_possibly_configurable(new_device):
            return False
        for name in (u'plugin', u'config', u'mac', u'ip', u'vendor',
                     u'model', u'version'):
            if old_device.get(name) != new_device.get(name):
                return True
        return False
    
    def _dev_deconfigure(self, device, plugin):
        # Return true if device has been updated, else false
        updated = False
        if plugin is None:
            logging.info('Not deconfiguring device "%s" because plugin is None', device)
        else:
            logger.info('Deconfiguring device "%s" with plugin "%s"', device, plugin.name)
            try:
                plugin.deconfigure(device)
            except Exception:
                logging.error('Error while deconfiguring device "%s"', device, exc_info=True)
            else:
                if device[u'configured']:
                    device[u'configured'] = False
                    updated = True
        return updated
    
    def _dev_deconfigure_if_possible(self, device):
        # Return true if device has been updated, else false
        plugin = self._dev_get_plugin(device)
        return self._dev_deconfigure(device, plugin)
    
    def _dev_is_possibly_deconfigurable(self, device):
        # Return true if device is possibly deconfigurable, i.e. if it has
        # a u'plugin' attribute.
        return u'plugin' in device
    
    def _dev_needs_deconfiguration(self, old_device, new_device):
        # Return true if old_device needs to be deconfigured, else false
        if old_device[u'configured']:
            assert u'plugin' in old_device
            old_pg_id = old_device[u'plugin']
            new_pg_id = new_device.get(u'plugin')
            return old_pg_id != new_pg_id
        return False

    def _dev_synchronize(self, device, plugin, raw_config):
        # Return a deferred that will fire with None once the device
        # synchronization is completed, or 
        if None in (plugin, raw_config):
            logging.info('Not synchronizing device "%s" because one of plugin or raw_config is None',
                         device)
            return defer.fail(Exception('Missing information to synchronize device "%s"' % device))
        else:
            logger.info('Synchronizing device "%s" with plugin "%s"', device, plugin.name)
            return plugin.synchronize(device, raw_config)
    
    @defer.inlineCallbacks
    def _dev_synchronize_if_possible(self, device):
        # Return a deferred that will fire with None once the device
        # synchronization is completed
        plugin, raw_config = yield self._dev_get_plugin_and_raw_config(device)
        defer.returnValue(self._dev_synchronize(device, plugin, raw_config))
    
    @defer.inlineCallbacks
    def _dev_get_or_raise(self, id):
        device = yield self._dev_collection.retrieve(id)
        if device is None:
            raise InvalidIdError('invalid device ID "%s"' % id)
        else:
            defer.returnValue(device)
    
    @_wlock
    @defer.inlineCallbacks
    def dev_insert(self, device):
        """Insert a new device into the provisioning application.
        
        Return a deferred that will fire with the ID of the device.
        
        The deferred will fire it's errback with a ValueError if device
        is not a valid device object, i.e. invalid key value, invalid
        type, etc.
        
        The deferred will fire it's errback with an Exception if an 'id'
        key is specified but there's already one device with the same ID.
        
        If device has no 'id' key, one will be added after the device is
        successfully inserted.
        
        Device will be automatically configured if there's enough information
        to do so.
        
        """
        self._dev_check_validity(device)
        # next line might raise an persist.InvalidIdError, which
        # is not quite the right type
        id = yield self._dev_collection.insert(device)
        updated = yield self._dev_configure_if_possible(device)
        if updated:
            yield self._dev_collection.update(device)
        defer.returnValue(id)
    
    @_wlock
    @defer.inlineCallbacks
    def dev_update(self, device):
        """Update the device.
        
        Return a deferred that fire with None once the update is completed.
        
        The deferred will fire its errback with an exception if device has
        no 'id' key.
        
        The deferred will fire its errback with an InvalidIdError if device
        has unknown id.
        
        The device is automatically deconfigured/configured if needed.
        
        """
        self._dev_check_validity(device)
        try:
            id = device[ID_KEY]
        except KeyError:
            raise ValueError('no id key for device "%s"' % device)
        else:
            old_device = yield self._dev_get_or_raise(id)
            if old_device == device:
                logger.info('device has not changed, ignoring update')
            else:
                if self._dev_needs_deconfiguration(old_device, device):
                    self._dev_deconfigure_if_possible(old_device)
                if self._dev_needs_configuration(old_device, device):
                    yield self._dev_configure_if_possible(device)
                # next line might raise an persist.InvalidIdError if the
                # device has been deleted
                yield self._dev_collection.update(device)
    
    @_wlock
    @defer.inlineCallbacks
    def dev_delete(self, id):
        """Delete the device with the given ID.
        
        Return a deferred that will fire with None once the device is
        deleted.
        
        The deferred will fire its errback with an InvalidIdError if device
        has unknown id.
        
        The device is automatically deconfigured if needed.
        
        """
        device = yield self._dev_get_or_raise(id)
        # next line might raise an persist.InvalidIdError
        yield self._dev_collection.delete(id)
        if device[u'configured']:
            self._dev_deconfigure_if_possible(device)
    
    def dev_retrieve(self, id):
        """Return a deferred that fire with the device with the given ID, or
        fire with None if there's no such document.
        
        """
        return self._dev_collection.retrieve(id)
    
    def dev_find(self, selector):
        return self._dev_collection.find(selector)
    
    def dev_find_one(self, selector):
        return self._dev_collection.find(selector)
    
    @_wlock
    @defer.inlineCallbacks
    def dev_reconfigure(self, id):
        """Force the reconfiguration of the device. This is usually not
        necessary since configuration is usually done automatically.
        
        Return a deferred that will fire with None once the device
        reconfiguration is completed.
        
        The deferred will fire its errback with an exception if id is not a
        valid device ID.
        
        The deferred will fire its errback with an exception if the device can't
        be configured because there's either no config or no plugin. Note
        that the value of the configured key of the device has no influence.
        
        """
        device = yield self._dev_get_or_raise(id)
        updated = yield self._dev_configure_if_possible(device)
        if updated:
            # next line might raise an exception
            yield self._dev_collection.update(device)
    
    @_rlock
    @defer.inlineCallbacks
    def dev_synchronize(self, id):
        """Synchronize the physical device with its config.
        
        Return a deferred that will fire with None once the device is
        synchronized.
        
        The deferred will fire its errback with an exception if id is not a
        valid device ID.
        
        The deferred will fire its errback with an exception if the device
        can't be configured since it has not been configured yet.
        
        """
        device = yield self._dev_get_or_raise(id)
        if not device[u'configured']:
            raise Exception('can\'t synchronize not configured device "%s"' % device)
        else:
            defer.returnValue(self._dev_synchronize_if_possible(device))
    
    # config methods
    
    def _cfg_check_validity_std_keys(self, device):
        # TODO implement if useful... this might go below in device collection
        #      or above in the REST server
        pass
    
    def _cfg_check_validity(self, config):
        self._cfg_check_validity_std_keys(config)
        
    @defer.inlineCallbacks
    def _cfg_get_or_raise(self, id):
        config = yield self._cfg_collection.retrieve(id)
        if config is None:
            raise InvalidIdError('invalid config ID "%s"' % id)
        else:
            defer.returnValue(config)
    
    @_wlock
    @defer.inlineCallbacks
    def cfg_insert(self, config):
        """Insert a new config into the provisioning application.
        
        Return a deferred that will fire with the ID of the config.
        
        The deferred will fire it's errback with a ValueError if config
        is not a valid config object, i.e. invalid key value, invalid
        type, etc.
        
        The deferred will fire it's errback with an Exception if an 'id'
        key is specified but there's already one config with the same ID.
        
        If config has no 'id' key, one will be added after the config is
        successfully inserted.
        
        """
        self._cfg_check_validity(config)
        # XXX next line might throw an prov2.persist.common.InvalidIdError. We
        #     may want to catch it and throw a InvalidIdError...
        id = yield self._cfg_collection.insert(config)
        defer.returnValue(id)
    
    @_wlock
    @defer.inlineCallbacks
    def cfg_update(self, config):
        """Update the config.
        
        Return a deferred that fire with None once the update is completed.
        
        The deferred will fire its errback with an exception if config has
        no 'id' key.
        
        The deferred will fire its errback with an InvalidIdError if config
        has unknown id.
        
        Note that device might be reconfigured.
        
        """
        self._cfg_check_validity(config)
        try:
            id = config[ID_KEY]
        except KeyError:
            raise ValueError('no id key for config "%s"' % config)
        else:
            old_config = yield self._cfg_get_or_raise(id)
            if old_config == config:
                logger.info('config has not changed, ignoring update')
            else:
                yield self._cfg_collection.update(config)
                # 1. get the set of affected configs
                affected_cfg_ids = yield self._cfg_collection.get_descendants(id)
                affected_cfg_ids.add(id)
                # 2. get the raw_config of every affected config
                raw_configs = {}
                for affected_cfg_id in affected_cfg_ids:
                    raw_configs[affected_cfg_id] = yield self._cfg_collection.get_raw_config()
                # 3. reconfigure each device having a direct dependency on
                #    one of the affected cfg id
                affected_devices = yield self._dev_collection.find({u'config': {u'$in': list(affected_cfg_ids)}})
                for device in affected_devices:
                    plugin = self._dev_get_plugin(device)
                    raw_config = raw_configs[device[u'config']]
                    if self._dev_configure(device, plugin, raw_config):
                        yield self._dev_collection.update(device)
    
    @_wlock
    @defer.inlineCallbacks
    def cfg_delete(self, id):
        """Delete the config with the given ID. Does not delete any reference
        to it from other configs.
        
        Return a deferred that will fire with None once the config is
        deleted.
        
        The deferred will fire its errback with an InvalidIdError if config
        has unknown id.
        
        The devices depending directly or indirectly over this config are
        automatically reconfigured if needed.
        
        """
        # next line might raise an persist.InvalidIdError
        yield self._cfg_collection.delete(id)
        # 1. get the set of affected configs
        affected_cfg_ids = yield self._cfg_collection.get_descendants(id)
        affected_cfg_ids.add(id)
        # 2. get the raw_config of every affected config
        raw_configs = {}
        for affected_cfg_id in affected_cfg_ids:
            raw_configs[affected_cfg_id] = yield self._cfg_collection.get_raw_config()
        # 3. reconfigure/deconfigure each affected devices
        affected_devices = yield self._dev_collection.find({u'config': {u'$in': list(affected_cfg_ids)}})
        for device in affected_devices:
            plugin = self._dev_get_plugin(device)
            raw_config = raw_configs[device[u'config']]
            if device[u'config'] == id:
                # deconfigure
                assert raw_config is None
                if self._dev_deconfigure(device, plugin):
                    yield self._dev_collection.update(device)
            else:
                # reconfigure
                assert raw_config is not None
                if self._dev_configure(device, plugin, raw_config):
                    yield self._dev_collection.update(device)
    
    def cfg_retrieve(self, id):
        """Return a deferred that fire with the config with the given ID, or
        fire with None if there's no such document.
        
        """
        return self._cfg_collection.retrieve(id)
    
    def cfg_find(self, selector):
        return self._cfg_collection.find(selector)
    
    def cfg_find_one(self, selector):
        return self._cfg_collection.find_one(selector)
    
    # plugin methods
    
    def _pg_configure_pg(self, id):
        # Raise an exception if configure_common fail
        plugin = self.pg_mgr[id]
        common_config = copy.deepcopy(self._splitted_config['common_config'])
        logger.info('Configuring plugin "%s"', id)
        try:
            plugin.configure_common(common_config)
        except Exception:
            logger.error('Error while configuring plugin "%s"', id)
            raise
        
    def _pg_load(self, id):
        # Raise an exception if plugin loading or common configuration fail
        gen_cfg = self._splitted_config['general']
        spec_cfg = self._splitted_config.get('plugin_config', {}).get(id, {})
        logger.info('Loading plugin "%s', id)
        try:
            self.pg_mgr.load(id, gen_cfg, spec_cfg)
        except Exception:
            logger.error('Error while loading plugin "%s"', id, exc_info=True)
            raise
        else:
            self._pg_configure_pg(id)
    
    def _pg_unload(self, id):
        logger.info('Unloading plugin "%s', id)
        try:
            self.pg_mgr.unload(id)
        except Exception:
            logger.error('Error while unloading plugin "%s"', id, exc_info=True)
            raise
    
    @defer.inlineCallbacks
    def _pg_configure_all_devices(self, id):
        # Reconfigure all the devices that use the given plugin id
        devices = yield self._dev_collection.find({u'plugin': id})
        for device in devices:
            updated = yield self._dev_configure_if_possible(device)
            if updated:
                yield self._dev_collection.update(device)
    
    @_wlock
    def pg_install(self, id):
        """Install the plugin with the given id.
        
        Return a deferred that will fire with an object providing the
        IProgressOperation interface once the plugin installation is started.
        
        The deferred will fire its errback with:
          - an Exception if the plugin is already installed.
          - an Exception if there's no installable plugin with the specified
            name.
          - an Exception if there's already an install/upgrade operation
            in progress for the plugin.
          - an InvalidParameterError if the plugin package is not in cache
            and no 'server' param has been set.
        
        Affected devices are automatically configured if needed.
        
        """
        logger.info('Installing plugin "%s"', id)
        if self.pg_mgr.is_installed(id):
            raise Exception('plugin "%s" is already installed' % id)
        
        def on_success(_):
            # next line might raise an exception, which is ok
            self._pg_load(id)
            return self._pg_configure_all_devices(id)
        pop = self.pg_mgr.install(id)
        pop.deferred.addCallback(on_success)
        return pop
    
    @_wlock
    def pg_upgrade(self, id):
        """Upgrade the plugin with the given id.
        
        Same contract as pg_install, except that the plugin must already be
        installed.
        
        Affected devices are automatically reconfigured if needed.
        
        """
        logger.info('Upgrading plugin "%s"', id)
        if not self.pg_mgr.is_installed(id):
            raise Exception('plugin "%s" is not already installed' % id)
        
        def on_success(_):
            if id in self.pg_mgr:
                # next line might raise an exception, which is ok
                self._pg_unload(id)
            # next line might raise an exception, which is ok
            self._pg_load(id)
            return self._pg_configure_all_devices(id)
        # XXX we probably want to check that the plugin is 'really' upgradeable
        pop = self.pg_mgr.upgrade(id)
        pop.deferred.addCallback(on_success)
        return pop
    
    @_wlock
    @defer.inlineCallbacks
    def pg_uninstall(self, id):
        """Uninstall the plugin with the given id.
        
        Return a deferred that will fire with None once the operation is
        completed.
        
        The deferred will fire its errback with an Exception if the plugin
        is not already installed.
        
        Affected devices are automatically deconfigured if needed.
        
        """
        logger.info('Uninstallating plugin "%s"', id)
        if not self.pg_mgr.is_installed(id):
            raise Exception('plugin "%s" is not already installed' % id)
        
        self.pg_mgr.uninstall(id)
        self._pg_unload(id)
        # soft deconfigure all the device that were configured by this device
        # note that there is no point in calling plugin.deconfigure for every
        # of these devices since the plugin is removed anyway
        affected_devices = yield self._dev_collection.find({u'plugin': id,
                                                            u'configured': True})
        for device in affected_devices:
            device[u'configured'] = False
            yield self._dev_collection.update(device)
    
    def pg_retrieve(self, id):
        return self.pg_mgr[id]


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
    u'id': u'base',
    u'parent_ids': [],
    u'raw_config': {
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
}

# a 'guest' configuration
guest_cfg = {
    u'id': u'guest',
    u'parent_ids': [u'base'],
    u'raw_config': {
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
}

# a configuration for a device
dev1_cfg = {
    u'id': u'dev1',
    u'parent_ids': [u'base'],
    u'raw_config': {
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
}


class ProvisioningService(Service):
    _DB_FACTORIES = {
        'list': MemoryDatabaseFactory(),
        'dict': MemoryDatabaseFactory(),
        'shelve': ShelveDatabaseFactory()
    }
    
    def __init__(self, config):
        self._config = config

    def _extract_database_config(self):
        db_config = {}    
        for k, v in self._config.iteritems():
            pre, sep, post = k.partition('.')
            if pre == 'database' and sep:
                db_config[post] = v
        return db_config
    
    def _create_database(self):
        type = self._config['database.type']
        generator = self._config['database.generator']
        db_config = self._extract_database_config()
        db_factory = self._DB_FACTORIES[type]
        return db_factory.new_database(type, generator, **db_config)
    
    def startService(self):
        Service.startService(self)
        self.database = self._create_database()
        self.app = ProvisioningApplication(self.database, self._config)
        
        # XXX next lines are for testing purpose only
        def add_cfg(config):
            d = self.app.cfg_insert(config)
            d.addErrback(lambda _: None)
        add_cfg(base_cfg)
        add_cfg(guest_cfg)
        add_cfg(dev1_cfg)
    
    def stopService(self):
        Service.stopService(self)
        try:
            self.database.close()
        except Exception:
            logger.error('error while closing database', exc_info=True)
        try:
            self.app.close()
        except Exception:
            logger.error('error while closing application', exc_info=True)


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
