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

$appvoicemail = &$ipbx->get_application('voicemail');

dwho::load_class('dwho_prefs');
$prefs = new dwho_prefs('voicemails');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$context = strval($prefs->get('context', ''));
$sort    = $prefs->flipflop('sort', 'fullname');

$info = array();

$param = array();
$param['act'] = 'list';

if($search !== '')
	$param['search'] = $search;

switch($act)
{
	case 'add':
		$result = $fm_save = $error = null;

		if(isset($_QR['fm_send']) === true && dwho_issa('voicemail',$_QR) === true)
		{
			if($appvoicemail->set_add($_QR) === false
			|| $appvoicemail->add() === false)
			{
				$fm_save = false;
				$result = $appvoicemail->get_result();
				$error = $appvoicemail->get_error();
			}
			else
			{
				$ipbx->discuss(array('xivo[voicemail,update]','voicemail reload'));
				$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);
			}
		}

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/submenu.js');

		$_TPL->set_var('info',$result);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appvoicemail->get_elements());
		$_TPL->set_var('tz_list',$appvoicemail->get_timezones());
		$_TPL->set_var('context_list',$appvoicemail->get_context_list(null,null,null,false,'internal'));
		break;

	case 'edit':
		if(isset($_QR['id']) === false
		|| ($info = $appvoicemail->get($_QR['id'])) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);

		$result = $fm_save = $error = null;
		$return = &$info;

		if(isset($_QR['fm_send']) === true && dwho_issa('voicemail',$_QR) === true)
		{
			$return = &$result;

			if($appvoicemail->set_edit($_QR) === false
			|| $appvoicemail->edit() === false)
			{
				$fm_save = false;
				$result = $appvoicemail->get_result();
				$error = $appvoicemail->get_error();
			}
			else
			{
				$ipbx->discuss(array('xivo[voicemail,update]','voicemail reload'));
				$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);
			}
		}

		$dhtml = &$_TPL->get_module('dhtml');
		$dhtml->set_js('js/dwho/submenu.js');

		$_TPL->set_var('id',$info['voicemail']['uniqueid']);
		$_TPL->set_var('info',$return);
		$_TPL->set_var('error',$error);
		$_TPL->set_var('fm_save',$fm_save);
		$_TPL->set_var('element',$appvoicemail->get_elements());
		$_TPL->set_var('tz_list',$appvoicemail->get_timezones());
		$_TPL->set_var('context_list',$appvoicemail->get_context_list(null,null,null,false,'internal'));
		break;

	case 'delete':
		$param['page'] = $page;

		if(isset($_QR['id']) === false || $appvoicemail->get($_QR['id']) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);

		$appvoicemail->delete();

		$ipbx->discuss(array('xivo[voicemail,update]','voicemail reload'));
		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);
		break;

	case 'deletes':
		$param['page'] = $page;

		if(($values = dwho_issa_val('voicemails',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appvoicemail->get($values[$i]) !== false)
				$appvoicemail->delete();
		}

		$ipbx->discuss(array('xivo[voicemail,update]','voicemail reload'));
		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);
		break;

	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('voicemails',$_QR)) === false)
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appvoicemail->get($values[$i]) === false)
				continue;
			else if($act === 'disables')
				$appvoicemail->disable();
			else
				$appvoicemail->enable();
		}

		$ipbx->discuss(array('xivo[voicemail,update]','voicemail reload'));
		$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);
		break;

	default:
		$act = 'list';
		$prevpage = $page - 1;
		$nbbypage = XIVO_SRE_IPBX_AST_NBBYPAGE;

		$order = array();
		$order[$sort[1]] = $sort[0];

		$limit = array();
		$limit[0] = $prevpage * $nbbypage;
		$limit[1] = $nbbypage;

		if($search !== '')
			$list = $appvoicemail->get_voicemail_search($search,null,$order,$limit);
		else
			$list = $appvoicemail->get_voicemail_list(null,$order,$limit);

		$total = $appvoicemail->get_cnt();

		if($list === false && $total > 0 && $prevpage > 0)
		{
			$param['page'] = $prevpage;
			$_QRY->go($_TPL->url('service/ipbx/pbx_settings/voicemail'),$param);
		}

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
		$_TPL->set_var('list',$list);
		$_TPL->set_var('search',$search);
		$_TPL->set_var('sort',$sort);
}

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/pbx_settings/voicemail');

$_TPL->set_var('act',$act);
$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/pbx_settings/voicemail/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
