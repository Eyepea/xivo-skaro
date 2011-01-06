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

$stats_queue = new xivo_statistics_queue(&$_XOBJ,&$ipbx);
if (isset($_QR['confid']) === true)
	$stats_queue->set_idconf($_QR['confid'],true);
$stats_queue->set_data_custom('qos',$queue_qos);
$stats_queue->parse_log();

$xivo_statistics->set_name('queue');

$xivo_statistics->set_rows('queuename',$stats_queue->get_queue_list(),'name');

$xivo_statistics->set_data_custom('queue',$stats_queue->_result);

$xivo_statistics->set_col_struct('lol');
$xivo_statistics->add_col('presented',
					'direct',
					'custom:queue,[name],presented');
$xivo_statistics->add_col('answered',
					'direct',
					'custom:queue,[name],answered');
$xivo_statistics->add_col('abandoned',
					'direct',
					'custom:queue,[name],abandoned');

$xivo_statistics->set_col_struct('deterred');
$xivo_statistics->add_col('on_close',
					'direct',
					'custom:queue,[name],deterred_on_close');
$xivo_statistics->add_col('on_saturation',
					'direct',
					'custom:queue,[name],deterred_on_saturation');

$xivo_statistics->set_col_struct('rerouted');
$xivo_statistics->add_col('on_hungup',
					'direct',
					'custom:queue,[name],rerouted_on_hungup');
$xivo_statistics->add_col('on_guide',
					'direct',
					'custom:queue,[name],rerouted_on_guide');
$xivo_statistics->add_col('on_number',
					'direct',
					'custom:queue,[name],rerouted_on_number');

$xivo_statistics->set_col_struct('default');
$xivo_statistics->add_col('average_time_waiting',
					'expression',
					'{custom:queue,[name],total_time_waiting}/{custom:queue,[name],answered}',
					'time');
$xivo_statistics->add_col('home_rated',
					'expression',
					'{custom:queue,[name],answered}/{custom:queue,[name],presented}',
					'percent');
$xivo_statistics->add_col('qos',
					'expression',
					'{custom:queue,[name],qos}/{custom:queue,[name],answered}',
					'percent');
/*
var_dump($xivo_statistics->get_val_expression('custom:queue,[name],total_time_waiting','queue8001'));
var_dump($xivo_statistics->get_val_expression('custom:queue,[name],answered','queue8001'));
*/

$xivo_statistics->gener_table();
$xivo_statistics->gener_graph('t1','stats1');
$table1 = $xivo_statistics;


$_TPL->set_var('confid',$stats_queue->get_idconf());
$_TPL->set_var('table1',$table1);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics');

$_TPL->set_bloc('main',"statistics/stats1");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
