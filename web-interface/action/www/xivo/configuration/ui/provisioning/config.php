<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Proformatique <technique@proformatique.com>
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

$access_category = 'provisioning';
$access_subcategory = 'config';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$act = $_QRY->get('act');
$ipbx = &$_SRE->get('ipbx');

$provdconfig = &$_XOBJ->get_module('provdconfig');
$appdevice = &$ipbx->get_application('device',null,false);

switch($act)
{
	case 'getbydeviceid':
		if (isset($_QR['id']) === false
		|| ($device = $appdevice->get($_QR['id'])) === false
		|| isset($device['devicefeatures']) === false
		|| ($deviceid = $device['devicefeatures']['deviceid']) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}
		$_QR['id'] = $deviceid;
	case 'get':
		if (isset($_QR['id']) === false
		|| ($res = $provdconfig->get($_QR['id'])) === false
		|| ($raw_config = $res['raw_config']) === null
		|| isset($raw_config['sip_lines']) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}
		$sip_lines = $raw_config['sip_lines'];
		$_TPL->set_var('act',$act);
		$_TPL->set_var('list',array_keys($sip_lines));
		$_TPL->display('/struct/page/genericjson');
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
}

?>