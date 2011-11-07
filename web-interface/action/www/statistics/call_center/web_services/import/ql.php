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

dwho::load_class('dwho_http');

$http_response = dwho_http::factory('response');

$act = $_QRY->get('act');
$client = $_QRY->get('client');

if ($client === null
|| ($input = $_QRY->get_input()) === '')
{
	$http_response->set_status_line(400);
	$http_response->send(true);
}

$tmpfile = date('YmdHis').'-'.$client;
$qlogdircache = DWHO_PATH_CACHE_STATS.DWHO_SEP_DIR.'qlog';
$qlogdircacheuser = $qlogdircache.DWHO_SEP_DIR.$client;

if ($_SERVER['CONTENT_TYPE'] === 'application/gzip')
	$tmpfile = $tmpfile.'.gz';

switch($act)
{
	case 'file':
		$qlogdircacheuserqlog = $qlogdircacheuser.DWHO_SEP_DIR.'spool-qlog';
		$qlogfiletmp = $qlogdircacheuserqlog.DWHO_SEP_DIR.$tmpfile;

		if (@file_put_contents($qlogfiletmp.'.tmp' , $input) === false)
		{
			echo 'ERR: Can\'t write data in: '.$qlogfiletmp.'.tmp';
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		rename($qlogfiletmp.'.tmp', $qlogfiletmp);
		break;
	case 'agent':
		$qlogdircacheuseragent = $qlogdircacheuser.DWHO_SEP_DIR.'spool-agent';
		$qlogfiletmp = $qlogdircacheuseragent.DWHO_SEP_DIR.$tmpfile;

		if (@file_put_contents($qlogfiletmp.'.tmp' , $input) === false)
		{
			echo 'ERR: Can\'t write data in: '.$qlogfiletmp.'.tmp';
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		rename($qlogfiletmp.'.tmp', $qlogfiletmp);
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
}

$http_response->set_status_line(200);
$http_response->send(true);

?>
