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

require_once('xivo.php');

if($_USR->mk_active() === false)
	$_QRY->go($_TPL->url('xivo/logoff'));

$file = '/var/backups/pf-xivo/'.$_QR['path'];

if(dwho_file::is_f_r($file) === false)
	die('File not exist.');

header("Content-type: application/force-download");
header("X-Accel-Buffering: yes");
header("X-Accel-Charset: utf-8");
header("X-Accel-Redirect: /dlbackup/".$_QR['path']);

?>