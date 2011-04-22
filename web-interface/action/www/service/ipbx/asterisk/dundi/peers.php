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

$apppeer = &$ipbx->get_application('dundipeer');

$act 		  = isset($_QR['act']) === true ? $_QR['act'] : '';
$page 		= isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$search 	= isset($_QR['search']) === true ? strval($_QR['search']) : '';
$context 	= isset($_QR['context']) === true ? strval($_QR['context']) : '';

$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/dundi/peers/add.i18n', 'global');

// default view mode == list
$param = array('act' => 'list');

if($search !== '')
	$param['search'] = $search;
else if($context !== '')
	$param['context'] = $context;

$contexts = false;
$error    = false;

$modcert = &$_XOBJ->get_module('certificate');

switch($act)
{
	case 'add':
		$fm_save = true;

		if(isset($_QR['fm_send']) 	 === true 
		&& dwho_issa('dundipeer', $_QR) === true)
		{	
			var_dump($_QR);
			// save item
			if($apppeer->set_add($_QR) === true
			&& $apppeer->add() === true)
				$_QRY->go($_TPL->url('service/ipbx/dundi/peers'), $param);

			$error = $apppeer->get_error();
			$_TPL->set_var('info', $_QR);
			$fm_save = false;
			$_TPL->set_var('fm_save' , $fm_save);
		}

		function pkfilter($key)
		{ return $key['type'] == 'private'; }

		function pubkfilter($key)
		{	return $key['type'] == 'public';	}

		$keys = $modcert->get_keys();
		//var_dump($keys);
		$_TPL->set_var('privkeys', array_filter($keys, "pkfilter"));
		$_TPL->set_var('pubkeys' , array_filter($keys, "pubkfilter"));

		break;

	case 'edit':
		$fm_save  = true;

		if(isset($_QR['id']) === false || ($info = $apppeer->get($_QR['id'])) === false)
		{ $_QRY->go($_TPL->url('service/ipbx/dundi/peers'), $param); }
		
		$act = 'edit';
		if(isset($_QR['fm_send']) 		=== true
		&& dwho_issa('dundipeer', $_QR) 	=== true)
		{
			if($apppeer->set_edit($_QR) === true
			&& $apppeer->edit($_QR['id']) === true)
				$_QRY->go($_TPL->url('service/ipbx/dundi/peers'), $param);

			$fm_save = false;

			// on update error
			$error = $apppeer->get_error();
			$info  = $_QR;
			$info['dundipeer']['id'] = $_QR['id'];
		}

		function pkfilter($key)
		{ return $key['type'] == 'private'; }

		function pubkfilter($key)
		{	return $key['type'] == 'public';	}

		$keys = $modcert->get_keys();
		//var_dump($keys);
		$_TPL->set_var('privkeys', array_filter($keys, "pkfilter"));
		$_TPL->set_var('pubkeys' , array_filter($keys, "pubkfilter"));


		$_TPL->set_var('id'      , $info['dundipeer']['id']);
		$_TPL->set_var('info'    , $info);
		$_TPL->set_var('fm_save' , $fm_save);
		break;

	case 'delete':
		if(isset($_QR['id']))
			$apppeer->delete($_QR['id']);

		$_QRY->go($_TPL->url('service/ipbx/dundi/peers'),$param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('peers',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/dundi/peers'),$param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$apppeer->delete($values[$i]);

		$_QRY->go($_TPL->url('service/ipbx/dundi/peers'), $param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('peers',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/dundi/peers'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$apppeer->disable($values[$i]);
			else
				$apppeer->enable($values[$i]);
		}

		$_QRY->go($_TPL->url('service/ipbx/dundi/peers'),$param);
		break;

	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$order = array();
		$order['macaddr'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list  = $apppeer->get_dundipeer_list(null,$order,$limit);
		$total = $apppeer->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/dundi/peers'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act'      , $act);
$_TPL->set_var('contexts' , $contexts);
$_TPL->set_var('error'    , $error);
$_TPL->set_var('element'  , $apppeer->get_elements());

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/dundi/peers');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/dundi/peers/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
