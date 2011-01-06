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

if(xivo::load_class('xivo_statistics_agent',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','agent',false) === false)
	die('Can\'t load xivo_statistics_agent object');

$stats_agent = new xivo_statistics_agent(&$_XOBJ,&$ipbx);
if (isset($_QR['confid']) === true)
	$stats_agent->set_idconf($_QR['confid']);
$stats_agent->parse_log();

$xivo_statistics->set_name('agent');

$xivo_statistics->set_rows('agent',$stats_agent->get_agent_list(),'number');

$xivo_statistics->set_data_custom('agent',$stats_agent->_result);

$xivo_statistics->set_col_struct('default');
$xivo_statistics->add_col('login',
					'direct',
					'custom:agent,agent/[number],logintime');

$xivo_statistics->set_col_struct('traitment');
$xivo_statistics->add_col('total',
					'direct',
					'custom:agent,agent/[number],traitmenttime',
					'time');
$xivo_statistics->add_col('total_with_talk',
					'direct',
					'custom:agent,agent/[number],traitmenttime',
					'time');
$xivo_statistics->add_col('total_with_wup',
					'direct',
					'custom:agent,agent/[number],traitmenttime',
					'time');

$xivo_statistics->set_col_struct('default');
$xivo_statistics->add_col('available',
					'expression',
					'{custom:agent,agent/[number],logintime}-{custom:agent,agent/[number],calltime}',
					'time');

$xivo_statistics->set_col_struct('withdrawal');
$xivo_statistics->add_col('totalwithdrawal',
					'direct',
					'custom:agent,agent/[number],pausetime');

$xivo_statistics->gener();
#$xivo_statistics->render_graph();
$table1 = $xivo_statistics;
#$xivo_statistics->reset();

$_TPL->set_var('confid',$stats_agent->get_idconf());
$_TPL->set_var('table1',$table1);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics');

$_TPL->set_bloc('main',"statistics/stats3");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>

