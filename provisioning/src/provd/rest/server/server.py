# -*- coding: UTF-8 -*-

"""Module that defines the REST server for the provisioning server
configuration.

"""

__license__ = """
    Copyright (C) 2011  Avencall

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

# TODO we sometimes return 400 error when it's not a client error but a server error;
#      that said raised exceptions sometimes does not permit to differentiate...
# XXX passing a 'dhcp_request_processing_service' around doesn't look really
#     good and we might want to create an additional indirection level so that
#     it's a bit cleaner

import functools
import json
import logging
from binascii import a2b_base64
from provd.app import InvalidIdError
from provd.localization import get_locale_and_language
from provd.operation import format_oip, operation_in_progres_from_deferred
from provd.persist.common import ID_KEY
from provd.plugins import BasePluginManagerObserver
from provd.rest.util import PROV_MIME_TYPE, uri_append_path
from provd.rest.server.util import accept_mime_type, numeric_id_generator
from provd.services import InvalidParameterError
from provd.util import norm_mac, norm_ip
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.cred.portal import Portal
from twisted.web import http
from twisted.web.guard import DigestCredentialFactory, HTTPAuthSessionWrapper
from twisted.web.resource import Resource, IResource
from twisted.web.server import NOT_DONE_YET

logger = logging.getLogger(__name__)

REL_INSTALL_SRV = u'srv.install'
REL_INSTALL = u'srv.install.install'
REL_UNINSTALL = u'srv.install.uninstall'
REL_INSTALLED = u'srv.install.installed'
REL_INSTALLABLE = u'srv.install.installable'
REL_UPGRADE = u'srv.install.upgrade'
REL_UPDATE = u'srv.install.update'
REL_CONFIGURE_SRV = u'srv.configure'
REL_CONFIGURE_PARAM = u'srv.configure.param'
REALM_NAME = 'provd server'


_PPRINT = False
if _PPRINT:
    json_dumps = functools.partial(json.dumps, sort_keys=True, indent=4)
else:
    json_dumps = functools.partial(json.dumps, separators=(',', ':'))


def new_id_generator():
    return numeric_id_generator(start=1)


def respond_no_content(request, response_code=http.NO_CONTENT):
    request.setResponseCode(response_code)
    # next lines are tricks for twisted to omit the 'Content-Type' and 'Content-Length'
    # of 'No content' response. This is not strictly necessary per the RFC, but it certainly
    # makes the HTTP response cleaner (but not my source code)
    request.responseHeaders.removeHeader('Content-Type')
    request.finish()
    return NOT_DONE_YET


def respond_created_no_content(request, location):
    request.setHeader('Location', location)
    return respond_no_content(request, http.CREATED)


def respond_error(request, err_msg, response_code=http.BAD_REQUEST):
    request.setResponseCode(response_code)
    request.setHeader('Content-Type', 'text/plain; charset=ascii')
    return str(err_msg)


def respond_bad_json_entity(request, err_msg=None):
    if err_msg is None:
        err_msg = 'Missing information in received entity'
    return respond_error(request, err_msg)


def respond_no_resource(request, response_code=http.NOT_FOUND):
    request.setResponseCode(response_code)
    request.setHeader('Content-Type', 'text/plain; charset=ascii')
    return 'No such resource'


def deferred_respond_no_content(request, response_code=http.NO_CONTENT):
    request.setResponseCode(response_code)
    request.responseHeaders.removeHeader('Content-Type')
    request.finish()


def deferred_respond_error(request, err_msg, response_code=http.BAD_REQUEST):
    request.setResponseCode(response_code)
    request.setHeader('Content-Type', 'text/plain; charset=ascii')
    request.write(str(err_msg))
    request.finish()


def deferred_respond_ok(request, data, response_code=http.OK):
    request.setResponseCode(response_code)
    request.write(data)
    request.finish()


def deferred_respond_no_resource(request, response_code=http.NOT_FOUND):
    request.setResponseCode(response_code)
    request.setHeader('Content-Type', 'text/plain; charset=ascii')
    request.write('No such resource')
    request.finish()


def json_response_entity(fun):
    """To use on resource render's method that respond with a PROV_MIME_TYPE
    entity.
    
    This check that the request is ready to accept such entity, and it will
    set the Content-Type of the response before handling the request to the
    wrapped function. That way, it's still possible for the render function
    to respond with a different content.
    
    """
    @functools.wraps(fun)
    def aux(self, request):
        if not accept_mime_type(PROV_MIME_TYPE, request):
            return respond_error(request,
                                 'You must accept the "%s" MIME type.' % PROV_MIME_TYPE,
                                 http.NOT_ACCEPTABLE)
        else:
            request.setHeader('Content-Type', PROV_MIME_TYPE)
            return fun(self, request)
    return aux


def json_request_entity(fun):
    """To use on resource render's method that receive a PROV_MIME_TYPE
    entity.
    
    The entity will be deserialized and passed as a third argument to the
    render function.
    
    """
    @functools.wraps(fun)
    def aux(self, request):
        content_type = request.getHeader('Content-Type')
        if content_type != PROV_MIME_TYPE:
            return respond_error(request,
                                 'Entity must be in media type "%s".' % PROV_MIME_TYPE,
                                 http.UNSUPPORTED_MEDIA_TYPE)
        else:
            try:
                content = json.loads(request.content.getvalue())
            except ValueError, e:
                logger.info('Received invalid JSON document: %s', e)
                return respond_error(request, 'Invalid JSON document: %s' % e)
            else:
                return fun(self, request, content)
    return aux


def _add_selector_parameter(args, result):
    # q={"configured": false}
    result['selector'] = {}
    if 'q64' in args:
        try:
            raw_selector = a2b_base64(args['q64'][0])
        except Exception, e:
            logger.warning('Invalid q64 value: %s', e)
        else:
            try:
                selector = json.loads(raw_selector)
            except ValueError, e:
                logger.warning('Invalid q64 value: %s', e)
            else:
                result['selector'] = selector
    elif 'q' in args:
        raw_selector = args['q'][0]
        try:
            selector = json.loads(raw_selector)
        except ValueError, e:
            logger.warning('Invalid q value: %s', e)
        else:
            result['selector'] = selector


def _add_fields_parameter(args, result):
    # fields=mac,ip
    if 'fields' in args:
        raw_fields = args['fields'][0]
        fields = raw_fields.split(',')
        result['fields'] = fields


def _add_skip_parameter(args, result):
    # skip=10
    if 'skip' in args:
        raw_skip = args['skip'][0]
        try:
            skip = int(raw_skip)
        except ValueError, e:
            logger.warning('Invalid skip value: %s', e)
        else:
            result['skip'] = skip


def _add_limit_parameters(args, result):
    # limit=10
    if 'limit' in args:
        raw_limit = args['limit'][0]
        try:
            limit = int(raw_limit)
        except ValueError, e:
            logger.warning('Invalid limit value: %s', e)
        else:
            result['limit'] = limit


def _add_sort_parameters(args, result):
    # sort=mac
    # sort=mac&sort_ord=ASC
    if 'sort' in args:
        key = args['sort'][0]
        direction = 1
        if 'sort_ord' in args:
            raw_direction = args['sort_ord'][0]
            if raw_direction == 'ASC':
                direction = 1
            elif raw_direction == 'DESC':
                direction = -1
            else:
                logger.warning('Invalid sort_ord value: %s', raw_direction)
        result['sort'] = (key, direction)


def find_arguments_from_request(request):
    # Return a dictionary representing the different find parameters that
    # were passed in the request. The dictionary is usable as **kwargs for
    # the find method of collections.
    result = {}
    args = request.args
    _add_selector_parameter(args, result)
    _add_fields_parameter(args, result)
    _add_skip_parameter(args, result)
    _add_limit_parameters(args, result)
    _add_sort_parameters(args, result)
    return result


def _return_value(value):
    # Return a function that when called will return the value passed in
    # arguments. This can be useful when working with deferred.
    def aux(*args, **kwargs):
        return value
    return aux


_return_none = _return_value(None)

def _ignore_deferred_error(deferred):
    # Ignore any error raise by the deferred by placing an errback that
    # will return None. This is useful if you don't care about the deferred
    # yet you don't want to see an error message in the log when the deferred
    # will be garbage collected.
    deferred.addErrback(_return_none)


class IntermediaryResource(Resource):
    # TODO document better and maybe change the name

    def __init__(self, links):
        """
        links -- a list of tuple (rel, path, resource)
        
        For example:
        links = [(u'foo', 'foo_sub_uri', server.Data('text/plain', 'foo'),
                 (u'bar', 'bar_sub_uri', server.Data('text/plain', 'bar')]
        IntermediaryResource(links)
         
        The difference between this resource and a plain Resource is that a
        GET request will yield something.
        
        """
        Resource.__init__(self)
        self._links = links
        self._register_childs()

    def _register_childs(self):
        for _, path, resource in self._links:
            self.putChild(path, resource)

    def _build_links(self, base_uri):
        links = []
        for rel, path, _ in self._links:
            href = uri_append_path(base_uri, path)
            links.append({u'rel': rel, u'href': href})
        return links

    @json_response_entity
    def render_GET(self, request):
        content = {u'links': self._build_links(request.path)}
        return json_dumps(content)


def ServerResource(app, dhcp_request_processing_service):
    links = [(u'dev', 'dev_mgr', DeviceManagerResource(app, dhcp_request_processing_service)),
             (u'cfg', 'cfg_mgr', ConfigManagerResource(app)),
             (u'pg', 'pg_mgr', PluginManagerResource(app)),
             (REL_CONFIGURE_SRV, 'configure', ConfigureServiceResource(app.configure_service))]
    return IntermediaryResource(links)


class OperationInProgressResource(Resource):
    # Note that render_DELETE might be implemented in classes creating these
    # objects, and not on the class itself
    def __init__(self, oip, on_delete=None):
        """
        oip -- an operation in progress object
        on_delete -- either None or a callable taking no argument
        """
        Resource.__init__(self)
        self._oip = oip
        self._on_delete = on_delete

    @json_response_entity
    def render_GET(self, request):
        content = {u'status': format_oip(self._oip)}
        return json_dumps(content)

    def render_DELETE(self, request):
        if self._on_delete is not None:
            self._on_delete()
        return respond_no_content(request)


class ConfigureServiceResource(Resource):
    def __init__(self, cfg_srv):
        """
        cfg_srv -- an object providing the IConfigureService interface
        """
        Resource.__init__(self)
        self._cfg_srv = cfg_srv

    def getChild(self, path, request):
        return ConfigureParameterResource(self._cfg_srv, path)

    def _get_localized_description_list(self):
        locale, lang = get_locale_and_language()
        cfg_srv = self._cfg_srv
        if locale is not None:
            locale_name = 'description_%s' % locale
            try:
                return getattr(cfg_srv, locale_name)
            except AttributeError:
                if lang != locale:
                    lang_name = 'description_%s' % lang
                    try:
                        return getattr(cfg_srv, lang_name)
                    except AttributeError:
                        pass
        # in last case, return the non-localized description
        return cfg_srv.description

    @json_response_entity
    def render_GET(self, request):
        description_list = self._get_localized_description_list()
        params = []
        for id_, description in description_list:
            value = self._cfg_srv.get(id_)
            href = uri_append_path(request.path, id_)
            params.append({u'id': id_,
                           u'description': description,
                           u'value': value,
                           u'links': [{u'rel': REL_CONFIGURE_PARAM,
                                       u'href': href}]})
        content = {u'params': params}
        return json_dumps(content)


class ConfigureParameterResource(Resource):
    def __init__(self, cfg_srv, key):
        Resource.__init__(self)
        # key is not necessary to be valid
        self._cfg_srv = cfg_srv
        self._key = key

    @json_response_entity
    def render_GET(self, request):
        try:
            value = self._cfg_srv.get(self._key)
        except KeyError:
            logger.info('Invalid/unknown key: %s', self._key)
            return respond_no_resource(request)
        else:
            content = {u'param': {u'value': value}}
            return json_dumps(content)

    @json_request_entity
    def render_PUT(self, request, content):
        try:
            value = content[u'param'][u'value']
        except KeyError:
            return respond_error(request, 'Wrong information in entity')
        else:
            try:
                self._cfg_srv.set(self._key, value)
            except InvalidParameterError, e:
                logger.info('Invalid value for key %s: %r', self._key, value)
                return respond_error(request, e)
            except KeyError:
                logger.info('Invalid/unknown key: %s', self._key)
                return respond_no_resource(request)
            else:
                return respond_no_content(request)


def InstallServiceResource(install_srv):
    links = [(REL_INSTALL, 'install', InstallResource(install_srv)),
             (REL_UNINSTALL, 'uninstall', UninstallResource(install_srv)),
             (REL_INSTALLED, 'installed', InstalledResource(install_srv)),
             (REL_INSTALLABLE, 'installable', InstallableResource(install_srv))]
    if hasattr(install_srv, 'upgrade'):
        links.append((REL_UPGRADE, 'upgrade', UpgradeResource(install_srv)))
    if hasattr(install_srv, 'update'):
        links.append((REL_UPDATE, 'update', UpdateResource(install_srv)))
    return IntermediaryResource(links)


class _OipInstallResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self._id_gen = new_id_generator()

    def _add_new_oip(self, oip, request):
        # add a new child to this resource, and return the location
        # of the child
        path = self._id_gen.next()
        def on_delete():
            try:
                del self.children[path]
            except KeyError:
                logger.warning('ID "%s" has already been removed' % path)
        op_in_progress_res = OperationInProgressResource(oip, on_delete)
        self.putChild(path, op_in_progress_res)
        return uri_append_path(request.path, path)


class InstallResource(_OipInstallResource):
    def __init__(self, install_srv):
        _OipInstallResource.__init__(self)
        self._install_srv = install_srv

    @json_request_entity
    def render_POST(self, request, content):
        try:
            pkg_id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            try:
                deferred, oip = self._install_srv.install(pkg_id)
            except Exception, e:
                # XXX should handle the exception differently if it was
                #     because there's already an install in progress
                return respond_error(request, e)
            else:
                _ignore_deferred_error(deferred)
                location = self._add_new_oip(oip, request)
                return respond_created_no_content(request, location)


class UninstallResource(Resource):
    def __init__(self, install_srv):
        Resource.__init__(self)
        self._install_srv = install_srv

    @json_request_entity
    def render_POST(self, request, content):
        try:
            pkg_id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            try:
                self._install_srv.uninstall(pkg_id)
            except Exception, e:
                return respond_error(request, e)
            else:
                return respond_no_content(request)


class UpgradeResource(_OipInstallResource):
    def __init__(self, install_srv):
        _OipInstallResource.__init__(self)
        self._install_srv = install_srv

    @json_request_entity
    def render_POST(self, request, content):
        try:
            pkg_id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            try:
                deferred, oip = self._install_srv.upgrade(pkg_id)
            except Exception, e:
                # XXX should handle the exception differently if it was
                #     because there's already an upgrade in progress
                return respond_error(request, e)
            else:
                _ignore_deferred_error(deferred)
                location = self._add_new_oip(oip, request)
                return respond_created_no_content(request, location)


class UpdateResource(_OipInstallResource):
    def __init__(self, install_srv):
        _OipInstallResource.__init__(self)
        self._install_srv = install_srv

    @json_request_entity
    def render_POST(self, request, content):
        try:
            deferred, oip = self._install_srv.update()
        except Exception, e:
            # XXX should handle the exception differently if it was
            #     because there's already an update in progress
            logger.error('Error while updating packages', exc_info=True)
            return respond_error(request, e, http.INTERNAL_SERVER_ERROR)
        else:
            _ignore_deferred_error(deferred)
            location = self._add_new_oip(oip, request)
            return respond_created_no_content(request, location)


class _ListInstallxxxxResource(Resource):
    def __init__(self, install_srv, method_name):
        Resource.__init__(self)
        self._install_srv = install_srv
        self._method_name = method_name

    @json_response_entity
    def render_GET(self, request):
        fun = getattr(self._install_srv, self._method_name)
        try:
            pkgs = fun()
        except Exception, e:
            logger.error('Error while listing install packages', exc_info=True)
            return respond_error(request, e, http.INTERNAL_SERVER_ERROR)
        else:
            content = {u'pkgs': pkgs}
            return json_dumps(content)


def InstalledResource(install_srv):
    return _ListInstallxxxxResource(install_srv, 'list_installed')


def InstallableResource(install_srv):
    return _ListInstallxxxxResource(install_srv, 'list_installable')


def DeviceManagerResource(app, dhcp_request_processing_service):
    links = [(u'dev.synchronize', 'synchronize', DeviceSynchronizeResource(app)),
             (u'dev.reconfigure', 'reconfigure', DeviceReconfigureResource(app)),
             (u'dev.dhcpinfo', 'dhcpinfo', DeviceDHCPInfoResource(dhcp_request_processing_service)),
             (u'dev.devices', 'devices', DevicesResource(app))]
    return IntermediaryResource(links)


class DeviceSynchronizeResource(_OipInstallResource):
    def __init__(self, app):
        _OipInstallResource.__init__(self)
        self._app = app

    @json_request_entity
    def render_POST(self, request, content):
        try:
            id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            deferred = self._app.dev_synchronize(id)
            oip = operation_in_progres_from_deferred(deferred)
            _ignore_deferred_error(deferred)
            location = self._add_new_oip(oip, request)
            return respond_created_no_content(request, location)


class DeviceReconfigureResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app

    @json_request_entity
    def render_POST(self, request, content):
        try:
            id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            def on_callback(ign):
                deferred_respond_no_content(request)
            def on_errback(failure):
                deferred_respond_error(request, failure.value)
            d = self._app.dev_reconfigure(id)
            d.addCallbacks(on_callback, on_errback)
            return NOT_DONE_YET


class DeviceDHCPInfoResource(Resource):
    """Resource for pushing DHCP information into the provisioning server."""
    def __init__(self, dhcp_request_processing_service):
        Resource.__init__(self)
        self._dhcp_req_processing_srv = dhcp_request_processing_service

    def _transform_options(self, raw_options):
        options = {}
        for raw_option in raw_options:
            code = int(raw_option[:3], 10)
            value = ''.join(chr(int(token, 16)) for token in
                            raw_option[3:].split('.'))
            options[code] = value
        return options

    @json_request_entity
    def render_POST(self, request, content):
        try:
            raw_dhcp_info = content[u'dhcp_info']
            op = raw_dhcp_info[u'op']
            ip = norm_ip(raw_dhcp_info[u'ip'])
            if op == u'commit':
                mac = norm_mac(raw_dhcp_info[u'mac'])
                options = self._transform_options(raw_dhcp_info[u'options'])
        except (KeyError, TypeError, ValueError), e:
            logger.warning('Invalid DHCP info content: %s', e)
            return respond_error(request, e)
        else:
            if op == u'commit':
                dhcp_request = {u'ip': ip, u'mac': mac, u'options': options}
                self._dhcp_req_processing_srv.handle_dhcp_request(dhcp_request)
                return respond_no_content(request)
            elif op == u'expiry' or op == u'release':
                # we are keeping this only for compatibility -- release and
                # expiry event doesn't interest us anymore
                return respond_no_content(request)
            else:
                return respond_error(request, 'invalid operation value')


class DevicesResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app

    def getChild(self, path, request):
        return DeviceResource(self._app, path)

    @json_response_entity
    def render_GET(self, request):
        find_arguments = find_arguments_from_request(request)
        def on_callback(devices):
            data = json_dumps({u'devices': list(devices)})
            deferred_respond_ok(request, data)
        def on_errback(failure):
            deferred_respond_error(request, failure.value)
        d = self._app.dev_find(**find_arguments)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET

    @json_request_entity
    def render_POST(self, request, content):
        # XXX praise KeyError
        device = content[u'device']
        def on_callback(id):
            location = uri_append_path(request.path, str(id))
            request.setHeader('Location', location)
            data = json_dumps({u'id': id})
            deferred_respond_ok(request, data, http.CREATED)
        def on_errback(failure):
            deferred_respond_error(request, failure.value)
        d = self._app.dev_insert(device)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET


class DeviceResource(Resource):
    def __init__(self, app, id):
        Resource.__init__(self)
        self._app = app
        self._id = id

    @json_response_entity
    def render_GET(self, request):
        def on_callback(device):
            if device is None:
                deferred_respond_no_resource(request)
            else:
                data = json_dumps({u'device': device})
                deferred_respond_ok(request, data)
        def on_error(failure):
            deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
        d = self._app.dev_retrieve(self._id)
        d.addCallbacks(on_callback, on_error)
        return NOT_DONE_YET

    @json_request_entity
    def render_PUT(self, request, content):
        # XXX praise KeyError
        device = content[u'device']
        # XXX praise TypeError if device not dict
        device[ID_KEY] = self._id
        def on_callback(_):
            deferred_respond_no_content(request)
        def on_errback(failure):
            if failure.check(InvalidIdError):
                deferred_respond_no_resource(request)
            else:
                deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
        d = self._app.dev_update(device)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET

    def render_DELETE(self, request):
        def on_callback(_):
            deferred_respond_no_content(request)
        def on_errback(failure):
            if failure.check(InvalidIdError):
                deferred_respond_no_resource(request)
            else:
                deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
        d = self._app.dev_delete(self._id)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET


def ConfigManagerResource(app):
    links = [(u'cfg.configs', 'configs', ConfigsResource(app)),
             (u'cfg.autocreate', 'autocreate', AutocreateConfigResource(app))]
    return IntermediaryResource(links)


class AutocreateConfigResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app

    @json_request_entity
    def render_POST(self, request, content):
        def on_callback(id):
            location = uri_append_path(request.path, str(id))
            request.setHeader('Location', location)
            data = json_dumps({u'id': id})
            deferred_respond_ok(request, data, http.CREATED)
        def on_errback(failure):
            deferred_respond_error(request, failure.value)
        d = self._app.cfg_create_new()
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET


class ConfigsResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app

    def getChild(self, path, request):
        return ConfigResource(self._app, path)

    @json_response_entity
    def render_GET(self, request):
        find_arguments = find_arguments_from_request(request)
        def on_callback(configs):
            data = json_dumps({u'configs': list(configs)})
            deferred_respond_ok(request, data)
        def on_errback(failure):
            deferred_respond_error(request, failure.value)
        d = self._app.cfg_find(**find_arguments)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET

    @json_request_entity
    def render_POST(self, request, content):
        # XXX praise KeyError
        config = content[u'config']
        def on_callback(id):
            location = uri_append_path(request.path, str(id))
            request.setHeader('Location', location)
            data = json_dumps({u'id': id})
            deferred_respond_ok(request, data, http.CREATED)
        def on_errback(failure):
            deferred_respond_error(request, failure.value)
        d = self._app.cfg_insert(config)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET


class ConfigResource(Resource):
    def __init__(self, app, id):
        Resource.__init__(self)
        self._app = app
        self._id = id

    def getChild(self, path, request):
        if path == 'raw':
            return RawConfigResource(self._app, self._id)
        else:
            return Resource.getChild(self, path, request)

    @json_response_entity
    def render_GET(self, request):
        def on_callback(config):
            if config is None:
                deferred_respond_no_resource(request)
            else:
                data = json_dumps({u'config': config})
                deferred_respond_ok(request, data)
        def on_error(failure):
            deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
        d = self._app.cfg_retrieve(self._id)
        d.addCallbacks(on_callback, on_error)
        return NOT_DONE_YET

    @json_request_entity
    def render_PUT(self, request, content):
        # XXX praise KeyError
        config = content[u'config']
        # XXX praise TypeError if config not dict
        config[ID_KEY] = self._id
        def on_callback(_):
            deferred_respond_no_content(request)
        def on_errback(failure):
            if failure.check(InvalidIdError):
                deferred_respond_no_resource(request)
            else:
                deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
        d = self._app.cfg_update(config)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET

    def render_DELETE(self, request):
        def on_callback(_):
            deferred_respond_no_content(request)
        def on_errback(failure):
            if failure.check(InvalidIdError):
                deferred_respond_no_resource(request)
            else:
                deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
        d = self._app.cfg_delete(self._id)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET


class RawConfigResource(Resource):
    def __init__(self, app, id):
        self._app = app
        self._id = id

    @json_response_entity
    def render_GET(self, request):
        def on_callback(raw_config):
            if raw_config is None:
                deferred_respond_no_resource(request)
            else:
                data = json_dumps({u'raw_config': raw_config})
                deferred_respond_ok(request, data)
        def on_errback(failure):
            deferred_respond_error(request, failure.value, http.INTERNAL_SERVER_ERROR)
            return failure
        d = self._app.cfg_retrieve_raw_config(self._id)
        d.addCallbacks(on_callback, on_errback)
        return NOT_DONE_YET


def PluginManagerResource(app):
    links = [(REL_INSTALL_SRV, 'install', PluginManagerInstallServiceResource(app)),
             (u'pg.plugins', 'plugins', PluginsResource(app.pg_mgr)),
             (u'pg.reload', 'reload', PluginReloadResource(app))]
    return IntermediaryResource(links)


def PluginManagerInstallServiceResource(app):
    install_srv = _PluginManagerInstallServiceAdapter(app)
    pg_mgr_uninstall_res = PluginManagerUninstallResource(app)
    links = [(REL_INSTALL, 'install', InstallResource(install_srv)),
             (REL_UNINSTALL, 'uninstall', pg_mgr_uninstall_res),
             (REL_INSTALLED, 'installed', InstalledResource(install_srv)),
             (REL_INSTALLABLE, 'installable', InstallableResource(install_srv)),
             (REL_UPGRADE, 'upgrade', UpgradeResource(install_srv)),
             (REL_UPDATE, 'update', UpdateResource(install_srv))]
    return IntermediaryResource(links)


class _PluginManagerInstallServiceAdapter(object):
    # Adapt every method of the IService except uninstall
    def __init__(self, app):
        self._app = app

    def install(self, pkg_id):
        return self._app.pg_install(pkg_id)

    def upgrade(self, pkg_id):
        return self._app.pg_upgrade(pkg_id)

    @staticmethod
    def _clean_info(pkg_info):
        return dict((k, v) for (k, v) in pkg_info.iteritems() if k != 'filename')

    @staticmethod
    def _clean_installable_pkgs(pkg_infos):
        clean_info = _PluginManagerInstallServiceAdapter._clean_info
        return dict((k, clean_info(v)) for (k, v) in pkg_infos.iteritems())

    def list_installable(self):
        return self._clean_installable_pkgs(self._app.pg_mgr.list_installable())

    def list_installed(self):
        return self._app.pg_mgr.list_installed()

    def update(self):
        return self._app.pg_mgr.update()


class PluginManagerUninstallResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app

    @json_request_entity
    def render_POST(self, request, content):
        try:
            pkg_id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            def callback(_):
                deferred_respond_no_content(request)
            def errback(failure):
                deferred_respond_error(request, failure.value)
            d = self._app.pg_uninstall(pkg_id)
            d.addCallbacks(callback, errback)
            return NOT_DONE_YET


class PluginsResource(Resource):
    def __init__(self, pg_mgr):
        Resource.__init__(self)
        self._pg_mgr = pg_mgr
        self._childs = dict((pg_id, PluginResource(pg)) for
                            (pg_id, pg) in self._pg_mgr.iteritems())
        # observe plugin loading/unloading and keep a reference to the weakly
        # referenced observer
        self._obs = BasePluginManagerObserver(self._on_plugin_load,
                                              self._on_plugin_unload)
        pg_mgr.attach(self._obs)

    def _on_plugin_load(self, pg_id):
        self._childs[pg_id] = PluginResource(self._pg_mgr[pg_id])

    def _on_plugin_unload(self, pg_id):
        del self._childs[pg_id]

    def getChild(self, path, request):
        try:
            return self._childs[path]
        except KeyError:
            return Resource.getChild(self, path, request)

    @json_response_entity
    def render_GET(self, request):
        plugins = {}
        for pg_id in self._pg_mgr:
            href = uri_append_path(request.path, pg_id)
            links = [{u'rel': u'pg.plugin', 'href': href}]
            plugins[pg_id] = {u'links': links}
        content = {u'plugins': plugins}
        return json_dumps(content)


class PluginReloadResource(Resource):
    def __init__(self, app):
        Resource.__init__(self)
        self._app = app

    @json_request_entity
    def render_POST(self, request, content):
        try:
            id = content[u'id']
        except KeyError:
            return respond_bad_json_entity(request, 'Missing "id" key')
        else:
            def on_callback(ign):
                deferred_respond_no_content(request)
            def on_errback(failure):
                deferred_respond_error(request, failure.value)
            d = self._app.pg_reload(id)
            d.addCallbacks(on_callback, on_errback)
            return NOT_DONE_YET


class PluginInfoResource(Resource):
    def __init__(self, plugin):
        Resource.__init__(self)
        self._plugin = plugin

    @json_response_entity
    def render_GET(self, request):
        return json_dumps({u'plugin_info': self._plugin.info()})


def PluginResource(plugin):
    links = [(u'pg.info', 'info', PluginInfoResource(plugin))]
    if 'install' in plugin.services:
        install_srv = plugin.services['install']
        links.append((REL_INSTALL_SRV, 'install', InstallServiceResource(install_srv)))
    if 'configure' in plugin.services:
        configure_srv = plugin.services['configure']
        links.append((REL_CONFIGURE_SRV, 'configure', ConfigureServiceResource(configure_srv)))
    return IntermediaryResource(links)


def new_server_resource(app, dhcp_request_processing_service):
    """Create and return a new server resource."""
    return ServerResource(app, dhcp_request_processing_service)


class _SimpleRealm(object):
    # implements(IRealm)

    def __init__(self, resource):
        self._resource = resource

    def requestAvatar(self, avatarID, mind, *interfaces):
        if IResource in interfaces:
            return IResource, self._resource, lambda: None
        else:
            raise NotImplementedError()


def new_restricted_server_resource(app, dhcp_request_processing_service,
                                   credentials, realm_name=REALM_NAME):
    """Create and return a new server resource that will be accessible only
    if the given credentials are present in the HTTP requests.
    
    credentials is a (username, password) tuple.
    
    """
    server_resource = ServerResource(app, dhcp_request_processing_service)
    pwd_checker = InMemoryUsernamePasswordDatabaseDontUse()
    pwd_checker.addUser(*credentials)
    realm = _SimpleRealm(server_resource)
    portal = Portal(realm, [pwd_checker])
    credentialFactory = DigestCredentialFactory('MD5', realm_name)
    wrapper = HTTPAuthSessionWrapper(portal, [credentialFactory])
    return wrapper
