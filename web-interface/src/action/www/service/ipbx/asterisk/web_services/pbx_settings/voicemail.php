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

$access_category = 'pbx_settings';
$access_subcategory = 'voicemail';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$act = $_QRY->get('act');

switch($act)
{
	case 'view':
		$appvoicemail = &$ipbx->get_application('voicemail');

		$nocomponents = array('contextmember'	=> true);

		if(($info = $appvoicemail->get($_QRY->get('id'),
					       null,
					       $nocomponents)) === false)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		}

		$_TPL->set_var('info',$info);
		break;
	case 'add':
		$appvoicemail = &$ipbx->get_application('voicemail');

		$status = $appvoicemail->add_from_json() === true ? 200 : 400;

		$http_response->set_status_line($status);
		$http_response->send(true);
		break;
	case 'edit':
		if(XIVO_LOC_WEBSERVICES_MODE !== 'private')
		{
			$http_response->set_status_line(403);
			$http_response->send(true);
		}

		$appvoicemail = &$ipbx->get_application('voicemail');

		if($appvoicemail->get($_QRY->get('id')) === false)
			$status = 404;
		else if($appvoicemail->edit_from_json() === true)
			$status = 200;
		else
			$status = 400;

		$http_response->set_status_line($status);
		$http_response->send(true);
		break;
	case 'delete':
		$appvoicemail = &$ipbx->get_application('voicemail');

		if($appvoicemail->get($_QRY->get('id')) === false)
			$status = 404;
		else if($appvoicemail->delete() === true)
			$status = 200;
		else
			$status = 500;

		$http_response->set_status_line($status);
		$http_response->send(true);
		break;
	case 'search':
		$appvoicemail = &$ipbx->get_application('voicemail',null,false);

		if(($list = $appvoicemail->get_voicemail_search($_QRY->get('search'))) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
		break;
	case 'list':
	default:
		$act = 'list';

		$appvoicemail = &$ipbx->get_application('voicemail',null,false);

		if(($list = $appvoicemail->get_voicemail_list()) === false)
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
