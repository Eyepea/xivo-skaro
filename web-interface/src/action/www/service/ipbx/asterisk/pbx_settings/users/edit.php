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


if(isset($_QR['id']) === false || ($info = $appuser->get($_QR['id'])) === false)
	$_QRY->go($_TPL->url('service/ipbx/pbx_settings/users'),$param);

$return = &$info;
$result = $fm_save = $error = null;

$gmember = $qmember = $rightcall = array();
$gmember['list'] = $qmember['list'] = $rightcall['list'] = false;
$gmember['info'] = $qmember['info'] = $rightcall['info'] = false;
$gmember['slt'] = $qmember['slt'] = $rightcall['slt'] = array();

$appgroup = &$ipbx->get_application('group',null,false);
$order = array('name' => SORT_ASC);
if(($groups = $appgroup->get_groups_list(null, $order, null, true)) !== false) {
	$gmember['list'] = $groups;
}

$appqueue = &$ipbx->get_application('queue',null,false);
$order = array('name' => SORT_ASC);
if(($queues = $appqueue->get_queues_list(null, $order, null, true)) !== false) {
	$qmember['list'] = $queues;
}

$apprightcall = &$ipbx->get_application('rightcall',null,false);
$order = array('name' => SORT_ASC);
if(($rightcalls = $apprightcall->get_rightcalls_list(null, $order, null, true)) !== false) {
	$rightcall['list'] = $rightcalls;
}

if(isset($_QR['fm_send']) === true
&& dwho_issa('userfeatures',$_QR) === true)
{
	if($appuser->set_edit($_QR) === false
	|| $appuser->edit() === false)
	{
		$fm_save = false;
		$result = $appuser->get_result();
		$result['dialaction'] = $appuser->get_dialaction_result();
		$result['phonefunckey'] = $appuser->get_phonefunckey_result();
		$result['voicemail-option'] = $_QRY->get('voicemail-option');

		$return = array_merge($return,$result);
		$error = $appuser->get_error();
	}
	else
	{
		/**
		 * sip reload: refresh pickup groups
		 * */
		$ipbx->discuss(array('dialplan reload',
							'xivo[userlist,update]',
							'xivo[phonelist,update]',
							'module reload app_queue.so',
							'sip reload'
		));
		if(dwho_issa('voicemail',$_QR) === true)
			$ipbx->discuss(array('voicemail reload',
								'xivo[voicemaillist,update]'));
		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/users'),$param);
	}
}

dwho::load_class('dwho_sort');

if($gmember['list'] !== false && dwho_ak('groupmember',$return) === true)
{
	$gmember['slt'] = dwho_array_intersect_key($return['groupmember'],
						   $gmember['list'],
						   'groupfeaturesid');

	if($gmember['slt'] !== false)
	{
		$gmember['info'] = dwho_array_copy_intersect_key($return['groupmember'],
								 $gmember['slt'],
								 'groupfeaturesid');
		$gmember['list'] = dwho_array_diff_key($gmember['list'],$gmember['slt']);

		$groupsort = new dwho_sort(array('key' => 'name'));
		uasort($gmember['slt'],array(&$groupsort,'str_usort'));
	}
}

if($qmember['list'] !== false && dwho_ak('queuemember',$return) === true)
{
	$qmember['slt'] = dwho_array_intersect_key($return['queuemember'],
						   $qmember['list'],
						   'queuefeaturesid');

	if($qmember['slt'] !== false)
	{
		$qmember['info'] = dwho_array_copy_intersect_key($return['queuemember'],
								 $qmember['slt'],
								 'queuefeaturesid');
		$qmember['list'] = dwho_array_diff_key($qmember['list'],$qmember['slt']);

		$queuesort = new dwho_sort(array('key' => 'name'));
		uasort($qmember['slt'],array(&$queuesort,'str_usort'));
	}
}

if($rightcall['list'] !== false && dwho_issa('rightcall',$return) === true
&& ($rightcall['slt'] = dwho_array_intersect_key($return['rightcall'],$rightcall['list'],'rightcallid')) !== false)
	$rightcall['slt'] = array_keys($rightcall['slt']);

$element = $appuser->get_elements();

if(empty($return) === false)
{
	if(dwho_issa('dialaction',$return) === false || empty($return['dialaction']) === true)
		$return['dialaction'] = null;

	if(dwho_issa('voicemail',$return) === false || empty($return['voicemail']) === true)
		$return['voicemail'] = null;
}
else
	$return = null;

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

$element['queueskills'] =  $appqueue->skills_gettree();

$modpark = &$ipbx->get_module('parkinglot');

$_TPL->set_var('id',$_QR['id']);
$_TPL->set_var('info',$return);
$_TPL->set_var('error',$error);
$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('voicemail',$return['voicemail']);
$_TPL->set_var('dialaction',$return['dialaction']);
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
$_TPL->set_var('bsfilter_list',$appuser->get_bsfilter_list());
$_TPL->set_var('fkidentity_list',$appuser->get_phonefunckey_identity());
$_TPL->set_var('fktype_list',$appuser->get_phonefunckey_type());
$_TPL->set_var('profileclient_list',$appuser->get_profileclient_list());
$_TPL->set_var('order_list', $order_list);
$_TPL->set_var('softkeys_list', $softkeys_list);
$_TPL->set_var('parking_list', $modpark->get_all());
$_TPL->set_var('schedule_id', $return['schedule_id']);

?>
