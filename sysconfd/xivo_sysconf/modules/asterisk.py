# -*- coding: utf8 -*-
from __future__ import with_statement
"""asterisk stuff-related module
"""
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
	Copyright (C) 2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License along
	with this program; if not, write to the Free Software Foundation, Inc.,
	51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import os, os.path, logging

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW, CMD_R

class Asterisk(object):
	"""
	"""
	def __init__(self):
		super(Asterisk, self).__init__()
		#self.log = logging.getLogger('xivo_sysconf.modules.commonconf')

		http_json_server.register(self.deleteVoicemail, CMD_R,
						name='delete_voicemail', safe_init=self.safe_init)

	def safe_init(self, args):
		pass

	def deleteVoicemail(self, args, options):
		"""Delete spool dir associated with voicemail

			options:
				name    : voicemail name
				context : voicemail context (opt. default is 'default')
		"""
		print args, options
		if 'name' not in options:
			raise HttpReqError(400, "missing 'name' arg", json=True)
		context = options.get('context', 'default')

		vmpath = os.path.join('/var/spool/asterisk/voicemail', context, options['name'])
		if not os.path.exists(vmpath):
			raise HttpReqError(404, "voicemail spool dir not found", json=True)

		for root, dirs, files in os.walk(vmpath, topdown=False):
			for name in files:
				os.remove(os.path.join(root, name))
			for name in dirs:
				os.rmdir(os.path.join(root, name))
		os.rmdir(os.path.join(vmpath))

		return True


asterisk = Asterisk()
