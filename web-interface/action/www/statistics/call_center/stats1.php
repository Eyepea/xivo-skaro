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

include(dirname(__FILE__).'/common.php');

$appqueue = &$ipbx->get_application('queue');
$queue_qos = $appqueue->get_qos();

if(xivo::load_class('xivo_statistics_queue',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','queue',false) === false)
	die('Can\'t load xivo_statistics_queue object');

$stats_queue = new xivo_statistics_queue(&$_XS);
$stats_queue->set_data_custom('qos',$queue_qos);
$stats_queue->parse_log();

$tpl_statistics->set_name('queue');
$tpl_statistics->set_baseurl('statistics/call_center/stats1');

$tpl_statistics->set_data_custom('axetype',$_XS->get_axtype());
switch ($_XS->get_axtype())
{
	case 'day':
		$tpl_statistics->set_rows('hour',$_XS->get_listhour(),'value');
		$tpl_statistics->set_data_custom('hour_range',$_XS->get_hour_range());
		break;
	case 'week':
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_week(),'value');
		$tpl_statistics->set_data_custom('week_range',$_XS->get_week_range());
		break;
	case 'month':
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_month(),'value');
		break;
	case 'year':
		break;
	case 'type':
	default:
		$tpl_statistics->set_rows('queuename',$stats_queue->get_queue_list(),'name');
}

$tpl_statistics->set_data_custom('queue',$stats_queue->_result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('presented',
					'direct',
					'custom:queue,[name],presented');
$tpl_statistics->add_col('connect',
					'direct',
					'custom:queue,[name],answered');
$tpl_statistics->add_col('abandon',
					'direct',
					'custom:queue,[name],abandoned');

$tpl_statistics->set_col_struct('deterred');
$tpl_statistics->add_col('on_close',
					'direct',
					'custom:queue,[name],deterred_on_close');
$tpl_statistics->add_col('on_saturation',
					'direct',
					'custom:queue,[name],deterred_on_saturation');

$tpl_statistics->set_col_struct('rerouted');
$tpl_statistics->add_col('on_hungup',
					'direct',
					'custom:queue,[name],rerouted_on_hungup');
$tpl_statistics->add_col('on_guide',
					'direct',
					'custom:queue,[name],rerouted_on_guide');
$tpl_statistics->add_col('on_number',
					'direct',
					'custom:queue,[name],rerouted_on_number');

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('average_time_waiting',
					'expression',
					'{custom:queue,[name],total_time_waiting}/{custom:queue,[name],answered}',
					'time');
$tpl_statistics->add_col('home_rated',
					'expression',
					'{custom:queue,[name],answered}/{custom:queue,[name],presented}',
					'percent');
$tpl_statistics->add_col('qos',
					'expression',
					'{custom:queue,[name],qos}/{custom:queue,[name],answered}',
					'percent');

$tpl_statistics->gener_table();
#$tpl_statistics->gener_graph('t1','stats1');
$table1 = $tpl_statistics;

$_TPL->set_var('table1',$table1);
$_TPL->set_var('listobject',$_XS->get_object_list());
$_TPL->set_var('objectkey',$_XS->get_objectkey());

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/stats1");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
