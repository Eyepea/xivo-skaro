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

dwho::load_class('dwho_prefs');
$prefs = new dwho_prefs('provd_config');

$act = isset($_QR['act']) === true ? $_QR['act']  : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));

$param = array();
$param['act'] = 'list';
$param['page'] = $page;

if($search !== '')
	$param['search'] = $search;

$result = $fm_save = $error = null;

$appprovdconfig = &$_XOBJ->get_application('provdconfig');
$modprovdconfig = &$_XOBJ->get_module('provdconfig');

switch($act)
{
	case 'edit':
		if(isset($_QR['id']) === false || ($info = $appprovdconfig->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/configdevice'),$param);
			
		$_TPL->set_var('id',$_QR['id']);
		$_TPL->set_var('info',$info);
		break;
	case 'delete':
		$param['page'] = $page;

		if(isset($_QR['id']) === false || $appprovdconfig->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/config'),$param);

		$appprovdconfig->delete();

		$_QRY->go($_TPL->url('xivo/configuration/provisioning/configdevice'),$param);
		break;
	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = 20;

		$order = array();
		$order['name'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if (($list = $appprovdconfig->get_config_list($search,$order,$limit)) === false)
			$list = array();
			
		$total = $appprovdconfig->get_cnt();
		
		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/configdevice'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search',$search);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('error',$error);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/xivo/configuration');
$menu->set_toolbar('toolbar/xivo/configuration/provisioning/configdevice');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/xivo/configuration/provisioning/config.js');
$dhtml->set_js('js/dwho/submenu.js');

$_TPL->set_bloc('main','xivo/configuration/provisioning/configdevice/'.$act);
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');

?>
