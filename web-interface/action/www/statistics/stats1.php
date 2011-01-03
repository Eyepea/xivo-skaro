<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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

$appqueue = &$ipbx->get_application('queue');
$list_queue = $appqueue->get_queues_list();

$appagent = &$ipbx->get_application('agent');
$list_agent = $appagent->get_agentfeatures();

$appqueue_log = &$ipbx->get_application('queue_log');
$ls_queue_log = $appqueue_log->get_queue_logs_list();

$appstats_conf = &$_XOBJ->get_application('stats_conf');
$conf = $appstats_conf->get(14);

if(xivo::load_class('xivo_statistics_queue',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','queue',false) === false)
	die('Can\'t load xivo_statistics_queue object');

$tmp = new xivo_statistics_queue($conf,$ls_queue_log);
$tmp->set_data_custom('qos',$queue_qos);
$tmp->parse_log();

$xivo_statistics->set_name('queue');

$xivo_statistics->set_rows('queuename',$list_queue,'name');

$xivo_statistics->set_data_custom('queue',$tmp->_result);

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
					'custom:queue,[name],deterred');
$xivo_statistics->add_col('on_saturation',
					'direct',
					'custom:queue,[name],deterred');

$xivo_statistics->set_col_struct('rerouted');
$xivo_statistics->add_col('on_hangup',
					'direct',
					'custom:queue,[name],rerouted');
$xivo_statistics->add_col('on_guide',
					'direct',
					'custom:queue,[name],rerouted');
$xivo_statistics->add_col('on_number',
					'direct',
					'custom:queue,[name],rerouted');

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

$xivo_statistics->gener();
#$xivo_statistics->render_graph();
$table1 = $xivo_statistics;
#$xivo_statistics->reset();


$_TPL->set_var('statistics',$xivo_statistics);
$_TPL->set_var('conf',$conf);
$_TPL->set_var('ls_queue',$list_queue);
$_TPL->set_var('queue_log',$list_queue_log);
$_TPL->set_var('table1',$table1);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');

$_TPL->set_bloc('main',"statistics/stats1");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
