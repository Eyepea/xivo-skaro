# -*- coding: UTF-8 -*-

"""Main module of the provisioning server.

Setup all the stuff and then run...

"""

from __future__ import with_statement

# XXX this is really dirty, you should see this as experimental/prototypal/bunch
#     of unstructured functional tests

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010  Proformatique <technique@proformatique.com>

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

import atexit
import time
import sys
from ConfigParser import RawConfigParser
from pprint import pprint
from prov2.devices.ident import *
from prov2.devices.pgasso import PluginAssociatorDeviceUpdater,\
    AlphabeticConflictSolver
from prov2.servers.tftp.service import TFTPLogService
from prov2.servers.tftp.proto import TFTPProtocol
from prov2.servers.http import HTTPLogService
from prov2.servers.http_site import Site
from prov2.devices.config import ConfigManager
from prov2.devices.device import DeviceManager
from prov2.devices.util import NumericIdGenerator
from prov2.plugins import PluginManager
from prov2.rest.server import DevicesResource,\
    ConfigsResource, DeviceSynchronizeResource,\
    PluginMgrUpdateResource, PluginMgrListInstallableResource,\
    PluginMgrListInstalledResource, PluginMgrListUpgradeableResource,\
    PluginMgrConfigureResource, PluginMgrInstallResource, PluginMgrUninstallRecourse,\
    PluginMgrUpgradeResource, PluginsResource, DHCPInfoResource
from twisted.python.util import println


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


def _read_config(filename):
    config = RawConfigParser()
    with open(filename, 'r') as fobj:
        config.readfp(fobj)

    # XXX right now, we only transform the RawConfigParser object to
    # a more manipulable mapping of mapping object
    result = {'pg_mgr': {'plugins_dir': '/var/lib/pf-xivo/prov2/plugins',
                         'cache_dir': '/var/cache/pf-xivo/prov2/plugins'}}
    for section in config.sections():
        in_result = result.setdefault(section, {})
        for option in config.options(section):
            in_result[option] = config.get(section, option)
    
    # check if every mandatory options are specified
    #mandatory = {'pg_mgr': ['server']}
    mandatory = {}
    for section in mandatory:
        if section not in result:
            raise ValueError('mandatory section "%s" not specified' % section)
        in_result = result[section]
        for option in mandatory[section]:
            if option not in in_result:
                raise ValueError('mandatory option "%s" in section "%s" not specified' %
                                 (option, section))
    return result


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
    
    DEF_CONFIG_FILENAME = '../../test-resources/etc/prov2.conf'
    
    def __init__(self, config_filename=DEF_CONFIG_FILENAME):
        config = _read_config(config_filename)
        self.dev_mgr = DeviceManager()
        self.cfg_mgr = ConfigManager()
        self.pg_mgr = PluginManager(self,
                                    config['pg_mgr']['plugins_dir'],
                                    config['pg_mgr']['cache_dir'])
        if 'server' in config['pg_mgr']:
            self.pg_mgr.server = config['pg_mgr']['server']
        self._config = config
        self._dev_id_gen = NumericIdGenerator()
        self._cfg_id_gen = NumericIdGenerator()
        
        for pg_info in self.pg_mgr.list_installed():
            pg_id = pg_info['name']
            self._load_pg(pg_id)
    
    def close(self):
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
        """Return the flattened config of dev, or None."""
        if 'config' in dev:
            cfg_id = dev['config']
            if cfg_id in self.cfg_mgr:
                return self.cfg_mgr.flatten(cfg_id)
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
            plugin.configure(dev, config)
    
    def _deconfigure_dev(self, dev):
        """Call plugin.deconfigure(dev) if possible.
        
        Its possible if dev has a plugin ID which refer to a valid plugin.
        
        """
        plugin = self._get_plugin(dev)
        if plugin is not None:
            plugin.deconfigure(dev)
    
    def _synchronize_dev(self, dev):
        """Call plugin.synchronize(dev, config) if possible."""
        plugin, config = self._get_plugin_and_config(dev)
        if plugin is not None:
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
        self._check_valid_dev(dev)
        if dev_id is None:
            dev_id = self._dev_id_gen.next_id(self.dev_mgr)
            assert dev_id not in self.dev_mgr
        elif dev_id in self.dev_mgr:
            raise UsedIdError(dev_id)
        self.dev_mgr[dev_id] = dev
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
        try:
            dev = self.dev_mgr[dev_id]
        except KeyError:
            raise UnusedIdError(dev_id)
        else:
            self._deconfigure_dev(dev)
            
    def synchronize_dev(self, dev_id):
        """Force the device to synchronize it's configuration."""
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
        self._check_valid_cfg(cfg)
        if cfg_id is None:
            cfg_id = self._cfg_id_gen.next_id(self.cfg_mgr)
            assert cfg_id not in self.cfg_mgr
        elif cfg_id in self.cfg_mgr:
            raise UsedIdError(cfg_id)
        self.cfg_mgr[cfg_id] = cfg
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
    
    def _load_pg(self, pg_id):
        gen_cfg = self._config['general']
        spec_cfg = self._config.get('pluginconfig_' + pg_id, {})
        self.pg_mgr.load(pg_id, gen_cfg, spec_cfg)
    
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
        if not self.pg_mgr.is_installed(pg_id):
            raise Exception("plugin '%s' is not already installed" % pg_id)
        
        # XXX we probably want to cheeck that the plugin is 'really' upgradeable
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
        if not self.pg_mgr.is_installed(pg_id):
            raise Exception("plugin '%s' is not already installed" % pg_id)
        if not self._is_plugin_unused(pg_id):
            raise Exception("plugin '%s' is used by at least a device" % pg_id)
        
        self.pg_mgr.uninstall(pg_id)
        self.pg_mgr.unload(pg_id)


