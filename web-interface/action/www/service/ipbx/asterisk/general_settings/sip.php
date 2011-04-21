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

$config = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');

$appsip = &$ipbx->get_apprealstatic('sip');
$appgeneralsip = &$appsip->get_module('general');
$modauth = &$ipbx->get_module('sipauthentication');
$modpark = &$ipbx->get_module('parkinglot');

$fm_save = $error = null;

$info = $appgeneralsip->get_all_val_by_category(false);
$auth = $modauth->get_all_where(array('usersip_id' => null));
$modcert = &$_XOBJ->get_module('certificate');

if(isset($_QR['fm_send']) === true)
{
	$fm_save = false;

	$_QR['tlscadir'] = $config['tls']['cadir'];

	// replace authentications
	$auth   = array();
	$error  = array('auth' => array());

	for($i = 0; $i < count($_QR['auth']['user'])-1; $i++)
	{
		$auth[] = array(
			'usersip_id' => null,
			'user'       => $_QR['auth']['user'][$i],
			'secretmode' => $_QR['auth']['secretmode'][$i],
			'secret'     => $_QR['auth']['secret'][$i],
			'realm'      => $_QR['auth']['realm'][$i]
		);

		if($modauth->chk_values($auth[count($auth)-1]) === false)
		{ $error['auth'][$i] = $modauth->get_filter_error(); continue; }
	}

	// error on outbound authentications
	if(count($error['auth']) > 0)
	{
		$fm_save = false;
	} else {
		$modauth->delete_where(array('usersip_id' => null));

		foreach($auth as $_auth)
			$modauth->add($_auth);

		unset($_QR['auth']);

		if(($rs = $appgeneralsip->set_save_all($_QR)) !== false)
		{
			$info = $rs['result'];
			$error = $rs['error'];
			$fm_save = empty($error);
		}
	}
}

$element = $appgeneralsip->get_element();
$element['auth'] = $modauth->get_element();

if(dwho_issa('allow',$element) === true
&& dwho_issa('value',$element['allow']) === true
&& isset($info['allow']) === true
&& dwho_has_len($info['allow'],'var_val') === true)
{
	$info['allow']['var_val'] = explode(',',$info['allow']['var_val']);
	$element['allow']['value'] = array_diff($element['allow']['value'],$info['allow']['var_val']);
}

if(dwho_issa('localnet',$info) === true
&& array_key_exists('var_val',$info['localnet']) === true
&& dwho_has_len($info['localnet']['var_val']) === false)
	$info['localnet'] = null;

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->set_js('js/service/ipbx/asterisk/general/sip.js');

$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('info',$info);
$_TPL->set_var('auth',$auth);
$_TPL->set_var('error',$error);
$_TPL->set_var('element',$element);
$_TPL->set_var('moh_list',$appgeneralsip->get_musiconhold());
$_TPL->set_var('context_list',$appgeneralsip->get_context_list());
$_TPL->set_var('parking_list', $modpark->get_all());

function cafilter($cert)
{ return $cert['CA']; }

function certfilter($cert)
{	return !$cert['CA'];	}

$allcerts = $modcert->get_all();
$_TPL->set_var('tlscertfiles', array_filter($allcerts, "certfilter"));
$_TPL->set_var('tlscafiles'  , array_filter($allcerts, "cafilter"));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());

$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/general_settings/sip');
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
