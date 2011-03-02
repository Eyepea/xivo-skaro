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

$bench_start = microtime(true);
$base_memory = memory_get_usage();

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

if(xivo::load_class('xivo_statistics_cel',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','cel',false) === false)
	die('Can\'t load xivo_statistics_cel object');
	
$stats_cel = new xivo_statistics_cel();
$result = $stats_cel->parse_data('trunk');
$listkey = $stats_cel->get_trunk_list();

$tpl_statistics = &$_TPL->get_module('statistics');
$tpl_statistics->set_name('cel');
$tpl_statistics->set_baseurl('statistics/cdr/index');
$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_rows('row',$listkey,'key');

$tpl_statistics->set_data_custom('cel',$result);
/*
var_dump($result);
var_dump($listkey);
*/
$tpl_statistics->set_col_struct('nb');
$tpl_statistics->add_col('nb_intern',
					'direct',
					'custom:cel,[key],nb_intern');
$tpl_statistics->add_col('nb_in',
					'direct',
					'custom:cel,[key],nb_in');
$tpl_statistics->add_col('nb_out',
					'direct',
					'custom:cel,[key],nb_out');
$tpl_statistics->add_col('nb_total',
					'direct',
					'custom:cel,[key],nb_total');

$tpl_statistics->set_col_struct('duration');
$tpl_statistics->add_col('duration_intern',
					'direct',
					'custom:cel,[key],duration_intern',
					'time');
$tpl_statistics->add_col('duration_in',
					'direct',
					'custom:cel,[key],duration_in',
					'time');
$tpl_statistics->add_col('duration_out',
					'direct',
					'custom:cel,[key],duration_out',
					'time');
$tpl_statistics->add_col('duration_total',
					'direct',
					'custom:cel,[key],duration_total',
					'time');

$tpl_statistics->set_col_struct('average_call_duration');
$tpl_statistics->add_col('average_call_duration_intern',
					'expression',
					'{custom:cel,[key],duration_intern}/{custom:cel,[key],nb_intern}',
					'time',
					'average');
$tpl_statistics->add_col('average_call_duration_in',
					'expression',
					'{custom:cel,[key],duration_in}/{custom:cel,[key],nb_in}',
					'time',
					'average');
$tpl_statistics->add_col('average_call_duration_out',
					'expression',
					'{custom:cel,[key],duration_out}/{custom:cel,[key],nb_out}',
					'time',
					'average');
$tpl_statistics->add_col('average_call_duration_total',
					'expression',
					'{custom:cel,[key],duration_total}/{custom:cel,[key],nb_total}',
					'time',
					'average');

$tpl_statistics->set_col_struct('max_concurrent_calls');
$tpl_statistics->add_col('max_concurrent_calls_intern',
					'direct',
					'custom:cel,[key],max_concurrent_calls_intern');
$tpl_statistics->add_col('max_concurrent_calls_in',
					'direct',
					'custom:cel,[key],max_concurrent_calls_in');
$tpl_statistics->add_col('max_concurrent_calls_out',
					'direct',
					'custom:cel,[key],max_concurrent_calls_out');
$tpl_statistics->add_col('max_concurrent_calls_total',
					'direct',
					'custom:cel,[key],max_concurrent_calls_total');

$tpl_statistics->gener_table();

if($act === 'exportcsv')
{
	$_TPL->set_var('result',$tpl_statistics->render_csv());
	$_TPL->set_var('name','calls_summary_by_trunk');
	$arr = array();
	$arr['dbeg'] = date('Y-m-d').' 00:00:01';
	$arr['dend'] = date('Y-m-d H:i:s');
	$_TPL->set_var('date',$arr);
	$_TPL->display('/bloc/statistics/exportcsv');
	die();
}

$_TPL->set_var('table1',$tpl_statistics);
$_TPL->set_var('showdashboard_cdr',true);
$_TPL->set_var('xivo_jqplot',$xivo_jqplot);
$_TPL->set_var('mem_info',(memory_get_usage() - $base_memory));
$_TPL->set_var('bench',(microtime(true) - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/cdr');

$_TPL->set_bloc('main',"statistics/cdr/index");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
