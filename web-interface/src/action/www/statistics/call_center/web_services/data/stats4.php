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
$access_subcategory = 'stats4';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));
include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

$_STS->load_ressource('period');

$stats_period = new stats_ressource_period(&$_XS);
$stats_period->get_data();

$tpl_statistics->set_name('period');
$tpl_statistics->set_baseurl('statistics/call_center/data/stats4');
$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_data_custom('listtype',$stats_period->get_list_by_type());
$itl = $_XS->get_datecal();

switch ($axetype)
{
	case 'day':
		$tpl_statistics->set_rows('hour', $_XS->get_listhour(), 'key');
		$tpl_statistics->set_row_total('hour');
		break;
	case 'week':
		$tpl_statistics->set_rows('day',$stats_period->get_rows(),'key');
		$tpl_statistics->set_row_total('day');
		break;
	case 'month':
		$tpl_statistics->set_rows('day', $stats_period->get_rows(),'key');
		$tpl_statistics->set_row_total('day');
		break;
	case 'year':
		$tpl_statistics->set_rows('month',dwho_date::get_listmonth(),'key');
		$tpl_statistics->set_row_total('month');
		break;
	case 'type':
	default:
		$tpl_statistics->set_rows('queuename',$stats_period->get_queue_list(),'keyfile',true);
		$tpl_statistics->set_row_total('queuename');
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

$_TPL->set_var('list',$tpl_statistics->get_data_table());
$_TPL->display('/statistics/call_center/generic');

?>
