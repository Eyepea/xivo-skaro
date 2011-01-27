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
	
$stats_period = new xivo_statistics_period(&$_XS);
$stats_period->get_data();

$tpl_statistics->set_name('period');
$tpl_statistics->set_baseurl('statistics/call_center/stats4');

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
		$tpl_statistics->set_rows('queuename',$stats_period->get_queue_list(),'name',true);
		$tpl_statistics->set_data_custom('date_process',$_XS->get_datecal());
}

$tpl_statistics->set_data_custom('period',$stats_period->_result);

$tpl_statistics->set_col_struct('connect');
$tpl_statistics->add_col('tperiod1',
					'direct',
					'custom:period,[key],answered,period1');
$tpl_statistics->add_col('tperiod2',
					'direct',
					'custom:period,[key],answered,period2');
$tpl_statistics->add_col('tperiod3',
					'direct',
					'custom:period,[key],answered,period3');
$tpl_statistics->add_col('tperiod4',
					'direct',
					'custom:period,[key],answered,period4');
$tpl_statistics->add_col('tperiod5',
					'direct',
					'custom:period,[key],answered,period5');

$tpl_statistics->set_col_struct('abandoned');
$tpl_statistics->add_col('aperiod1',
					'direct',
					'custom:period,[key],abandoned,period1');
$tpl_statistics->add_col('aperiod2',
					'direct',
					'custom:period,[key],abandoned,period2');
$tpl_statistics->add_col('aperiod3',
					'direct',
					'custom:period,[key],abandoned,period3');
$tpl_statistics->add_col('aperiod4',
					'direct',
					'custom:period,[key],abandoned,period4');
$tpl_statistics->add_col('aperiod5',
					'direct',
					'custom:period,[key],abandoned,period5');

$tpl_statistics->gener_table();
#$tpl_statistics->gener_graph('t1','stats1');
$table1 = $tpl_statistics;

$_TPL->set_var('table1',$table1);
$_TPL->set_var('listobject',$_XS->get_object_list());
$_TPL->set_var('objectkey',$_XS->get_objectkey());
$_TPL->set_var('hascachetype',$_XS->has_cache_type());
$_TPL->set_var('showdashboard',true);

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/stats4");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>

