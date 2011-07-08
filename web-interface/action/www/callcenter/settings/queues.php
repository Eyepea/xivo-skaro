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
$prefs = new dwho_prefs('queues');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$context = strval($prefs->get('context', ''));
$sort    = $prefs->flipflop('sort', 'name');

$appschedule  = &$ipbx->get_application('schedule');
$appstatus = &$ipbx->get_application('ctistatus');
$ctistatus = array();
foreach($appstatus->get_status_list() as $itm)
{ $ctistatus[$itm['ctistatus']['id']] = $itm['ctistatus']; }

$apppenalty  = &$ipbx->get_application('queuepenalty');

$param = array();
$param['act'] = 'list';

$info = $result = array();

switch($act)
{
	case 'add':
		$appqueue = &$ipbx->get_application('queue');

		$fm_save = $error = null;
		$result = array();

		$pannounce = array();
		$pannounce['list'] = $appqueue->get_announce();
		$pannounce['slt'] = array();

		$user = $agentgroup = $agent = array();
		$user['slt'] = $agentgroup['slt'] = $agent['slt'] = array();

		$userorder = array();
		$userorder['firstname'] = SORT_ASC;
		$userorder['lastname'] = SORT_ASC;
		$userorder['number'] = SORT_ASC;
		$userorder['context'] = SORT_ASC;
		$userorder['name'] = SORT_ASC;

		$appuser = &$ipbx->get_application('user',null,false);
		$user['list'] = $appuser->get_users_list(null,null,$userorder,null,true);

		$appagentgroup = &$ipbx->get_application('agentgroup',null,false);
		$agentgroup['list'] = $appagentgroup->get_agentgroups_list(null,
									   array('name'	=> SORT_ASC),
									   null,
									   true);

		$appagent = &$ipbx->get_application('agent',null,false);
		$agent['list'] = $appagent->get_agents_list(null,
							    array('firstname'	=> SORT_ASC,
								  'lastname'	=> SORT_ASC,
								  'number'	=> SORT_ASC,
								  'context'	=> SORT_ASC),
							    null,
							    true);

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('queuefeatures',$_QR) === true
		&& dwho_issa('queue',$_QR) === true)
		{
			$err = false;
			$errval = array(
				'ctipresence' => array(),
				'nonctipresence' => array()
			);

			$cti = array();
			for($i = 0; $i < count($_QR['ctipresence-name'])-1; $i++)
			{
				$errval['ctipresence'][$i] = array();

				if(strlen($_QR['ctipresence-name'][$i]) == 0)
					{ $err = true; $errval['ctipresence'][$i]['name'] = 'empty'; }
				if(!is_numeric($_QR['ctipresence-weight'][$i]))
					{ $err = true; $errval['ctipresence'][$i]['weight'] = 'cast'; }

				$cti[] = $_QR['ctipresence-name'][$i].':'.$_QR['ctipresence-weight'][$i];
			}
			$_QR['queuefeatures']['ctipresence']    = implode(',',$cti);

			$cti = array();
			for($i = 0; $i < count($_QR['nonctipresence-name'])-1; $i++)
			{
				$errval['nonctipresence'][$i] = array();

				if(strlen($_QR['nonctipresence-name'][$i]) == 0)
					{ $err = true; $errval['nonctipresence'][$i]['name'] = 'empty'; }
				if(!is_numeric($_QR['nonctipresence-weight'][$i]))
					{ $err = true; $errval['nonctipresence'][$i]['weight'] = 'cast'; }

				$cti[] = $_QR['nonctipresence-name'][$i].':'.$_QR['nonctipresence-weight'][$i];
			}
			$_QR['queuefeatures']['nonctipresence']    = implode(',',$cti);

			if(is_array($_QR['queue']['joinempty']))
				$_QR['queue']['joinempty'] = implode(',', $_QR['queue']['joinempty']);
			if(is_array($_QR['queue']['leavewhenempty']))
				$_QR['queue']['leavewhenempty'] = implode(',', $_QR['queue']['leavewhenempty']);

			if($appqueue->set_add($_QR) === false
			|| $err === true
			|| $appqueue->add() === false)
			{
				$fm_save = false;
				$result = $appqueue->get_result();
				$error = array_merge($appqueue->get_error(), $errval);
				$result['dialaction'] = $appqueue->get_dialaction_result();
			}
			else
			{
				// sip reload:: refresh pickup groups
				$ipbx->discuss(array('xivo[queuelist,update]', 'sip reload'));
				$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);
			}
		}

		if($pannounce['list'] !== false
		&& dwho_issa('queue',$result) === true
		&& dwho_ak('periodic-announce',$result['queue']) === true
		&& empty($result['queue']['periodic-announce']) === false)
		{
			if(is_array($result['queue']['periodic-announce']) === false)
				$pannounce['slt'] = explode('|',$result['queue']['periodic-announce']);
			else
				$pannounce['slt'] = $result['queue']['periodic-announce'];

			$pannounce['slt'] = dwho_array_intersect_key(array_flip($pannounce['slt']),
								     $pannounce['list']);

			if(empty($pannounce['slt']) === false)
				$pannounce['list'] = dwho_array_diff_key($pannounce['list'],
									 $pannounce['slt']);
		}

		dwho::load_class('dwho_sort');

		if($user['list'] !== false && dwho_issa('user',$result) === true
		&& ($user['slt'] = dwho_array_intersect_key($result['user'],$user['list'],'userid')) !== false)
			$user['slt'] = array_keys($user['slt']);

		if($agentgroup['list'] !== false && dwho_issa('agentgroup',$result) === true
		&& ($agentgroup['slt'] = dwho_array_intersect_key($result['agentgroup'],$agentgroup['list'],'userid')) !== false)
			$agentgroup['slt'] = array_keys($agentgroup['slt']);

		if($agent['list'] !== false && dwho_issa('agent',$result) === true
		&& ($agent['slt'] = dwho_array_intersect_key($result['agent'],$agent['list'],'userid')) !== false)
			$agent['slt'] = array_keys($agent['slt']);

		if(empty($result) === false)
		{
			if(dwho_issa('dialaction',$result) === false || empty($result['dialaction']) === true)
				$result['dialaction'] = null;

			if(dwho_issa('callerid',$result) === false || empty($result['callerid']) === true)
				$result['callerid'] = null;
		}

		// CTI presences
		if(array_key_exists('queuefeatures', $_QR))
		{
			$pres = array();
			if(strlen($_QR['queuefeatures']['ctipresence']) > 0)
			{
				foreach(split(',',$_QR['queuefeatures']['ctipresence']) as $ctitem)
				{
					list($pid, $num) = explode(':',$ctitem);
					$pres[] = array($ctistatus[$pid], $num);
				}
			}
			$result['queuefeatures']['ctipresence'] = $pres;

			$pres = array();
			if(strlen($_QR['queuefeatures']['nonctipresence']) > 0)
			{
				foreach(split(',',$_QR['queuefeatures']['nonctipresence']) as $ctitem)
				{
					list($pid, $num) = explode(':',$ctitem);
					$pres[] = array($ctistatus[$pid], $num);
				}
			}
			$result['queuefeatures']['nonctipresence'] = $pres;
		}

		if(array_key_exists('queue',$result))
		{
			if(!is_null($result['queue']['joinempty']))
				$result['queue']['joinempty'] = explode(',', $result['queue']['joinempty']);

			if(!is_null($result['queue']['leavewhenempty']))
				$result['queue']['leavewhenempty'] = explode(',', $result['queue']['leavewhenempty']);
		}

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/dwho/suggest.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/dialaction.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/callerid.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/queues.js');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->load_js_multiselect_files();

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		if(array_key_exists('dialaction',$result))
			$_TPL->set_var('dialaction',$result['dialaction']);
		$_TPL->set_var('dialaction_from','queue');
		$_TPL->set_var('element',$appqueue->get_elements());
		$_TPL->set_var('user',$user);
		$_TPL->set_var('agentgroup',$agentgroup);
		$_TPL->set_var('agent',$agent);
		$_TPL->set_var('pannounce',$pannounce);
		$_TPL->set_var('destination_list',$appqueue->get_dialaction_destination_list());
		$_TPL->set_var('moh_list',$appqueue->get_musiconhold());
		$_TPL->set_var('announce_list',$appqueue->get_announce());
		$_TPL->set_var('context_list',$appqueue->get_context_list());
		$_TPL->set_var('ctipresence', $ctistatus);
		$_TPL->set_var('nonctipresence', $ctistatus);
		if(array_key_exists('schedule_id', $result))
			$_TPL->set_var('schedule_id', $result['schedule_id']);
		break;

	case 'edit':
		$appqueue = &$ipbx->get_application('queue');

		if(isset($_QR['id']) === false || ($info = $appqueue->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);

		$result = $fm_save = $error = null;
		$return = &$info;

		$pannounce = array();
		$pannounce['list'] = $appqueue->get_announce();
		$pannounce['slt'] = array();

		$user = $agentgroup = $agent = array();
		$user['slt'] = $agentgroup['slt'] = $agent['slt'] = array();

		$userorder = array();
		$userorder['firstname'] = SORT_ASC;
		$userorder['lastname'] = SORT_ASC;
		$userorder['number'] = SORT_ASC;
		$userorder['context'] = SORT_ASC;
		$userorder['name'] = SORT_ASC;

		$appuser = &$ipbx->get_application('user',null,false);
		$user['list'] = $appuser->get_users_list(null,null,$userorder,null,true);

		$appagentgroup = &$ipbx->get_application('agentgroup',null,false);
		$agentgroup['list'] = $appagentgroup->get_agentgroups_list(null,
									   array('name'	=> SORT_ASC),
									   null,
									   true);

		$appagent = &$ipbx->get_application('agent',null,false);
		$agent['list'] = $appagent->get_agents_list(null,
							    array('firstname'	=> SORT_ASC,
								  'lastname'	=> SORT_ASC,
								  'number'	=> SORT_ASC,
								  'context'	=> SORT_ASC),
							    null,
									true);

		if(isset($_QR['fm_send']) === true
		&& dwho_issa('queuefeatures',$_QR) === true
		&& dwho_issa('queue',$_QR) === true)
		{
			$return = &$result;
			$err = false;
			$errval = array(
				'ctipresence' => array(),
				'nonctipresence' => array()
			);

			$cti = array();
			for($i = 0; $i < count($_QR['ctipresence-name'])-1; $i++)
			{
				$errval['ctipresence'][$i] = array();

				if(strlen($_QR['ctipresence-name'][$i]) == 0)
					{ $err = true; $errval['ctipresence'][$i]['name'] = 'empty'; }
				if(!is_numeric($_QR['ctipresence-weight'][$i]))
					{ $err = true; $errval['ctipresence'][$i]['weight'] = 'cast'; }

				$cti[] = $_QR['ctipresence-name'][$i].':'.$_QR['ctipresence-weight'][$i];
			}
			$_QR['queuefeatures']['ctipresence']    = implode(',',$cti);

			$cti = array();
			for($i = 0; $i < count($_QR['nonctipresence-name'])-1; $i++)
			{
				$errval['nonctipresence'][$i] = array();

				if(strlen($_QR['nonctipresence-name'][$i]) == 0)
					{ $err = true; $errval['nonctipresence'][$i]['name'] = 'empty'; }
				if(!is_numeric($_QR['nonctipresence-weight'][$i]))
					{ $err = true; $errval['nonctipresence'][$i]['weight'] = 'cast'; }

				$cti[] = $_QR['nonctipresence-name'][$i].':'.$_QR['nonctipresence-weight'][$i];
			}
			$_QR['queuefeatures']['nonctipresence']    = implode(',',$cti);

			if(is_array($_QR['queue']['joinempty']))
				$_QR['queue']['joinempty'] = implode(',', $_QR['queue']['joinempty']);
			if(is_array($_QR['queue']['leavewhenempty']))
				$_QR['queue']['leavewhenempty'] = implode(',', $_QR['queue']['leavewhenempty']);

			if($appqueue->set_edit($_QR) === false
			|| $err === true
			|| $appqueue->edit() === false)
			{
				$fm_save = false;
				$result = $appqueue->get_result();
				$error = array_merge($appqueue->get_error(), $errval);
				$result['dialaction'] = $appqueue->get_dialaction_result();
			}
			else
			{
				// sip reload:: refresh pickup groups
				$ipbx->discuss(array('xivo[queuelist,update]', 'sip reload'));
				$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);
			}
		}

		if($pannounce['list'] !== false
		&& dwho_issa('queue',$return) === true
		&& dwho_ak('periodic-announce',$return['queue']) === true
		&& empty($return['queue']['periodic-announce']) === false)
		{
			if(is_array($return['queue']['periodic-announce']) === false)
				$pannounce['slt'] = explode('|',$return['queue']['periodic-announce']);
			else
				$pannounce['slt'] = $return['queue']['periodic-announce'];

			$pannounce['slt'] = dwho_array_intersect_key(array_flip($pannounce['slt']),
								     $pannounce['list']);

			if(empty($pannounce['slt']) === false)
				$pannounce['list'] = dwho_array_diff_key($pannounce['list'],
									 $pannounce['slt']);
		}

		dwho::load_class('dwho_sort');

		if($user['list'] !== false && dwho_issa('user',$return) === true
		&& ($user['slt'] = dwho_array_intersect_key($return['user'],$user['list'],'userid')) !== false)
			$user['slt'] = array_keys($user['slt']);

		if($agentgroup['list'] !== false && dwho_issa('agentgroup',$return) === true
		&& ($agentgroup['slt'] = dwho_array_intersect_key($return['agentgroup'],$agentgroup['list'],'userid')) !== false)
			$agentgroup['slt'] = array_keys($agentgroup['slt']);

		if($agent['list'] !== false && dwho_issa('agent',$return) === true
		&& ($agent['slt'] = dwho_array_intersect_key($return['agent'],$agent['list'],'userid')) !== false)
			$agent['slt'] = array_keys($agent['slt']);

		if(empty($return) === false)
		{
			if(dwho_issa('dialaction',$return) === false || empty($return['dialaction']) === true)
				$return['dialaction'] = null;

			if(dwho_issa('callerid',$return) === false || empty($return['callerid']) === true)
				$return['callerid'] = null;
		}

		// CTI presences
		$pres = array();
		if(strlen($return['queuefeatures']['ctipresence']) > 0)
		{
			foreach(split(',',$return['queuefeatures']['ctipresence']) as $ctitem)
			{
				list($pid, $num) = explode(':',$ctitem);
				$pres[] = array($ctistatus[$pid], $num);
			}
		}
		$return['queuefeatures']['ctipresence'] = $pres;

		$pres = array();
		if(strlen($return['queuefeatures']['nonctipresence']) > 0)
		{
			foreach(split(',',$return['queuefeatures']['nonctipresence']) as $ctitem)
			{
				list($pid, $num) = explode(':',$ctitem);
				$pres[] = array($ctistatus[$pid], $num);
			}
		}
		$return['queuefeatures']['nonctipresence'] = $pres;

		if(!is_null($return['queue']['joinempty']))
			$return['queue']['joinempty'] = explode(',', $return['queue']['joinempty']);

		if(!is_null($return['queue']['leavewhenempty']))
			$return['queue']['leavewhenempty'] = explode(',', $return['queue']['leavewhenempty']);

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/uri.js');
		$dhtml->set_js('js/dwho/http.js');
		$dhtml->set_js('js/dwho/suggest.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/dialaction.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/callerid.js');
		$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/queues.js');
		$dhtml->set_js('js/dwho/submenu.js');
		$dhtml->load_js_multiselect_files();

		$_TPL->set_var('id',$info['queuefeatures']['id']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('dialaction',$return['dialaction']);
		$_TPL->set_var('dialaction_from','queue');
		$_TPL->set_var('element',$appqueue->get_elements());
		$_TPL->set_var('user',$user);
		$_TPL->set_var('agentgroup',$agentgroup);
		$_TPL->set_var('agent',$agent);
		$_TPL->set_var('pannounce',$pannounce);
		$_TPL->set_var('destination_list',$appqueue->get_dialaction_destination_list());
		$_TPL->set_var('moh_list',$appqueue->get_musiconhold());
		$_TPL->set_var('announce_list',$appqueue->get_announce());
		$_TPL->set_var('context_list',$appqueue->get_context_list());
		if(array_key_exists('schedule_id',$return))
			$_TPL->set_var('schedule_id', $return['schedule_id']);
		$_TPL->set_var('ctipresence', $ctistatus);
		$_TPL->set_var('nonctipresence', $ctistatus);
		break;

	case 'delete':
		$param['page'] = $page;

		$appqueue = &$ipbx->get_application('queue');

		if(isset($_QR['id']) === false || $appqueue->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);

		$appqueue->delete();

		// sip reload:: refresh pickup groups
		$ipbx->discuss(array('xivo[queuelist,update]', 'sip reload'));

		$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);
		break;
	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('queues',$_QR)) === false)
			$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);

		$appqueue = &$ipbx->get_application('queue');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appqueue->get($values[$i]) !== false)
				$appqueue->delete();
		}

		// sip reload:: refresh pickup groups
		$ipbx->discuss(array('xivo[queuelist,update]', 'sip reload'));

		$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);
		break;
	case 'disables':
	case 'enables':
		$param['page'] = $page;
		$disable = $act === 'disables';
		$invdisable = $disable === false;

		if(($values = dwho_issa_val('queues',$_QR)) === false)
			$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);

		$queuefeatures = &$ipbx->get_module('queuefeatures');
		$queue = &$ipbx->get_module('queue');

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if(($info = $queuefeatures->get($values[$i])) !== false)
				$queue->disable($info['name'],$disable);
		}

		// sip reload:: refresh pickup groups
		$ipbx->discuss(array('xivo[queuelist,update]', 'sip reload'));

		$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);
		break;
	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$appqueue = &$ipbx->get_application('queue',null,false);

		$order = array();
		$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		$list = $appqueue->get_queues_list(null,$order,$limit);
		$total = $appqueue->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('callcenter/settings/queues'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('sort',$sort);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('schedules',$appschedule->get_schedules_list());
$_TPL->set_var('defaultrules',$apppenalty->get_queuepenalty_list());

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/callcenter/menu');
$menu->set_toolbar('toolbar/callcenter/settings/queues');

$_TPL->set_bloc('main','callcenter/settings/queues/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');
?>
