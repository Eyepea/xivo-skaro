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

$access_category = 'pbx_services';
$access_subcategory = 'parkinglot';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$appark = $ipbx->get_module('parkinglot');

$act = $_QRY->get('act');

switch($act)
{
	case 'add':
		$_QRY = &dwho_gct::get('dwho_query');

		$ret = array();
		if(dwho::load_class('dwho_json') === false
		|| ($data = dwho_json::decode($_QRY->get_input(),true)) === false
		|| is_array($data) === false
		|| $data = $appark->chk_values($data) === false
		|| ($id = $appark->add($data)) === false)
		{
			$http_response->set_status_line(500);
			$http_response->send(true);

			header(dwho_json::get_header());
			die($appark->get_filter_error());			
		}

		$_TPL->set_var('list', $id);
		break;

	case 'delete':
		$id = $_QRY->get('id');
		if(is_null($id ))
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		if($appark->delete($id) === 0)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		};

		$http_response->set_status_line(200);
		$http_response->send(true);
		break;

	case 'edit':
		$id = $_QRY->get('id');
		if(is_null($id ))
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		if(($data = $appark->get($id)) === false)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		};

		$ret = array();
		if(dwho::load_class('dwho_json') === false
		|| ($data = dwho_json::decode($_QRY->get_input(),true)) === false
		|| is_array($data) === false
		|| $data = $appark->chk_values($data) === false
		|| ($id = $appark->edit($id, $data)) === false)
		{
			$http_response->set_status_line(500);
			$http_response->send(true);

			header(dwho_json::get_header());
			die($appark->get_filter_error());			
		}

		$http_response->set_status_line(200);
		$http_response->send(true);
		break;

	case 'view':
		$id = $_QRY->get('id');
		if(is_null($id ))
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		if(($data = $appark->get($id)) === false)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		};

		$_TPL->set_var('info', $data);
		break;

	case 'list':
	default:
		$act = 'list';
		
		$order = array('name' => SORT_ASC);
		$list  = $appark->get_all(null,true,$order);

		$_TPL->set_var('list', $list);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
