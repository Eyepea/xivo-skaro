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
$info = array();
$element = array();

$appagents = &$ipbx->get_apprealstatic('agents');
$appgeneralagents = &$appagents->get_module('general');
$info['generalagents'] = $appgeneralagents->get_all_by_category();
$element['generalagents'] = $appgeneralagents->get_elements();

$appoptionsagents = &$appagents->get_module('agentoptions');
$info['agentoptions']  = $appoptionsagents->get_all_by_category();
$element['agentoptions']  = $appoptionsagents->get_elements();

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
$error['generalagents'] = array();
$error['agentoptions']  = array();
$error['generalqueues'] = array();
$error['generalmeetme'] = array();

$fm_save = null;

if(isset($_QR['fm_send']) === true)
{
	if(dwho_issa('generalagents',$_QR) === false)
		$_QR['generalagents'] = array();

	if(($rs = $appgeneralagents->set_save_all($_QR['generalagents'])) !== false)
	{
		$info['generalagents'] = $rs['result'];
		$error['generalagents'] = $rs['error'];

		if(isset($rs['error'][0]) === true)
			$fm_save = false;
		else if($fm_save !== false)
			$fm_save = true;
	}

	if(dwho_issa('agentoptions',$_QR) === false)
		$_QR['agentoptions'] = array();

	if(($rs = $appoptionsagents->set_save_all($_QR['agentoptions'])) !== false)
	{
		$info['agentoptions'] = $rs['result'];
		$error['agentoptions'] = $rs['error'];

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

	$rs_sccp = array();
	$rs_sccp['commented'] = 0;
	$rs_sccp['var_name'] = 'hotline_enabled';

	$rs_sip = array();
	$rs_sip['commented'] = 0;
	$rs_sip['var_name'] = 'autocreatepeer';

	if(isset($_QR['userinternal']['guest']) === true)
	{
		$rs_sccp['var_val'] = 'yes';
		$rs_sip['var_val'] = 'yes';
		$info['userinternal']['guest'] = true;
	}
	else
	{
		$rs_sccp['var_val'] = 'no';
		$rs_sip['var_val'] = 'no';
		$info['userinternal']['guest'] = false;
	}

	if($appgeneralsip->set($rs_sip) === false
	|| $appgeneralsip->set($rs_sccp) === false
	|| $appgeneralsip->save() === false)
	{
		dwho_report::push('error', 'Can\'t edit autocreatepeer in staticsip table');
		return false;
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
	{
		$info['general'] = $_QR['general'];
		$ipbx->discuss(array('xivo[cticonfig,update]'));
	}
}

$_TPL->set_var('fm_save'      , $fm_save);
$_TPL->set_var('error'        , $error);
$_TPL->set_var('generalagents', $info['generalagents']);
$_TPL->set_var('generalqueues', $info['generalqueues']);
$_TPL->set_var('generalmeetme', $info['generalmeetme']);
$_TPL->set_var('userinternal' , $info['userinternal']);
$_TPL->set_var('general'      , $info['general']);
$_TPL->set_var('info'         , $info);
$_TPL->set_var('element'      , $element);


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
