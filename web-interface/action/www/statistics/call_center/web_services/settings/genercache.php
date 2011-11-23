<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

$access_category = 'call_center';
$access_subcategory = 'genercache';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(xivo::load_class('xivo_statistics',XIVO_PATH_OBJECT,null,false) === false)
	die('Failed to load xivo_statistics object');


$base_memory = memory_get_usage();

$act = $_QRY->get('act');

switch($act)
{
	case 'generbyidconf':
		if (((int) $idconf = $_QRY->get('idconf')) === 0
		|| ($type = $_QRY->get('type')) === null)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		$erase = $_QRY->get('erase');

		$_XS = new xivo_statistics(&$_XOBJ,&$ipbx);
		$_XS->set_idconf($idconf,true);
		echo "Update cache for $type in progress.. \n";
		$_XS->_objectkey = 0;
		$listobject = $_XS->get_list_by_type($type);
		while($listobject !== false && ($object = array_shift($listobject)))
		{
			if (empty($object) === true)
				continue;
			$_XS->update_cache($idconf,$type,$object,(bool) $erase);
			echo "-- memory usage: ", dwho_byte_to(memory_get_usage() - $base_memory), "\n";
		}
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);

}

echo "-- full memory usage: ", dwho_byte_to(memory_get_peak_usage()), "\n";

exit("-- successfully finished --\n");
?>
<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

$access_category = 'call_center';
$access_subcategory = 'genercache';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(xivo::load_class('xivo_statistics',XIVO_PATH_OBJECT,null,false) === false)
	die('Failed to load xivo_statistics object');


$base_memory = memory_get_usage();

$act = $_QRY->get('act');

switch($act)
{
	case 'generbyidconf':
		if (((int) $idconf = $_QRY->get('idconf')) === 0
		|| ($type = $_QRY->get('type')) === null)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		$erase = $_QRY->get('erase');

		$_XS = new xivo_statistics(&$_XOBJ,&$ipbx);
		$_XS->set_idconf($idconf,true);
		echo "Update cache for $type in progress.. \n";
		$_XS->_objectkey = 0;
		$listobject = $_XS->get_list_by_type($type);
		while($listobject !== false && ($object = array_shift($listobject)))
		{
			if (empty($object) === true)
				continue;
			$_XS->update_cache($idconf,$type,$object,(bool) $erase);
			echo "-- memory usage: ", dwho_byte_to(memory_get_usage() - $base_memory), "\n";
		}
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);

}

echo "-- full memory usage: ", dwho_byte_to(memory_get_peak_usage()), "\n";

exit("-- successfully finished --\n");
?>
<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

$access_category = 'settings';
$access_subcategory = 'genercache';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'stats','stats.inc'));
$_XS = new xivo_stats_lib();

$base_memory = memory_get_usage();

$act = $_QRY->get('act');
$erase = $_QRY->get('erase');

switch($act)
{
	case 'generbyidconf':
		if (((int) $idconf = $_QRY->get('idconf')) === 0)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		$_XS->set_idconf($idconf,true);

		$listype = $_XS->get_listtype();
		$nblt = count($listype);
		for($i=0;$i<$nblt;$i++)
		{
			$type = $listype[$i];
			echo "Update cache for $type in progress.. \n";
			$_XS->_objectkey = 0;
			$listobject = $_XS->get_list_by_type($type);
			while($listobject !== false && ($object = array_shift($listobject)))
			{
				if (empty($object) === true)
					continue;
				$_XS->update_cache($idconf,$type,$object,(bool) $erase);
				echo "-- memory usage: ", dwho_byte_to(memory_get_usage() - $base_memory), "\n";
			}
		}
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);

}

echo "-- full memory usage: ", dwho_byte_to(memory_get_peak_usage()), "\n";

exit("-- successfully finished --\n");
?>