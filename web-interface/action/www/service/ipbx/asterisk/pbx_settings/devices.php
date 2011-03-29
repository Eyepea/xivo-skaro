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
$prefs = new dwho_prefs('devices');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';

if($search !== '')
	$param['search'] = $search;

$contexts = false;

switch($act)
{
	case 'add':
	case 'edit':
		$appdevice = &$ipbx->get_application('device');

		include(dirname(__FILE__).'/devices/'.$act.'.php');
		break;
	case 'delete':
		$param['page'] = $page;

		$appdevice = &$ipbx->get_application('device');

		if(isset($_QR['id']) === false || $appdevice->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);

		$appdevice->delete();

		$ipbx->discuss('xivo[userlist,update]');

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('devices',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);

		$appdevice = &$ipbx->get_application('device');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appdevice->get($values[$i]) !== false)
				$appdevice->delete();
		}

		$ipbx->discuss('xivo[userlist,update]');

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		break;
	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('devices',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);

		$appdevice = &$ipbx->get_application('device',null,false);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appdevice->get($values[$i]) === false)
				continue;
			else if($act === 'disables')
				$appdevice->disable();
			else
				$appdevice->enable();
		}

		$ipbx->discuss('xivo[devicelist,update]');

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		break;
	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$appdevice = &$ipbx->get_application('device');

		$order = array();
		if($sort[1] == 'name')
			$order['name'] = $sort[0];
		else
			$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if($search !== '')
			$list = $appdevice->get_devices_search($search,$context,null,null,$order,$limit);
		else
			$list = $appdevice->get_devices_list(null,null,$order,$limit,null,null);

		$total = $appdevice->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search',$search);
		$_TPL->set_var('sort',$sort);
}

$_TPL->set_var('act',$act);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/pbx_settings/devices');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/pbx_settings/devices/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
