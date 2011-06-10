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

$access_category = 'statistics';
$access_subcategory = 'call_center';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

if(xivo::load_class('xivo_statistics_agent',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','agent',false) === false)
	die('Can\'t load xivo_statistics_agent object');

$stats_agent = new xivo_statistics_agent(&$_XS);
$stats_agent->get_data();

$tpl_statistics->set_name('agent');
$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_data_custom('listtype',$stats_agent->get_list_by_type());
$itl = $_XS->get_datecal();
switch ($axetype)
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
		$tpl_statistics->set_rows('agent',$stats_agent->get_agent_list(),'keyfile',true);
		$tpl_statistics->set_data_custom('date_process',$_XS->get_datecal());
}

$tpl_statistics->set_data_custom('agent',$stats_agent->_result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('productivity',
					'expression',
					'{custom:agent,[key],calltime}/{custom:agent,[key],logintime}',
					'percent');

$tpl_statistics->set_col_struct('call_counter');
$tpl_statistics->add_col('connect',
					'direct',
					'custom:agent,[key],connect');
$tpl_statistics->add_col('transfer',
					'direct',
					'custom:agent,[key],transfer');
$tpl_statistics->add_col('ringnoanswer',
					'direct',
					'custom:agent,[key],ringnoanswer');
$tpl_statistics->add_col('outgoing',
					'direct',
					'-');

$tpl_statistics->set_col_struct('total_time');
$tpl_statistics->add_col('login',
					'direct',
					'custom:agent,[key],logintime');
$tpl_statistics->add_col('available',
					'expression',
					'{custom:agent,[key],logintime}-{custom:agent,[key],calltime}',
					'time');
$tpl_statistics->add_col('pause',
					'direct',
					'custom:agent,[key],pausetime');
$tpl_statistics->add_col('traitment',
					'direct',
					'custom:agent,[key],traitmenttime');

$tpl_statistics->set_col_struct('average_time');
$tpl_statistics->add_col('dmt',
					'expression',
					'{custom:agent,[key],traitmenttime}/{custom:agent,[key],connect}',
					'time');
$tpl_statistics->add_col('dmmeg',
					'expression',
					'{custom:agent,[key],pausetime}/{custom:agent,[key],connect}',
					'time');
$tpl_statistics->add_col('dmwu',
					'direct',
					'0',
					'time');

$tpl_statistics->gener_table();

$_TPL->set_var('list',$tpl_statistics->get_data_table());
$_TPL->display('/statistics/call_center/generic');

?>
