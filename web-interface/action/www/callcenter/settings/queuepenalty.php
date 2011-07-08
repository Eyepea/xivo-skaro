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

$appqpenalties = &$ipbx->get_application('queuepenalty');

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
		&& dwho_issa('queuepenalty', $_QR) === true)
		{
			$changes = array();
			for($i = 0; $i < count($_QR['queuepenalty_seconds'])-1; $i++)
				$changes[] = array(
					'seconds'        => $_QR['queuepenalty_seconds'][$i],
					'maxp_sign'   => $_QR['queuepenalty_maxp_sign'][$i],
					'maxp_value'  => $_QR['queuepenalty_maxp_value'][$i],
					'minp_sign'   => $_QR['queuepenalty_minp_sign'][$i],
					'minp_value'  => $_QR['queuepenalty_minp_value'][$i]
				);
			$_QR['changes'] = $changes;

			// save item
			if($appqpenalties->set_add($_QR) === true
			&& $appqpenalties->add() === true)
				$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'), $param);

			$error = $appqpenalties->get_error();
			$_TPL->set_var('info'    , $_QR);
			$fm_save = false;
		}

		$_TPL->set_var('fm_save', $fm_save);
		break;

	case 'edit':
		$fm_save  = true;

		if(isset($_QR['id']) === false || ($info = $appqpenalties->get($_QR['id'])) === false)
		{ $_QRY->go($_TPL->url('callcenter/settings/queuepenalty'), $param); }

		$act = 'edit';
		if(isset($_QR['fm_send']) 		=== true
		&& dwho_issa('queuepenalty', $_QR) 	=== true)
		{
			$changes = array();
			for($i = 0; $i < count($_QR['queuepenalty_seconds'])-1; $i++)
				$changes[] = array(
					'seconds'        => $_QR['queuepenalty_seconds'][$i],
					'maxp_sign'   => $_QR['queuepenalty_maxp_sign'][$i],
					'maxp_value'  => $_QR['queuepenalty_maxp_value'][$i],
					'minp_sign'   => $_QR['queuepenalty_minp_sign'][$i],
					'minp_value'  => $_QR['queuepenalty_minp_value'][$i]
				);
			$_QR['changes'] = $changes;

			if($appqpenalties->set_edit($_QR) === true
			&& $appqpenalties->edit($_QR['id']) === true)
				$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'), $param);

			$fm_save = false;

			// on update error
			$error = $appqpenalties->get_error();
			$info  = $_QR;
			$info['queuepenalty']['id'] = $_QR['id'];
		}

		$_TPL->set_var('id'      , $info['queuepenalty']['id']);
		$_TPL->set_var('info'    , $info);
		$_TPL->set_var('fm_save' , $fm_save);
		break;

	case 'delete':
		if(isset($_QR['id']))
			$appqpenalties->delete($_QR['id']);

		$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'),$param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('queuepenalty',$_QR)) === false)
			$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'),$param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$appqpenalties->delete($values[$i]);

		$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'), $param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('queuepenalty',$_QR)) === false)
			$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$appqpenalties->disable($values[$i]);
			else
				$appqpenalties->enable($values[$i]);
		}

		$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'),$param);
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

		$list  = $appqpenalties->get_queuepenalty_list($order,$limit);
		$total = $appqpenalties->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('callcenter/settings/queuepenalty'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act'      , $act);
$_TPL->set_var('contexts' , $contexts);
$_TPL->set_var('error'    , $error);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/callcenter/menu');
$menu->set_toolbar('toolbar/callcenter/settings/queuepenalty');

$_TPL->set_bloc('main','callcenter/settings/queuepenalty/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
