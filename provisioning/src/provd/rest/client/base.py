# -*- coding: UTF-8 -*-

"""Low-level client for the REST API of the provisioning server. This is
not made to be used directly, but as a base to build for 'higher-level'
client.

Note that arguments should be unicode strings instead of byte strings when
applicable. That said, that's not because we're using unicode string that
some characters are accepted (for example, most ID are still restricted
to characters available in ASCII).

"""

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

# XXX this implementation use undocumented URI templates, so it's supposed
#     to be more fragile vs an implementation using standard HTTP mechanism
#     with cache to speed up the whole thing. That said, cache management
#     and everything around it seems like a high cost to pay, especially
#     since twisted doesn't offer anything special for this... this might
#     eventually evolve, yet this has to be seen...

import urllib
import urllib2
import urlparse
import json
from provd.rest.client.util import once_per_instance, DeleteRequest,\
    PutRequest, No2xxErrorHTTPErrorProcessor
from provd.rest.util import PROV_MIME_TYPE, uri_append_path, uri_append_query

GET_HEADERS  = {'Accept': PROV_MIME_TYPE}
POST_HEADERS = {'Accept': PROV_MIME_TYPE, 'Content-Type': PROV_MIME_TYPE}


def new_get_request(uri):
    return urllib2.Request(uri, None, GET_HEADERS)


def new_post_request(uri, obj):
    data = json.dumps(obj)
    return urllib2.Request(uri, data, POST_HEADERS)


def new_put_request(uri, obj):
    data = json.dumps(obj)
    return PutRequest(uri, data, POST_HEADERS)


def new_delete_request(uri):
    return DeleteRequest(uri, None, GET_HEADERS)


class RequestBroker(object):
    def __init__(self, opener):
        self._opener = opener
    
    def json_content(self, request):
        # send the request, parse the response as json, and return a tuple
        # (decoded json object, response headers)
        f = self._opener.open(request)
        try:
            obj = json.load(f)
        finally:
            f.close()
        return obj, f.info()
    
    def ignore_content(self, request):
        # send the request, ignore the response and return a tuple
        # (None, response headers)
        f = self._opener.open(request)
        try:
            f.read()
        finally:
            f.close()
        return None, f.info()
    
    def raw_content(self, request):
        # send the request, read the response and return a tuple
        # (raw data, response headers)
        f = self._opener.open(request)
        try:
            data = f.read()
        finally:
            f.close()
        return data, f.info()


class OperationInProgressResource(object):
    def __init__(self, op_in_progress_uri, broker):
        self._uri = op_in_progress_uri
        self._broker = broker
    
    def status(self):
        request = new_get_request(self._uri)
        response, _ = self._broker.json_content(request)
        return response[u'status']
    
    def delete(self):
        request = new_delete_request(self._uri)
        self._broker.ignore_content(request)


class ConfigureServiceResource(object):
    def __init__(self, config_uri, broker):
        self._config_uri = config_uri
        self._broker = broker
    
    def get(self, id):
        param_uri = uri_append_path(self._config_uri, id)
        return ConfigureParameterResource(param_uri, self._broker)
    
    def parameters(self):
        """Return a dictionary where each keys are parameter name and values
        are description of the parameter.
        
         """
        request = new_get_request(self._config_uri)
        response, _ = self._broker.json_content(request)
        result = {}
        for param_id, param_info in response[u'params'].iteritems():
            result[param_id] = param_info[u'description']
        return result


class ConfigureParameterResource(object):
    def __init__(self, param_uri, broker):
        self._param_uri = param_uri
        self._broker = broker
    
    def get(self):    
        request = new_get_request(self._param_uri)
        response, _ = self._broker.json_content(request)
        return response[u'param'][u'value']
    
    def _build_set_request(self, value):
        content = {u'param': {u'value': value}}
        return new_put_request(self._param_uri, content)
    
    def set(self, value):
        request = self._build_set_request(value)
        self._broker.ignore_content(request)
    

