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

define('DWHO_SESS_ENABLE',false);

require_once('xivo.php');

dwho::load_class('dwho_http');

$conf = &dwho_gat::get('stats_accounts');
$client = $_QRY->get('client');

$http_response = dwho_http::factory('response');

if(isset($_SERVER['PHP_AUTH_USER'],$_SERVER['PHP_AUTH_PW']) === false)
{
	$http_response->authent_basic('Access Restricted');
	$http_response->set_status_line(401);
	$http_response->send(true);
}
elseif (array_key_exists($client, $conf) === false
|| $conf[$client]['login'] !== $_SERVER['PHP_AUTH_USER']
|| $conf[$client]['password'] !== $_SERVER['PHP_AUTH_PW'])
{
	$http_response->set_status_line(403);
	$http_response->send(true);
}

$action_path = $_LOC->get_action_path('statistics/call_center/web_services/',3);

if($action_path === false)
{
	$http_response->set_status_line(404);
	$http_response->send(true);
}

die(include($action_path));

?>
