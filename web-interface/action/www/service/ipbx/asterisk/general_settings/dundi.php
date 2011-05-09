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

$dundi   = &$ipbx->get_module('dundi');

$fm_save = null;
$info = $error = array();

if(isset($_QR['fm_send']) === true && dwho_issa('dundi',$_QR) === true)
{
	$fm_save = true;

	if($dundi->edit(1, $_QR['dundi']) === false)
	{
			$info['dundi']    = $_QR['dundi'];
			$fm_save = false;
	}
}

if (!array_key_exists('dundi', $info))
	$info['dundi'] = $dundi->get(1);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('element', array('dundi' => $dundi->get_element()));
$_TPL->set_var('info',$info);
$_TPL->set_var('error',$error);
$_TPL->set_var('countries',dwho_i18n::get_territory_translated_list());

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/general_settings/dundi');
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
