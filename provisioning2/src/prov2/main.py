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

import time
import sys
from ConfigParser import RawConfigParser
from pprint import pprint
from prov2.devices.ident import *
from prov2.servers.tftp.service import TFTPLogService
from prov2.servers.tftp.proto import TFTPProtocol
from prov2.servers.http import HTTPLogService
from prov2.servers.http_site import Site
from prov2.devices.config import ConfigManager
from prov2.devices.device import DeviceManager
from prov2.devices.util import simple_id_generator
from prov2.plugins import PluginManager
from prov2.rest.server import RestService, DevicesResource,\
    ConfigsResource, DeviceReconfigureResource, DeviceReloadResource


CONFIG_FILENAME = '../../test-resources/etc/prov2.conf'

def read_config(filename=CONFIG_FILENAME):
    config = RawConfigParser()
    with open(filename, 'r') as fobj:
        config.readfp(fobj)
    
    # XXX right now, we only transform the RawConfigParser object to
    # a more manipulable mapping of mapping object
    result = {'plugins': {'plugins_dir': '/var/lib/pf-xivo/prov2/plugins'}}
    for section in config.sections():
        in_result = result.setdefault(section, {})
        for option in config.options(section):
            in_result[option] = config.get(section, option)
    
    # check if every mandatory options are specified
    mandatory = {'plugins': ['server']}
    for section in mandatory:
        if section not in result:
            raise ValueError('mandatory section "%s" not specified' % section)
        in_result = result[section]
        for option in mandatory[section]:
            if option not in in_result:
                raise ValueError('mandatory option "%s" in section "%s" not specified' %
                                 (option, section))
    return result

config = read_config()
#print config


#plugins_dir = '../../plugins'
#pm = PluginManager(plugins_dir, 'http://127.0.0.1:8000/')
pm = PluginManager(config['plugins']['plugins_dir'], config['plugins']['server'])

#pm.update()
#print list(pm.list_installable())
#pm.install('xivo-aastra-2.6.0.1008')
#pm.upgrade()
#pm.uninstall('xivo-aastra-2.6.0.1008')
#print list(pm.list_installed())
#sys.exit()

# create config dicts
plugin_config = {}
for section in config:
    if section.startswith('pluginconfig_'):
        pg_name = section[len('pluginconfig_'):]
        plugin_config[pg_name] = config[section]

# load all plugins
#print plugin_config
plugins = list(pm.load_all(config['general'], plugin_config))
pg_map = dict((pg.name, pg) for pg in plugins)
#pprint(plugins)
#sys.exit()

# install aastra plugin
for pg in plugins:
    if pg.name.startswith('xivo-aastra'):
        pg_aastra = pg
        break
else:
    print >>sys.stderr, "no aastra plugin"
    sys.exit(1)
#print pg_aastra.services()
list_ed_srv = pg_aastra.services()['list_installed']
list_able_srv = pg_aastra.services()['list_installable']
#print list(list_ed_srv())
#print list(list_able_srv())
#pg_aastra.services()['install']('aastra-6731i', 'aastra-6757i')
#sys.exit()


# a 'base' configuration
xivo_ip = '192.168.33.4'
prov_ip = '192.168.33.1'
prov_http_port = '8080'
base_cfg = {
    'prov_ip': prov_ip,
    'prov_http_port': prov_http_port,
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

# common configure of the aastra plugin
cfg_mgr = ConfigManager()
cfg_mgr['base'] = (base_cfg, [])
cfg_mgr['guest'] = (guest_cfg, ['base'])
cfg_mgr['dev1'] = (dev1_cfg, ['base'])
#pg_aastra.configure_common(cfg_mgr.flatten('base'))
#fake_dev = {'mac': '\x00' * 6, 'ip': '\x00' * 4, 'vendor': 'Aastra',
#            'model': '6731i', 'version': '2.6.0.2010'}
#pg_aastra.configure(fake_dev, cfg_mgr.flatten('dev1'))
#sys.exit()

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

# create a device manager
dev_mgr = DeviceManager(simple_id_generator())

def metaaff(prefix):
    def aff(message):
        print prefix, message
    return aff


http_xtors = [xtor for pg in plugins for xtor in pg.http_dev_info_extractors()]
tftp_xtors = [xtor for pg in plugins for xtor in pg.tftp_dev_info_extractors()]
http_xtor = LongestDeviceInfoExtractor(http_xtors)
tftp_xtor = LongestDeviceInfoExtractor(tftp_xtors)
request_dependant_xtor = TypeBasedDeviceInfoExtractor({'http': http_xtor, 'tftp': tftp_xtor})
root_xtor = request_dependant_xtor

ip_retriever = IpDeviceRetriever()
add_retriever = AddDeviceRetriver()
cmpz_retriever = FirstCompositeDeviceRetriever([ip_retriever, add_retriever])
root_retriever = cmpz_retriever

static_cfg_updater = StaticDeviceUpdater('config', 'guest')
pg_updater = MappingPluginDeviceUpdater()
for pg in plugins:
    pg_updater.add_plugin(pg)
static_pg_updater = StaticDeviceUpdater('plugin', 'zero')
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
every_updater = EverythingDeviceUpdater()
cmpz_updater = CompositeDeviceUpdater([static_cfg_updater, pg_updater, static_pg_updater, weird_updater])
root_updater = cmpz_updater

process_service = RequestProcessingService(dev_mgr, cfg_mgr, pg_map)
process_service.dev_info_extractor = root_xtor
process_service.dev_retriever = root_retriever
process_service.dev_updater = root_updater


# tftp
def new_tftp_service():
    postprocess_service_map = {}
    for pg in plugins:
        pg_service = pg.tftp_service()
        postprocess_service_map[pg.name] = TFTPLogService(metaaff('tftp-post ' + pg.name + ':'), pg_service)
    
    tftp_process_service = TFTPRequestProcessingService(process_service, postprocess_service_map)
    preprocess_service = TFTPLogService(metaaff('tftp-pre:'), tftp_process_service)

    return preprocess_service

tftp_service = new_tftp_service()


# http
def new_http_service():
    postprocess_service_map = {}
    for pg in plugins:
        pg_service = pg.http_service()
        postprocess_service_map[pg.name] = HTTPLogService(metaaff('http-post ' + pg.name + ':'), pg_service)
    
    http_process_service = HTTPRequestProcessingService(process_service, postprocess_service_map)
    preprocess_service = HTTPLogService(metaaff('http-pre:'), http_process_service)
    
    return preprocess_service

http_service = new_http_service()
http_site = Site(http_service)


service = RestService(cfg_mgr, dev_mgr, pg_map)
dev_res = DevicesResource(service)
cfg_res = ConfigsResource(service)
dev_configure_res = DeviceReconfigureResource(service)
dev_reload_res = DeviceReloadResource(service)
root = Resource()
root.putChild('devices', dev_res)
root.putChild('dev_reconfigure', dev_configure_res)
root.putChild('dev_reload', dev_reload_res)
root.putChild('configs', cfg_res)
rest_site = Site(root)


from twisted.python import log
log.startLogging(sys.stdout)

from twisted.internet import reactor
reactor.listenUDP(6969, TFTPProtocol(tftp_service))
reactor.listenTCP(8080, http_site)
reactor.listenTCP(8081, rest_site)
reactor.run()
