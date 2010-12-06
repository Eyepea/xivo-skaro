# -*- coding: UTF-8 -*-

"""Plugin for a bunch of Cisco SCCP phones.

This plugin defines 2 configuration key:

username -- the username to use to download files on cisco.com website
password -- the password to use to download files on cisco.com website

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

import re
from prov2.plugins import StandardPlugin, FetchfwPluginHelper
from prov2.util import norm_mac
from twisted.internet import defer


_TFTP_FILENAME_REGEX = [
    # We known this pattern is not unique to the 7900
    re.compile(r'^SEP[\dA-F]{12}\.cnf\.xml$'),
    re.compile(r'^CTLSEP([\dA-F]{12})\.tlv$'),
    re.compile(r'^ITLSEP([\dA-F]{12})\.tlv$'),
    re.compile(r'^ITLFile\.tlv$'),
    re.compile(r'^g3-tones\.xml$'),
]

def _tftp_identifier(packet):
    filename = packet['filename']
    for regex in _TFTP_FILENAME_REGEX:
        m = regex.match(filename)
        if m:
            dev = {'vendor': 'Cisco'}
            if m.lastindex == 1:
                dev['mac'] = norm_mac(m.group(1))
            return dev


class _TFTPDeviceInfoExtractor(object):
    def extract(self, request, request_type):
        return defer.succeed(_tftp_identifier(request))


class CiscoSccpPlugin(StandardPlugin):
    IS_PLUGIN = True
    
    def __init__(self, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, plugin_dir, gen_cfg, spec_cfg)
        # XXX I think next line could be moved in StandardPlugin
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, gen_cfg.get('http_proxy'))
        if 'username' in spec_cfg and 'password' in spec_cfg:
            self._fetchfw_helper.downloaders['cisco'].set_password(spec_cfg['username'],
                                                                   spec_cfg['password'])
    
    def services(self):
        return self._fetchfw_helper.services()
    
    def tftp_dev_info_extractor(self):
        return _TFTPDeviceInfoExtractor()
    
    def device_types(self):
        return [('Cisco', model, '9.0.3') for model in ('7941G', '7961G')]
