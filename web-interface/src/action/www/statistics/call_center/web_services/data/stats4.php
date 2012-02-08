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

$access_category = 'statistics';
$access_subcategory = 'call_center';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

$_STS->load_ressource('period');

$stats_period = new stats_ressource_period(&$_XS);
$stats_period->get_data();

$tpl_statistics->set_name('period');
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
		$tpl_statistics->set_rows('day',dwho_date::get_listday_for_week(),'key');
		break;
	case 'month':
		$date = dwho_date::all_to_unixtime($itl['dmonth']);
		$year = date('Y',$date);
		$month = date('m',$date);
		$tpl_statistics->set_rows('day',$_XS->get_listday_for_month($year,$month),'key');
		$tpl_statistics->set_data_custom('month_process',$_XS->get_datecal());
		break;
	case 'year':
		$tpl_statistics->set_rows('month',dwho_date::get_listmonth(),'key');
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

$_TPL->set_var('list',$tpl_statistics->get_data_table());
$_TPL->display('/statistics/call_center/generic');

?>
