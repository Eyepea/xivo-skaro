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

$apppaging = $ipbx->get_application('paging');

$act = isset($_QR['act']) === true ? $_QR['act'] : '';
$page = isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$search = isset($_QR['search']) === true ? strval($_QR['search']) : '';

// default view mode == list
$param = array('act' => 'list');

if($search !== '')
	$param['search'] = $search;

$error = false;

switch($act)
{
	case 'add':
		$fm_save = true;
		
		$files = array();
		$musiconhold = &$ipbx->get_module('musiconhold');
		if(($listfiles = $musiconhold->get_category('playback')) !== false
		&& ($files = $listfiles['dir']['files']) !== false)
		{
			dwho::load_class('dwho_sort');
			$sort = new dwho_sort(array('key' => 'name'));
			usort($files,array(&$sort,'strnat_usort'));
		}

		$paginguser = array();
		$paginguser['slt'] = array();

		$appuser = &$ipbx->get_application('user',null,false);
		$sort = array('firstname' => SORT_ASC,'lastname' => SORT_ASC);
		$paginguser['list'] = $appuser->get_users_list(null,$sort,null,true);

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('paging', $_QR) === true)
		{
			if($apppaging->set_add($_QR) === false
			|| $apppaging->add() === false)
			{
				$fm_save = false;
				$result = $apppaging->get_result();
				$error = $apppaging->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'),$param);
		}
		
		if($paginguser['list'] !== false && dwho_issa('paginguser',$result) === true)
		{
			$paginguser['slt'] = dwho_array_intersect_key($result['paginguser'],$paginguser['list'],'userfeaturesid');
			$paginguser['slt'] = array_keys($paginguser['slt']);
		}
		
		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/paging.js');
		
		$dhtml->set_css('/extra-libs/multiselect/css/ui.multiselect.css', true);
		$dhtml->set_css('css/xivo.multiselect.css');

		$dhtml->set_js('/extra-libs/multiselect/js/plugins/localisation/jquery.localisation-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/plugins/scrollTo/jquery.scrollTo-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/ui.multiselect.js', true);

		$_TPL->set_var('paginguser',$paginguser);
		$_TPL->set_var('fm_save', $fm_save);
		$_TPL->set_var('error', $error);
		$_TPL->set_var('element', $apppaging->get_elements());
		$_TPL->set_var('files', $files);
		break;

	case 'edit':
		$fm_save  = true;

		if(isset($_QR['id']) === false || ($info = $apppaging->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'), $param);
			
		$return = &$info;

		$files = array();
		$musiconhold = &$ipbx->get_module('musiconhold');
		if(($listfiles = $musiconhold->get_category('playback')) !== false
		&& ($files = $listfiles['dir']['files']) !== false)
		{
			dwho::load_class('dwho_sort');
			$sort = new dwho_sort(array('key' => 'name'));
			usort($files,array(&$sort,'strnat_usort'));
		}

		$paginguser = array();
		$paginguser['slt'] = array();

		$appuser = &$ipbx->get_application('user',null,false);
		$sort = array('firstname' => SORT_ASC,'lastname' => SORT_ASC);
		$paginguser['list'] = $appuser->get_users_list(null,$sort,null,true);

		$act = 'edit';
		if(isset($_QR['fm_send']) === true
		&& dwho_issa('paging', $_QR) === true)
		{
			$return = &$result;
			if($apppaging->set_edit($_QR) === false
			|| $apppaging->edit() === false)
			{
				$fm_save = false;
				$result = $apppaging->get_result();
				$error = $apppaging->get_error();
			}
			else
				$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'),$param);
		}
		
		if($paginguser['list'] !== false && dwho_issa('paginguser',$return) === true)
		{
			$paginguser['slt'] = dwho_array_intersect_key($return['paginguser'],$paginguser['list'],'userfeaturesid');
			$paginguser['slt'] = array_keys($paginguser['slt']);
		}
		
		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/paging.js');
		
		$dhtml->set_css('/extra-libs/multiselect/css/ui.multiselect.css', true);
		$dhtml->set_css('css/xivo.multiselect.css');

		$dhtml->set_js('/extra-libs/multiselect/js/plugins/localisation/jquery.localisation-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/plugins/scrollTo/jquery.scrollTo-min.js', true);
		$dhtml->set_js('/extra-libs/multiselect/js/ui.multiselect.js', true);

		$_TPL->set_var('id', $info['paging']['id']);
		$_TPL->set_var('info', $info);
		$_TPL->set_var('error', $error);
		$_TPL->set_var('files', $files);
		$_TPL->set_var('element', $apppaging->get_elements());
		$_TPL->set_var('paginguser',$paginguser);
		$_TPL->set_var('fm_save' , $fm_save);
		break;

	case 'delete':
		if(isset($_QR['id']))
			$apppaging->delete($_QR['id']);

		$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'),$param);
		break;

	case 'deletes':
		// delete multiple items
		$param['page'] = $page;

		if(($values = dwho_issa_val('pagings',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'),$param);

		$nb = count($values);
		for($i = 0; $i < $nb; $i++)
			$apppaging->delete($values[$i]);

		$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'), $param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('pagings',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($act === 'disables')
				$apppaging->disable($values[$i]);
			else
				$apppaging->enable($values[$i]);
		}

		$_QRY->go($_TPL->url('service/ipbx/pbx_services/paging'),$param);
		break;

	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$order = array();
		$order['number'] = SORT_ASC;

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		//TODO: order, filter
		$list  = $apppaging->get_pagings_list(null,$order,$limit);
		$total = $apppaging->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/general/paging'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search'	, $search);
}

$_TPL->set_var('act', $act);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/pbx_services/paging');

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/pbx_services/paging/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
