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

# XXX right now, if we install a plugin that has a bug and can't be loaded,
#     the only way to uninstall it is manually...
# XXX incoherent handling of exceptions in ProvisioningApplication

import copy
import logging
import functools
from provd.devices.config import RawConfigError
from provd.operation import OIP_PROGRESS, OIP_FAIL, OIP_SUCCESS
from provd.persist.common import ID_KEY, InvalidIdError as PersistInvalidIdError
from provd.plugins import PluginManager
from provd.synchro import DeferredRWLock
from twisted.internet import defer

logger = logging.getLogger(__name__)


class InvalidIdError(Exception):
    """Raised when a passed ID is invalid, not necessary because of its type,
    but because of its semantic.
    
    """
    pass


def _rlock_arg(rw_lock):
    def decorator(fun):
        @functools.wraps(fun)
        def aux(*args, **kwargs):
            d = rw_lock.read_lock.run(fun, *args, **kwargs)
            return d
        return aux
    return decorator


def _wlock_arg(rw_lock):
    def decorator(fun):
        @functools.wraps(fun)
        def aux(*args, **kwargs):
            d = rw_lock.write_lock.run(fun, *args, **kwargs)
            return d
        return aux
    return decorator


def _rlock(fun):
    # Decorator for instance method of ProvisioningApplication that need to
    # acquire the read lock
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        d = self._rw_lock.read_lock.run(fun, self, *args, **kwargs)
        return d
    return aux

    
def _wlock(fun):
    # Decorator for instance method of ProvisioningApplication that need to
    # acquire the write lock
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        d = self._rw_lock.write_lock.run(fun, self, *args, **kwargs)
        return d
    return aux


def _check_common_raw_config_validity(raw_config):
    # Check if the common raw config is valid or raise an exception
    for param in [u'ip', u'http_port', u'tftp_port']:
        if param not in raw_config:
            raise RawConfigError('missing "%s" parameter' % param)


def _check_raw_config_validity(raw_config):
    # check if all the mandatory parameters are present
    # XXX this is bit repetitive...
    if u'http_port' not in raw_config and u'tftp_port' not in raw_config:
        raise RawConfigError('missing one of http or tftp port')
    for param in [u'ip', u'protocol']:
        if param not in raw_config:
            raise RawConfigError('missing parameter "%s"' % param)
    if u'sip' in raw_config:
        sip = raw_config[u'sip']
        if u'lines' in sip:
            for line_no, line in sip[u'lines'].iteritems():
                for param in [u'proxy_ip', u'username', u'password', u'display_name']:
                    if param not in line:
                        raise RawConfigError('missing parameter "sip.lines.%s.%s"' %
                                             (line_no, param))
    if u'sccp' in raw_config:
        sccp = raw_config[u'sccp']
        if u'call_managers' in sccp:
            for priority, call_manager in sccp[u'call_managers'].iteritems():
                for param in [u'ip']:
                    if param not in call_manager:
                        raise RawConfigError('missing parameter "sccp.call_managers.%s.%s"' %
                                             (priority, param))
    if u'funckeys' in raw_config:
        funckeys = raw_config[u'funckeys']
        for funckey in funckeys.itervalues():
            for param in [u'exten']:
                if param not in funckey:
                    raise RawConfigError('missing parameter "funckeys.x.%s"' %
                                         param)


def _set_if_absent(dict_, key, value):
    # dict_[key] = value if key not in dict_
    if key not in dict_:
        dict_[key] = value


def _set_defaults_raw_config(raw_config):
    # modify raw_config by setting default parameter value
    if u'sip' in raw_config:
        sip = raw_config[u'sip']
        if u'lines' not in sip:
            sip[u'lines'] = {}
        else:
            lines = sip[u'lines']
            for line in lines.itervalues():
                _set_if_absent(line, u'registrar_ip', line[u'proxy_ip'])
                _set_if_absent(line, u'auth_username', line[u'username'])
    if u'sccp' in raw_config:
        sccp = raw_config[u'sccp']
        _set_if_absent(sccp, u'call_managers', {})
    _set_if_absent(raw_config, u'exten', {})
    if u'funckeys' not in raw_config:
        raw_config[u'funckeys'] = {}
    else:
        funckeys = raw_config[u'funckeys']
        for funckey in funckeys:
            _set_if_absent(funckey, u'supervision', False)    


