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
$prefs = new dwho_prefs('servicesgroup');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$trunk 	 = strval($prefs->get('trunk', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';

$info = $result = array();

switch($act)
{
	case 'add':
		$appservicesgroup = &$ipbx->get_application('servicesgroup');
		$appuser = &$ipbx->get_application('user',null,false);

		$user = array();
		$user['slt'] = array();
		$user['list'] = $appuser->get_users_list(null,null,null,null,true);

		$result = $fm_save = $error = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('servicesgroup',$_QR) === true)
		{
			if($appservicesgroup->set_add($_QR) === false
			|| $appservicesgroup->add() === false)
			{
				$fm_save = false;
				$result = $appservicesgroup->get_result();
				$error = $appservicesgroup->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);
		}

		dwho::load_class('dwho_sort');

		if($user['list'] !== false && dwho_ak('user',$result) === true)
		{
			$user['slt'] = dwho_array_intersect_key($result['user'],$user['list'],'id');
			if($user['slt'] !== false)
			{
				$user['list'] = dwho_array_diff_key($user['list'],$user['slt']);
				$usersort = new dwho_sort(array('key' => 'identity'));
				uasort($user['slt'],array(&$usersort,'str_usort'));
			}
		}

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appservicesgroup->get_elements());
		$_TPL->set_var('user',$user);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/servicesgroup.js');
		$dhtml->set_js('js/dwho/submenu.js');
		break;

	case 'edit':
		$appservicesgroup = &$ipbx->get_application('servicesgroup');
		$appuser = &$ipbx->get_application('user',null,false);

		if(isset($_QR['id']) === false || ($info = $appservicesgroup->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);

		$fm_save = $error = null;
		$return = &$info;

		$user = array();
		$user['slt'] = array();
		$user['list'] = $appuser->get_users_list(null,null,null,true);

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('servicesgroup',$_QR) === true)
		{
			if($appservicesgroup->set_edit($_QR) === false
			|| $appservicesgroup->edit() === false)
			{
				$fm_save = false;
				$result = $appservicesgroup->get_result();
				$error = $appservicesgroup->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);
		}

		dwho::load_class('dwho_sort');

		if($user['list'] !== false && dwho_ak('user',$return) === true)
		{
			$user['slt'] = dwho_array_intersect_key($return['user'],$user['list'],'id');
			if($user['slt'] !== false)
			{
				$user['list'] = dwho_array_diff_key($user['list'],$user['slt']);
				$usersort = new dwho_sort(array('key' => 'identity'));
				uasort($user['slt'],array(&$usersort,'str_usort'));
			}
		}

		$_TPL->set_var('id',$info['servicesgroup']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appservicesgroup->get_elements());
		$_TPL->set_var('user',$user);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/servicesgroup.js');
		$dhtml->set_js('js/dwho/submenu.js');
		break;
	case 'delete':
		$param['page'] = $page;

		$appservicesgroup = &$ipbx->get_application('servicesgroup');

		if(isset($_QR['id']) === false || $appservicesgroup->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);

		$appservicesgroup->delete();

		$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('servicesgroup',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);

		$appservicesgroup = &$ipbx->get_application('servicesgroup');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appservicesgroup->get($values[$i]) !== false)
				$appservicesgroup->delete();
		}

		$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);
		break;
	case 'disables':
	case 'enables':
		$param['page'] = $page;
		$disable = $act === 'disables';
		$invdisable = $disable === false;

		if(($values = dwho_issa_val('servicesgroup',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);

		$servicesgroup = &$ipbx->get_module('servicesgroup');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if(($info = $servicesgroup->get($values[$i])) !== false)
				$servicesgroup->disable($info['id'],$disable);
		}

		$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);
		break;
	// list
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$appservicesgroup = &$ipbx->get_application('servicesgroup',null,false);

		$order = array();
		$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list = $appservicesgroup->get_servicesgroup_list(null,$order,$limit);
		$total = $appservicesgroup->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/cost_center/servicesgroup'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('sort',$sort);
}

$_TPL->set_var('act',$act);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/cost_center/servicesgroup');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/cost_center/servicesgroup/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
