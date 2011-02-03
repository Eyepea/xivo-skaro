# -*- coding: UTF-8 -*-

"""Plugin that offers no configuration service and rejects TFTP/HTTP requests
by returning file not found errors.

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

from provd.plugins import Plugin
from provd.servers.tftp.service import TFTPNullService
from twisted.web.resource import NoResource


MSG = 'Null plugin always reject requests'

class NullPlugin(Plugin):
    IS_PLUGIN = True
    
    http_service = NoResource(MSG)
    tftp_service = TFTPNullService(errmsg=MSG) 
