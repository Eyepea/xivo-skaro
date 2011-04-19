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

$act = isset($_QR['act']) === true ? $_QR['act']  : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));

$param = array();
$param['act'] = 'list';
$param['page'] = $page;

if($search !== '')
	$param['search'] = $search;

$result = $fm_save = $error = null;

$ipbx = &$_SRE->get('ipbx');	
$provd = &$_XOBJ->get_module('provd');
$provd_plugin = &$provd->get_module('plugin');

$_TPL->set_var('provd_plugin',$provd_plugin);

switch($act)
{
	case 'update':
		if ($provd_plugin->update() === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_update'));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_updated'));
		$param['act'] = 'list';
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'install':
		if (isset($_QR['id']) === false
		|| $provd_plugin->install($_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_installation',array($_QR['id'])));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_installed',array($_QR['id'])));
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'uninstall':
		if (isset($_QR['id']) === false
		|| $provd_plugin->uninstall($_QR['id']) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_uninstallation',array($_QR['id'])));
		else	
			dwho_report::push('info',dwho_i18n::babelfish('successfully_uninstalled',array($_QR['id'])));
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
		break;
	case 'edit':
		if(isset($_QR['id']) === false || ($info = $provd_plugin->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/plugin'),$param);
			
		$_TPL->set_var('id',$_QR['id']);
		$_TPL->set_var('info',$info);
		break;
	case 'install-pkgs':
		if (isset($_QR['id']) === false
		|| isset($_QR['plugin']) === false
		|| $provd_plugin->install_pkgs($_QR['plugin'],$_QR['id']) === false)
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
		|| $provd_plugin->uninstall_pkgs($_QR['plugin'],$_QR['id']) === false)
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

		if (($list_installed = $provd_plugin->get_plugin_installed($search,$order,$limit)) === false)
			$list_installed = array();
		
		if (($list_installable = $provd_plugin->get_plugin_installable($search,$order,$limit,true)) === false)
			$list_installable = array();
		
		$plugins = array();
		$plugins['list'] = $list_installable;
		$plugins['slt'] = dwho_array_intersect_key($list_installed,$plugins['list'],'name');
		$plugins['info'] = false;

		if($plugins['slt'] !== false)
		{
			$plugins['info'] = dwho_array_copy_intersect_key($list_installed,$plugins['slt'],'name');
			$plugins['list'] = dwho_array_diff_key($plugins['list'],$plugins['slt']);
		}
		
		$list = array_merge($plugins['info'],$plugins['list']);
		$list = array_values($list);
				
		$total = count($list);		
		for($i=0;$i<$total;$i++)
		{
			if ($i >= $limit[0] && $i <= ($limit[0]+$limit[1]))
				continue;
			unset($list[$i]);
		}
		
		$list = array_values($list);
		
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
$_TPL->set_var('fm_save',$fm_save);
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
