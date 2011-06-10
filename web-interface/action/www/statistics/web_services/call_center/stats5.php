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

if(xivo::load_class('xivo_statistics_incall',dwho_file::joinpath(XIVO_PATH_OBJECT,'statistics'),'incall',false) === false)
	die('Can\'t load xivo_statistics_incall object');

$stats_incall = new xivo_statistics_incall(&$_XS);
$stats_incall->get_data();

$tpl_statistics->set_name('incall');
$tpl_statistics->set_baseurl('statistics/call_center/stats5');
$tpl_statistics->set_data_custom('axetype',$axetype);
$tpl_statistics->set_data_custom('listtype',$stats_incall->get_list_by_type());
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
		$tpl_statistics->set_rows('queuename',$stats_incall->get_incall_list(),'keyfile',true);
		$tpl_statistics->set_data_custom('date_process',$_XS->get_datecal());
}

$tpl_statistics->set_data_custom('incall',$stats_incall->_result);

$tpl_statistics->set_col_struct(null);
$tpl_statistics->add_col('presented',
					'direct',
					'custom:incall,[key],chanstart');

$tpl_statistics->gener_table();

$_TPL->set_var('list',$tpl_statistics->get_data_table());
$_TPL->display('/statistics/call_center/generic');

?>
