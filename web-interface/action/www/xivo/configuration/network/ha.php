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
$appHA = &$_XOBJ->get_application('ha');

$fm_save    = null;
// XiVO server network interfaces
$netifaces  = $appHA->get_netifaces();
// HA node status
//$status     = $appHA->get_status();

$info = null;
if(isset($_QR['fm_send']) === true)
{
    $fm_save    = true;

		$cnodes = array();
		for($i = 0; $i < count($_QR['cnodes']['device'])-1; $i++)
		{
			$cnodes[] = array(
				'device' => $_QR['cnodes']['device'][$i],
				'address' => $_QR['cnodes']['address'][$i]
			);
		}
		$_QR['cnodes'] = $cnodes;

		foreach($_QR['service'] as $key => &$val)
		{
			if(!isset($val['active']))
				$val['active'] = 0;
			else
				$val['active'] = 1;
		}

		if(!isset($_QR['ha']['cluster_group']))
			$_QR['ha']['cluster_group'] = 0;

//var_dump($_QR); die(1);		
		if($appHA->set($_QR) === false)
		{
			$fm_save = false;
			$_TPL->set_var('error'        , $appHA->get_error());

			$info = $_QR;
    }
}

if(is_null($info))
	$info = $appHA->get();

$_TPL->set_var('fm_save'     , $fm_save);
$_TPL->set_var('info'        , $info);
$_TPL->set_var('netifaces'   , $netifaces);
//$_TPL->set_var('status'      , $status);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/xivo/configuration');

$_TPL->set_bloc('main','xivo/configuration/network/ha');
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');

?>
