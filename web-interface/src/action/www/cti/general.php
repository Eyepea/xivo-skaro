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

$fm_save = null;

if(isset($_QR['fm_send']) === true)
{
	$fm_save = false;
	$ret = 0;
	foreach(array('cti','ctis','webi','info','announce') as $k)
		$_QR['cti'][$k.'_active'] = isset($_QR['cti'][$k.'_active'])?1:0;

	if (!isset($_QR['cti']['context_separation']))
		$_QR['cti']['context_separation'] = 0;

	if (!isset($_QR['cti']['live_reload_conf']))
		$_QR['cti']['live_reload_conf'] = 0;

	if(($rs = $ctimain->chk_values($_QR['cti'])) === false)
		dwho_report::push('error', $ctimain->get_filter_error());
	else
		$ret = $ctimain->edit(1, $rs);

	if($ret == 1)
		$fm_save = true;
}

$info = array();
$info['ctimain'] = $ctimain->get(1);
$element = array();
$element['ctimain'] = $ctimain->get_element();

$_TPL->set_var('fm_save',$fm_save);
$_TPL->set_var('element',$element);
$_TPL->set_var('info', $info);

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
