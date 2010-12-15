# -*- coding: UTF-8 -*-

"""Plugin for a bunch of Cisco SCCP phones.

This plugin defines 2 configuration key:

username -- the username to use to download files on cisco.com website
password -- the password to use to download files on cisco.com website

"""

from __future__ import with_statement

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

import contextlib
import cookielib
import re
import urllib
import urllib2
from fetchfw2.download import DefaultDownloader, InvalidCredentialsError,\
    DownloadError, new_handlers, new_downloaders
from fetchfw2.storage import RemoteFileBuilder
from prov2.plugins import StandardPlugin, FetchfwPluginHelper
from prov2.util import norm_mac
from twisted.internet import defer


class WeakCiscoCredentialsError(DownloadError):
    pass


class CiscoDownloader(DefaultDownloader):
    # XXX no provision for logging right now, that's why there's 'logger' line
    #     commented
    _C14N_LOGIN_URL = 'http://www.cisco.com/cgi-bin/login'
    
    def __init__(self, handlers):
        DefaultDownloader.__init__(self, *handlers)
        self._cookiejar = cookielib.CookieJar()
        self._opener.add_handler(urllib2.HTTPCookieProcessor(self._cookiejar))
        self._form_params = None
        self._is_authenticated = False
    
    def set_password(self, user, passwd):
        self._is_authenticated = False
        self._cookiejar.clear()
        self._form_params = {'USER': user, 'PASSWORD': passwd}
    
    def _do_download(self, url):
        if not self._form_params:
            raise InvalidCredentialsError("no Cisco username/password have been set")
        if not self._is_authenticated:
            self._authenticate()
        assert self._is_authenticated
        f = self._opener.open(url)
        # Cisco website is not using HTTP 4xx status code to signal that we can't access an URL, so...
        if f.info().type == 'text/html':
            f.close()
            raise WeakCiscoCredentialsError("it seems like your Cisco username/password doesn't give you " 
                                            "access to this URL (or this URL might be no longer valid)")
        return f
    
    def _authenticate(self):
        form_url = self._get_form_url()
        data = urllib.urlencode(self._form_params)
        #logger.debug('Trying to authenticate on Cisco website')
        with contextlib.closing(self._opener.open(form_url, data)) as f:
            #logger.debug("Checking for authentication failure - url '%s'", f.geturl())
            for line in f:
                if 'title' in line.lower():
                    if 'login' in line.lower():
                        break
                    else:
                        raise InvalidCredentialsError("authentification failed on Cisco website")
            else:
                #logger.debug("No sign of authentication failure - assuming success")
                pass
        self._is_authenticated = True
        
    def _get_form_url(self):
        # This step is not strictly required but this way we have less chance to be
        # affected by an URL modification
        #logger.debug('Getting Cisco form URL from C14N URL')
        with contextlib.closing(self._opener.open(self._C14N_LOGIN_URL)) as login:
            url = login.geturl()
            #logger.debug("Form URL is '%s'", url)
            return url


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
        
        handlers = new_handlers(gen_cfg.get('http_proxy'))
        dlers = new_downloaders(handlers)
        self._cisco_dler = CiscoDownloader(handlers)
        dlers['x-cisco'] = self._cisco_dler
        rfile_builder = RemoteFileBuilder(dlers) 
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, rfile_builder)
        if 'username' in spec_cfg and 'password' in spec_cfg:
            self._cisco_dler.set_password(spec_cfg['username'], spec_cfg['password'])
        self.services = self._fetchfw_helper.services() 
    
    tftp_dev_info_extractor = _TFTPDeviceInfoExtractor() 
    
    device_types = [('Cisco', model, 'SCCP/9.0.3') for model in ('7941G', '7961G')]
