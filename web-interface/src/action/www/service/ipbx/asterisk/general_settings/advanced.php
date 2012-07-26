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
$info = array();
$element = array();

$appagentglobalparams =  &$ipbx->get_application('agentglobalparams');
$info['agentglobalparams']  = $appagentglobalparams->get_options('agents');
$element['agentglobalparams']  = $appagentglobalparams->get_elements();

$appagentgeneralparams =  &$ipbx->get_application('agentgeneralparams');
$info['agentgeneralparams']  = $appagentgeneralparams->get_options('general');
$element['agentgeneralparams']  = $appagentgeneralparams->get_elements();

$appqueues = &$ipbx->get_apprealstatic('queues');
$appgeneralqueues = &$appqueues->get_module('general');
$info['generalqueues'] = $appgeneralqueues->get_all_by_category();
$element['generalqueues'] = $appgeneralqueues->get_elements();

$appmeetme = &$ipbx->get_apprealstatic('meetme');
$appgeneralmeetme = &$appmeetme->get_module('general');
$info['generalmeetme'] = $appgeneralmeetme->get_all_by_category();
$element['generalmeetme'] = $appgeneralmeetme->get_elements();

$appsip = &$ipbx->get_apprealstatic('sip');
$appgeneralsip = &$appsip->get_module('general');
$autocreatepeer = $appgeneralsip->get('autocreatepeer');
$autocreatepeerval = $autocreatepeer['general']['var_val'];
$info['userinternal'] = array();
$info['userinternal']['guest'] = ($autocreatepeerval === 'yes') ? true : false;

$general = &$ipbx->get_module('general');
$info['general'] = $general->get(1);
$element['general'] = array_keys(dwho_i18n::get_timezone_list());

$error = array();
$error['agentgeneralparams'] = array();
$error['generalqueues'] = array();
$error['generalmeetme'] = array();
$error['agentglobalparams'] = array();

$fm_save = null;
if(isset($_QR['fm_send']) === true)
{
	if(dwho_issa('agentgeneralparams',$_QR) === false)
		$_QR['agentgeneralparams'] = array();

	if(($rs = $appagentgeneralparams->save_agent_general_params($_QR['agentgeneralparams'])) !== false)
	{
		$info['agentgeneralparams'] = $appagentgeneralparams->get_result('agentgeneralparams');
		$error['agentgeneralparams'] = $appagentgeneralparams->get_error();

		if(isset($rs['error'][0]) === true)
			$fm_save = false;
		else if($fm_save !== false)
			$fm_save = true;
	}

	if(dwho_issa('agentglobalparams',$_QR) === false)
		$_QR['agentglobalparams'] = array();

	if(($rs = $appagentglobalparams->save_agent_global_params($_QR['agentglobalparams'])) !== false)
	{
		$info['agentglobalparams'] = $appagentglobalparams->get_result('agentglobalparams');
		$error['agentglobalparams'] = $appagentglobalparams->get_error();

		if(isset($rs['error'][0]) === true)
			$fm_save = false;
		else if($fm_save !== false)
			$fm_save = true;
	}

	if(dwho_issa('generalqueues',$_QR) === false)
		$_QR['generalqueues'] = array();

	if(($rs = $appgeneralqueues->set_save_all($_QR['generalqueues'])) !== false)
	{
		$info['generalqueues'] = $rs['result'];
		$error['generalqueues'] = $rs['error'];

		if(isset($rs['error'][0]) === true)
			$fm_save = false;
		else if($fm_save !== false)
			$fm_save = true;
	}

	if(dwho_issa('generalmeetme',$_QR) === true
			&& ($rs = $appgeneralmeetme->set_save_all($_QR['generalmeetme'])) !== false)
	{
		$info['generalmeetme'] = $rs['result'];
		$error['generalmeetme'] = $rs['error'];

		if(isset($rs['error'][0]) === true)
			$fm_save = false;
		else if($fm_save !== false)
			$fm_save = true;
	}

	if(dwho_issa('userinternal',$_QR) === false)
		$_QR['userinternal'] = array();

	$rs_sip = array();
	$rs_sip['commented'] = 0;
	$rs_sip['var_name'] = 'autocreatepeer';

	if(isset($_QR['userinternal']['guest']) === true)
	{
		$rs_sip['var_val'] = 'yes';
		$info['userinternal']['guest'] = true;
	}
	else
	{
		$rs_sip['var_val'] = 'no';
		$info['userinternal']['guest'] = false;
	}

	if($appgeneralsip->set($rs_sip) === false
			|| $appgeneralsip->save() === false)
	{
		dwho_report::push('error', 'Can\'t edit autocreatepeer in staticsip table');
	}

	if(dwho_issa('general',$_QR) === false)
		$_QR['general'] = array();
	if(!array_key_exists('dundi',$_QR['general']))
		$_QR['general']['dundi'] = 0;

	if(!$general->edit(1, $_QR['general']))
	{
		$info['general']  = $general->get_filter_result();
		$error['general'] = $general->get_filter_error();

		$fm_save = false;
	}
	else
		$info['general'] = $_QR['general'];
}

$_TPL->set_var('beep_list',$appagentglobalparams->get_beep());
$_TPL->set_var('goodbye_list',$appagentglobalparams->get_goodbye());
$_TPL->set_var('fm_save', $fm_save);
$_TPL->set_var('error', $error);
$_TPL->set_var('agentgeneralparams', $info['agentgeneralparams']);
$_TPL->set_var('agentglobalparams', $info['agentglobalparams']);
$_TPL->set_var('generalqueues', $info['generalqueues']);
$_TPL->set_var('generalmeetme', $info['generalmeetme']);
$_TPL->set_var('userinternal', $info['userinternal']);
$_TPL->set_var('general', $info['general']);
$_TPL->set_var('info', $info);
$_TPL->set_var('element', $element);


$appagent = &$ipbx->get_application('agent',null,false);
$_TPL->set_var('moh_list'     , $appagent->get_musiconhold());

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/general_settings/advanced');
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
