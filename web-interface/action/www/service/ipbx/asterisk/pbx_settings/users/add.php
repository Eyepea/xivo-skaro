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

$result = $fm_save = $error = null;

$gmember = $qmember = $rightcall = array();
$gmember['list'] = $qmember['list'] = false;
$gmember['info'] = $qmember['info'] = false;
$gmember['slt'] = $qmember['slt'] = $rightcall['slt'] = array();

$appgroup = &$ipbx->get_application('group',null,false);

if(($groups = $appgroup->get_groups_list(null,
					 array('name' => SORT_ASC),
					 null,
					 true)) !== false)
	$gmember['list'] = $groups;

$appqueue = &$ipbx->get_application('queue',null,false);

if(($queues = $appqueue->get_queues_list(null,
					 array('name' => SORT_ASC),
					 null,
					 true)) !== false)
	$qmember['list'] = $queues;

$apprightcall = &$ipbx->get_application('rightcall',null,false);

$rightcall['list'] = $apprightcall->get_rightcalls_list(null,
							array('name' => SORT_ASC),
							null,
							true);

$queueskills = array();

if(isset($_QR['fm_send']) === true
&& dwho_issa('userfeatures',$_QR) === true
&& dwho_issa('queueskill-skill',$_QR) === true
&& dwho_issa('queueskill-weight',$_QR) === true)
{
	$appqueue = &$ipbx->get_application('queue');
	$queueskills = array();

	// skipping the last one (empty entry)
	$count = count($_QR['queueskill-skill']) - 1;
	for($i = 0; $i < $count; $i++)
	{
		$queueskills[] = array(
			'id'    	=> $_QR['queueskill-skill'][$i],
			'weight'	=> $_QR['queueskill-weight'][$i],
		);
	}
	$_QR['queueskills'] = $queueskills;

	if($appuser->set_add($_QR) === false
	|| $appuser->add() === false)
	{
		$fm_save = false;

		$result = $appuser->get_result();
		$result['dialaction'] = $appuser->get_dialaction_result();
		$result['phonefunckey'] = $appuser->get_phonefunckey_result();

		$error = $appuser->get_error();

		$result['voicemail-option'] = $_QRY->get('voicemail-option');
	} else {
		$ipbx->discuss('xivo[userlist,update]');
		// must reload app_queue
		$ipbx->discuss('module reload app_queue.so');
		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/users'),$param);
	}

}

dwho::load_class('dwho_sort');

if($gmember['list'] !== false && dwho_ak('groupmember',$result) === true)
{
	$gmember['slt'] = dwho_array_intersect_key($result['groupmember'],
						   $gmember['list'],
						   'groupfeaturesid');

	if($gmember['slt'] !== false)
	{
		$gmember['info'] = dwho_array_copy_intersect_key($result['groupmember'],
								 $gmember['slt'],
								 'groupfeaturesid');
		$gmember['list'] = dwho_array_diff_key($gmember['list'],$gmember['slt']);

		$groupsort = new dwho_sort(array('key' => 'name'));
		uasort($gmember['slt'],array(&$groupsort,'str_usort'));
	}
}

if($qmember['list'] !== false && dwho_ak('queuemember',$result) === true)
{
	$qmember['slt'] = dwho_array_intersect_key($result['queuemember'],
						   $qmember['list'],
						   'queuefeaturesid');

	if($qmember['slt'] !== false)
	{
		$qmember['info'] = dwho_array_copy_intersect_key($result['queuemember'],
								 $qmember['slt'],
								 'queuefeaturesid');
		$qmember['list'] = dwho_array_diff_key($qmember['list'],$qmember['slt']);

		$queuesort = new dwho_sort(array('key' => 'name'));
		uasort($qmember['slt'],array(&$queuesort,'str_usort'));
	}
}

if($rightcall['list'] !== false && dwho_ak('rightcall',$result) === true)
{
	$rightcall['slt'] = dwho_array_intersect_key($result['rightcall'],
						     $rightcall['list'],
						     'rightcallid');

	if($rightcall['slt'] !== false)
	{
		$rightcall['list'] = dwho_array_diff_key($rightcall['list'],$rightcall['slt']);

		$rightcallsort = new dwho_sort(array('browse' => 'rightcall','key' => 'name'));
		uasort($rightcall['slt'],array(&$rightcallsort,'str_usort'));
	}
}

