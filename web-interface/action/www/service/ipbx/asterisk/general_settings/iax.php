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

$appiax = &$ipbx->get_apprealstatic('iax');
$appgeneraliax = &$appiax->get_module('general');
$modcalllimits = &$ipbx->get_module('iaxcallnumberlimits');
$modpark = &$ipbx->get_module('parkinglot');

$fm_save = $error = null;

$info = $appgeneraliax->get_all_by_category();
$calllimits = $modcalllimits->get_all();

if(isset($_QR['fm_send']) === true)
{
	$fm_save = false;
	
	// calllimits
	$calllimits = array();
	$error  = array('calllimits' => array());

	for($i = 0; $i < count($_QR['calllimits']['destination'])-1; $i++)
	{
		$calllimits[] = array(
			'destination' => $_QR['calllimits']['destination'][$i],
			'netmask'     => $_QR['calllimits']['netmask'][$i],
			'calllimits'  => $_QR['calllimits']['calllimits'][$i]
		);

		if($modcalllimits->chk_values($calllimits[count($calllimits)-1]) === false)
		{ $error['calllimits'][$i] = $modcalllimits->get_filter_error(); continue; }
	}

	// error on call limits
	if(count($error['calllimits']) > 0)
	{
		$fm_save = false;
	} else {
		$modcalllimits->delete_all();

		foreach($calllimits as $_calllimits)
			$modcalllimits->add($_calllimits);

		unset($_QR['calllimits']);

		if(($rs = $appgeneraliax->set_save_all($_QR)) !== false)
		{
			$info = $rs['result'];
			$error = $rs['error'];
			$fm_save = empty($error);
		}
	}
}

$element = $appgeneraliax->get_element();
$element['calllimits'] = $modcalllimits->get_element();

if(dwho_issa('allow',$element) === true
&& dwho_issa('value',$element['allow']) === true
&& isset($info['allow']) === true
&& dwho_has_len($info['allow'],'var_val') === true)
{
	$info['allow']['var_val'] = explode(',',$info['allow']['var_val']);
	$element['allow']['value'] = array_diff($element['allow']['value'],$info['allow']['var_val']);
}

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('info',$info);
$_TPL->set_var('calllimits',$calllimits);
$_TPL->set_var('error',$error);
$_TPL->set_var('element',$element);
$_TPL->set_var('moh_list',$appgeneraliax->get_musiconhold());
$_TPL->set_var('context_list',$appgeneraliax->get_context_list());
$_TPL->set_var('parking_list', $modpark->get_all());

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/general_settings/iax');
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
