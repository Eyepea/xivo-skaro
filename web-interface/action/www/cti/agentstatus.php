<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
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

$act = isset($_QR['act']) === true ? $_QR['act'] : 'listgroup';
$idagentstatus = isset($_QR['idagentstatus']) === true ? dwho_uint($_QR['idagentstatus'],1) : 1;
$idgroup = isset($_QR['idgroup']) === true ? dwho_uint($_QR['idgroup'],1) : 1;
$page = isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;

$param = array();
$param['act'] = 'listgroup';
$param['idagentstatus'] = $idagentstatus;
$param['idgroup'] = $idgroup;

$info = $result = array();
$info['access_status'] = array();
$info['access_status']['info'] = array();
$info['access_status']['slt'] = array();

switch($act)
{
	case 'addgroup':
		$app = &$ipbx->get_application('ctiagentstatusgroup');

		$result = $fm_save = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('agentstatusgroup',$_QR) === true)
		{
			if($app->set_add($_QR) === false
			|| $app->add() === false)
			{
				$fm_save = false;
				$result = $app->get_result();
			}
			else
			{
			    $ipbx->discuss('xivo[cticonfig,update]');
				$_QRY->go($_TPL->url('cti/agentstatus'),$param);
			}
		}

		dwho::load_class('dwho_sort');

		$_TPL->set_var('info',$result);
		$_TPL->set_var('fm_save',$fm_save);
		break;

	case 'editgroup':
		$app = &$ipbx->get_application('ctiagentstatusgroup');

		if(isset($_QR['idgroup']) === false
		|| ($info = $app->get($_QR['idgroup'])) === false)
			$_QRY->go($_TPL->url('cti/agentstatus'),$param);

		$result = $fm_save = null;
		$return = &$info;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('agentstatusgroup',$_QR) === true)
		{
			$return = &$result;
			if($app->set_edit($_QR) === false
			|| $app->edit() === false)
			{
				$fm_save = false;
				$result = $app->get_result();
			}
			else
			{
			    $ipbx->discuss('xivo[cticonfig,update]');
				$_QRY->go($_TPL->url('cti/agentstatus'),$param);
			}
		}

		dwho::load_class('dwho_sort');

		$_TPL->set_var('info',$return);
		$_TPL->set_var('fm_save',$fm_save);
		break;

	case 'deletegroup':
		$param['page'] = $page;

		$app = &$ipbx->get_application('ctiagentstatusgroup');

		if(isset($_QR['idgroup']) === false
		|| ($info = $app->get($_QR['idgroup'])) === false)
			$_QRY->go($_TPL->url('cti/agentstatus'),$param);

		$app->delete();
		$ipbx->discuss('xivo[cticonfig,update]');

		$_QRY->go($_TPL->url('cti/agentstatus'),$param);
		break;

	case 'add':
		$app = &$ipbx->get_application('ctiagentstatus');
		$param['idgroup'] = $idgroup;

		$result = $fm_save = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('agentstatus',$_QR) === true)
		{
		    $_QR['agentstatus']['idgroup'] = $idgroup;
			if($app->set_add($_QR) === false
			|| $app->add() === false)
			{
				$fm_save = false;
				$result = $app->get_result();
				$error = $app->get_error();
				dwho_var_dump($error);
			}
			else
			{
			    $ipbx->discuss('xivo[cticonfig,update]');
				$_QRY->go($_TPL->url('cti/agentstatus'),$param);
			}
		}

		dwho::load_class('dwho_sort');

		$_TPL->set_var('info',$result);
		$_TPL->set_var('fm_save',$fm_save);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->set_js('js/jscolor/jscolor.js');
		break;

	case 'edit':
		$app = &$ipbx->get_application('ctiagentstatus');
		$param['idgroup'] = $idgroup;

		if(isset($_QR['idagentstatus']) === false
		|| ($info = $app->get($_QR['idagentstatus'])) === false)
			$_QRY->go($_TPL->url('cti/agentstatus'),$param);

		$result = $fm_save = null;
		$return = &$info;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('agentstatus',$_QR) === true)
		{
			$return = &$result;

			$_QR['agentstatus']['idgroup'] = $idgroup;

			if($app->set_edit($_QR) === false
			|| $app->edit() === false)
			{
				$fm_save = false;
				$result = $app->get_result();
			}
			else
			{
			    $ipbx->discuss('xivo[cticonfig,update]');
				$_QRY->go($_TPL->url('cti/agentstatus'),$param);
			}
		}

		dwho::load_class('dwho_sort');

		$_TPL->set_var('idagentstatus',$info['agentstatus']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('fm_save',$fm_save);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->set_js('js/jscolor/jscolor.js');
		break;

	case 'delete':
		$param['page'] = $page;

		$app = &$ipbx->get_application('ctiagentstatus');

		if(isset($_QR['idagentstatus']) === false
		|| ($info = $app->get($_QR['idagentstatus'])) === false)
			$_QRY->go($_TPL->url('cti/agentstatus'),$param);

		$app->delete();
	    $ipbx->discuss('xivo[cticonfig,update]');

		$_QRY->go($_TPL->url('cti/agentstatus'),$param);
		break;

	case 'list':
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$app = &$ipbx->get_application('ctiagentstatus',null,false);

		$order = array();
		$order['name'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list = $app->get_agentstatus_list($order,$limit,false,$idgroup);
		$total = $app->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('cti/agentstatus'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		break;

	default:
	case 'listgroup':
		$act = 'listgroup';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$app = &$ipbx->get_application('ctiagentstatusgroup',null,false);

		$order = array();
		$order['name'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list = $app->get_agentstatusgroup_list($order);
		$total = $app->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('cti/agentstatus'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('idgroup',$idgroup);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/cti/menu');

$menu->set_toolbar('toolbar/cti/agentstatus');

$_TPL->set_bloc('main','/cti/agentstatus/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
