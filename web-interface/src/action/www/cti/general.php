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

$ctimain = &$ipbx->get_module('ctimain');
$ctipresences = &$ipbx->get_module('ctipresences');
$ctiaccounts = &$ipbx->get_module('ctiaccounts');

$appxivoserver = $ipbx->get_application('serverfeatures',array('feature' => 'phonebook','type' => 'xivo'));

$info = array();
$load_inf = $ctimain->get_all();
$info['ctimain'] = $load_inf[0];
$element = array();
$element['ctimain'] = $ctimain->get_element();

$error = array();
$error['ctimain'] = array();
$fm_save = null;

if(isset($_QR['fm_send']) === true)
{
	$fm_save = false;
	$parting = array();
	if(isset($_QR['cti']['parting_astid_context']))
		$parting[] = 'context';
	if(isset($_QR['cti']['parting_astid_ipbx']))
		$parting[] = 'astid';
	$parting_str = implode(',', $parting);
	$_QR['cti']['parting_astid_context'] = $parting_str;

	if(isset($_QR['xivoserver']))
		$_QR['cti']['asterisklist'] = implode(",", $_QR['xivoserver']);
	else
		$_QR['cti']['asterisklist'] = '';

	foreach(array('fagi','cti','ctis','webi','info','announce') as $k)
		$_QR['cti'][$k.'_active'] = isset($_QR['cti'][$k.'_active'])?1:0;

	if(($rs = $ctimain->chk_values($_QR['cti'])) === false)
	{
		$err = $ctimain->get_filter_error();
		foreach ($err as $k => $v)
			dwho_report::push('error', $k.'=> '.$v);
		$ret = 0;
	} else {
		if($ctimain->exists(null,null,1) === true)
			$ret = $ctimain->edit(1, $rs);
		else
			$ret = $ctimain->add($rs);
	}

	if($ret == 1)
	{
		$fm_save = true;
		$ipbx->discuss('xivo[cticonfig,update]');
	}
	$load_inf = $ctimain->get_all();
	$info['ctimain'] = $load_inf[0];
}

$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('error',$error);
$_TPL->set_var('element',$element);
$_TPL->set_var('info', $info);
$_TPL->set_var('listaccount', $ctiaccounts->get_all());

function certfilter($cert)
{ return count($cert['types']) == 1 && $cert['types'][0] == 'certificate'; }

function privkeyfilter($cert)
{ return count($cert['types']) == 1 && $cert['types'][0] == 'privkey'; }

$modcert = &$_XOBJ->get_module('certificate');
$allcerts = $modcert->get_all();
$_TPL->set_var('tlscertfiles', array_filter($allcerts, "certfilter"));
$_TPL->set_var('tlsprivkeyfiles', array_filter($allcerts, "privkeyfilter"));

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->load_js_multiselect_files();
$dhtml->set_js('js/utils/dyntable.js');
$dhtml->set_js('js/cti/general.js');

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/cti/menu');

$_TPL->set_bloc('main','/cti/general');
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>
