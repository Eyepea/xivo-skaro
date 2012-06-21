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

dwho::load_class('dwho_json');

$appreversedir = &$ipbx->get_application('ctireversedirectories');
$appdir = &$ipbx->get_application('ctidirectories');

$fm_save = $error = null;

$dirlist = $appdir->get_directories_list();
$diravail = array();
foreach($dirlist as $v)
{
	$p = $v['ctidirectories'];
	$diravail[] = $p['name'];
}

if(isset($_QR['fm_send']) === true)
{
	$str = '[';
	foreach($_QR['directories'] as $v)
	{
		$str .= '"'.trim($diravail[$v]).'",';
	}
	$str = trim($str, ',');
	$str .= ']';
	$_QR['directories'] = $str;

	if($appreversedir->set($_QR) === false)
	{
		$fm_save = false;
		$error = $appreversedir->get_error();
	}
	else
	{
		$fm_save = true;
	    $ipbx->discuss('xivo[cticonfig,update]');
	}

	$info = $_QR;
}
else
{
	$info = $appreversedir->get();
}

$info['directoriz']['slt'] = array();
$info['directoriz']['list'] = $diravail;

if(isset($info['directories']) && dwho_has_len($info['directories']))
{
	$sel = dwho_json::decode($info['directories'], true);
	$info['directoriz']['slt'] =
		array_intersect(
			$info['directoriz']['list'],$sel);
	$info['directoriz']['list'] =
		array_diff(
			$info['directoriz']['list'],
			$info['directoriz']['slt']);
}

$_TPL->set_var('info'		, $info);
$_TPL->set_var('fm_save'	, $fm_save);
$_TPL->set_var('error'		, $error);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/cti/menu');

$_TPL->set_bloc('main','/cti/reversedirectories');
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
