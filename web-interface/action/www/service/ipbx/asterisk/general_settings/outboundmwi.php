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

#$appomwi = &$ipbx->get_application('outboundmwi');
$sip = &$ipbx->get_apprealstatic('sip');
$appomwi = $sip->get_module('outboundmwi');

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

$contexts = false;
$error    = false;

switch($act)
{
	case 'add':
		$fm_save = true;

		if(isset($_QR['fm_send']) 	 === true 
		&& dwho_issa('outboundmwi', $_QR) === true)
		{	
			// save item
			if($appomwi->set_outboundmwi($_QR['outboundmwi']) === true
			&& $appomwi->add_outboundmwi() === true)
				$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'), $param);
			
			$error = $appomwi->get_error();
			$_TPL->set_var('info'    , $_QR['outboundmwi']);
			$fm_save = false;
		}

		$_TPL->set_var('fm_save', $fm_save);
		break;

	case 'edit':
		$fm_save  = true;

		// id not set or skillcat[id] not found => redirect to list view
		if(isset($_QR['id']) === false || ($info = $appomwi->get($_QR['id'])) === false)
		{ $_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'), $param); }
		
		$act = 'edit';
		if(isset($_QR['fm_send']) 		=== true
		&& dwho_issa('outboundmwi', $_QR) 	=== true)
		{
			if($appomwi->set_outboundmwi($_QR['outboundmwi']) === true
			&& $appomwi->edit_outboundmwi($_QR['id']) === true)
				$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'), $param);

			$fm_save = false;

			// on update error
			$error = $appomwi->get_error();
			$info  = $_QR['outboundmwi'];
			$info['id'] = $_QR['id'];
		}

		$_TPL->set_var('id'      , $info['id']);
		$_TPL->set_var('info'    , $info);
		$_TPL->set_var('fm_save' , $fm_save);
		break;

	case 'delete':
		if(isset($_QR['id']))
			$appomwi->delete_outboundmwi('delete', $_QR['id']);

		$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'),$param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('outboundmwis',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'),$param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$appomwi->delete_outboundmwi('delete', $values[$i]);

		$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'), $param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('outboundmwis',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$appomwi->disable($values[$i]);
			else
				$appomwi->enable($values[$i]);
		}

		$_QRY->go($_TPL->url('service/ipbx/general_settings/outboundmwi'),$param);
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

		$list  = $appomwi->get_all($order,$limit);
		$total = $appomwi->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/general/outboundmwi'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act'      , $act);
$_TPL->set_var('contexts' , $contexts);
$_TPL->set_var('error'    , $error);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/general_settings/outboundmwi');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/general_settings/outboundmwi/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
