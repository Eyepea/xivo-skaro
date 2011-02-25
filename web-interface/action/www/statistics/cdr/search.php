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

$info = null;
$result = false;

if(empty($search['dbeg']) === false
&& empty($search['dend']) === false)
{
	if(($info = $cdr->chk_values($search,false)) === false)
		$info = $cdr->get_filter_result();
	else
	{
		if(($result = $cdr->search($info,'calldate')) !== false && $result !== null)
			$total = $cdr->get_cnt();

		if($result === false)
			$info = null;
	}
}

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

$stats_cdr->init_result_by_list($listkey);
$result = $stats_cdr->parse_data($result,$axetype);

$tpl_statistics = &$_TPL->get_module('statistics');
$tpl_statistics->set_name('cdr');
$tpl_statistics->set_baseurl('statistics/cdr/search');
$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_rows('row',$listkey,'key');

$tpl_statistics->set_data_custom('cdr',$result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('nb',
					'direct',
					'custom:cdr,[key],nb');
$tpl_statistics->add_col('duration',
					'direct',
					'custom:cdr,[key],duration',
					'time');
$tpl_statistics->add_col('average_call_duration',
					'expression',
					'{custom:cdr,[key],duration}/{custom:cdr,[key],nb}',
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
		$xivo_jqplot->gener_graph('cdr','chart1','cdr_performance');
		break;
	default:
}

$_TPL->set_var('table1',$tpl_statistics);
$_TPL->set_var('element',$element);
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