class InstallServiceResource(object):
    def __init__(self, install_uri, broker):
        self._create_sub_resources(install_uri, broker)
    
    def _create_sub_resources(self, install_srv_uri, broker):
        install_uri = uri_append_path(install_srv_uri, 'install')
        self._install_res = InstallResource(install_uri, broker)
        
        uninstall_uri = uri_append_path(install_srv_uri, 'uninstall')
        self._uninstall_res = UninstallResource(uninstall_uri, broker)
        
        installed_uri = uri_append_path(install_srv_uri, 'installed')
        self._installed_res = InstalledResource(installed_uri, broker)
        
        installable_uri = uri_append_path(install_srv_uri, 'installable')
        self._installable_res = InstallableResource(installable_uri, broker)
        
        upgrade_uri = uri_append_path(install_srv_uri, 'upgrade')
        self._upgrade_res = UpgradeResource(upgrade_uri, broker)
        
        update_uri = uri_append_path(install_srv_uri, 'update')
        self._update_res = UpdateResource(update_uri, broker)
        
    def install_res(self):
        return self._install_res
    
    def uninstall_res(self):
        return self._uninstall_res
    
    def installed_res(self):
        return self._installed_res
    
    def installable_res(self):
        return self._installable_res
    
    def upgrade_res(self):
        return self._upgrade_res
    
    def update_res(self):
        return self._update_res


class InstallResource(object):
    def __init__(self, install_uri, broker):
        self._install_uri = install_uri
        self._broker = broker
    
    def install(self, id):
        """Install the package with the given ID and return an
        OperationInProgress resource.
        
        """
        content = {u'id': id}
        request = new_post_request(self._install_uri, content)
        # XXX do not handle the 303 case correctly
        _, headers = self._broker.ignore_content(request)
        op_in_progress_uri = urlparse.urljoin(self._install_uri, headers['Location'])
        return OperationInProgressResource(op_in_progress_uri, self._broker)


class UninstallResource(object):
    def __init__(self, uninstall_uri, broker):
        self._uninstall_uri = uninstall_uri
        self._broker = broker
    
    def uninstall(self, id):
        """Uninstall the package with the given ID."""
        content = {u'id': id}
        request = new_post_request(self._uninstall_uri, content)
        self._broker.ignore_content(request)


class InstalledResource(object):
    def __init__(self, installed_uri, broker):
        self._installed_uri = installed_uri
        self._broker = broker
    
    def installed(self):
        """Return a dictionary of installed package, where keys are package
        IDs and value are dictionary giving info about the package.
        
        """
        request = new_get_request(self._installed_uri)
        response, _ = self._broker.json_content(request)
        return response[u'pkgs']


class InstallableResource(object):
    def __init__(self, installable_uri, broker):
        self._installable_uri = installable_uri
        self._broker = broker
    
    def installable(self):
        """Similar to InstalledResource.installed()."""
        request = new_get_request(self._installable_uri)
        response, _ = self._broker.json_content(request)
        return response[u'pkgs']


class UpgradeResource(object):
    def __init__(self, upgrade_uri, broker):
        self._upgrade_uri = upgrade_uri
        self._broker = broker
    
    def upgrade(self, id):
        """Upgrade the package with the given ID and return an
        OperationInProgress resource.
        
        """
        content = {u'id': id}
        request = new_post_request(self._upgrade_uri, content)
        # XXX do not handle the 303 case correctly
        _, headers = self._broker.ignore_content(request)
        op_in_progress_uri = urlparse.urljoin(self._upgrade_uri, headers['Location'])
        return OperationInProgressResource(op_in_progress_uri, self._broker)


class UpdateResource(object):
    def __init__(self, update_uri, broker):
        self._update_uri = update_uri
        self._broker = broker
    
    def update(self):
        request = new_post_request(self._update_uri, {})
        _, headers = self._broker.ignore_content(request)
        # XXX do not handle the 303 case correctly
        op_in_progress_uri = urlparse.urljoin(self._update_uri, headers['Location'])
        return OperationInProgressResource(op_in_progress_uri, self._broker)


class ServerResource(object):
    def __init__(self, server_uri, broker):
        self._broker = broker
        self._server_uri = server_uri
        self._create_sub_resources()
    
    def _create_sub_resources(self):
        dev_mgr_uri = uri_append_path(self._server_uri, 'dev_mgr')
        self._dev_mgr = DeviceManagerResource(dev_mgr_uri, self._broker)
        
        cfg_mgr_uri = uri_append_path(self._server_uri, 'cfg_mgr')
        self._cfg_mgr = ConfigManagerResource(cfg_mgr_uri, self._broker)

        pg_mgr_uri = uri_append_path(self._server_uri, 'pg_mgr')
        self._pg_mgr = PluginManagerResource(pg_mgr_uri, self._broker)
    
    def dev_mgr_res(self):
        return self._dev_mgr
    
    def cfg_mgr_res(self):
        return self._cfg_mgr
    
    def pg_mgr_res(self):
        return self._pg_mgr
    
    def test_connectivity(self):
        # raise an exception if there seems to be connectivity issues
        request = new_get_request(self._server_uri)
        self._broker.ignore_content(request)


