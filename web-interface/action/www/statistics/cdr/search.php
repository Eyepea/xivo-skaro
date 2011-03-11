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

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

if(xivo::load_class('xivo_statistics_cel',dwho_file::joinpath(XIVO_PATH_OBJECT,'statistics'),'cel',false) === false)
	die('Can\'t load xivo_statistics_cel object');

$stats_cel = new xivo_statistics_cel();

$cel = &$ipbx->get_module('cel');

$info = null;
$result = false;

switch ($axetype)
{
	case 'period':
		$listkey = dwho_date::get_listday_for_interval($search['dbeg'],$search['dend']);
		break;
	case 'day':
		$listkey = dwho_date::get_listhour();
		break;
	case 'week':
		$listkey = dwho_date::get_listday_for_week();
		break;
	case 'month':
		$date = dwho_date::all_to_unixtime($infocal['dmonth']);
		$year = date('Y',$date);
		$month = date('m',$date);
		$listkey = dwho_date::get_listday_for_month($year,$month);
		break;
	default:
}

$tpl_statistics = &$_TPL->get_module('statistics');

$tpl_statistics->set_name('cel');
$tpl_statistics->set_data_custom('axetype','trunk');
$tpl_statistics->set_rows('row',$listkey,'key');

$stats_cel->init_result_by_list($listkey);
$result = $stats_cel->parse_data($axetype,$search);

$tpl_statistics->set_data_custom('cel',$result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('nb',
					'direct',
					'custom:cel,[key],nb_total');
$tpl_statistics->add_col('duration',
					'direct',
					'custom:cel,[key],duration_total',
					'time');
$tpl_statistics->add_col('average_call_duration',
					'expression',
					'{custom:cel,[key],duration_total}/{custom:cel,[key],nb_total}',
					'time',
					'average');

$tpl_statistics->gener_table();

if($act === 'exportcsv')
{
	$_TPL->set_var('result',$tpl_statistics->render_csv());
	$_TPL->set_var('name','cdr');
	$_TPL->set_var('date',$search);
	$_TPL->display('/bloc/statistics/exportcsv');
	die();
}

$xivo_jqplot->init_data_full($tpl_statistics);

switch ($axetype)
{
	case 'type':
		break;
	case 'day':
	case 'week':
	case 'month':
	case 'year':
		$xivo_jqplot->gener_graph('cel','chart1','cel_performance');
		break;
	default:
}

$_TPL->set_var('table1',$tpl_statistics);
$_TPL->set_var('info',$info);
$_TPL->set_var('result',$result);
$_TPL->set_var('showdashboard_cdr',true);
$_TPL->set_var('xivo_jqplot',$xivo_jqplot);
$_TPL->set_var('mem_info',(memory_get_usage() - $base_memory));
$_TPL->set_var('bench',(microtime(true) - $bench_start));

$dhtml = &$_TPL->get_module('dhtml');
$xivo_jqplot->write_js_loaded_plugin(&$dhtml);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/cdr');

$_TPL->set_bloc('main',"statistics/cdr/search");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
