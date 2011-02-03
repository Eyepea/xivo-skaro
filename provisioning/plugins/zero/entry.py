# -*- coding: UTF-8 -*-

"""Plugin that offers no configuration service and serves TFTP/HTTP requests
in its var/tftpboot directory.

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
from provd.plugins import Plugin
from provd.servers.tftp.service import TFTPFileService
from twisted.web.static import File


# XXX note that right now, this class is the same as the StandardPlugin class,
#     so we should either modify the StandardPlugin class, or make this class
#     inherit from it
class ZeroPlugin(Plugin):
    IS_PLUGIN = True
    
    def __init__(self, app, plugin_dir, gen_cfg, spec_cfg):
        Plugin.__init__(self, app, plugin_dir, gen_cfg, spec_cfg)
        doc_root = os.path.join(self._plugin_dir, 'var', 'tftpboot')
        self.tftp_service = TFTPFileService(doc_root)
        # TODO this permits directory listing, which might or might not be
        #      desirable
        self.http_service = File(doc_root)
