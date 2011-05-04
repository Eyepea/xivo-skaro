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

switch($act)
{
	case 'update':
		$appdevice = &$ipbx->get_application('device');
		if ($appdevice->update() === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_update'));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_updated'));
		$act = 'list';
		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		break;
	case 'add':
		$appdevice = &$ipbx->get_application('device');
		$modprovdplugin = &$_XOBJ->get_module('provdplugin');
		
		$plugininstalled = $modprovdplugin->get_plugin_installed();

		$result = $fm_save = $error = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('devicefeatures',$_QR) === true)
		{
			if($appdevice->set_add($_QR) === false
			|| $appdevice->add('provd') === false)
			{
				$fm_save = false;
				$result = $appdevice->get_result();
				$error = $appdevice->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		}

		$element = $appdevice->get_elements();

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('plugininstalled',$plugininstalled);
		$_TPL->set_var('element',$element);
		break;
	case 'edit':
		$appdevice = &$ipbx->get_application('device');

		if(isset($_QR['id']) === false || ($info = $appdevice->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
			
		$modprovdplugin = &$_XOBJ->get_module('provdplugin');		
		$plugininstalled = $modprovdplugin->get_plugin_installed();
		
		$appline = &$ipbx->get_application('line');
		$order = array('num' => SORT_ASC);
		$listline = $appline->get_lines_device((int) $_QR['id'],'',null,$order);
		
		$return = &$info;

		$result = $fm_save = $error = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('devicefeatures',$_QR) === true)
		{
			$return = &$result;

			if($appdevice->set_edit($_QR) === false
			|| $appdevice->edit('provd') === false)
			{
				$fm_save = false;
				$result = $appdevice->get_result();
				$error = $appdevice->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
		}
		
		$element = $appdevice->get_elements();

		$_TPL->set_var('id',$info['devicefeatures']['id']);
		$_TPL->set_var('deviceid',$info['devicefeatures']['deviceid']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('plugininstalled',$plugininstalled);
		$_TPL->set_var('listline',$listline);
		$_TPL->set_var('element',$element);
		break;
	case 'delete':
		$param['page'] = $page;

		$appdevice = &$ipbx->get_application('device');

		if(isset($_QR['id']) === false || $appdevice->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);

		$appdevice->delete();

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
			$list = $appdevice->get_devices_search($search,null,$order,$limit);
		else
			$list = $appdevice->get_devices_list(null,$order,$limit);

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
