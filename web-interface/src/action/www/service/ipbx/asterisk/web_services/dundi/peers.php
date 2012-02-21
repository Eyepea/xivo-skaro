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

$access_category = 'dundi';
$access_subcategory = 'peers';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$apppeer = &$ipbx->get_application('dundipeer');

$act = $_QRY->get('act');

switch($act)
{
	case 'add':
		if($apppeer->add_from_json() === true)
			$status = 200;
		else
			$status = 400;

		$http_response->set_status_line($status);
		$http_response->send(true);

		break;

	case 'edit':
		// TO DO
		break;

	case 'delete':
		if(isset($_QR['id']))
			$apppeer->delete($_QR['id']);
		
		$http_response->set_status_line(200);
		$http_response->send(true);
		
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('peers',$_QR)) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$apppeer->delete($values[$i]);

		
		$http_response->set_status_line(200);
		$http_response->send(true);
		
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('peers',$_QR)) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$apppeer->disable($values[$i]);
			else
				$apppeer->enable($values[$i]);
		}
		
		$http_response->set_status_line(200);
		$http_response->send(true);

		break;

	case 'list':
	default:
		$act = 'list';

		if(($list = $apppeer->get_dundipeer_list()) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
