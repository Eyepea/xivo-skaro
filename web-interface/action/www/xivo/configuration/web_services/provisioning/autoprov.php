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

$access_category    = 'provisioning';
$access_subcategory = 'autoprov';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(defined('XIVO_LOC_UI_ACTION') === true)
	$act = XIVO_LOC_UI_ACTION;
else
	$act = $_QRY->get('act');
	
$ipbx = &$_SRE->get('ipbx');

switch($act)
{
	case 'configure':
		$_QRY = &dwho_gct::get('dwho_query');

		if(dwho::load_class('dwho_json') === false
		|| ($data = dwho_json::decode($_QRY->get_input(),true)) === false
		|| is_array($data) === false
		|| isset($data['ip'],$data['code']) === false)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		$provddevice = &$_XOBJ->get_module('provddevice');
		$appdevice = &$ipbx->get_application('device',null,false);
		$linefeatures = &$ipbx->get_module('linefeatures');
		$userfeatures = &$ipbx->get_module('userfeatures');
		$appline = &$ipbx->get_application('line');
		
		$appdevice->update();
		
		if(($device = $appdevice->get_by_ip($data['ip'])) === false
		|| ($devicefeatures = $device['devicefeatures']) === false)
			$http_response->set_status_line(204);
		elseif ($data['code'] === 'autoprov')
		{
			$provddevice->update_configid($devicefeatures['deviceid'],'autoprov');
			$http_response->set_status_line(200);
		}
		elseif(($line = $linefeatures->get_where(array('provisioningid' => $data['code']))) === false
		|| ($rs = $appline->get($line['id'])) === false
		|| ($rs['userfeatures'] = $userfeatures->get($line['iduserfeatures'])) === false
		|| $provddevice->update_config_from_line($rs,$devicefeatures['deviceid']) === false)
			$http_response->set_status_line(204);
		else
			$http_response->set_status_line(200);
		$http_response->send(true);
		break;
	default:
		$http_response->set_status_line(404);
		$http_response->send(true);
}

?>
