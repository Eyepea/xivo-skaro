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

$appha = &$_XOBJ->get_application('ha');

$element = $appha->get_elements();

$element['master_ws_login'] = array(
	'default'  => $appha->gen_passphrase(6,true),
	'readonly' => true,
	'class'    => 'it-disabled'
);
$element['master_ws_passwd'] = array(
	'default'  => $appha->gen_passphrase(8),
	'readonly' => true,
	'class'    => 'it-disabled'
);

$info = $appha->get();
$fm_save = $error = null;
if(isset($_QR['fm_send']) === true)
{
	$fm_save = $error = false;
	$return = &$result;

	if($appha->set($_QR) === false)
	{
		$fm_save = false;
		$error = $appha->get_error();
	}
	else
	{
		$fm_save = true;
	}
	$info = $_QR;
}

$_TPL->set_var('element',$element);
$_TPL->set_var('fm_save', $fm_save);
$_TPL->set_var('error', $error);
$_TPL->set_var('info', $info);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/xivo/configuration/manage/ha.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/xivo/configuration');
$menu->set_toolbar('toolbar/xivo/configuration/manage/ha');

$_TPL->set_bloc('main','xivo/configuration/manage/ha');
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');