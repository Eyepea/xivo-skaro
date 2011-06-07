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

if(xivo::load_class('xivo_statistics_period',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','period',false) === false)
	die('Can\'t load xivo_statistics_period object');
	
$stats_period = new xivo_statistics_period(&$_XS);
$stats_period->get_data();

$tpl_statistics->set_name('period');
$tpl_statistics->set_baseurl('statistics/call_center/stats4');
$tpl_statistics->set_data_custom('axetype',$_XS->get_axetype());
$tpl_statistics->set_data_custom('listtype',$stats_period->get_list_by_type());
$itl = $_XS->get_datecal();
switch ($axetype)
{
	case 'day':
		$tpl_statistics->set_rows('hour',$_XS->get_listhour(),'key');
		$tpl_statistics->set_data_custom('day_process',$_XS->get_datecal());
		break;
	case 'week':
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_week(),'key');
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
		$tpl_statistics->set_rows('queuename',$stats_period->get_queue_list(),'keyfile',true);
		$tpl_statistics->set_data_custom('date_process',$_XS->get_datecal());
}

$tpl_statistics->set_data_custom('period',$stats_period->_result);

$tpl_statistics->set_col_struct('connect');
$tpl_statistics->add_col('tperiod1',
					'direct',
					'custom:period,[key],connect,period1');
$tpl_statistics->add_col('tperiod2',
					'direct',
					'custom:period,[key],connect,period2');
$tpl_statistics->add_col('tperiod3',
					'direct',
					'custom:period,[key],connect,period3');
$tpl_statistics->add_col('tperiod4',
					'direct',
					'custom:period,[key],connect,period4');
$tpl_statistics->add_col('tperiod5',
					'direct',
					'custom:period,[key],connect,period5');

$tpl_statistics->set_col_struct('abandon');
$tpl_statistics->add_col('aperiod1',
					'direct',
					'custom:period,[key],abandon,period1');
$tpl_statistics->add_col('aperiod2',
					'direct',
					'custom:period,[key],abandon,period2');
$tpl_statistics->add_col('aperiod3',
					'direct',
					'custom:period,[key],abandon,period3');
$tpl_statistics->add_col('aperiod4',
					'direct',
					'custom:period,[key],abandon,period4');
$tpl_statistics->add_col('aperiod5',
					'direct',
					'custom:period,[key],abandon,period5');

$tpl_statistics->gener_table();

$_TPL->set_var('table1',$tpl_statistics);
$_TPL->set_var('listobject',$_XS->get_object_list());
$_TPL->set_var('objectkey',$_XS->get_objectkey());
$_TPL->set_var('showdashboard_call_center',true);

if($act === 'exportcsv')
{
	$_TPL->set_var('result',$tpl_statistics->render_csv());
	$_TPL->set_var('name','period');
	$_TPL->set_var('date',$itl);
	$_TPL->display('/bloc/statistics/exportcsv');
	die();
}

$xivo_jqplot->init_data_full($tpl_statistics);

switch ($axetype)
{
	case 'type':
		$xivo_jqplot->gener_graph('period_pie_connect','chart1','total_call_connect_by_period');
		$xivo_jqplot->gener_graph('period_pie_abandon','chart2','total_call_abandon_by_period');
		break;
	case 'day':
	case 'week':
	case 'month':
	case 'year':
		break;
	default:
}

$_TPL->set_var('xivo_jqplot',$xivo_jqplot);
$_TPL->set_var('mem_info',(memory_get_usage() - $base_memory));
$_TPL->set_var('bench',(microtime(true) - $bench_start));

$dhtml = &$_TPL->get_module('dhtml');
$xivo_jqplot->write_js_loaded_plugin(&$dhtml);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/call_center');

$_TPL->set_bloc('main',"statistics/call_center/stats4");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>

