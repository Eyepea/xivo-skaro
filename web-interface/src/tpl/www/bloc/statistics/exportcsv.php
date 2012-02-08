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

$url = &$this->get_module('url');

$result = $this->get_var('result');
$date = $this->get_var('date');
$axetype = $this->get_var('axetype');
$name = $this->get_var('name');

if($result === false
|| is_null($name) === true
|| isset($date['dbeg']) === false
|| isset($date['dend']) === false)
	die();

$dbeg = $date['dbeg'];
$dend = $date['dend'];

header('Pragma: no-cache');
header('Cache-Control: private, must-revalidate');
header('Last-Modified: '.
	date('D, d M Y H:i:s',mktime()).' '.
	dwho_i18n::strftime_l('%Z',null));
header('Content-Disposition: attachment; filename=xivo_stats-'.
	$name.'-'.
	$dbeg.'-to-'.
	$dend.
	//dwho_i18n::strftime_l('%Y-%m-%d-%H:%M:%S',null).
	'.csv');
header('Content-Type: text/csv; charset=UTF-8');

ob_start();

if($result === null)
	echo $this->bbf('no_stats-result');
else 
	echo $result;

header('Content-Length: '.ob_get_length());
ob_end_flush();
die();

?>
