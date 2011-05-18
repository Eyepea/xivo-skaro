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

$appark   = $ipbx->get_module('parkinglot');
$contexts = $ipbx->get_module('context');
$moh      = $ipbx->get_module('musiconhold');

$act 		  = isset($_QR['act']) === true ? $_QR['act'] : '';
$page 		= isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$search 	= isset($_QR['search']) === true ? strval($_QR['search']) : '';
$context 	= isset($_QR['context']) === true ? strval($_QR['context']) : '';

// default view mode == list
$param = array('act' => 'list');

if($search !== '')
	$param['search'] = $search;
else if($context !== '')
	$param['context'] = $context;

$error    = false;

switch($act)
{
	case 'add':
		$fm_save = true;

		if(isset($_QR['fm_send']) 	 === true 
		&& dwho_issa('parkinglot', $_QR) === true)
		{	
			// save item
			if(($arr = $appark->chk_values($_QR['parkinglot'])) !== false
			&& $appark->add($arr) !== false)
				$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'), $param);

			$error = $appark->get_filter_error();
			$_TPL->set_var('info', $_QR['parkinglot']);
			$fm_save = false;
		}

		$_TPL->set_var('fm_save', $fm_save);
		break;

	case 'edit':
		$fm_save  = true;

		if(isset($_QR['id']) === false || ($info = $appark->get($_QR['id'])) === false)
		{ $_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'), $param); }

		$act = 'edit';
		if(isset($_QR['fm_send']) 		=== true
		&& dwho_issa('parkinglot', $_QR) 	=== true)
		{
			if(($arr = $appark->chk_values($_QR['parkinglot'])) !== false
			&& $appark->edit($_QR['id'], $arr) !== false)
				$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'), $param);

			$fm_save = false;

			// on update error
			$error = $appark->get_filter_error();
			$info  = $_QR['parkinglot'];
			$info['id'] = $_QR['id'];
		}

		$_TPL->set_var('id'      , $info['id']);
		$_TPL->set_var('info'    , $info);
		$_TPL->set_var('fm_save' , $fm_save);
		break;

	case 'delete':
		if(isset($_QR['id']))
			$appark->delete($_QR['id']);

		$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'),$param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('parkinglots',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'),$param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$appark->delete($values[$i]);

		$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'), $param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('parkinglots',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$appark->disable($values[$i]);
			else
				$appark->enable($values[$i]);
		}

		$_QRY->go($_TPL->url('service/ipbx/pbx_services/parkinglot'),$param);
		break;

	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$order = array();
		$order['name'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		//TODO: order, filter
		$list  = $appark->get_all(null,true,$order,$limit);
		$total = $appark->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/general/parkinglot'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act'      , $act);
$_TPL->set_var('contexts' , $contexts->get_all());
$_TPL->set_var('moh'      , $moh->get_all_category(null, false));
$_TPL->set_var('error'    , array('parkinglot' => $error));
$_TPL->set_var('element'  , array('parkinglot' => $appark->get_element()));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/pbx_services/parkinglot');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/pbx_services/parkinglot/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
