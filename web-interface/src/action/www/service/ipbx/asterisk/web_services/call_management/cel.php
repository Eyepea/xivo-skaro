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

$access_category = 'call_management';
$access_subcategory = 'cel';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$_STS->load_ressource('cel');

$stats_cel = new stats_ressource_cel();
$cel = &$ipbx->get_module('cel');

$act = $_QRY->get('act');
$limit = (!is_null($_QRY->get('limit')) && $_QRY->get('limit') < 5000) ?  $_QRY->get('limit') : 5000;

switch($act)
{
	case 'searchid':
		if(isset($_QR['idbeg']) !== false
		&& ($list = $cel->search_idbeg($_QR['idbeg'],'eventtime',$limit)) !== false)
		{
			if($list === null)
			{
				$http_response->set_status_line(204);
				$http_response->send(true);
			}
		}
		else
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		break;
	case 'search':
		if(($info = $cel->chk_values($_QRY->request_meth_raw(),false)) !== false
		&& ($list = $stats_cel->get_calls_records($info,'eventtime',$limit)) !== false)
		{
			if($list === null)
			{
				$http_response->set_status_line(204);
				$http_response->send(true);
			}
		}
		else
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		break;
	default:
	case 'searchdb':
		if(($info = $cel->chk_values($_QRY->request_meth_raw(),false)) !== false
		&& ($list = $cel->search($info,'eventtime',$limit)) !== false)
		{
			if($list === null)
			{
				$http_response->set_status_line(204);
				$http_response->send(true);
			}
		}
		else
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		break;
}

$_TPL->set_var('list',$list);
$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