def _split_config(config):
    splitted_config = {}
    for k, v in config.iteritems():
        current_dict = splitted_config
        key_tokens = k.split('.')
        for key_token in key_tokens[:-1]:
            current_dict = current_dict.setdefault(key_token, {})
        current_dict[key_tokens[-1]] = v
    return splitted_config


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
    
    def __init__(self, cfg_collection, dev_collection, config):
        self._cfg_collection = cfg_collection
        self._dev_collection = dev_collection
        self.pg_mgr = PluginManager(self,
                                    config['general.plugins_dir'],
                                    config['general.cache_dir'])
        self.dhcp_infos = {}
        if 'general.plugin_server' in config:
            self.pg_mgr.server = config['general.plugin_server']
        self._base_raw_config = config['general.base_raw_config']
        logger.info('Using base raw config %s', self._base_raw_config)
        _check_common_raw_config_validity(self._base_raw_config)
        self._splitted_config = _split_config(config)
        self._rw_lock = DeferredRWLock()
        self._pg_load_all(True)
    
    @_wlock
    def close(self):
        logger.info('Closing provisioning application...')
        self.pg_mgr.close()
        logger.info('Provisioning application closed')
    
    # device methods
    
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
            return self._cfg_collection.get_raw_config(cfg_id, self._base_raw_config)
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
            logging.info('Not configuring device %s', device)
        else:
            logger.info('Configuring device %s with plugin %s', device, plugin.id)
            try:
                _check_raw_config_validity(raw_config)
            except Exception, e:
                logging.error('Invalid raw config: %s', e)
            else:
                _set_defaults_raw_config(raw_config)
                try:
                    plugin.configure(device, raw_config)
                except Exception:
                    logger.error('Error while configuring device %s', device, exc_info=True)
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
            logging.info('Not deconfiguring device %s', device)
        else:
            logger.info('Deconfiguring device %s with plugin %s', device, plugin.id)
            try:
                plugin.deconfigure(device)
            except Exception:
                logging.error('Error while deconfiguring device %s', device, exc_info=True)
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
            logging.info('Not synchronizing device %s because one of plugin or raw_config is None',
                         device)
            return defer.fail(Exception('Missing information to synchronize device %s' % device))
        else:
            logger.info('Synchronizing device %s with plugin %s', device, plugin.id)
            return plugin.synchronize(device, raw_config)
    
    @defer.inlineCallbacks
    def _dev_synchronize_if_possible(self, device):
        # Return a deferred that will fire with None once the device
        # synchronization is completed
        plugin, raw_config = yield self._dev_get_plugin_and_raw_config(device)
        yield self._dev_synchronize(device, plugin, raw_config)
    
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
        
        Note that the value of 'configured' is ignored if given.
        
        """
        logging.info('Inserting new device')
        # new device are never configured
        device[u'configured'] = False
        try:
            id = yield self._dev_collection.insert(device)
        except PersistInvalidIdError, e:
            raise InvalidIdError(e)
        else:
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
        
        Note that the value of 'configured' is ignored if given.
        
        """
        logging.info('Updating device')
        try:
            id = device[ID_KEY]
        except KeyError:
            raise ValueError('no id key for device %s' % device)
        else:
            old_device = yield self._dev_get_or_raise(id)
            # configured value must be the same
            device[u'configured'] = old_device[u'configured']
            if old_device == device:
                logger.info('device has not changed, ignoring update')
            else:
                if self._dev_needs_deconfiguration(old_device, device):
                    self._dev_deconfigure_if_possible(old_device)
                if self._dev_needs_configuration(old_device, device):
                    yield self._dev_configure_if_possible(device)
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
        logging.info('Deleting device %s', id)
        device = yield self._dev_get_or_raise(id)
        try:
            yield self._dev_collection.delete(id)
        except PersistInvalidIdError, e:
            raise InvalidIdError(e)
        else:
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
        return self._dev_collection.find_one(selector)
    
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
        logger.info('Reconfiguring device %s', id)
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
        logger.info('Synchronizing device %s', id)
        device = yield self._dev_get_or_raise(id)
        if not device[u'configured']:
            raise Exception('can\'t synchronize not configured device %s' % device)
        else:
            yield self._dev_synchronize_if_possible(device)
    
    # config methods
    
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
        logging.info('Inserting new config')
        try:
            id = yield self._cfg_collection.insert(config)
        except PersistInvalidIdError, e:
            raise InvalidIdError(e)
        else:
            # configure each device that depend on the newly inserted config
            devices = yield self._dev_collection.find({u'config': id})
            if devices:
                raw_config = yield self._cfg_collection.get_raw_config(id, self._base_raw_config)
                for device in devices:
                    plugin = self._dev_get_plugin(device)
                    if self._dev_configure(device, plugin, raw_config):
                        yield self._dev_collection.update(device)
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
        logging.info('Updating config')
        try:
            id = config[ID_KEY]
        except KeyError:
            raise ValueError('no id key for config %s' % config)
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
                    raw_configs[affected_cfg_id] = yield self._cfg_collection.get_raw_config(
                                                             affected_cfg_id, self._base_raw_config)
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
        logging.info('Deleting config %s', id)
        try:
            yield self._cfg_collection.delete(id)
        except PersistInvalidIdError, e:
            raise InvalidIdError(e)
        else:
            # 1. get the set of affected configs
            affected_cfg_ids = yield self._cfg_collection.get_descendants(id)
            affected_cfg_ids.add(id)
            # 2. get the raw_config of every affected config
            raw_configs = {}
            for affected_cfg_id in affected_cfg_ids:
                raw_configs[affected_cfg_id] = yield self._cfg_collection.get_raw_config(
                                                         affected_cfg_id, self._base_raw_config)
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
    
    def cfg_retrieve_raw_config(self, id):
        return self._cfg_collection.get_raw_config(id, self._base_raw_config)
    
    def cfg_find(self, selector):
        return self._cfg_collection.find(selector)
    
    def cfg_find_one(self, selector):
        return self._cfg_collection.find_one(selector)
    
    # plugin methods
    
    def _pg_load_all(self, catch_error=False):
        logger.info('Loading all plugins')
        loaded_plugins = 0
        for pg_id in self.pg_mgr.list_installed():
            try:
                self._pg_load(pg_id)
                loaded_plugins += 1
            except Exception:
                if catch_error:
                    logger.error('Could not load plugin %s', pg_id)
                else:
                    raise
        logger.info('Loaded %d plugins.', loaded_plugins)
    
    def _pg_configure_pg(self, id):
        # Raise an exception if configure_common fail
        plugin = self.pg_mgr[id]
        common_config = copy.deepcopy(self._base_raw_config)
        logger.info('Configuring plugin %s with config %s', id, common_config)
        try:
            plugin.configure_common(common_config)
        except Exception:
            logger.error('Error while configuring plugin %s', id, exc_info=True)
            raise
        
    def _pg_load(self, id):
        # Raise an exception if plugin loading or common configuration fail
        gen_cfg = self._splitted_config['general']
        spec_cfg = self._splitted_config.get('plugin_config', {}).get(id, {})
        try:
            self.pg_mgr.load(id, gen_cfg, spec_cfg)
        except Exception:
            logger.error('Error while loading plugin %s', id, exc_info=True)
            raise
        else:
            self._pg_configure_pg(id)
    
    def _pg_unload(self, id):
        try:
            self.pg_mgr.unload(id)
        except Exception:
            logger.error('Error while unloading plugin %s', id, exc_info=True)
            raise
    
    @defer.inlineCallbacks
    def _pg_configure_all_devices(self, id):
        # Reconfigure all the devices that use the given plugin id
        logger.info('Reconfiguring all devices using plugin %s', id)
        devices = yield self._dev_collection.find({u'plugin': id})
        for device in devices:
            updated = yield self._dev_configure_if_possible(device)
            if updated:
                yield self._dev_collection.update(device)
    
    def pg_install(self, id):
        """Install the plugin with the given id.
        
        Return a tuple (deferred, operation in progress).
        
        This method raise the following exception:
          - an Exception if the plugin is already installed.
          - an Exception if there's no installable plugin with the specified
            name.
          - an Exception if there's already an install/upgrade operation
            in progress for the plugin.
          - an InvalidParameterError if the plugin package is not in cache
            and no 'server' param has been set.
        
        Affected devices are automatically configured if needed.
        
        """
        logger.info('Installing and loading plugin %s', id)
        if self.pg_mgr.is_installed(id):
            logger.error('Error: plugin %s is already installed', id)
            raise Exception('plugin %s is already installed' % id)
        
        def callback1(_):
            # reset the state to in progress
            oip.state = OIP_PROGRESS
        @_wlock_arg(self._rw_lock)
        def callback2(_):
            # The lock apply only to the deferred return by this function
            # and not on the function itself
            # next line might raise an exception, which is ok
            self._pg_load(id)
            return self._pg_configure_all_devices(id)
        def callback3(_):
            oip.state = OIP_SUCCESS
        def errback3(err):
            oip.state = OIP_FAIL
            return err
        deferred, oip = self.pg_mgr.install(id)
        deferred.addCallback(callback1)
        deferred.addCallback(callback2)
        deferred.addCallbacks(callback3, errback3)
        return deferred, oip
    
    def pg_upgrade(self, id):
        """Upgrade the plugin with the given id.
        
        Same contract as pg_install, except that the plugin must already be
        installed.
        
        Affected devices are automatically reconfigured if needed.
        
        """
        logger.info('Upgrading and reloading plugin %s', id)
        if not self.pg_mgr.is_installed(id):
            logger.error('Error: plugin %s is not already installed', id)
            raise Exception('plugin %s is not already installed' % id)
        
        def callback1(_):
            # reset the state to in progress
            oip.state = OIP_PROGRESS
        @_wlock_arg(self._rw_lock)
        def callback2(_):
            # The lock apply only to the deferred return by this function
            # and not on the function itself
            if id in self.pg_mgr:
                # next line might raise an exception, which is ok
                self._pg_unload(id)
            # next line might raise an exception, which is ok
            self._pg_load(id)
            return self._pg_configure_all_devices(id)
        def callback3(_):
            oip.state = OIP_SUCCESS
        def errback3(err):
            oip.state = OIP_FAIL
            return err
        # XXX we probably want to check that the plugin is 'really' upgradeable
        deferred, oip = self.pg_mgr.upgrade(id)
        deferred.addCallback(callback1)
        deferred.addCallback(callback2)
        deferred.addCallbacks(callback3, errback3)
        return deferred, oip
    
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
        logger.info('Uninstalling and unloading plugin %s', id)
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
