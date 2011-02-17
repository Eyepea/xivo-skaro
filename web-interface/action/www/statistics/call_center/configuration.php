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
		$result = $fm_save = $error = null;

		$incall = array();
		$incall['slt'] = array();		
		$appincall = &$ipbx->get_application('incall');
		$incall['list'] = $appincall->get_incalls_list(null,'exten',null,true);
		
		$queue = array();
		$queue['slt'] = array();		
		$appqueue = &$ipbx->get_application('queue');
		$queue['list'] = $appqueue->get_queues_list(null,'name',null,true);

		$group = array();
		$group['slt'] = array();		
		$appgroup = &$ipbx->get_application('group');
		$group['list'] = $appgroup->get_groups_list(null,'name',null,true);
		
		$agent = array();
		$agent['slt'] = array();		
		$appagent = &$ipbx->get_application('agent');
		$agent['list'] = $appagent->get_agentfeatures(null,'name',null,true);

		$user = array();
		$user['slt'] = array();		
		$appuser = &$ipbx->get_application('user');
		$user['list'] = $appuser->get_users_list(null,null,'name',null,true);
		
		$workhour_start = array();
		$workhour_end = array();
		
		if(isset($_QR['fm_send']) === true
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
		
				$info_hour_start = explode(':',$result['stats_conf']['hour_start']);
				$workhour_start['h'] = $info_hour_start[0];
				$workhour_start['m'] = $info_hour_start[1];
				$info_hour_end = explode(':',$result['stats_conf']['hour_end']);
				$workhour_end['h'] = $info_hour_end[0];
				$workhour_end['m'] = $info_hour_end[1];
			}
			else
				$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
		}

		dwho::load_class('dwho_sort');
		
		if($incall['list'] !== false && dwho_ak('incall',$return) === true)
		{
			$incall['slt'] = dwho_array_intersect_key($return['incall'],$incall['list'],'id');
			if($incall['slt'] !== false)
			{
				$incall['list'] = dwho_array_diff_key($incall['list'],$incall['slt']);
				$incallsort = new dwho_sort(array('key' => 'name'));
				uasort($incall['slt'],array(&$incallsort,'str_usort'));
			}
		}

		$listqos = array();
		if($queue['list'] !== false && dwho_ak('queue',$result) === true)
		{
			$queue['slt'] = dwho_array_intersect_key($result['queue'],$queue['list'],'id');
			if($queue['slt'] !== false)
			{
				$listq = $result['queue'];
				while($listq) 
				{
					$q = array_shift($listq);
					$queue['slt'][$q['id']]['stats_qos'] = $q['stats_qos'];
					$listqos[$q['id']] = $q['stats_qos'];
				}
				$queue['list'] = dwho_array_diff_key($queue['list'],$queue['slt']);
				$queuesort = new dwho_sort(array('key' => 'name'));
				uasort($queue['slt'],array(&$queuesort,'str_usort'));
			}
		}

		if($group['list'] !== false && dwho_ak('group',$result) === true)
		{
			$group['slt'] = dwho_array_intersect_key($result['group'],$group['list'],'id');
			if($group['slt'] !== false)
			{
				$group['list'] = dwho_array_diff_key($group['list'],$group['slt']);
				$queuesort = new dwho_sort(array('key' => 'name'));
				uasort($group['slt'],array(&$queuesort,'str_usort'));
			}
		}

		if($agent['list'] !== false && dwho_ak('agent',$return) === true)
		{
			$agent['slt'] = dwho_array_intersect_key($return['agent'],$agent['list'],'id');
			if($agent['slt'] !== false)
			{
				$agent['list'] = dwho_array_diff_key($agent['list'],$agent['slt']);
				$agentsort = new dwho_sort(array('key' => 'name'));
				uasort($agent['slt'],array(&$agentsort,'str_usort'));
			}
		}

		if($user['list'] !== false && dwho_ak('user',$return) === true)
		{
			$user['slt'] = dwho_array_intersect_key($return['user'],$user['list'],'id');
			if($user['slt'] !== false)
			{
				$user['list'] = dwho_array_diff_key($user['list'],$user['slt']);
				$usersort = new dwho_sort(array('key' => 'name'));
				uasort($user['slt'],array(&$usersort,'str_usort'));
			}
		}
		
		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appstats_conf->get_elements());
		$_TPL->set_var('workhour_start',$workhour_start);
		$_TPL->set_var('workhour_end',$workhour_end);
		$_TPL->set_var('listqos',$listqos);
		$_TPL->set_var('incall',$incall);
		$_TPL->set_var('queue',$queue);
		$_TPL->set_var('group',$group);
		$_TPL->set_var('agent',$agent);
		$_TPL->set_var('user',$user);
		break;
	case 'edit':
		
		if(isset($_QR['id']) === false || ($info = &$appstats_conf->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
		
		$result = $fm_save = $error = null;
		$return = &$info;
		
		$incall = array();
		$incall['slt'] = array();		
		$appincall = &$ipbx->get_application('incall');
		$incall['list'] = $appincall->get_incalls_list(null,'exten',null,true);
		
		$queue = array();
		$queue['slt'] = array();		
		$appqueue = &$ipbx->get_application('queue');
		$queue['list'] = $appqueue->get_queues_list(null,'name',null,true);

		$group = array();
		$group['slt'] = array();		
		$appgroup = &$ipbx->get_application('group');
		$group['list'] = $appgroup->get_groups_list(null,'name',null,true);
		
		$agent = array();
		$agent['slt'] = array();		
		$appagent = &$ipbx->get_application('agent');
		$agent['list'] = $appagent->get_agentfeatures(null,'name',null,true);

		$user = array();
		$user['slt'] = array();		
		$appuser = &$ipbx->get_application('user');
		$user['list'] = $appuser->get_users_list(null,null,'name',null,true);
				
		$workhour_start = array();
		$workhour_end = array();
		
		$info_hour_start = explode(':',$info['stats_conf']['hour_start']);
		$workhour_start['h'] = $info_hour_start[0];
		$workhour_start['m'] = $info_hour_start[1];
		$info_hour_end = explode(':',$info['stats_conf']['hour_end']);
		$workhour_end['h'] = $info_hour_end[0];
		$workhour_end['m'] = $info_hour_end[1];
		
		if(isset($_QR['fm_send']) === true 
		&& dwho_issa('stats_conf',$_QR) === true
		&& dwho_issa('workhour_start',$_QR) === true
		&& dwho_issa('workhour_end',$_QR) === true)
		{
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
				$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);		
		}

		dwho::load_class('dwho_sort');
		
		if($incall['list'] !== false && dwho_ak('incall',$return) === true)
		{
			$incall['slt'] = dwho_array_intersect_key($return['incall'],$incall['list'],'id');
			if($incall['slt'] !== false)
			{
				$incall['list'] = dwho_array_diff_key($incall['list'],$incall['slt']);
				$incallsort = new dwho_sort(array('key' => 'name'));
				uasort($incall['slt'],array(&$incallsort,'str_usort'));
			}
		}

		$listqos = array();
		if($queue['list'] !== false && dwho_ak('queue',$return) === true)
		{
			$queue['slt'] = dwho_array_intersect_key($return['queue'],$queue['list'],'id');
			if($queue['slt'] !== false)
			{
				$listq = $return['queue'];
				while($listq) 
				{
					$q = array_shift($listq);
					$queue['slt'][$q['id']]['stats_qos'] = $q['stats_qos'];
					$listqos[$q['id']] = $q['stats_qos'];
				}
				$queue['list'] = dwho_array_diff_key($queue['list'],$queue['slt']);
				$queuesort = new dwho_sort(array('key' => 'name'));
				uasort($queue['slt'],array(&$queuesort,'str_usort'));
			}
		}
		
		if($group['list'] !== false && dwho_ak('group',$return) === true)
		{
			$group['slt'] = dwho_array_intersect_key($return['group'],$group['list'],'id');
			if($group['slt'] !== false)
			{
				$group['list'] = dwho_array_diff_key($group['list'],$group['slt']);
				$groupsort = new dwho_sort(array('key' => 'name'));
				uasort($group['slt'],array(&$groupsort,'str_usort'));
			}
		}

		if($agent['list'] !== false && dwho_ak('agent',$return) === true)
		{
			$agent['slt'] = dwho_array_intersect_key($return['agent'],$agent['list'],'id');
			if($agent['slt'] !== false)
			{
				$agent['list'] = dwho_array_diff_key($agent['list'],$agent['slt']);
				$agentsort = new dwho_sort(array('key' => 'name'));
				uasort($agent['slt'],array(&$agentsort,'str_usort'));
			}
		}

		if($user['list'] !== false && dwho_ak('user',$return) === true)
		{
			$user['slt'] = dwho_array_intersect_key($return['user'],$user['list'],'id');
			if($user['slt'] !== false)
			{
				$user['list'] = dwho_array_diff_key($user['list'],$user['slt']);
				$usersort = new dwho_sort(array('key' => 'name'));
				uasort($user['slt'],array(&$usersort,'str_usort'));
			}
		}
		
		$_TPL->set_var('info',$info);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('id',$_QR['id']);
		$_TPL->set_var('element',$appstats_conf->get_elements());
		$_TPL->set_var('workhour_start',$workhour_start);
		$_TPL->set_var('workhour_end',$workhour_end);
		$_TPL->set_var('listqos',$listqos);
		$_TPL->set_var('incall',$incall);
		$_TPL->set_var('queue',$queue);
		$_TPL->set_var('group',$group);
		$_TPL->set_var('agent',$agent);
		$_TPL->set_var('user',$user);
		break;
	case 'delete':
		$param['page'] = $page;

		if(isset($_QR['id']) === false || $appstats_conf->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);

		$appstats_conf->delete();

		$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appstats_conf->get($values[$i]) !== false)
				$appstats_conf->delete();
		}

		$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
		break;
	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);

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

		$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
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
			$list = $appstats_conf->get_stats_conf_list(null,'name');	

		$total = $appstats_conf->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
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
$menu->set_toolbar('toolbar/statistics/call_center/configuration');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$_TPL->set_bloc('main','statistics/call_center/configuration/'.$act);
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
