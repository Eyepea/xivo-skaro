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

$_STS->load_ressource('queue');

$stats_queue = new stats_ressource_queue(&$_XS);
$stats_queue->get_data();

$tpl_statistics->set_name('queue');
$tpl_statistics->set_baseurl('statistics/call_center/data/stats1');
$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_data_custom('listtype',$stats_queue->get_list_by_type());
$itl = $_XS->get_datecal();


switch ($axetype)
{
	case 'day':
		$tpl_statistics->set_rows('hour', $_XS->get_listhour(),'key');
		break;
	case 'week':
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_week(),'key');
		break;
	case 'month':
		$date = dwho_date::all_to_unixtime($itl['dmonth']);
		$year = date('Y',$date);
		$month = date('m',$date);
		$tpl_statistics->set_rows('day', $_XS->get_listday_for_month($year,$month),'key');
		break;
	case 'year':
		$tpl_statistics->set_rows('month',dwho_date::get_listmonth(),'key');
		break;
	case 'type':
	default:
		$tpl_statistics->set_rows('queuename',$stats_queue->get_queue_list(),'keyfile',true);
}

$tpl_statistics->set_data_custom('queue',$stats_queue->_result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('presented',
					'direct',
					'custom:queue,[key],presented');
$tpl_statistics->set_col_struct('traitment');

$tpl_statistics->add_col('connect',
					'direct',
					'custom:queue,[key],connect');
$tpl_statistics->add_col('abandon',
					'direct',
					'custom:queue,[key],abandon');

$tpl_statistics->set_col_struct('deterred');
$tpl_statistics->add_col('on_close',
					'direct',
					'custom:queue,[key],deterred_on_close');
$tpl_statistics->add_col('on_saturation',
					'direct',
					'custom:queue,[key],deterred_on_saturation');

$tpl_statistics->set_col_struct('lost');
$tpl_statistics->add_col('on_joinempty',
					'direct',
					'custom:queue,[key],joinempty');
$tpl_statistics->add_col('on_leaveempty',
					'direct',
					'custom:queue,[key],leaveempty');
$tpl_statistics->add_col('on_timeout',
					'direct',
					'custom:queue,[key],timeout');

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('average_time_waiting',
                         'direct',
                         'custom:queue,[key],average_wait_time',
                         'time',
                         'average');
$tpl_statistics->add_col('home_rated',
					'expression',
					'{custom:queue,[key],connect}/{custom:queue,[key],enterqueue}',
					'percent',
					'average');
$tpl_statistics->add_col('qos',
                         'direct',
                         'custom:queue,[key],qos',
                         'percent');
$tpl_statistics->gener_table();

$_TPL->set_var('table1',$tpl_statistics);
$_TPL->set_var('listrow',$tpl_statistics->get_data_rows());
$_TPL->set_var('listobject',$_XS->get_object_list());
$_TPL->set_var('objectkey',$_XS->get_objectkey());
$_TPL->set_var('showdashboard_call_center',true);

if($act === 'exportcsv')
{
	$_TPL->set_var('result',$tpl_statistics->render_csv());
	$_TPL->set_var('name','queue');
	$_TPL->set_var('date',$itl);
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
		$xivo_jqplot->gener_graph('pie','chart1','total_call_repartition_by_event');
		$xivo_jqplot->gener_graph('queue_perf','chart2','queue_performance');
		break;
	default:
}

$_TPL->set_var('xivo_jqplot',$xivo_jqplot);
$_TPL->set_var('mem_info',(memory_get_usage() - $base_memory));
$_TPL->set_var('bench',(microtime(true) - $bench_start));

$dhtml = &$_TPL->get_module('dhtml');
$xivo_jqplot->write_js_loaded_plugin($dhtml);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/data/stats1");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
