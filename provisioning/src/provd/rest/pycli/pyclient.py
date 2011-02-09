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

from provd.rest.client.client import new_provisioning_client

# XXX catch exception in wrapper class and print meaningful message to
#     stdout/stderr
# TODO complete

_DEFAULT_BACKGROUND = False
_CATCH_EXCEPTION = True


class ProvisioningClient(object):
    def __init__(self, prov_client):
        self._prov_client = prov_client
    
    @property
    def config_manager(self):
        return self._prov_client.config_manager()
    
    @property
    def device_manager(self):
#        return DeviceManager(self._prov_client.device_manager())
        return self._prov_client.device_manager()
    
    @property
    def plugin_manager(self):
        return self._prov_client.plugin_manager()


class ConfigManager(object):
    def __init__(self, cfg_mgr):
        self._cfg_mgr = cfg_mgr
    
    def find(self, selector={}):
        return self._cfg_mgr.find(selector)
    
    def __getattr__(self, name):
        return getattr(self._cfg_mgr, name)


class DeviceManager(object):
    def __init__(self, dev_mgr):
        self._dev_mgr = dev_mgr
    
    def synchronize(self, id, background=_DEFAULT_BACKGROUND):
        # TODO complete...
        pass
    
    def reconfigure(self, id):
        pass
    
    def add(self, device):
        pass
    
    def get(self, device):
        pass
    
    def update(self, device):
        pass
    
    def remove(self, device):
        pass
    
    def find(self, selector):
        pass


def new_pycli_provisioning_client(server_uri, credentials):
    prov_client = new_provisioning_client(server_uri, credentials)
    return ProvisioningClient(prov_client)

