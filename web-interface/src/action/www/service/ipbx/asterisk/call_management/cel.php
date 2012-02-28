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

// force loading translation file
$_TPL->load_i18n_file('tpl/www/bloc/statistics/statistics', 'global');
$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/'.$ipbx->get_name().'/call_management/cel/index.i18n', 'global');

$page = isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$act = isset($_QR['act']) === false || $_QR['act'] !== 'exportcsv' ? 'advanced_search' : 'exportcsv';

$_STS->load_ressource('cel');

$stats_cel = new stats_ressource_cel();
$cel = &$ipbx->get_module('cel');

if($act !== 'exportcsv')
{
	$appcontext = &$ipbx->get_application('context');

	$order = array();
	$order['displayname'] = SORT_ASC;
	$order['name'] = SORT_ASC;

	if(($list = $appcontext->get_contexts_list(null,$order)) === false
	|| ($nb = count($list)) === 0)
		$context_list = array();

	$context_list = array();
	for($i=0;$i<$nb;$i++)
	{
		$ref = $list[$i];
		$context_list[$i] = $ref['context'];
	}

	$_TPL->set_var('context_list',$context_list);
}

$total = 0;
$nbbypage = 25;

$info = null;
$result = false;

if(isset($_QR['fm_send']) === true || isset($_QR['search']) === true)
{
	if(($info = $cel->chk_values($_QR,false)) === false)
		$info = $cel->get_filter_result();
	else
	{
		if($act === 'exportcsv')
			$limit = null;
		else
		{
			$limit = array();
			$limit[0] = ($page - 1) * $nbbypage;
			$limit[1] = $nbbypage;
		}

		if(($result = $stats_cel->get_calls_records($_QR,'eventtime',$limit)) !== false && $result !== null)
			$total = $stats_cel->get_cnt();

		if($result === false)
			$info = null;

		$_TPL->set_var('pager',dwho_calc_page($page,$nbbypage,$total));
	}

	if($act === 'exportcsv' && $info !== null)
		$info['amaflagsmeta'] = $info['amaflags'] !== '' ? $cel->amaflags_meta($info['amaflags']) : '';
}

$_TPL->set_var('total',$total);
$_TPL->set_var('element',$cel->get_element());
$_TPL->set_var('info',$info);
$_TPL->set_var('result',$result);
$_TPL->set_var('act',$act);

if($act === 'exportcsv')
{
	if($result === false)
		$_QRY->go($_TPL->url('service/ipbx/'.$ipbx->get_name().'/call_management/cel/advanced_search'));

	$_TPL->display('/bloc/service/ipbx/'.$ipbx->get_name().'/call_management/cel/exportcsv');
	die();
}

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/service/ipbx/'.$ipbx->get_name());
$menu->set_toolbar('toolbar/service/ipbx/'.$ipbx->get_name().'/call_management/cel');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->set_css('/css/statistics/statistics.css');
$dhtml->add_js('/struct/js/date.js.php');
$dhtml->set_js('js/service/ipbx/'.$ipbx->get_name().'/cel.js');

$_TPL->set_var('act',$act);
$_TPL->set_bloc('main','service/ipbx/'.$ipbx->get_name().'/call_management/cel/'.$act);
$_TPL->set_struct('service/ipbx/'.$ipbx->get_name());
$_TPL->display('index');

?>