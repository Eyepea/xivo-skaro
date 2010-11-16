# -*- coding: UTF-8 -*-

"""Plugin that offers no configuration service and serves TFTP/HTTP requests
in its var/lib/tftpboot directory.

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

import os.path
from prov2.plugins import Plugin
from prov2.servers.tftp.service import TFTPFileService
from twisted.web.static import File


class ZeroPlugin(Plugin):
    IS_PLUGIN = True
    
    def _doc_root(self):
        return os.path.join(self._plugin_dir, 'var', 'lib', 'tftpboot')
    
    def tftp_service(self):
        return TFTPFileService(self._doc_root())
    
    def http_service(self):
        # FIXME this permits directory listing, which might nobe desirable
        # FIXME also, not sure of what we should do with the content-type
        return File(self._doc_root(), 'text/plain')
