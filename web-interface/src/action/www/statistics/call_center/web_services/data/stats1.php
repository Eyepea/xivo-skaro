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

$access_category = 'data';
$access_subcategory = 'stats1';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));
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
		$tpl_statistics->set_rows('hour', $_XS->get_listhour(), 'key');
		$tpl_statistics->set_row_total('hour');
		break;
	case 'week':
		$tpl_statistics->set_rows('day',$stats_queue->get_rows(),'key');
		$tpl_statistics->set_row_total('day');
		break;
	case 'month':
		$tpl_statistics->set_rows('day', $stats_queue->get_rows(),'key');
		$tpl_statistics->set_row_total('day');
		break;
	case 'year':
		$tpl_statistics->set_rows('month',dwho_date::get_listmonth(),'key');
		$tpl_statistics->set_row_total('month');
		break;
	case 'type':
	default:
		$tpl_statistics->set_rows('queuename',$stats_queue->get_queue_list(),'keyfile',true);
		$tpl_statistics->set_row_total('queuename');
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

$tpl_statistics->set_col_struct('schedule');
$tpl_statistics->add_col('on_close',
		'direct',
		'custom:queue,[key],deterred_on_close');

$tpl_statistics->set_col_struct('redistributed');
$tpl_statistics->add_col('on_timeout',
		'direct',
		'custom:queue,[key],timeout');
$tpl_statistics->add_col('on_saturation',
		'direct',
		'custom:queue,[key],deterred_on_saturation');
$tpl_statistics->add_col('on_joinempty',
		'direct',
		'custom:queue,[key],joinempty');
$tpl_statistics->add_col('on_leaveempty',
		'direct',
		'custom:queue,[key],leaveempty');

$tpl_statistics->set_col_struct("ratio");
$tpl_statistics->add_col('average_time_waiting',
		'direct',
		'custom:queue,[key],average_wait_time',
		'time',
		'average');
$tpl_statistics->add_col('home_rated',
		'direct',
		'custom:queue,[key],home_rated',
		'percent');
$tpl_statistics->add_col('qos',
		'direct',
		'custom:queue,[key],qos',
		'percent');

$tpl_statistics->gener_table();

$_TPL->set_var('list',$tpl_statistics->get_data_table());
$_TPL->display('/statistics/call_center/generic');

?>
