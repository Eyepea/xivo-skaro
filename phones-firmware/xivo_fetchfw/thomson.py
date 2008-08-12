__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2008  Proformatique

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

import os
import os.path
import shutil
import fetchfw

fw_files = {
	'ST2022': {
		'1.58': "v2022SG.071214.3.58.6.zz",
		'1.59': "v2022SG.080227.3.59.3.zz",
		'1.62': "v2022SG.080619.3.62.3.zz"
	},

	'ST2030': {
		'1.58': "v2030SG.071214.1.58.6.zz",
		'1.59': "v2030SG.080227.1.59.3.zz",
		'1.62': "v2030SG.080619.1.62.3.zz"
	}
}

def thomson_install(firmware):
	try:
		fw_file = fw_files[firmware.model][firmware.version]
	except KeyError:
		fetchfw.die("unsupported model/version (%s/%s)" % (firmware.model, firmware.version))

	assert len(firmware.remote_files) == 1
	zip_path = fetchfw.zip_extract_all(firmware.name, firmware.remote_files[0].path)
	fw_src_path = os.path.join(zip_path, "Binary", fw_file)
	fw_dst_dir = os.path.join(fetchfw.tftp_path, "Thomson", "binary")
	fw_dst_path = os.path.join(fw_dst_dir, fw_file)

	try:
		os.makedirs(fw_dst_dir)
	except OSError:
		pass

	shutil.copy2(fw_src_path, fw_dst_path)

fetchfw.register_install_fn("Thomson", None, thomson_install)
