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

$stats_agent = new xivo_statistics_agent(&$_XS);
$stats_agent->parse_log();

$tpl_statistics->set_name('agent');

$tpl_statistics->set_rows('agent',$stats_agent->get_agent_list(),'number');

$tpl_statistics->set_data_custom('agent',$stats_agent->_result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('login',
					'direct',
					'custom:agent,agent/[number],logintime');

$tpl_statistics->set_col_struct('traitment');
$tpl_statistics->add_col('total',
					'direct',
					'custom:agent,agent/[number],traitmenttime',
					'time');
$tpl_statistics->add_col('total_with_talk',
					'direct',
					'custom:agent,agent/[number],traitmenttime',
					'time');
$tpl_statistics->add_col('total_with_wup',
					'direct',
					'custom:agent,agent/[number],traitmenttime',
					'time');

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('available',
					'expression',
					'{custom:agent,agent/[number],logintime}-{custom:agent,agent/[number],calltime}',
					'time');

$tpl_statistics->set_col_struct('withdrawal');
$tpl_statistics->add_col('totalwithdrawal',
					'direct',
					'custom:agent,agent/[number],pausetime');

$tpl_statistics->gener_table();
#$tpl_statistics->gener_graph('t1','stats1');
$table1 = $tpl_statistics;

$_TPL->set_var('table1',$table1);
$_TPL->set_var('showdashboard',true);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/stats3");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>

