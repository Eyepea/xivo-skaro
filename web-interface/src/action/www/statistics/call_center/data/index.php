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

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

$_STS->load_ressource('general');

if($_SESSION['_USR']->meta !== 'root')
	$_QRY->go($_TPL->url('statistics/call_center/data/stats1'));

if (($listconf = $_TPL->get_var('listconf')) === null
|| ($nb = count($listconf)) === 0)
{
	$table_queue = $_TPL->bbf('no_conf');
	$table_agent = $_TPL->bbf('no_conf');
}
else
{
	$arr = array();
	$arr['axetype'] = 'type';
	$arr['dbeg'] = date('Y-m-d');
	$arr['dend'] = date('Y-m-d');
	$stats_general = false;
	$rsconf = array();
	$stats_general = new stats_ressource_general();
	for($i=0;$i<$nb;$i++)
	{
		$ref = &$listconf[$i];
		if ($ref['homepage'] === false)
			continue;
		$arr['confid'] = $ref['id'];
		$_XS->global_init($arr);
		$stats_general->set_xs($_XS);
		$stats_general->parse_log('queue',$ref['name']);
		$stats_general->parse_log('agent',$ref['name']);
		array_push($rsconf,$ref);
	}

	if (($result = $stats_general->get_result()) === false
	|| empty($result) === true)
	{
		$table_general = $_TPL->bbf('no_conf_selected_for_homepage');
	}
	else
	{
		$resultqueue = $result['queue'];
		$resultagent = $result['agent'];

		$tpl_statistics->set_name('queue');
		$tpl_statistics->set_rows('confname',$rsconf,'name',true);
		$tpl_statistics->set_data_custom('queue',$resultqueue);
		$tpl_statistics->set_data_custom('agent',$resultagent);
		$tpl_statistics->set_data_custom('axetype',$axetype);

		$tpl_statistics->set_col_struct('queue');
/*
		$tpl_statistics->add_col('presented',
            					'direct',
            					'custom:queue,[key],presented');
*/
		$tpl_statistics->add_col('connect',
            					'direct',
            					'custom:queue,[key],connect');
		$tpl_statistics->add_col('average_time_waiting',
            					'expression',
            					'{custom:queue,[key],total_time_waiting}/{custom:queue,[key],connect}',
            					'time');
		$tpl_statistics->add_col('home_rated',
            					'expression',
            					'{custom:queue,[key],connect}/{custom:queue,[key],enterqueue}',
            					'percent');
		$tpl_statistics->add_col('qos',
            					'expression',
            					'{custom:queue,[key],qos}/{custom:queue,[key],connect}',
            					'percent');
/*
		$tpl_statistics->set_col_struct('agent');
		$tpl_statistics->add_col('productivity',
            					'expression',
            					'{custom:agent,[key],calltime}/{custom:agent,[key],logintime}',
            					'percent');
*/
		$tpl_statistics->gener_table();
		$table_general = $tpl_statistics->render_html(false,true);

		#$xivo_jqplot->init_data_full($tpl_statistics);
		#$xivo_jqplot->gener_graph('index_general','chart1','index_general');
	}
}

$_TPL->set_var('table_general',$table_general);
$_TPL->set_var('xivo_jqplot',$xivo_jqplot);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$dhtml = &$_TPL->get_module('dhtml');
$xivo_jqplot->write_js_loaded_plugin($dhtml);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/data/index");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
