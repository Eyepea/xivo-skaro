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
$prefs = new dwho_prefs('operator');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$trunk = strval($prefs->get('trunk', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';

$info = $result = array();

switch($act)
{
	case 'add':
		$appoperator = &$ipbx->get_application('operator');

		$trunk = array();
		$trunk['slt'] = array();
		$trunk['list'] = $appoperator->get_trunk_list(false,null,null,true);

		$result = $fm_save = $error = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('operator',$_QR) === true)
		{
			if($appoperator->set_add($_QR) === false
			|| $appoperator->add() === false)
			{
				$fm_save = false;
				$result = $appoperator->get_result();
				$error = $appoperator->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);
		}

		dwho::load_class('dwho_sort');

		if($trunk['list'] !== false && dwho_ak('trunk',$result) === true)
		{
			$trunk['slt'] = dwho_array_intersect_key($result['trunk'],$trunk['list'],'id');
			if($trunk['slt'] !== false)
			{
				$trunk['list'] = dwho_array_diff_key($trunk['list'],$trunk['slt']);
				$trunksort = new dwho_sort(array('key' => 'identity'));
				uasort($trunk['slt'],array(&$trunksort,'str_usort'));
			}
		}

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appoperator->get_elements());
		$_TPL->set_var('trunk',$trunk);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/operator.js');
		$dhtml->set_js('js/dwho/submenu.js');
		break;

	case 'edit':
		$appoperator = &$ipbx->get_application('operator');

		if(isset($_QR['id']) === false || ($info = $appoperator->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);

		$result = $fm_save = $error = null;
		$return = &$info;

		$trunk = array();
		$trunk['slt'] = array();
		$trunk['list'] = $appoperator->get_trunk_list(false,null,null,true);

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('operator',$_QR) === true)
		{
			$return = &$result;

			if($appoperator->set_edit($_QR) === false
			|| $appoperator->edit() === false)
			{
				$fm_save = false;
				$result = $appoperator->get_result();
				$error = $appoperator->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);
		}

		dwho::load_class('dwho_sort');

		if($trunk['list'] !== false && dwho_ak('trunk',$return) === true)
		{
			$trunk['slt'] = dwho_array_intersect_key($return['trunk'],$trunk['list'],'id');
			if($trunk['slt'] !== false)
			{
				$trunk['list'] = dwho_array_diff_key($trunk['list'],$trunk['slt']);

				$trunksort = new dwho_sort(array('key' => 'identity'));
				uasort($trunk['slt'],array(&$trunksort,'str_usort'));
			}
		}

		$_TPL->set_var('id',$info['operator']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appoperator->get_elements());
		$_TPL->set_var('trunk',$trunk);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/operator.js');
		$dhtml->set_js('js/dwho/submenu.js');
		break;
	case 'delete':
		$param['page'] = $page;

		$appoperator = &$ipbx->get_application('operator');

		if(isset($_QR['id']) === false || $appoperator->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);

		$appoperator->delete();

		$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('operator',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);

		$appoperator = &$ipbx->get_application('operator');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appoperator->get($values[$i]) !== false)
				$appoperator->delete();
		}

		$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);
		break;
	case 'disables':
	case 'enables':
		$param['page'] = $page;
		$disable = $act === 'disables';
		$invdisable = $disable === false;

		if(($values = dwho_issa_val('operator',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);

		$operator = &$ipbx->get_module('operator');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if(($info = $operator->get($values[$i])) !== false)
				$operator->disable($info['id'],$disable);
		}

		$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);
		break;

	// list
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$appoperator = &$ipbx->get_application('operator',null,false);

		$order = array();
		$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list = $appoperator->get_operator_list(null,$order,$limit);
		$total = $appoperator->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/cost_center/operator'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('sort',$sort);
}

$_TPL->set_var('act',$act);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/cost_center/operator');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/cost_center/operator/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
