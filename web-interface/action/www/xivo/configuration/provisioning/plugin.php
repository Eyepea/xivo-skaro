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
$prefs = new dwho_prefs('provd_plugin');

$act = isset($_QR['act']) === true ? $_QR['act']  : 'list';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));

$param = array();
$param['act'] = $act;
$param['page'] = $page;

if($search !== '')
	$param['search'] = $search;
	
$error = false;

$appprovdplugin = &$_XOBJ->get_application('provdplugin');
$provdplugin = &$_XOBJ->get_module('provdplugin');

switch($act)
{
	case 'update':
		if ($provdplugin->update() === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_update'));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_updated'));
		$param['act'] = 'list';
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'upgrade':
		if (isset($_QR['id']) === false
		|| $provdplugin->upgrade($_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_upgrade',array($_QR['id'])));
		else
			dwho_report::push('info',dwho_i18n::babelfish('successfully_upgraded',array($_QR['id'])));
		$param['act'] = 'list';
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'install':
		if (isset($_QR['id']) === false
		|| $provdplugin->install($_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_installation',array($_QR['id'])));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_installed',array($_QR['id'])));
		$param['act'] = 'list';
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'uninstall':
		if (isset($_QR['id']) === false
		|| $provdplugin->uninstall($_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_uninstallation',array($_QR['id'])));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_uninstalled',array($_QR['id'])));
		$param['act'] = 'list';
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'edit':
		if(isset($_QR['id']) === false || ($info = $appprovdplugin->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
			
		$_TPL->set_var('id',$_QR['id']);
		$_TPL->set_var('info',$info);
		break;
	case 'install-pkgs':
		if (isset($_QR['id']) === false
		|| isset($_QR['plugin']) === false
		|| $provdplugin->install_pkgs($_QR['plugin'],$_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_installation',array($_QR['id'])));
		else
			dwho_report::push('info',dwho_i18n::babelfish('successfully_installed',array($_QR['id'])));
			
		$param['act'] = 'edit';
		$param['id'] = $_QR['plugin'];
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'uninstall-pkgs':
		if (isset($_QR['id']) === false
		|| isset($_QR['plugin']) === false
		|| $provdplugin->uninstall_pkgs($_QR['plugin'],$_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_uninstallation',array($_QR['id'])));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_uninstalled',array($_QR['id'])));
			
		$param['act'] = 'edit';
		$param['id'] = $_QR['plugin'];
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = 20;

		$order = array();
		$order['name'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;
		
		$list = $appprovdplugin->get_plugin_list($search,$order,$limit);
		$total = $appprovdplugin->get_cnt();
		
		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search',$search);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('error',$error);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/xivo/configuration');
$menu->set_toolbar('toolbar/xivo/configuration/provisioning/plugin');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/xivo/configuration/provisioning/plugin.js');

$_TPL->set_bloc('main','xivo/configuration/provisioning/plugin/'.$act);
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');

?>
