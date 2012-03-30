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

if(xivo_user::chk_acl('settings','configuration') === false)
	$_QRY->go($_TPL->url('statistics/call_center'));

$_I18N->load_file('tpl/www/bloc/statistics/statistics');

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

$appqueue_log = &$ipbx->get_application('queue_log');
if (($interval = $appqueue_log->get_min_and_max_time()) === false)
	$dbegcachedefault = null;
else
	$dbegcachedefault = strtotime($interval['min']);

$_TPL->set_var('defaultdatebegin',date('Y-m',$dbegcachedefault));

switch($act)
{
	case 'add':
		$result = $fm_save = $error = null;

		$queue_sort = array('name' => SORT_ASC);
		$agent_sort = array('name' => SORT_ASC);

		$queue = array();
		$queue['slt'] = array();
		$queuefeatures = &$ipbx->get_module('queuefeatures');
		$queue['list'] = $queuefeatures->get_all(null,true,$queue_sort,null,true);

		$agent = array();
		$agent['slt'] = array();
		$agentfeatures = &$ipbx->get_module('agentfeatures');
		$agent['list'] = $agentfeatures->get_all_assoc();

		$xivouser = array();
		$xivouser['slt'] = array();
		$xivouser['list'] = $_USR->get_all_where(array('meta' => 'admin'),null,true,array('login' => SORT_ASC),null,true);

		$listqos = array();
		if(isset($_QR['fm_send']) === true
		&& dwho_issa('stats_conf',$_QR) === true)
		{
			if($appstats_conf->set_add($_QR) === false
			|| $appstats_conf->add() === false)
			{
				$fm_save = false;
				$result = $appstats_conf->get_result();
				$error  = $appstats_conf->get_error();
				$listqos = isset($result['queue_qos']) ? $result['queue_qos'] : array();
			}
			else
				$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);
		}

		dwho::load_class('dwho_sort');

		if($queue['list'] !== false && dwho_issa('queue',$result) === true
		&& ($queue['slt'] = dwho_array_intersect_key($result['queue'],$queue['list'],'id')) !== false)
			$queue['slt'] = array_keys($queue['slt']);

		if($agent['list'] !== false && dwho_issa('agent',$result) === true
		&&($agent['slt'] = dwho_array_intersect_key($result['agent'],$agent['list'],'id')) !== false)
			$agent['slt'] = array_keys($agent['slt']);

		if($xivouser['list'] !== false && dwho_issa('xivouser',$result) === true
		&&($xivouser['slt'] = dwho_array_intersect_key($result['xivouser'],$xivouser['list'],'id')) !== false)
			$xivouser['slt'] = array_keys($xivouser['slt']);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/statistics/call_center/settings/configuration.js');
		$dhtml->load_js_multiselect_files();

		// timepicker
		$dhtml->set_css('extra-libs/timepicker/jquery-ui-timepicker-addon.css',true);
		$dhtml->set_js('extra-libs/timepicker/jquery-ui-timepicker-addon.js',true);

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appstats_conf->get_elements());
		$_TPL->set_var('listqos',$listqos);
		$_TPL->set_var('queue',$queue);
		$_TPL->set_var('agent',$agent);
		$_TPL->set_var('xivouser',$xivouser);
		break;
	case 'edit':
		if(isset($_QR['id']) === false || ($info = &$appstats_conf->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);

		$queue_qos = false;
		$result = $fm_save = $error = null;
		$return = &$info;

		$queue_sort = array('name' => SORT_ASC);
		$agent_sort = array('name' => SORT_ASC);

		$queue = array();
		$queue['slt'] = array();
		$queuefeatures = &$ipbx->get_module('queuefeatures');
		$queue['list'] = $queuefeatures->get_all(null,true,$queue_sort,null,true);

		$agent = array();
		$agent['slt'] = array();
		$agentfeatures = &$ipbx->get_module('agentfeatures');
		$agent['list'] = $agentfeatures->get_all_assoc();

		$xivouser = array();
		$xivouser['slt'] = array();
		$xivouser['list'] = $_USR->get_all_where(array('meta' => 'admin'),null,true,array('login' => SORT_ASC),null,true);

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('stats_conf',$_QR) === true)
		{
			if($appstats_conf->set_edit($_QR) === false
			|| $appstats_conf->edit() === false)
			{
				$fm_save = false;
				$return = $appstats_conf->get_result();
				$error  = $appstats_conf->get_error();
			}
			else
				$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);
		}

		dwho::load_class('dwho_sort');

		if($queue['list'] !== false && dwho_issa('queue',$return) === true
		&& ($queue['slt'] = dwho_array_intersect_key($return['queue'],$queue['list'],'id')) !== false)
		{
			$queue_qos = $queue['slt'];
			$queue['slt'] = array_keys($queue['slt']);
		}

		$listqos = array();
		if($queue_qos !== false)
		{
			if (isset($return['queue_qos']) === true)
				$listqos = $return['queue_qos'];
			else
			{
				$listq = $return['queue'];
				while($listq)
				{
					$q = array_shift($listq);
					$queue_qos[$q['id']]['stats_qos'] = $q['stats_qos'];
					$listqos[$q['id']] = $q['stats_qos'];
				}
			}
		}

		if($agent['list'] !== false && dwho_issa('agent',$return) === true
		&&($agent['slt'] = dwho_array_intersect_key($return['agent'],$agent['list'],'id')) !== false)
			$agent['slt'] = array_keys($agent['slt']);

		if($xivouser['list'] !== false && dwho_issa('xivouser',$return) === true
		&&($xivouser['slt'] = dwho_array_intersect_key($return['xivouser'],$xivouser['list'],'id')) !== false)
			$xivouser['slt'] = array_keys($xivouser['slt']);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/statistics/call_center/settings/configuration.js');
		$dhtml->load_js_multiselect_files();

		// timepicker
		$dhtml->set_css('extra-libs/timepicker/jquery-ui-timepicker-addon.css',true);
		$dhtml->set_js('extra-libs/timepicker/jquery-ui-timepicker-addon.js',true);

		$_TPL->set_var('info',$info);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('id',$_QR['id']);
		$_TPL->set_var('element',$appstats_conf->get_elements());
		$_TPL->set_var('listqos',$listqos);
		$_TPL->set_var('queue',$queue);
		$_TPL->set_var('agent',$agent);
		$_TPL->set_var('xivouser',$xivouser);
		break;
	case 'delete':
		$param['page'] = $page;

		if(isset($_QR['id']) === false || $appstats_conf->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);

		$appstats_conf->delete();

		$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appstats_conf->get($values[$i]) !== false)
				$appstats_conf->delete();
		}

		$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);
		break;
	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);

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

		$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);
		break;
	case 'list':
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = 10;

		$order = array();
		$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if($search !== '')
			$list = $appstats_conf->get_stats_conf_search($search,null,$order,$limit);
		else
			$list = $appstats_conf->get_stats_conf_list(null,'name',$order,$limit);

		$total = $appstats_conf->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);
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

$_TPL->set_bloc('main','statistics/call_center/settings/configuration/'.$act);
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
