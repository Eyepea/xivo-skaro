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

if(xivo::load_class('xivo_statistics_queue',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','queue',false) === false)
	die('Can\'t load xivo_statistics_queue object');

$stats_queue = new xivo_statistics_queue(&$_XS);
$stats_queue->get_data();

$tpl_statistics->set_name('queue');
$tpl_statistics->set_baseurl('statistics/call_center/stats1');

$tpl_statistics->set_data_custom('axetype',$_XS->get_axetype());
$itl = $_XS->get_datecal();
switch ($_XS->get_axetype())
{
	case 'day':
		$tpl_statistics->set_rows('hour',$_XS->get_listhour(),'key');
		$tpl_statistics->set_data_custom('day_process',$_XS->get_datecal());
		break;
	case 'week':
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_week(),'key');
		#$tpl_statistics->set_data_custom('week_range',$_XS->get_week_range());
		break;
	case 'month':
		$date = $_XS->all_to_unixtime($itl['dmonth']);
		$year = date('Y',$date);
		$month = date('m',$date);
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_month($year,$month),'key');
		$tpl_statistics->set_data_custom('month_process',$_XS->get_datecal());
		break;
	case 'year':
		$tpl_statistics->set_rows('month',$_XS->get_listmonth(),'key');
		break;
	case 'type':
	default:
		$tpl_statistics->set_rows('queuename',$stats_queue->get_queue_list(),'name',true);
		$tpl_statistics->set_data_custom('date_process',$_XS->get_datecal());
}

$tpl_statistics->set_data_custom('queue',$stats_queue->_result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('presented',
					'direct',
					'custom:queue,[key],presented');
$tpl_statistics->add_col('connect',
					'direct',
					'custom:queue,[key],answered');
$tpl_statistics->add_col('abandon',
					'direct',
					'custom:queue,[key],abandoned');

$tpl_statistics->set_col_struct('deterred');
$tpl_statistics->add_col('on_close',
					'direct',
					'custom:queue,[key],deterred_on_close');
$tpl_statistics->add_col('on_saturation',
					'direct',
					'custom:queue,[key],deterred_on_saturation');

$tpl_statistics->set_col_struct('rerouted');
$tpl_statistics->add_col('on_hungup',
					'direct',
					'custom:queue,[key],rerouted_on_hungup');
$tpl_statistics->add_col('on_guide',
					'direct',
					'custom:queue,[key],rerouted_on_guide');
$tpl_statistics->add_col('on_number',
					'direct',
					'custom:queue,[key],rerouted_on_number');

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('average_time_waiting',
					'expression',
					'{custom:queue,[key],total_time_waiting}/{custom:queue,[key],answered}',
					'time');
$tpl_statistics->add_col('home_rated',
					'expression',
					'{custom:queue,[key],answered}/{custom:queue,[key],presented}',
					'percent');
$tpl_statistics->add_col('qos',
					'expression',
					'{custom:queue,[key],qos}/{custom:queue,[key],answered}',
					'percent');

$tpl_statistics->gener_table();
$table1 = $tpl_statistics;

$_TPL->set_var('table1',$table1);
$_TPL->set_var('listobject',$_XS->get_object_list());
$_TPL->set_var('objectkey',$_XS->get_objectkey());
$_TPL->set_var('hascachetype',$_XS->has_cache_type());
$_TPL->set_var('showdashboard',true);

if($act === 'exportcsv')
{
	$_TPL->set_var('result',$tpl_statistics->render_csv());
	$_TPL->set_var('name','queue');
	$_TPL->display('/bloc/statistics/call_center/exportcsv');
	die();
}

$_TPL->set_var('mem_info',(memory_get_usage() - $base_memory));
$_TPL->set_var('bench',(microtime(true) - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/stats1");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
