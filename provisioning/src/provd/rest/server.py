# -*- coding: UTF-8 -*-

"""Module that defines the REST server for the provisioning server
configuration.

"""

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

import binascii
try:
    import json
except ImportError:
    import simplejson as json
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.web import http
from provd.devices.util import NumericIdGenerator
from provd.services import InvalidParameterError
from provd.rest.util import *
from provd.util import norm_mac, norm_ip

# TODO input checking


PROV_MIME_TYPE = 'application/vnd.proformatique.provd+json'
_PPRINT = True
if _PPRINT:
    import functools
    json.dumps = functools.partial(json.dumps, sort_keys=True, indent=4)


def _process_request_failed(request, err_msg, response_code=http.BAD_REQUEST):
    request.setResponseCode(response_code)
    request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
    return str(err_msg).encode('UTF-8')


def dev_json_repr(dev, dev_id, dev_uri):
    """Return a application/vnd.proformatique.provd+json representation of
    a device.
    
    """
    links = [{'rel': 'device', 'href': dev_uri}]
    if 'plugin' in dev:
        links.append({'rel': 'plugin', 'href': '/plugins/installed/' + dev['plugin']})
    if 'config' in dev:
        links.append({'rel': 'config-i', 'href': '/config/individual/' + dev['config']})
    return json.dumps({'device': dev, 'id': dev_id, 'links': links})


class DeviceResource(Resource):
    def __init__(self, app, dev_id):
        Resource.__init__(self)
        self._app = app
        self._dev_id = dev_id
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        dev = self._app.retrieve_dev(self._dev_id)
        
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return dev_json_repr(dev, self._dev_id, request.path)

    def render_DELETE(self, request):
        # This will delete the entry in the device manager and this object should
        # now be unreacheable from the REST API, and since we are single threaded, no
        # need to be worried of race conditions
        self._app.delete_dev(self._dev_id)
        request.setResponseCode(http.NO_CONTENT)
        # next lines are tricks for twisted to omit the 'Content-Type' and 'Content-Length'
        # of 'No content' response. This is not strictly necessary per the RFC, but it certainly
        # makes the HTTP response cleaner (but not my source code)
        request.responseHeaders.removeHeader('Content-Type')
        request.finish()
        return NOT_DONE_YET
    
    @content_type([PROV_MIME_TYPE])
    def render_PUT(self, request):
        content = json.loads(request.content.getvalue())
        dev = content['device']
        self._app.update_dev(self._dev_id, dev)
        
        request.setResponseCode(http.NO_CONTENT)
        request.responseHeaders.removeHeader('Content-Type')
        return ""


class DevicesResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app
    
    def getChild(self, path, request):
        dev_id = path
        if dev_id in self._app.dev_mgr:
            return DeviceResource(self._app, dev_id)
        else:
            return Resource.getChild(self, path, request)
    
    @accept([PROV_MIME_TYPE])
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
            filter_fun = lambda x: True
        
        dev_mgr = self._app.dev_mgr
        devices = []
        for dev_id in dev_mgr.filter(filter_fun):
            dev = dev_mgr[dev_id]
            devices.append({'id': dev_id,
                            'device': dev,
                            'links': [{'rel': 'device', 'href': request.path + '/' + dev_id}]})
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'devices': devices})
    
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        dev = content['device']
        dev_id = self._app.create_dev(dev)
        dev_uri = request.path + '/' + dev_id
        
        request.setResponseCode(http.CREATED)
        request.setHeader('Location', dev_uri)
        request.responseHeaders.removeHeader('Content-Type')
        return dev_json_repr(dev, dev_id, dev_uri)


class DeviceSynchronizeResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app
        
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        dev_id = content['id']
        if dev_id not in self._app.dev_mgr:
            request.setResponseCode(http.BAD_REQUEST)
            request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
            return u"Device not found".encode('UTF-8')
        
        self._app.synchronize_dev(dev_id)
        request.setResponseCode(http.NO_CONTENT)
        return ""


