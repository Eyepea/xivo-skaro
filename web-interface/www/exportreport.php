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

require_once('xivo.php');

$bloc = isset($_QR['bloc']) === false ? '' : $_QR['bloc'];
$type = isset($_QR['type']) === false ? '' : $_QR['type'];

if(($result = dwho_report::get_bloc($type,$bloc)) === false)
	die;

$title = str_replace(' ','_',html_entity_decode(base64_decode($bloc)));

header('Pragma: no-cache');
header('Cache-Control: private, must-revalidate');
header('Last-Modified: '.date('D, d M Y H:i:s',mktime()).' '.dwho_i18n::strftime_l('%Z',null));
header('Content-Disposition: attachment; filename=xivo_report_'.$type.'-'.$title.'.txt');
header('Content-Type: text/txt; charset=UTF-8');

ob_start();

while($result)
	echo html_entity_decode(array_shift($result),ENT_QUOTES),"\n";

header('Content-Length: '.ob_get_length());
ob_end_flush();
die();

?>