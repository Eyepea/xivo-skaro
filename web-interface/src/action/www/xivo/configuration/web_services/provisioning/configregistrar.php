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

dwho::load_class('dwho_http');
$http_response = dwho_http::factory('response');

if(isset($_SERVER['REMOTE_ADDR']) === false
|| ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1'
	&& $_SERVER['REMOTE_ADDR'] !== '::1'))
{
	$http_response->set_status_line(403);
	$http_response->send(true);
}

$act = $_QRY->get('act');
$ipbx = &$_SRE->get('ipbx');

switch($act)
{
	case 'rebuild_required_config':
		$provdconfig = &$_XOBJ->get_module('provdconfig');
		$linefeatures = &$ipbx->get_module('linefeatures');
		$devicefeatures = &$ipbx->get_module('devicefeatures');

		$http_response->set_status_line(204);
		if (($list = $linefeatures->get_all_where(array('configregistrar' => 'default'))) !== false
		&& ($nb = count($list)) > 0)
		{
			$res = array();
			for($i=0;$i<$nb;$i++)
			{
				$ref = &$list[$i];
				$deviceid = $ref['device'];
				if (($device = $devicefeatures->get($deviceid)) === false
				|| ($config = $device['config']) === null)
					continue;
				array_push($res,$device['id']);
			}

			$listid = array_unique($res);
			$listid = array_values($listid);

			$nb = count($listid);
			for($i=0;$i<$nb;$i++)
				$provdconfig->rebuild_device_config($listid[$i]);
			$http_response->set_status_line(200);
		}

		$provdconfig->rebuild_required_config();

		$http_response->send(true);
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
}

?>
