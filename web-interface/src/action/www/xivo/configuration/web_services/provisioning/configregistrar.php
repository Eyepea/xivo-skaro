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
$provdconfig = &$_XOBJ->get_module('provdconfig');

switch($act)
{
	case 'rebuild_required_config':
		if (!$provdconfig->rebuild_required_config())
			$http_response->set_status_line(400);
		else
			$http_response->set_status_line(200);

		$http_response->send(true);
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
}

?>
