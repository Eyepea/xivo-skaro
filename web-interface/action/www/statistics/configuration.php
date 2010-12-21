<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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
$prefs = new dwho_prefs('stats_conf');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';

if($search !== '')
	$param['search'] = $search;

$appstats_conf = &$_XOBJ->get_application('stats_conf');

switch($act)
{
	case 'add':
		$result = $fm_save = null;

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('stats_qos',$_QR) === true
		&& dwho_issa('stats_conf',$_QR) === true
		&& dwho_issa('workhour_start',$_QR) === true
		&& dwho_issa('workhour_end',$_QR) === true)
		{
			if($appstats_conf->set_add($_QR) === false
			|| $appstats_conf->add() === false)
			{
				$fm_save = false;
				$result = $appstats_conf->get_result();
				$error  = $appstats_conf->get_error();
			}
			else
				$_QRY->go($_TPL->url('statistics/configuration'),$param);
		}
		$appqueue = &$ipbx->get_application('queue');
		$list_queue = $appqueue->get_queues_list();
		
		$_TPL->set_var('info'   ,$result);
		$_TPL->set_var('error'  ,$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appstats_conf->get_elements());
		$_TPL->set_var('ls_queue',$list_queue);
		break;
	case 'edit':
		
		if(isset($_QR['id']) === false || ($info = $appstats_conf->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('statistics/configuration'),$param);
			
		$return = $fm_save = null;
		
		$info_hour_start = explode(':',$info['stats_conf']['hour_start']);
		$workhour_start = array();
		$workhour_start['h'] = $info_hour_start[0];
		$workhour_start['m'] = $info_hour_start[1];
		$info_hour_end = explode(':',$info['stats_conf']['hour_end']);
		$workhour_end = array();
		$workhour_end['h'] = $info_hour_end[0];
		$workhour_end['m'] = $info_hour_end[1];
		
		if(isset($_QR['fm_send']) === true 
		&& dwho_issa('stats_qos',$_QR) === true
		&& dwho_issa('stats_conf',$_QR) === true
		&& dwho_issa('workhour_start',$_QR) === true
		&& dwho_issa('workhour_end',$_QR) === true)
		{
			$return = &$info;
			$workhour_start = $_QR['workhour_start'];
			$workhour_end = $_QR['workhour_end'];

			if($appstats_conf->set_edit($_QR) === false
			|| $appstats_conf->edit() === false)
			{
				$fm_save = false;
				$return = $appstats_conf->get_result();
				$error  = $appstats_conf->get_error();
			}
			else
				$_QRY->go($_TPL->url('statistics/configuration'),$param);
		}
		
		$appqueue = &$ipbx->get_application('queue');
		$list_queue = $appqueue->get_queues_list();
		
		$_TPL->set_var('info',$info);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('id',$_QR['id']);
		$_TPL->set_var('element',$appstats_conf->get_elements());	
		$_TPL->set_var('workhour_start',$workhour_start);
		$_TPL->set_var('workhour_end',$workhour_end);	
		$_TPL->set_var('ls_queue',$list_queue);
		
		break;
	case 'delete':
		$param['page'] = $page;

		if(isset($_QR['id']) === false || $appstats_conf->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('statistics/configuration'),$param);

		$appstats_conf->delete();

		$_QRY->go($_TPL->url('statistics/configuration'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/configuration'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appstats_conf->get($values[$i]) !== false)
				$appstats_conf->delete();
		}

		$_QRY->go($_TPL->url('statistics/configuration'),$param);
		break;
	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/configuration'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appstats_conf->get($values[$i]) === false)
				continue;
			else if($act === 'disables')
				$appstats_conf->disable();
			else
				$appstats_conf->enable();
		}

		$_QRY->go($_TPL->url('statistics/configuration'),$param);
		break;
	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$appstats_conf = &$_XOBJ->get_application('stats_conf');

		$order = array();
		$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if($search !== '')
			$list = $appstats_conf->get_stats_conf_search($search,null,$order,$limit);
		else
			$list = $appstats_conf->get_stats_conf_list();		

		$total = $appstats_conf->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('statistics/configuration'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search',$search);
		$_TPL->set_var('sort',$sort);
}

$_TPL->set_var('act',$act);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/xivo/statistics/configuration');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$_TPL->set_bloc('main','statistics/configuration/'.$act);
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
