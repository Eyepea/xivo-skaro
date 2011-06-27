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
$access_subcategory = 'configure';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$act = $_QRY->get('act');

$provdconfigure = &$_XOBJ->get_module('provdconfigure');

switch($act)
{
	case 'get':
		if (isset($_QR['uri']) === false
		|| ($uri = $_QR['uri']) === ''
		|| (($res = $provdconfigure->get_params($uri))) === false
		|| isset($res['value']) === false)
		{
			dwho_report::push('error',dwho_i18n::babelfish('error_during_get_params',array($value)));
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		die($res['value']);
		break;
	case 'edit':
		if (isset($_QR['uri']) === false
		|| ($uri = $_QR['uri']) === ''
		|| isset($_QR['value']) === false
		|| ($provdconfigure->edit_params($uri,$_QR['value'])) === false)
		{
			dwho_report::push('error',dwho_i18n::babelfish('error_during_edit_params',array($_QR['value'])));
			die(dwho_report::get_message('error'));
		}
		else
		{
			dwho_report::push('info','params_successfully_updated');
			die(dwho_report::get_message('info'));
		}
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
}

?>