class ConfigResource(Resource):
    def __init__(self, app, cfg_id):
        Resource.__init__(self)
        self._app = app
        self._cfg_id = cfg_id
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        if self._cfg_id not in self._app.cfg_mgr:
            return NoResource().render(request)
        else:
            if request.args.get('f', [None])[0] not in ('i', 'c'):
                request.setResponseCode(http.BAD_REQUEST)
                request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
                return u"Invalid request".encode('UTF-8')
             
            request.setResponseCode(http.OK)
            request.setHeader('Content-Type', PROV_MIME_TYPE)
            if request.args['f'][0] == 'i':
                return self._ind_repr()
            else:
                return self._comp_repr()
    
    def _ind_repr(self):
        cfg, cfg_bases = self._app.retrieve_cfg(self._cfg_id)
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
        flat_cfg = self._app.cfg_mgr.flatten(self._cfg_id)
        return json.dumps({'config': flat_cfg,
                           'id': self._cfg_id,
                           'links': [{'rel': 'config-i', 'href': '/configs/' + self._cfg_id + '?f=i'},
                                     {'rel': 'config-c', 'href': '/configs/' + self._cfg_id + '?f=c'}]})
    
    def render_DELETE(self, request):
        if self._cfg_id not in self._app.cfg_mgr:
            return NoResource().render(request)
        else:
            self._app.delete_cfg(self._cfg_id)
            request.setResponseCode(http.NO_CONTENT)
            # next lines are tricks for twisted to omit the 'Content-Type' and 'Content-Length'
            # of 'No content' response. This is not strictly necessary per the RFC, but it certainly
            # makes the HTTP response cleaner (but not my source code)
            request.responseHeaders.removeHeader('Content-Type')
            request.finish()
            return NOT_DONE_YET
    
    @content_type([PROV_MIME_TYPE])
    def render_PUT(self, request):
        # TODO check input validity
        received = json.loads(request.content.getvalue())
        config = received['config']
        cfg_bases = [cfg_base_entry['id'] for cfg_base_entry in received['config-bases']]
        if self._cfg_id in self._app.cfg_mgr:
            self._app.update_cfg(self._cfg_id, (config, cfg_bases))
        else:
            self._app.create_cfg((config, cfg_bases), self._cfg_id)

        request.setResponseCode(http.NO_CONTENT)
        request.responseHeaders.removeHeader('Content-Type')
        return ""


class ConfigsResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app
        
    def getChild(self, path, request):
        cfg_id = path
        return ConfigResource(self._app, cfg_id)

    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        configs = []
        for cfg_id in self._app.cfg_mgr.iterkeys():
            configs.append({'id': cfg_id,
                            'links': [{'rel': 'config-i', 'href': request.path + '/' + cfg_id + '?f=i'},
                                      {'rel': 'config-c', 'href': request.path + '/' + cfg_id + '?f=c'}]})
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'configs': configs})


class PopResource(Resource):
    # Pop is for 'Progress OPeration'
    # Note that render_DELETE might be implemented in classes creating these
    # objects, and not on the class itself
    def __init__(self, pop):
        """
        pop -- an object providing the IProgressingOperation interface
        """
        Resource.__init__(self)
        self._pop = pop

    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'pop.status': self._pop.status})


class PluginMgrUpdateResource(Resource):
    def __init__(self, pg_mgr, id_gen=None):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
        self._id_gen = NumericIdGenerator() if id_gen is None else id_gen
        self._childs = {}
    
    def getChild(self, path, request):
        if path in self._childs:
            return self._childs[path]
        else:
            return Resource.getChild(self, path, request)

    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        # right now, we can ignore the content, since it's supposed to be empty
        try:
            pop = self._pg_mgr.update()
        except Exception, e:
            # XXX not the right response code... but which one is ?
            return _process_request_failed(request, e, http.INTERNAL_SERVER_ERROR)
        else:
            id = self._id_gen.next_id(self._childs)
            pop_res = PopResource(pop)
            def on_pop_delete(request):
                del self._childs[id]
                request.setResponseCode(http.NO_CONTENT)
                return ""
            pop_res.render_DELETE = on_pop_delete
            self._childs[id] = pop_res
            
            request.setResponseCode(http.ACCEPTED)
            request.setHeader('Location', request.path + '/' + id)
            return ""


# The 3 PluginListXXX resource are closely similar... means we could refactor...
class PluginMgrListInstallableResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        list = [{'id': e['name'], 'version': e['version']} for e in
                self._pg_mgr.list_installable()]
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'pg_infos': list})


class PluginMgrListInstalledResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        list = []
        for e in self._pg_mgr.list_installed():
            # XXX e['name'] should probably be url-encoded and the base url
            #     should probably not be hard coded
            links = [{'rel': 'plugin', 'href': '/pg_mgr/plugins/%s' % e['name']}]
            cur = {'id': e['name'], 'version': e['version'], 'links': links}
            list.append(cur)
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'pg_infos': list})
        

class PluginMgrListUpgradeableResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        list = [{'id': e['name'], 'version': e['version']} for e in
                self._pg_mgr.list_upgradeable()]
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'pg_infos': list})


class PluginMgrConfigureParamResource(Resource):
    def __init__(self, cfg_service, param):
        Resource.__init__(self)
        self._cfg_service = cfg_service
        self._param = param
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        value = self._cfg_service.get(self._param)
        if value is None:
            return json.dumps({})
        else:
            return json.dumps({'value': value})
    
    @content_type([PROV_MIME_TYPE])
    def render_PUT(self, request):
        content = json.loads(request.content.getvalue())
        if 'value' in content:
            value = content['value']
        else:
            value = None
        try:
            self._cfg_service.set(self._param, value)
        except InvalidParameterError, e:
            # XXX not the 'right' response code
            request.setResponseCode(http.BAD_REQUEST)
            request.setHeader('Content-Type', 'text/plain; charset=UTF-8')
            return str(e).encode('UTF-8')
        else:
            request.setResponseCode(http.NO_CONTENT)
            return ""


class PluginMgrConfigureResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
    
    def getChild(self, path, request):
        cfg_service = self._pg_mgr.configure_service()
        if path not in cfg_service.description:
            return NoResource()
        else:
            res = PluginMgrConfigureParamResource(cfg_service, path)
            return res
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        cfg_service = self._pg_mgr.configure_service()
        params = {}
        for key in cfg_service.description.iterkeys():
            # XXX urlquote p_uri (in fact, only key)
            p_uri = request.path + '/' + key
            p_value = {'links': [{'rel': 'config.param', 'href': p_uri}]}
            value = cfg_service.get(key)
            if value is not None:
                p_value['value'] = str(value)
            params[key] = p_value
        
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'config': params})


class _PluginMgrInstallUpgradeResource(Resource):
    def __init__(self, app, id_gen=None):
        Resource.__init__(self)
        self._app = app
        self._id_gen = NumericIdGenerator() if id_gen is None else id_gen
        self._childs = {}

    def getChild(self, path, request):
        if path in self._childs:
            return self._childs[path]
        else:
            return Resource.getChild(self, path, request)
    
    def _do_call_app(self, pg_id):
        raise NotImplementedError('must be implemented in derived class')
    
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        try:
            pg_id = content['id']
        except KeyError, e:
            return _process_request_failed(request, e)
        else:
            try:
                pop = self._do_call_app(pg_id)
            except Exception, e:
                return _process_request_failed(request, e, http.INTERNAL_SERVER_ERROR)
            else:
                id = self._id_gen.next_id(self._childs)
                pop_res = PopResource(pop)
                def on_pop_delete(request):
                    del self._childs[id]
                    request.setResponseCode(http.NO_CONTENT)
                    return ""
                pop_res.render_DELETE = on_pop_delete
                self._childs[id] = pop_res
                
                request.setResponseCode(http.ACCEPTED)
                request.setHeader('Location', request.path + '/' + id)
                return ""


class PluginMgrInstallResource(_PluginMgrInstallUpgradeResource):
    def _do_call_app(self, pg_id):
        return self._app.install_pg(pg_id)


class PluginMgrUpgradeResource(_PluginMgrInstallUpgradeResource):
    def _do_call_app(self, pg_id):
        return self._app.upgrade_pg(pg_id)