$element = $appuser->get_elements();

$general_module   = &$ipbx->get_module('general');
$general = $general_module->get(1);
$element['userfeatures']['timezone']['default'] = $general['timezone'];

if(empty($result) === false)
{
	if(dwho_issa('dialaction',$result) === false || empty($result['dialaction']) === true)
		$result['dialaction'] = null;

	if(dwho_issa('voicemail',$result) === false || empty($result['voicemail']) === true)
		$result['voicemail'] = null;
}
else
	$result = null;


$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/pbx_settings/users/edit.i18n', 'global');

$order_list    = range(1, 20);
$softkeys_list = array(
	'redial'        => $_TPL->bbf('softkey_redial'),
	'newcall'       => $_TPL->bbf('softkey_newcall'),
	'cfwdall'       => $_TPL->bbf('softkey_cfwdall'),
	'cfwdbusy'      => $_TPL->bbf('softkey_cfwdbusy'),
	'cfwdnoanswer'  => $_TPL->bbf('softkey_cfwdnoanswer'),
	'pickup'        => $_TPL->bbf('softkey_pickup'),
	'gpickup'       => $_TPL->bbf('softkey_gpickup'),
	'conflist'      => $_TPL->bbf('softkey_conflist'),
	'dnd'           => $_TPL->bbf('softkey_dnd'),
	'hold'          => $_TPL->bbf('softkey_hold'),
	'endcall'       => $_TPL->bbf('softkey_endcall'),
	'park'          => $_TPL->bbf('softkey_park'),
	'select'        => $_TPL->bbf('softkey_select'),
	'idivert'       => $_TPL->bbf('softkey_idivert'),
	'resume'        => $_TPL->bbf('softkey_resume'),
	'transfer'      => $_TPL->bbf('softkey_transfer'),
	'dirtrfr'       => $_TPL->bbf('softkey_dirtrfr'),
	'answer'        => $_TPL->bbf('softkey_answer'),
	'transvm'       => $_TPL->bbf('softkey_transvm'),
	'private'       => $_TPL->bbf('softkey_private'),
	'meetme'        => $_TPL->bbf('softkey_meetme'),
	'barge'         => $_TPL->bbf('softkey_barge'),
	'cbarge'        => $_TPL->bbf('softkey_cbarge'),
	'conf'          => $_TPL->bbf('softkey_conf'),
	'backjoin'      => $_TPL->bbf('softkey_backjoin'),
);

$appqueue = &$ipbx->get_application('queue');
$element['queueskills'] =  $appqueue->skills_gettree();

$modpark = &$ipbx->get_module('parkinglot');

$_TPL->set_var('queueskills', $queueskills);
$_TPL->set_var('info',$result);
$_TPL->set_var('error',$error);
$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('voicemail',$result['voicemail']);
$_TPL->set_var('dialaction',$result['dialaction']);
$_TPL->set_var('dialaction_from','user');
$_TPL->set_var('groups',$groups);
$_TPL->set_var('gmember',$gmember);
$_TPL->set_var('queues',$queues);
$_TPL->set_var('qmember',$qmember);
$_TPL->set_var('rightcall',$rightcall);
$_TPL->set_var('element',$element);
$_TPL->set_var('agent_list',$appuser->get_agent_list());
$_TPL->set_var('destination_list',$appuser->get_destination_list());
$_TPL->set_var('moh_list',$appuser->get_musiconhold());
$_TPL->set_var('tz_list',$appuser->get_timezones());
$_TPL->set_var('fkidentity_list',$appuser->get_phonefunckey_identity());
$_TPL->set_var('fktype_list',$appuser->get_phonefunckey_type());
$_TPL->set_var('profileclient_list',$appuser->get_profileclient_list());
$_TPL->set_var('order_list', $order_list);
$_TPL->set_var('softkeys_list', $softkeys_list);
$_TPL->set_var('parking_list', $modpark->get_all());

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/uri.js');
$dhtml->set_js('js/dwho/http.js');
$dhtml->set_js('js/dwho/suggest.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/dialaction.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/phonefunckey.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/users.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/lines.js');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->add_js('/bloc/service/ipbx/'.$ipbx->get_name().'/pbx_settings/users/phonefunckey/phonefunckey.js.php');

?>
