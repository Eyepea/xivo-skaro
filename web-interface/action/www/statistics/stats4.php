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

if(xivo::load_class('xivo_statistics_period',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','period',false) === false)
	die('Can\'t load xivo_statistics_period object');
	
$stats_period = new xivo_statistics_period(&$_XOBJ,&$ipbx);
if (isset($_QR['confid']) === true)
	$stats_period->set_idconf($_QR['confid'],true);
$stats_period->parse_log();

$xivo_statistics->set_name('period');

$xivo_statistics->set_rows('queuename',$stats_period->get_queue_list(),'name');

$xivo_statistics->set_data_custom('period',$stats_period->_result);

$xivo_statistics->set_col_struct('treaties');
$xivo_statistics->add_col('tperiod1',
					'direct',
					'custom:period,[queuename],treaties,period1');
$xivo_statistics->add_col('tperiod2',
					'direct',
					'custom:period,[queuename],treaties,period2');
$xivo_statistics->add_col('tperiod3',
					'direct',
					'custom:period,[queuename],treaties,period3');
$xivo_statistics->add_col('tperiod4',
					'direct',
					'custom:period,[queuename],treaties,period4');
$xivo_statistics->add_col('tperiod5',
					'direct',
					'custom:period,[queuename],treaties,period5');

$xivo_statistics->set_col_struct('abandoned');
$xivo_statistics->add_col('aperiod1',
					'direct',
					'custom:period,[queuename],abandoned,period1');
$xivo_statistics->add_col('aperiod2',
					'direct',
					'custom:period,[queuename],abandoned,period2');
$xivo_statistics->add_col('aperiod3',
					'direct',
					'custom:period,[queuename],abandoned,period3');
$xivo_statistics->add_col('aperiod4',
					'direct',
					'custom:period,[queuename],abandoned,period4');
$xivo_statistics->add_col('aperiod5',
					'direct',
					'custom:period,[queuename],abandoned,period5');

$xivo_statistics->gener_table();
$xivo_statistics->gener_graph('t1','stats1');
$table1 = $xivo_statistics;
#$xivo_statistics->reset();

$_TPL->set_var('confid',$stats_period->get_idconf());
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