class DeviceManagerResource(object):
    def __init__(self, dev_mgr_uri, broker):
        self._create_sub_resources(dev_mgr_uri, broker)
    
    def _create_sub_resources(self, dev_mgr_uri, broker):
        resync_uri = uri_append_path(dev_mgr_uri, 'synchronize')
        self._resync_res = DeviceSynchronizeResource(resync_uri, broker)
        
        reconfigure_uri = uri_append_path(dev_mgr_uri, 'reconfigure')
        self._reconfigure_res = DeviceReconfigureResource(reconfigure_uri, broker)
        
        devices_uri = uri_append_path(dev_mgr_uri, 'devices')
        self._devices_res = DevicesResource(devices_uri, broker)
    
    def resync_res(self):
        return self._resync_res
    
    def reconfigure_res(self):
        return self._reconfigure_res
    
    def devices_res(self):
        return self._devices_res
    

class DeviceSynchronizeResource(object):
    def __init__(self, resync_uri, broker):
        self._resync_uri = resync_uri
        self._broker = broker
    
    def _build_resync_request(self, id):
        content = {u'id': id}
        return new_post_request(self._resync_uri, content)
    
    def resync(self, id):
        """Resynchronize the device with the given ID and return an
        OperationInProgress ressource.
        
        """
        request = self._build_resync_request(id)
        _, headers = self._broker.ignore_content(request)
        op_in_progress_uri = urlparse.urljoin(self._resync_uri, headers['Location'])
        return OperationInProgressResource(op_in_progress_uri, self._broker)


class DeviceReconfigureResource(object):
    def __init__(self, reconf_uri, broker):
        self._reconf_uri = reconf_uri
        self._broker = broker
    
    def _build_reconf_request(self, id):
        content = {u'id': id}
        return new_post_request(self._reconf_uri, content)
    
    def reconfigure(self, id):
        """Reconfigure the device with the given ID."""
        request = self._build_reconf_request(id)
        self._broker.ignore_content(request)


class DevicesResource(object):
    def __init__(self, devices_uri, broker):
        self._devices_uri = devices_uri
        self._broker = broker
    
    def _build_add_request(self, device):
        content = {u'device': device}
        return new_post_request(self._devices_uri, content)
    
    def add(self, device):
        """Add a device and return the ID of the newly added device."""
        request = self._build_add_request(device)
        response, _ = self._broker.json_content(request)
        return response[u'id']
    
    def _build_find_request(self, selector):
        if selector:
            query = urllib.urlencode(selector)
            uri = uri_append_query(self._devices_uri, query)
        else:
            uri = self._devices_uri
        return new_get_request(uri)
    
    def find(self, selector):
        """Return a list of device ID matching the selector.
        
        selector can only be 'simple' selector, where keys and values are
        only strings.
        
        """
        request = self._build_find_request(selector)
        response, _ = self._broker.json_content(request)
        ids = list(response[u'devices'].iterkeys())
        return ids
    
    def device_res(self, id):
        device_uri = uri_append_path(self._devices_uri, id)
        return DeviceResource(device_uri, self._broker)


class DeviceResource(object):
    def __init__(self, device_uri, broker):
        self._device_uri = device_uri
        self._broker = broker
    
    def _build_get_request(self):
        return new_get_request(self._device_uri)
    
    def get(self):
        """Return a device object (i.e. a dictionary)."""
        request = self._build_get_request()
        response, _ = self._broker.json_content(request)
        return response[u'device']
    
    def _build_update_request(self, device):
        content = {u'device': device}
        return new_put_request(self._device_uri, content)
    
    def update(self, device):
        """Update the remote device with the given device.
        
        Note that it's an error if device has no or a different ID.
        
        """
        request = self._build_update_request(device)
        self._broker.ignore_content(request)
    
    def _build_delete_request(self):
        return new_delete_request(self._device_uri)
    
    def delete(self):
        request = self._build_delete_request()
        self._broker.ignore_content(request)


class ConfigManagerResource(object):
    def __init__(self, cfg_mgr_uri, broker):
        self._create_sub_resources(cfg_mgr_uri, broker)
    
    def _create_sub_resources(self, cfg_mgr_uri, broker):
        configs_uri = uri_append_path(cfg_mgr_uri, 'configs')
        self._configs_res = ConfigsResource(configs_uri, broker)
    
    def configs_res(self):
        return self._configs_res


