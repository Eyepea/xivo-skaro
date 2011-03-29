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

if(isset($_QR['id']) === false || ($info = $appdevice->get($_QR['id'])) === false)
	$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);

$return = &$info;

$result = $fm_save = $error = null;

if(isset($info['protocol']['allow']) === true)
	$allow = $info['protocol']['allow'];
else
	$allow = array();

$sccp_addons = array('7914', '7915', '7916');

if(isset($_QR['fm_send']) === true
&& dwho_issa('protocol',$_QR) === true
&& dwho_issa('userfeatures',$_QR) === true
&& isset($_QR['protocol']['protocol']) === true)
{
	$return = &$result;
	$queueskills = array();

	// skipping the last one (empty entry)
	$count = count($_QR['queueskill-skill']) - 1;
	for($i = 0; $i < $count; $i++)
	{
		$queueskills[] = array(
			'userid'	=> $_QR['id'],
			'skillid'	=> $_QR['queueskill-skill'][$i],
			'weight'	=> $_QR['queueskill-weight'][$i],
		);
	}
	$skillerr = $appqueue->deviceskills_setedit($queueskills);

	// sccp addons
	if(count($_QR['sccp_addons']) > 0)
		unset($_QR['sccp_addons'][count($_QR['sccp_addons'])-1]);
	$_QR['protocol']['addons'] = $_QR['sccp_addons'];

	$softkeys = array();
	foreach($_QR['softkeys_order'] as $name => $positions)
	{
		$values     = $_QR['softkeys_key'][$name];
		$cursoftkey = array();

#		// sort values
		unset($positions[count($positions)-1]);
		$idxs = array_keys($positions);

/*
		function pos_sort($x, $y) {
				global $positions;
				return $positions[$x] - $positions[$y];
		}
		$res = usort(&$idxs, "pos_sort");
*/

		foreach($idxs as $idx)
			$cursoftkey[] = $values[$idx];

		$softkeys[$name] = $cursoftkey;
	}
	$_QR['protocol']['softkeys'] = $softkeys;

	if($appdevice->set_edit($_QR,$_QR['protocol']['protocol']) === false
	|| $skillerr === false
	|| $appdevice->edit() === false)
	{
		$fm_save = false;
		$result = $appdevice->get_result();
		$result['dialaction'] = $appdevice->get_dialaction_result();
		$result['phonefunckey'] = $appdevice->get_phonefunckey_result();

		$error = $appdevice->get_error();
		$error['queueskills'] = $appqueue->deviceskills_get_error();

		if(dwho_issa('protocol',$result) === true
		&& isset($result['protocol']['allow']) === true)
			$allow = $result['protocol']['allow'];

		$result['voicemail-option'] = $_QRY->get('voicemail-option');
		$_TPL->set_var('queueskills', $queueskills);
	}
	else
	{
		// updating skills
		$appqueue->deviceskills_edit($_QR['id'], $queueskills);

		$ipbx->discuss('xivo[userlist,update]');
		// must reload app_queue
			$ipbx->discuss('module reload app_queue.so');

		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/devices'),$param);
	}
}

$element = $appdevice->get_elements();

if(dwho_issa('allow',$element['protocol']['sip']) === true
&& dwho_issa('value',$element['protocol']['sip']['allow']) === true
&& empty($allow) === false)
{
	if(is_array($allow) === false)
		$allow = explode(',',$allow);

	$element['protocol']['sip']['allow']['value'] = array_diff($element['protocol']['sip']['allow']['value'],$allow);
}

if(dwho_issa('allow',$element['protocol']['iax']) === true
&& dwho_issa('value',$element['protocol']['iax']['allow']) === true
&& empty($allow) === false)
{
	if(is_array($allow) === false)
		$allow = explode(',',$allow);

	$element['protocol']['iax']['allow']['value'] = array_diff($element['protocol']['iax']['allow']['value'],$allow);
}

if(empty($return) === false)
{
	$return['protocol']['allow'] = $allow;

	if(dwho_issa('dialaction',$return) === false || empty($return['dialaction']) === true)
		$return['dialaction'] = null;

	if(dwho_issa('voicemail',$return) === false || empty($return['voicemail']) === true)
		$return['voicemail'] = null;

	if(dwho_issa('autoprov',$return) === false || empty($return['autoprov']) === true)
		$return['autoprov'] = null;
}
else
	$return = null;

$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/pbx_settings/devices/edit.i18n', 'global');

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

// AUTOGEN name/secret
$config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');
$ro = true;
if (isset($config['user']) === true)
	$ro = !($config['user']['readonly-idpwd'] == 'false');

$element['protocol']['name']   = array(
	'readonly' => $ro,
	'class'    => 'it-'.($ro?'disabled':'enabled')
);
$element['protocol']['secret']   = array(
	'readonly' => $ro,
	'class'    => 'it-'.($ro?'disabled':'enabled')
);

$_TPL->set_var('id',$info['userfeatures']['id']);
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
$_TPL->set_var('agent_list',$appdevice->get_agent_list());
$_TPL->set_var('destination_list',$appdevice->get_destination_list());
$_TPL->set_var('moh_list',$appdevice->get_musiconhold());
$_TPL->set_var('tz_list',$appdevice->get_timezones());
$_TPL->set_var('context_list',$appdevice->get_context_list());
$_TPL->set_var('autoprov_list',$appdevice->get_autoprov_list());
$_TPL->set_var('bsfilter_list',$appdevice->get_bsfilter_list());
$_TPL->set_var('fkidentity_list',$appdevice->get_phonefunckey_identity());
$_TPL->set_var('fktype_list',$appdevice->get_phonefunckey_type());
$_TPL->set_var('profileclient_list',$appdevice->get_profileclient_list());
$_TPL->set_var('sccp_addons',$sccp_addons);
$_TPL->set_var('order_list', $order_list);
$_TPL->set_var('softkeys_list', $softkeys_list);
if (isset($return['schedule_id']) === true)
	$_TPL->set_var('schedule_id', $return['schedule_id']);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/uri.js');
$dhtml->set_js('js/dwho/http.js');
$dhtml->set_js('js/dwho/suggest.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/dialaction.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/phonefunckey.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/devices.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/devices/sip.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/devices/iax.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/devices/sccp.js');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/devices/custom.js');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->add_js('/bloc/service/ipbx/'.$ipbx->get_name().'/pbx_settings/devices/phonefunckey/phonefunckey.js.php');

?>
