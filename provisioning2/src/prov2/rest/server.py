# -*- coding: UTF-8 -*-

"""Module that defines the REST server for the provisioning server
configuration.

"""

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

import simplejson as json
from twisted.python import log
from twisted.web.resource import Resource, NoResource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web import http
from prov2.devices.device import DeviceManager
from prov2.devices.util import NumericIdGenerator
from prov2.devices.config import ConfigManager
from prov2.plugins import PluginManager
from prov2.rest.util import *

# TODO input checking


PROV2_MIME_TYPE = 'application/vnd.proformatique.prov2+json'
_PPRINT = True
if _PPRINT:
    import functools
    json.dumps = functools.partial(json.dumps, sort_keys=True, indent=4)


class RestService(object):
    # FIXME useless now that we have an 'application' object ? probably
    
    def __init__(self, app):
        self._app = app
        
    def add_dev(self, dev):
        """Add a device to the device manager and return the ID of the newly
        created device.
        
        dev -- a device object
        
        """
        return self._app.create_dev(dev)
    
    def remove_dev(self, dev_id):
        """Remove the device with ID dev_id. Raise a KeyError if dev_id is
        not a known device ID.
        
        """
        self._app.delete_dev(dev_id)
        
    def has_dev(self, dev_id):
        return dev_id in self._app.dev_mgr
    
    def get_dev(self, dev_id):
        """Return the device object which ID is dev_id."""
        return self._app.retrieve_dev(dev_id)
    
    def set_dev(self, dev_id, dev):
        """Set the device object with ID dev_id."""
        self._app.update_dev(dev_id, dev)
    
    def reconfigure_dev(self, dev_id):
        pass
    
    def reload_dev(self, dev_id):
        """Make the device reload its configuration.
        
        """
        pass
    
    def list_dev(self, filter_fun=None):
        """Return the list of (device IDs, device) for which filter_fun(dev) is true.
        
        This return a generator object.
        
        """ 
        if filter_fun is None:
            return self._app.dev_mgr.iteritems()
        else:
            return ((dev_id, dev) for dev_id, dev in self._app.dev_mgr.iteritems() if filter_fun(dev))

    def remove_cfg(self, cfg_id):
        # TODO currently, this does nothing to any device using this config. We'll
        #      want to clearly specify the behavior
        self._app.cfg_mgr.remove(cfg_id)
    
    def has_cfg(self, cfg_id):
        return cfg_id in self._app.cfg_mgr
    
    def get_cfg(self, cfg_id):
        """Return a tuple (cfg, cfg_bases_id)."""
        return self._app.cfg_mgr[cfg_id]
    
    def set_cfg(self, cfg_id, cfg):
        """cfg is a tuple (cfg, cfg_bases_id)."""
        self._app.cfg_mgr[cfg_id] = cfg
    
    def list_cfg(self):
        """Return the list of config IDs.
        
        This return a generator object.
        
        """
        return self._app.cfg_mgr.iterkeys()
    
    def flatten_cfg(self, cfg_id):
        return self._app.cfg_mgr.flatten(cfg_id)


def dev_json_repr(dev, dev_id, dev_uri):
    """Return a application/vnd.proformatique.prov2+json representation of
    a device.
    
    """
    links = [{'rel': 'device', 'href': dev_uri}]
    if 'plugin' in dev:
        links.append({'rel': 'plugin', 'href': '/plugins/installed/' + dev['plugin']})
    if 'config' in dev:
        links.append({'rel': 'config-i', 'href': '/config/individual/' + dev['config']})
    return json.dumps({'device': dev, 'id': dev_id, 'links': links})


class DeviceResource(Resource):
    def __init__(self, service, dev_id):
        Resource.__init__(self)
        self._service = service
        self._dev_id = dev_id
    
    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        dev = self._service.get_dev(self._dev_id)
        
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV2_MIME_TYPE)
        return dev_json_repr(dev, self._dev_id, request.path)

    def render_DELETE(self, request):
        # This will delete the entry in the device manager and this object should
        # now be unreacheable from the REST API, and since we are single threaded, no
        # need to be worried of race conditions
        self._service.remove_dev(self._dev_id)
        request.setResponseCode(http.NO_CONTENT)
        # next lines are tricks for twisted to omit the 'Content-Type' and 'Content-Length'
        # of 'No content' response. This is not strictly necessary per the RFC, but it certainly
        # makes the HTTP response cleaner (but not my source code)
        request.responseHeaders.removeHeader('Content-Type')
        request.finish()
        return NOT_DONE_YET
    
    @content_type([PROV2_MIME_TYPE])
    def render_PUT(self, request):
        content = json.loads(request.content.getvalue())
        dev = content['device']
        self._service.set_dev(self._dev_id, dev)
        
        request.setResponseCode(http.NO_CONTENT)
        request.responseHeaders.removeHeader('Content-Type')
        return ""


class DevicesResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
    
    def getChild(self, path, request):
        if not path:
            return Resource.getChild(self, path, request)
        dev_id = path
        if self._service.has_dev(dev_id):
            return DeviceResource(self._service, dev_id)
        else:
            return NoResource()
    
    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        if request.args:
            # we do not accept multiple filter parameter right now
            args = request.args
            if len(args) != 1:
                request.setResponseCode(http.BAD_REQUEST)
                request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
                return u'Maximum of one filter parameter per request.'.encode('UTF-8')
            else:
                key, value = args.items()[0]
                if len(value) != 1:
                    request.setResponseCode(http.BAD_REQUEST)
                    request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
                    return u'Maximum of one filter parameter per request.'.encode('UTF-8')
                else:
                    value = value[0]
                    filter_fun = lambda x: x[key] == value
        else:
            filter_fun = None
            
        devices = []
        for dev_id, dev in self._service.list_dev(filter_fun):
            # TODO here we should transform 'ip' and 'mac' to their human
            #      readable form. What might be more useful is to always use
            #      these values as their normalized human readable form.
            devices.append({'id': dev_id,
                            'device': dev,
                            'links': [{'rel': 'device', 'href': request.path + '/' + dev_id}]})
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV2_MIME_TYPE)
        return json.dumps({'devices': devices})
    
    @content_type([PROV2_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        dev = content['device']
        dev_id = self._service.add_dev(dev)
        dev_uri = request.path + '/' + dev_id
        
        request.setResponseCode(http.CREATED)
        request.setHeader('Location', dev_uri)
        request.responseHeaders.removeHeader('Content-Type')
        return dev_json_repr(dev, dev_id, dev_uri)


class DeviceReconfigureResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
        
    @content_type([PROV2_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        dev_id = content['id']
        if not self._service.has_dev(dev_id):
            request.setResponseCode(http.BAD_REQUEST)
            request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
            return u"Device not found".encode('UTF-8')
        
        self._service.reconfigure_dev(dev_id)
        request.setResponseCode(http.NO_CONTENT)
        return ""
#        except ConfigurationError, e:
#            request.setResponseCode(http.BAD_REQUEST)
#            request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
#            resp_content = u"Error while configuring the device: %s" % e
#            return resp_content.encode('UTF-8')


class DeviceReloadResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
        
    @content_type([PROV2_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        dev_id = content['id']
        if not self._service.has_dev(dev_id):
            request.setResponseCode(http.BAD_REQUEST)
            request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
            return u"Device not found".encode('UTF-8')
        
        self._service.reload_dev(dev_id)
#        except ConfigurationError, e:
#            request.setResponseCode(http.BAD_REQUEST)
#            request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
#            resp_content = u"Error while configuring the device: %s" % e
#            return resp_content.encode('UTF-8')
        request.setResponseCode(http.NO_CONTENT)
        return ""


class ConfigResource(Resource):
    def __init__(self, service, cfg_id):
        Resource.__init__(self)
        self._service = service
        self._cfg_id = cfg_id
    
    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        if not self._service.has_cfg(self._cfg_id):
            return NoResource().render(request)
        else:
            if request.args.get('f', [None])[0] not in ('i', 'c'):
                request.setResponseCode(http.BAD_REQUEST)
                request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
                return u"Invalid request".encode('UTF-8')
             
            request.setResponseCode(http.OK)
            request.setHeader('Content-Type', PROV2_MIME_TYPE)
            if request.args['f'][0] == 'i':
                return self._ind_repr()
            else:
                return self._comp_repr()
    
    def _ind_repr(self):
        cfg, cfg_bases = self._service.get_cfg(self._cfg_id)
        bases = []
        for cfg_base_id in cfg_bases:
            bases.append({'id': cfg_base_id,
                          'links': [{'rel': 'config-i', 'href': '/configs/' + cfg_base_id + '?f=i'}]})
        return json.dumps({'config': cfg,
                           'config-bases': bases,
                           'id': self._cfg_id,
                           'links': [{'rel': 'config-i', 'href': '/configs/' + self._cfg_id + '?f=i'},
                                     {'rel': 'config-c', 'href': '/configs/' + self._cfg_id + '?f=c'}]})
    
    def _comp_repr(self):
        flat_cfg = self._service.flatten_cfg(self._cfg_id)
        return json.dumps({'config': flat_cfg,
                           'id': self._cfg_id,
                           'links': [{'rel': 'config-i', 'href': '/configs/' + self._cfg_id + '?f=i'},
                                     {'rel': 'config-c', 'href': '/configs/' + self._cfg_id + '?f=c'}]})
    
    def render_DELETE(self, request):
        if not self._service.has_cfg(self._cfg_id):
            return NoResource().render(request)
        else:
            self._service.remove_cfg(self._cfg_id)
            request.setResponseCode(http.NO_CONTENT)
            # next lines are tricks for twisted to omit the 'Content-Type' and 'Content-Length'
            # of 'No content' response. This is not strictly necessary per the RFC, but it certainly
            # makes the HTTP response cleaner (but not my source code)
            request.responseHeaders.removeHeader('Content-Type')
            request.finish()
            return NOT_DONE_YET
    
    @content_type([PROV2_MIME_TYPE])
    def render_PUT(self, request):
        # TODO check input validity
        received = json.loads(request.content.getvalue())
        config = received['config']
        cfg_bases = [cfg_base_entry['id'] for cfg_base_entry in received['config-bases']]
        self._service.set_cfg(self._cfg_id, (config, cfg_bases))

        request.setResponseCode(http.NO_CONTENT)
        request.responseHeaders.removeHeader('Content-Type')
        return ""


class ConfigsResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
        
    def getChild(self, path, request):
        if not path:
            return Resource.getChild(self, path, request)
        cfg_id = path
        return ConfigResource(self._service, cfg_id)

    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        configs = []
        for cfg_id in self._service.list_cfg():
            configs.append({'id': cfg_id,
                            'links': [{'rel': 'config-i', 'href': request.path + '/' + cfg_id + '?f=i'},
                                      {'rel': 'config-c', 'href': request.path + '/' + cfg_id + '?f=c'}]})
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV2_MIME_TYPE)
        return json.dumps({'configs': configs})


class InstalledPluginResource(Resource):
    def __init__(self, id, pg_mgr):
        Resource.__init__(self)
        self._pg_id = id
        self._pg_mgr = pg_mgr
        
    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        """Get information about this plugin, i.e. some generic information
        and the subservices this plugin expose.
        
        """
        pass
    
    def render_PUT(self, request):
        """Install this plugin if it's not installed.
        
        There's a problem though -- in this case, PUT is not idempotent.
        
        """
    
    def render_DELETE(self, request):
        """Uninstall this plugin if it's installed."""


class InstalledPluginsResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
        
    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        res = list(self._pg_mgr.list_installed())
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV2_MIME_TYPE)
        return json.dumps(res)
    

class InstallablePluginsResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
        
    @accept([PROV2_MIME_TYPE])
    def render_GET(self, request):
        res = list(self._pg_mgr.list_installable())
        for e in res:
            del e['filename']
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV2_MIME_TYPE)
        return json.dumps(res)


if __name__ == '__main__':
    import sys
    
    log.startLogging(sys.stderr)
    
    root = Resource()
    site = Site(root)
    
    id_gen = NumericIdGenerator()
    dev_mgr = DeviceManager(id_gen)
    dev_mgr.add({'mac': '00:11:22:33:44:55',
                 'ip': '192.168.32.105',
                 'vendor': 'Aastra',
                 'model': '6731i',
                 'config': '01'})
    dev_mgr.add({'ip': '0.0.0.0',
                 'vendor': 'Snom',
                 })
    dev_mgr.add({'mac': '00:99:88:33:44:55',
                 'ip': '192.168.32.106',
                 'vendor': 'Aastra',
                 'model': '6757i',
                 'config': '01',
                 'plugins': 'xivo-aastra-2.6.0.2010'})
    cfg_mgr = ConfigManager({'base': [{'prov_ip': '192.168.32.2', 'admin_passwd': '23456'}, []],
                             'dev-2': [{'admin_passwd': '54545'}, ['base']]})
    pg_mgr = PluginManager('/var/tmp/pf-xivo/prov2/plugins', 'http://xivo-test-prov2:8000/')
    plugins = list(pg_mgr.load_all())
    pg_map = dict((pg.name, pg) for pg in plugins)
    
    plugins = Resource()
    plugins.putChild('installed', InstalledPluginsResource(pg_mgr))
    plugins.putChild('installable', InstallablePluginsResource(pg_mgr))
    root.putChild('plugins', plugins)
    
    service = RestService(cfg_mgr, dev_mgr, pg_map)
    dev_res = DevicesResource(service)
    cfg_res = ConfigsResource(service)
    dev_configure_res = DeviceReconfigureResource(service)
    dev_reload_res = DeviceReloadResource(service)
    root.putChild('devices', dev_res)
    root.putChild('configs', cfg_res)
    root.putChild('dev_reconfigure', dev_configure_res)
    root.putChild('dev_reload', dev_reload_res)
    
    from twisted.internet import reactor
    reactor.listenTCP(8081, site)
    reactor.run()
