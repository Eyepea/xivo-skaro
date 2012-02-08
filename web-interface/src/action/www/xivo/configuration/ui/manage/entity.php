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

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(defined('XIVO_LOC_UI_ACTION') === true)
	$act = XIVO_LOC_UI_ACTION;
else
	$act = $_QRY->get('act');

switch($act)
{
	case 'get':
		$appentity = &$_XOBJ->get_application('entity');

		if(isset($_QR['id']) === false)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		if(($info = $appentity->get($_QR['id'],null,$_QRY->get('contexttype'))) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('info',$info);
		$_TPL->set_var('act',$act);
		$_TPL->display('/xivo/configuration/manage/entitylistcontext');
		break;
	case 'list':
	default:
		$act = 'list';
		$appentity = &$_XOBJ->get_application('entity',null,false);

		if(($list = $appentity->get_entities_list()) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
		$_TPL->set_var('except',$_QRY->get('except'));
		$_TPL->set_var('act',$act);
		$_TPL->display('/xivo/configuration/manage/generic');
		break;
}

?>