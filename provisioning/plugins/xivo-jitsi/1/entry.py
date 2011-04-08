# -*- coding: UTF-8 -*-

"""Plugin for the Jitsi softphone in version 1.x.

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

# provisioning url: http://<provd_ip>/${uuid}.properties

import os.path
import re
from provd.devices.config import RawConfigError
from provd.devices.pgasso import IMPROBABLE_SUPPORT, PROBABLE_SUPPORT,\
    FULL_SUPPORT, BasePgAssociator
from provd.plugins import StandardPlugin, TemplatePluginHelper
from provd.servers.http import HTTPNoListingFileService
from twisted.internet import defer


class JitsiHTTPDeviceInfoExtractor(object):
    _UA_REGEX = re.compile(r'^Jitsi/(\S+)$')
    _PATH_REGEX = re.compile(r'/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})\.properties$')
    
    def extract(self, request, request_type):
        assert request_type == 'http'
        return defer.succeed(self._do_extract(request))
    
    def _do_extract(self, request):
        ua = request.getHeader('User-Agent')
        if ua:
            dev_info = self._extract_from_ua(ua)
            if dev_info:
                self._extract_from_path(request.path, dev_info)
                return dev_info
        return None
    
    def _extract_from_ua(self, ua):
        # HTTP User-Agent:
        #   "Jitsi/1.0-beta1-nightly.build.3408"
        m = self._UA_REGEX.match(ua)
        if m:
            raw_version, = m.groups()
            return {u'vendor': u'Jitsi',
                    u'model': u'Jitsi',
                    u'version': raw_version.decode('ascii')}
        return None
    
    def _extract_from_path(self, path, dev_info):
        m = self._PATH_REGEX.search(path)
        if m:
            raw_uuid, = m.groups()
            dev_info[u'uuid'] = raw_uuid.decode('ascii')


class JitsiPgAssociator(BasePgAssociator):
    def _do_associate(self, vendor, model, version):
        if vendor == model == u'Jitsi':
            if version.startswith(u'1.'):
                return FULL_SUPPORT
            return PROBABLE_SUPPORT
        return IMPROBABLE_SUPPORT


class JitsiPlugin(StandardPlugin):
    IS_PLUGIN = True
    
    _ENCODING = 'UTF-8'
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        self._tpl_helper = TemplatePluginHelper(plugin_dir)
        
        self.http_service = HTTPNoListingFileService(self._tftpboot_dir)
    
    http_dev_info_extractor = JitsiHTTPDeviceInfoExtractor()
    
    pg_associator = JitsiPgAssociator()
    
    def _device_config_filename(self, device):
        # Return the device specific filename (not pathname) of device
        return device[u'uuid'] + '.properties'
    
    def _check_config(self, raw_config):
        if u'http_port' not in raw_config:
            raise RawConfigError('only support configuration via HTTP')
        if u'sip' not in raw_config:
            raise RawConfigError('must have a sip parameter')
    
    def _check_device(self, device):
        if u'uuid' not in device:
            raise Exception('UUID needed for device configuration')
    
    def configure(self, device, raw_config):
        self._check_config(raw_config)
        self._check_device(device)
        filename = self._device_config_filename(device)
        tpl = self._tpl_helper.get_dev_template(filename, device)
        
        path = os.path.join(self._tftpboot_dir, filename)
        self._tpl_helper.dump(tpl, raw_config, path, self._ENCODING)
    
    def deconfigure(self, device):
        path = os.path.join(self._tftpboot_dir, self._device_config_filename(device))
        try:
            os.remove(path)
        except OSError:
            # ignore
            pass