from twisted.internet import reactor

app = Application()
atexit.register(app.close)
#sys.exit()

cfg_mgr = app.cfg_mgr
dev_mgr = app.dev_mgr
pg_mgr = app.pg_mgr

# Create some config
# a 'base' configuration
xivo_ip = '192.168.33.4'
base_cfg = {
    'prov_ip': '192.168.33.1',
    'prov_http_port': '8080',
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

cfg_mgr['base'] = (base_cfg, [])
cfg_mgr['guest'] = (guest_cfg, ['base'])
cfg_mgr['dev1'] = (dev1_cfg, ['base'])

# fake configure a device with aastra plugin
#def new_fake_params(prefix, param_names):
#    return dict((name, prefix + name) for name in param_names)
#line_1 = new_fake_params('fake_',
#                         ['proxy_ip', 'registrar_ip', 'backup_proxy_ip', 'backup_registrar_ip',
#                          'display_name', 'user_id', 'auth_id', 'passwd'])
#cfg_base = new_fake_params('bfake_', ['subscribe_mwi'])
#cfg_base.update({'exten': new_fake_params('fake', ['pickup_prefix', 'voicemail', 'fwdunc', 'dnd']),
#                 'funckey': {1: {'exten': 4000, 'supervision': False, 'label': 'fake_label', 'line': 1}}})
#cfg_spec = {'sip': {'lines': {1: line_1}, 'dtmfmode': 'fake_dtmfmode'},
#            'timezone': 'America/Montreal', 'locale': 'fr_CA'}
#cfg_manager = {'base': (cfg_base, []),
#               'spec': (cfg_spec, ['base'])}
#flat_cfg = flatten_config(cfg_manager, 'spec')
#fake_dev = {'mac': '\x00' * 6, 'ip': '\x00' * 4, 'vendor': 'Aastra',
#            'model': '6731i', 'version': '2.6.0.1008'}
#pg_aastra.configure(fake_dev, flat_cfg)
#sys.exit()


# update the plugin definition file
#println(list(pg_mgr.list_installable()))
#pop = pg_mgr.update()
#pop.deferred.addCallback(lambda _: println(list(pg_mgr.list_installable())))
#pop.deferred.addBoth(lambda _: reactor.stop())
#pm_mgr.uninstall('xivo-aastra-2.6.0.1008')
#reactor.callLater(15, reactor.stop)
#reactor.run()
#sys.exit()

# uninstall the xivo-aastra-plugin
#print pg_mgr.items()
#app.uninstall_pg('xivo-aastra-2.6.0.1008')
#sys.exit()

# install the xivo-aastra plugin
#println(list(pg_mgr.list_installed()))
#pop = app.install_pg('xivo-aastra-2.6.0.1008')
#pop.deferred.addCallback(lambda _: println(list(pg_mgr.list_installed())))
#pop.deferred.addBoth(lambda _: println(pop.status))
#pop.deferred.addBoth(lambda _: reactor.stop())
#reactor.callLater(15, reactor.stop)
#reactor.run()
#sys.exit()

def metaaff(prefix):
    def aff(message):
        print prefix, message
    return aff

dhcpinfo_res = DHCPInfoResource()

#http_xtors = [xtor for xtor in map(lambda p: p.http_dev_info_extractor, plugins) if
#              xtor is not None]
#tftp_xtors = [xtor for xtor in map(lambda p: p.tftp_dev_info_extractor, plugins) if
#              xtor is not None]
#http_xtor = LongestDeviceInfoExtractor(http_xtors)
#tftp_xtor = LongestDeviceInfoExtractor(tftp_xtors)
#request_dependant_xtor = TypeBasedDeviceInfoExtractor({'http': http_xtor, 'tftp': tftp_xtor})
all_pg_xtor = AllPluginsDeviceInfoExtractor(LongestDeviceInfoExtractor, pg_mgr)
dhcp_xtor = DHCPDeviceInfoExtractor(dhcpinfo_res.dhcp_infos, all_pg_xtor)
collab_xtor = CollaboratingDeviceInfoExtractor(VotingUpdater, [dhcp_xtor, all_pg_xtor])
root_xtor = collab_xtor

mac_retriever = MacDeviceRetriever()
ip_retriever = IpDeviceRetriever()
add_retriever = AddDeviceRetriver()
cmpz_retriever = FirstCompositeDeviceRetriever([mac_retriever, add_retriever])
root_retriever = cmpz_retriever

guest_cfg_updater = StaticDeviceUpdater('config', 'guest')
pg_sstor_solver = AlphabeticConflictSolver()
pg_auto_updater = PluginAssociatorDeviceUpdater(pg_mgr, pg_sstor_solver)
zero_pg_updater = StaticDeviceUpdater('plugin', 'zero')
class MyWeirdDeviceUpdater():
    def update(self, dev, dev_info, request, request_type):
        if request_type == 'http' and request.path.endswith('aastra.cfg'):
            nb_req = dev.get('x-nb_req', 0)
            last_update = dev.get('x-last_up', 0)
            now = time.time()
            if now - last_update > 120:
                nb_req += 1
                dev['x-nb_req'] = nb_req
                dev['x-last_up'] = now
                if nb_req % 2 == 0:
                    dev['config'] = 'dev1'
                else:
                    dev['config'] = 'guest'
                return True
            else:
                return False
        return False
weird_updater = MyWeirdDeviceUpdater()
add_info_updater = AddInfoDeviceUpdater()
every_updater = EverythingDeviceUpdater()
cmpz_updater = CompositeDeviceUpdater([add_info_updater, guest_cfg_updater, pg_auto_updater])
root_updater = cmpz_updater

pg_router = PluginDeviceRouter()
static_router = StaticDeviceRouter('test-pull-dyn')
root_router = pg_router

process_service = RequestProcessingService(app)
process_service.dev_info_extractor = root_xtor
process_service.dev_retriever = root_retriever
process_service.dev_updater = root_updater
process_service.dev_router = root_router


def tftp_service_factory(pg_id, pg_service):
    return TFTPLogService(metaaff('tftp-post ' + pg_id + ':'), pg_service)
    
# tftp
def new_tftp_service():
    tftp_process_service = TFTPRequestProcessingService(process_service, pg_mgr)
    tftp_process_service.service_factory = tftp_service_factory
    preprocess_service = TFTPLogService(metaaff('tftp-pre:'), tftp_process_service)

    return preprocess_service

tftp_service = new_tftp_service()


def http_service_factory(pg_id, pg_service):
    return HTTPLogService(metaaff('http-post ' + pg_id + ':'), pg_service)

# http
def new_http_service():
    http_process_service = HTTPRequestProcessingService(process_service, pg_mgr)
    http_process_service.service_factory = http_service_factory
    preprocess_service = HTTPLogService(metaaff('http-pre:'), http_process_service)
    
    return preprocess_service

http_service = new_http_service()
http_site = Site(http_service)


root = Resource()

dev_res = DevicesResource(app)
dev_reload_res = DeviceSynchronizeResource(app)
root.putChild('devices', dev_res)
root.putChild('dev_sync', dev_reload_res)
root.putChild('dhcpinfo', dhcpinfo_res)

cfg_res = ConfigsResource(app)
root.putChild('configs', cfg_res)

pg_config_res = PluginMgrConfigureResource(pg_mgr)
pg_update_res = PluginMgrUpdateResource(pg_mgr)
pg_list_able_res = PluginMgrListInstallableResource(pg_mgr)
pg_list_ed_res = PluginMgrListInstalledResource(pg_mgr)
pg_list_upgradeable_res = PluginMgrListUpgradeableResource(pg_mgr)
pg_install_res = PluginMgrInstallResource(app)
pg_upgrade_res = PluginMgrUpgradeResource(app)
pg_uninstall_res = PluginMgrUninstallRecourse(app)
pg_plugins_res = PluginsResource(pg_mgr)
pg_mgr_res = Resource()
pg_mgr_res.putChild('config', pg_config_res)
pg_mgr_res.putChild('update', pg_update_res)
pg_mgr_res.putChild('installable', pg_list_able_res)
pg_mgr_res.putChild('installed', pg_list_ed_res)
pg_mgr_res.putChild('upgradeable', pg_list_upgradeable_res)
pg_mgr_res.putChild('install', pg_install_res)
pg_mgr_res.putChild('upgrade', pg_upgrade_res)
pg_mgr_res.putChild('uninstall', pg_uninstall_res)
pg_mgr_res.putChild('plugins', pg_plugins_res)
root.putChild('pg_mgr', pg_mgr_res)

class DebugResource(Resource):
    def render_GET(self, request):
        le_app = app
        print id(le_app)
        return ""
root.putChild('debug', DebugResource())
rest_site = Site(root)


from twisted.python import log
log.startLogging(sys.stdout)

reactor.listenUDP(6969, TFTPProtocol(tftp_service))
reactor.listenTCP(8080, http_site)
reactor.listenTCP(8081, rest_site)
reactor.run()
