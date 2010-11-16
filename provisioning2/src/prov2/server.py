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

import sys
from ConfigParser import RawConfigParser
from pprint import pprint
from prov2.plugins import PluginManager
from prov2.servers.tftp.service import TFTPLogService
from prov2.devices.device import DeviceManager
from prov2.servers.tftp.proto import TFTPProtocol
from prov2.servers.http import HTTPLogService
from prov2.devices.ident import *
from prov2.devices.config import flatten_config
from twisted.web.server import Site


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
#sys.exit(1)

# create config dicts
plugin_config = {}
for section in config:
    if section.startswith('pluginconfig_'):
        pg_name = section[len('pluginconfig_'):]
        plugin_config[pg_name] = config[section]

# load all plugins
#print plugin_config
plugins = list(pm.load_all(config['general'], plugin_config))
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
print pg_aastra.services()
list_ed_srv = pg_aastra.services()['list_installed']
list_able_srv = pg_aastra.services()['list_installable']
print list(list_ed_srv())
print list(list_able_srv())
#pg_aastra.services()['install']('aastra-6731i', 'aastra-6757i')
#sys.exit()

# configure a device with aastra plugin
def new_fake_params(prefix, param_names):
    return dict((name, prefix + name) for name in param_names)
line_1 = new_fake_params('fake_',
                         ['proxy_ip', 'registrar_ip', 'backup_proxy_ip', 'backup_registrar_ip',
                          'display_name', 'user_id', 'auth_id', 'passwd'])
cfg_base = new_fake_params('bfake_', ['subscribe_mwi'])
cfg_base.update({'exten': new_fake_params('fake', ['pickup_prefix', 'voicemail', 'fwdunc', 'dnd']),
                 'funckey': {1: {'exten': 4000, 'supervision': False, 'label': 'fake_label', 'line': 1}}})
cfg_spec = {'sip': {'lines': {1: line_1}, 'dtmfmode': 'fake_dtmfmode'},
            'timezone': 'America/Montreal', 'locale': 'fr_CA'}
cfg_manager = {'base': (cfg_base, []),
               'spec': (cfg_spec, ['base'])}
flat_cfg = flatten_config(cfg_manager, 'spec')
fake_dev = {'mac': '\x00' * 6, 'ip': '\x00' * 4, 'vendor': 'Aastra',
            'model': '6731i', 'version': '2.6.0.1008'}
pg_aastra.configure(fake_dev, flat_cfg)
sys.exit()

# create a device manager
device_mgr = DeviceManager()

def metaaff(prefix):
    def aff(message):
        print prefix, message
    return aff

# tftp
def new_tftp_service():
    services_map = {}
    for pg in plugins:
        pg_service = pg.tftp_service()
        services_map[pg.name] = TFTPLogService(metaaff('tftp-pre-pg ' + pg.name + ':'), pg_service)
         
    routing_service = TFTPDeviceBasedRoutingService(device_mgr, services_map)
    routing_service = TFTPLogService(metaaff('tftp-pre-route:'), routing_service)
        
    devi_extractor = FirstCompositeDeviceInfoExtractor()
    devi_extractor.extractors.extend(ifier for pg in plugins for ifier in pg.tftp_dev_info_extractors())
    
    pg_associator = FirstCompositePluginAssociator()
    map_associator = StandardMappingPluginAssociator()
    for pg in plugins:
        map_associator.add_plugin(pg)
    pg_associator.associators.append(map_associator.associate)
    pg_associator.associators.append(StaticPluginAssociator('zero').associate)
    
    ident_service = IdentificationService(devi_extractor.extract_info, retrieve_device_from_ip, device_mgr, tftp_ip_extractor, pg_associator.associate)
    ident_service.auto_create = True
    ident_service.auto_create_no_dev_info = True
    tftp_ident_service = TFTPIdentificationService(ident_service, routing_service)
    tftp_ident_service = TFTPLogService(metaaff('tftp-pre-ident:'), tftp_ident_service)
    
    return tftp_ident_service

tftp_service = new_tftp_service()


# http
def new_http_service():
    services_map = {}
    for pg in plugins:
        pg_service = pg.http_service()
        services_map[pg.name] = HTTPLogService(metaaff('http-pre-pg ' + pg.name + ':'), pg_service)
    
    routing_service = HTTPDeviceBasedRoutingService(device_mgr, services_map)
    routing_service = HTTPLogService(metaaff('http-pre-route:'), routing_service)
    
    devi_extractor = FirstCompositeDeviceInfoExtractor()
    devi_extractor.extractors.extend(ifier for pg in plugins for ifier in pg.http_dev_info_extractors())
    
    pg_associator = FirstCompositePluginAssociator()
    map_associator = StandardMappingPluginAssociator()
    for pg in plugins:
        map_associator.add_plugin(pg)
    pg_associator.associators.append(map_associator.associate)
    pg_associator.associators.append(StaticPluginAssociator('zero').associate)
    
    ident_service = IdentificationService(devi_extractor.extract_info, retrieve_device_from_ip, device_mgr, http_ip_extractor, pg_associator.associate)
    ident_service.auto_create = True
    ident_service.auto_create_no_dev_info = True
    identification_service = HTTPIdentificationService(ident_service, routing_service)
    identification_service = HTTPLogService(metaaff('http-pre-ident:'), identification_service)
    
    return identification_service

http_service = new_http_service()
http_site = Site(http_service)

from twisted.internet import reactor
reactor.listenUDP(6969, TFTPProtocol(tftp_service))
reactor.listenTCP(8080, http_site)
reactor.run()