class ConfigsResource(object):
    def __init__(self, configs_uri, broker):
        self._configs_uri = configs_uri
        self._broker = broker
    
    def _build_add_request(self, config):
        content = {u'config': config}
        return new_post_request(self._configs_uri, content)
    
    def add(self, config):
        """Add a config and return the ID of the newly added config."""
        request = self._build_add_request(config)
        response, _ = self._broker.json_content(request)
        return response[u'id']
    
    def _build_find_request(self, selector):
        if selector:
            query = urllib.urlencode(selector)
            uri = uri_append_query(self._configs_uri, query)
        else:
            uri = self._configs_uri
        return new_get_request(uri)
    
    def find(self, selector):
        """Return a list of config ID matching the selector."""
        request = self._build_find_request(selector)
        response, _ = self._broker.json_content(request)
        ids = list(response[u'configs'].iterkeys())
        return ids
    
    def config_res(self, id):
        config_uri = uri_append_path(self._configs_uri, id)
        return ConfigResource(config_uri, self._broker)
    
    def raw_config_res(self, id):
        raw_config_uri = uri_append_path(self._configs_uri, id, 'raw')
        return RawConfigResource(raw_config_uri, self._broker)
    

class ConfigResource(object):
    def __init__(self, config_uri, broker):
        self._config_uri = config_uri
        self._broker = broker
    
    def _build_get_request(self):
        return new_get_request(self._config_uri)
    
    def get(self):
        request = self._build_get_request()
        response, _ = self._broker.json_content(request)
        return response[u'config']
    
    def _build_update_request(self, config):
        content = {u'config': config}
        return new_put_request(self._config_uri, content)
    
    def update(self, config):
        """Update the remote config with the given config.
        
        Note that it's an error if config has no or a different ID.
        
        """
        request = self._build_update_request(config)
        self._broker.ignore_content(request)
    
    def _build_delete_request(self):
        return new_delete_request(self._config_uri)
    
    def delete(self):
        request = self._build_delete_request()
        self._broker.ignore_content(request)


class RawConfigResource(object):
    def __init__(self, raw_config_uri, broker):
        self._raw_config_uri = raw_config_uri
        self._broker = broker
    
    def _build_get_request(self):
        return new_get_request(self._raw_config_uri)
    
    def get(self):
        request = self._build_get_request()
        response, _ = self._broker.json_content(request)
        return response[u'raw_config']


class PluginManagerResource(object):
    def __init__(self, pg_mgr_uri, broker):
        self._create_sub_resources(pg_mgr_uri, broker)
    
    def _create_sub_resources(self, pg_mgr_uri, broker):
        install_uri = uri_append_path(pg_mgr_uri, 'install')
        self._install_res = InstallServiceResource(install_uri, broker)
        
        config_uri = uri_append_path(pg_mgr_uri, 'configure')
        self._config_res = ConfigureServiceResource(config_uri, broker)
        
        plugins_uri = uri_append_path(pg_mgr_uri, 'plugins')
        self._plugins_res = PluginsResource(plugins_uri, broker)
    
    def config_srv_res(self):
        return self._config_res
    
    def install_srv_res(self):
        return self._install_res
    
    def plugins_res(self):
        return self._plugins_res


class PluginsResource(object):
    def __init__(self, plugins_uri, broker):
        self._plugins_uri = plugins_uri
        self._broker = broker
    
    def get(self, id):
        plugin_uri = uri_append_path(self._plugins_uri, id)
        return PluginResource(plugin_uri, self._broker)
    
    def list(self):
        request = new_get_request(self._plugins_uri)
        response, _ = self._broker.json_content(request)
        ids = list(response[u'plugins'].iterkeys())
        return ids


class PluginResource(object):
    _SERVICE_MAP = {'srv.install': InstallServiceResource,
                    'srv.configure': ConfigureServiceResource}
    
    def __init__(self, plugin_uri, broker):
        self._plugin_uri = plugin_uri
        self._broker = broker
    
    @once_per_instance
    def _do_services(self):
        request = new_get_request(self._plugin_uri)
        response, _ = self._broker.json_content(request)
        services = {}
        # XXX note that multiple link with the same service 'relation' is not
        #     supported
        for link in response[u'links']:
            rel = link[u'rel']
            if rel in self._SERVICE_MAP:
                uri = urlparse.urljoin(self._plugin_uri, str(link[u'href']))
                services[rel] = self._SERVICE_MAP[rel](uri, self._broker)
        return services
    
    def services(self):
        return self._do_services()


def new_server_resource(server_uri, credentials=None):
    handlers = [No2xxErrorHTTPErrorProcessor]
    if credentials:
        user, passwd = credentials
        pwd_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pwd_manager.add_password(None, server_uri, user, passwd)
        handlers.append(urllib2.HTTPDigestAuthHandler(pwd_manager))
    opener = urllib2.build_opener(*handlers)
    broker = RequestBroker(opener)
    return ServerResource(server_uri, broker)