class PluginMgrUninstallRecourse(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app
    
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        try:
            pg_id = content['id']
        except KeyError, e:
            return _process_request_failed(request, e)
        else:
            try:
                self._app.uninstall_pg(pg_id)
            except Exception, e:
                return _process_request_failed(request, e, http.INTERNAL_SERVER_ERROR)
            else:
                request.setResponseCode(http.NO_CONTENT)
                return ""


class PluginsResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
        # FIXME we want to create PluginResource only once so that they can
        #       hold information for the lifetime of the plugin. The problem
        #       is, we need to support plugin hotswapping, and this clearly
        #       doesn't, especially that this resource is usually create at
        #       'start' time
        self._childs = dict((pg_id, PluginResource(pg_obj)) for
                            (pg_id, pg_obj) in pg_mgr.iteritems())
    
    def getChild(self, path, request):
        try:
            return self._childs[path]
        except KeyError:
            return Resource.getChild(self, path, request)


class PluginResource(Resource):
    def __init__(self, pg):
        Resource.__init__(self)
        self._id = pg.name
        self._service_res = PluginServicesResource(pg.services)
    
    def getChild(self, path, request):
        if path == "services":
            return self._service_res
        return Resource.getChild(self, path, request)
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        res = {"id": self._id,
               "links": [{"rel": "services",
                          "href": request.path + '/' + 'services'}]}
        return json.dumps({"plugin": res})


class PluginInstallServiceResource(Resource):
    def __init__(self, install_service):
        Resource.__init__(self)
        self._childs = {
            'install': PluginInstallServiceInstallResource(install_service),
            'uninstall': PluginInstallServiceUninstallResource(install_service),
            'installable': PluginInstallServiceListInstallableResource(install_service),
            'installed': PluginInstallServiceListInstalledResource(install_service)
        }
    
    def getChild(self, path, request):
        try:
            return self._childs[path]
        except KeyError:
            return Resource.getChild(self, path, request)
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        links = [{"rel": "service.install." + e, "href": request.path + '/' + e} for e in self._childs]
        res = {"type": "service.install",
               "links": links}
        return json.dumps({'service': res})


class PluginInstallServiceInstallResource(Resource):
    def __init__(self, install_service, id_gen=None):
        Resource.__init__(self)
        self._srv = install_service
        self._id_gen = NumericIdGenerator() if id_gen is None else id_gen
        self._childs = {}
    
    def getChild(self, path, request):
        if path in self._childs:
            return self._childs[path]
        else:
            return Resource.getChild(self, path, request)
        
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        try:
            pkg_id = content['id']
        except KeyError, e:
            return _process_request_failed(request, e)
        else:
            try:
                pop = self._srv.install(pkg_id)
            except Exception, e:
                return _process_request_failed(request, e, http.INTERNAL_SERVER_ERROR)
            else:
                id = self._id_gen.next_id(self._childs)
                pop_res = PopResource(pop)
                def on_pop_delete(request):
                    del self._childs[id]
                    request.setResponseCode(http.NO_CONTENT)
                    return ""
                pop_res.render_DELETE = on_pop_delete
                self._childs[id] = pop_res
                
                request.setResponseCode(http.ACCEPTED)
                request.setHeader('Location', request.path + '/' + id)
                return ""


class PluginInstallServiceUninstallResource(Resource):
    def __init__(self, install_service):
        Resource.__init__(self)
        self._srv = install_service
    
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        try:
            pkg_id = content['id']
        except KeyError, e:
            return _process_request_failed(request, e)
        else:
            try:
                self._srv.uninstall(pkg_id)
            except Exception, e:
                return _process_request_failed(request, e, http.INTERNAL_SERVER_ERROR)
            else:
                request.setResponseCode(http.NO_CONTENT)
                return ""


class PluginInstallServiceListInstalledResource(Resource):
    def __init__(self, install_service):
        Resource.__init__(self)
        self._srv = install_service
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        list = [{'id': e['id']} for e in self._srv.list_installed()]
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'pkg_infos': list})


class PluginInstallServiceListInstallableResource(Resource):
    def __init__(self, install_service):
        Resource.__init__(self)
        self._srv = install_service
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        list = []
        for e in self._srv.list_installable():
            d = {'id': e['id']}
            if 'dsize' in e:
                d['dsize'] = e['dsize']
            if 'isize' in e:
                d['isize'] = e['isize']
            list.append(d)
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({'pkg_infos': list})


class PluginUnknownServiceResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
    
    def getChild(self, path, request):
        if path == 'do':
            return PluginUnknownDoServiceResource(self._service)
        else:
            return Resource.getChild(self, path, request)
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        return json.dumps({"service": {"type": "service.unknown",
                                       "links": [{"rel": "service.unknown.do",
                                                  "href": self.path + '/' + 'do'}]}})


class PluginUnknownDoServiceResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self._service = service
    
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        value = content['value']
        try:
            ret_value = self._service.do(value)
        except Exception, e:
            return _process_request_failed(request, e, http.INTERNAL_SERVER_ERROR)
        else:
            request.setResponseCode(http.OK)
            request.setHeader('Content-Type', PROV_MIME_TYPE)
            return json.dumps({'value': str(ret_value)})


class PluginServicesResource(Resource):
    STANDARDIZED_SRVS = {
        "install": "service.install",
        "configure": "service.configure"
    }
    RES_FACTORIES = {
        "install": PluginInstallServiceResource,
    }
    
    def __init__(self, services):
        Resource.__init__(self)
        self._childs = {}
        for srv_name, srv_obj in services.iteritems():
            factory = self.RES_FACTORIES.get(srv_name, PluginUnknownServiceResource)
            resource = factory(srv_obj)
            self._childs[srv_name] = resource
        
    def getChild(self, path, request):
        try:
            return self._childs[path]
        except KeyError:
            return Resource.getChild(self, path, request)
    
    @accept([PROV_MIME_TYPE])
    def render_GET(self, request):
        request.setResponseCode(http.OK)
        request.setHeader('Content-Type', PROV_MIME_TYPE)
        res = []
        for srv_name in self._childs:
            type = self.STANDARDIZED_SRVS.get(srv_name, 'service.unknown')
            res.append({'type': type, 'links': [{'rel': type, 'href': request.path + '/' + srv_name}]})
        return json.dumps({"services": res})


class DHCPInfoResource(Resource):
    """Resource for pushing DHCP information into the provisioning server."""
    def __init__(self, dhcp_infos):
        """
        dhcp_infos is a dictionary object that will change as the server
          receive information
        
        """
        Resource.__init__(self)
        self._dhcp_infos = dhcp_infos
    
    def _transform_dhcp_opts(self, raw_dhcp_opts):
        dhcp_opts = {}
        for raw_dhcp_opt in raw_dhcp_opts:
            code = int(raw_dhcp_opt[:3], 10)
            value = binascii.unhexlify(raw_dhcp_opt[3:])
            dhcp_opts[code] = value
        return dhcp_opts
    
    @content_type([PROV_MIME_TYPE])
    def render_POST(self, request):
        content = json.loads(request.content.getvalue())
        op = content['op'].encode('ascii')
        ip = norm_ip(content['ip'].encode('ascii'))
        if op == 'commit':
            mac = norm_mac(content['mac'].encode('ascii'))
            dhcp_opts = self._transform_dhcp_opts(content['dhcp_opts'])
            self._dhcp_infos[ip] = {'mac': mac, 'dhcp_opts': dhcp_opts}
            request.setResponseCode(http.NO_CONTENT)
            return ""
        elif op in ('expiry', 'release'):
            if ip in self._dhcp_infos:
                del self._dhcp_infos[ip]
            request.setResponseCode(http.NO_CONTENT)
            return ""
        else:
            return _process_request_failed(request, 'invalid commit value')


def new_root_resource(app, dhcp_infos):
    root = Resource()
    dev_res = DevicesResource(app)
    dev_reload_res = DeviceSynchronizeResource(app)
    dhcpinfo_res = DHCPInfoResource(dhcp_infos)
    root.putChild('devices', dev_res)
    root.putChild('dev_sync', dev_reload_res)
    root.putChild('dhcpinfo', dhcpinfo_res)
    
    cfg_res = ConfigsResource(app)
    root.putChild('configs', cfg_res)
    
    pg_config_res = PluginMgrConfigureResource(app.pg_mgr)
    pg_update_res = PluginMgrUpdateResource(app.pg_mgr)
    pg_list_able_res = PluginMgrListInstallableResource(app.pg_mgr)
    pg_list_ed_res = PluginMgrListInstalledResource(app.pg_mgr)
    pg_list_upgradeable_res = PluginMgrListUpgradeableResource(app.pg_mgr)
    pg_install_res = PluginMgrInstallResource(app)
    pg_upgrade_res = PluginMgrUpgradeResource(app)
    pg_uninstall_res = PluginMgrUninstallRecourse(app)
    pg_plugins_res = PluginsResource(app.pg_mgr)
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
    return root
