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
$prefs = new dwho_prefs('configregistrar');

$act = isset($_QR['act']) === true ? $_QR['act']  : '';
$page = dwho_uint($prefs->get('page', 1));
$search = strval($prefs->get('search', ''));

$param = array();
$param['act'] = 'list';

$result = $fm_save = $error = null;

$ipbx = &$_SRE->get('ipbx');

$appprovdconfig = &$_XOBJ->get_application('provdconfig');
$modprovdconfig = &$_XOBJ->get_module('provdconfig');

switch($act)
{
	case 'add':
		if(isset($_QR['fm_send']) === true)
		{
			$_QR['config']['X_type'] = 'registrar';
			if($appprovdconfig->set_add($_QR,'registrar') === false
			|| $appprovdconfig->add() === false)
			{
				$fm_save = false;
				$result = $appprovdconfig->get_result('configregistrar');
				$error = $appprovdconfig->get_error('configregistrar');
			}
			else
				$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);
		}

		$_TPL->set_var('info',$result);
		$_TPL->set_var('element',$appprovdconfig->get_elements());
		break;
	case 'edit':
		if(isset($_QR['id']) === false || ($info = $appprovdconfig->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);

		$return = &$info['config'];

		if(isset($_QR['fm_send']) === true)
		{
			$return = &$result;

			$_QR['config']['X_type'] = 'registrar';
			if($appprovdconfig->set_edit($_QR,'registrar') === false
			|| $appprovdconfig->edit() === false)
			{
				$fm_save = false;
				$result = $appprovdconfig->get_result('configregistrar');
				$error = $appprovdconfig->get_error('configregistrar');
			}
			else
				$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);
		}

		$_TPL->set_var('id',$info['config']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('element',$appprovdconfig->get_elements());
		break;
	case 'delete':
		$param['page'] = $page;

		$appprovdconfig = &$_XOBJ->get_application('configregistrar');

		if(isset($_QR['id']) === false || $appprovdconfig->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);

		$appprovdconfig->delete();

		$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('configregistrar',$_QR)) === false)
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);

		$appprovdconfig = &$_XOBJ->get_application('configregistrar');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appprovdconfig->get($values[$i]) !== false)
				$appprovdconfig->delete();
		}

		$_QRY->go($_TPL->url('xivo/configuration/provisioning/configregistrar'),$param);
		break;
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = 20;

		$order = array();
		$order['id'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if (($list = $appprovdconfig->get_config_list($search,$order,$limit,false,false,'registrar')) === false)
			$list = array();
			
		$total = $appprovdconfig->get_cnt();
		
		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('xivo/configuration/provisioning/config'),$param);
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
$menu->set_toolbar('toolbar/xivo/configuration/provisioning/configregistrar');

$_TPL->set_bloc('main','xivo/configuration/provisioning/configregistrar/'.$act);
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');

?>
