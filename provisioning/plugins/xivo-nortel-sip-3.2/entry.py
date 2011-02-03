# -*- coding: UTF-8 -*-

"""Plugin for Nortel IP Phone 1220 SIP 3.2.

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

import urllib2
from fetchfw.download import DownloadError, new_handlers, new_downloaders
from fetchfw.storage import RemoteFileBuilder
from provd.plugins import StandardPlugin, FetchfwPluginHelper


class NortelDownloader(object):
    def __init__(self, downloader):
        self._downloader = downloader
        self._nnAkamaiAuth_keys = {}
        
    def add_auth_key(self, url, auth_key):
        self._nnAkamaiAuth_keys[url] = auth_key
    
    def download(self, url):
        if url not in self._nnAkamaiAuth_keys:
            raise DownloadError("missing nnAkamaiAuth key to download '%s'" % url)
        request = urllib2.Request(url)
        request.add_header('Cookie',  'nnAkamaiAuth=' + self._nnAkamaiAuth_keys[url])
        return self._downloader.download(request)


class NortelEnhancedRemoteFileBuilder(object):
    def __init__(self, rfile_builder, nortel_dler):
        self._rfile_builder = rfile_builder 
        self._nortel_dler = nortel_dler
        
    def build_remote_file(self, config, section):
        rfile = self._rfile_builder.build_remote_file(config, section)
        if config.has_option('x-nnAkamaiAuth'):
            self._nortel_dler.add_auth_key(rfile.url, config.get(section, 'x-nnAkamaiAuth'))
        return rfile


class NortelPlugin(StandardPlugin):
    # XXX incomplete... only the IDownloadService is available right now... no
    #     device configuration...
    IS_PLUGIN = True
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        StandardPlugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        
        handlers = new_handlers(gen_cfg.get('http_proxy'))
        dlers = new_downloaders(handlers)
        nortel_dler = NortelDownloader(handlers)
        dlers['x-nortel'] = nortel_dler
        rfile_builder = RemoteFileBuilder(dlers)
        enhanced_rfile_builder = NortelEnhancedRemoteFileBuilder(rfile_builder, nortel_dler) 
        self._fetchfw_helper = FetchfwPluginHelper(plugin_dir, enhanced_rfile_builder)
        self.services = self._fetchfw_helper.services()

    device_types = [('Nortel', model, 'SIP/3.2') for model in ('1220',)]
