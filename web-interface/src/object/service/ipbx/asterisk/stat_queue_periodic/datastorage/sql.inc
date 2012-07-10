<?php

#
# XiVO Web-Interface
# Copyright (C) 2012  Avencall
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

xivo_service_asterisk::required(array('abstract','datastorage','abstract','sql.inc'),true);

class xivo_service_asterisk_stat_queue_periodic_sql extends xivo_service_asterisk_abstract_sql
{

	public function get_min_time()
	{
		$field = array((object) ('MIN(time)'));
		$this->_dso->new_select($this->_table,$field);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return($r[0]);
	}

	public function get_max_time()
	{
		$field = array((object) ('MAX(time)'));
		$this->_dso->new_select($this->_table,$field);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return($r[0]);
	}

	public function queue_sum_by_event($event,$interval,$queue_id)
	{
		$field = array((object) ('SUM("'.$event.'")'));

		$this->_dso->new_select($this->_table,$field);

		$this->_dso->where(array('queue_id' => $queue_id));

		if (is_null($interval) === false)
			$this->_dso->wherebetween('time',
										strftime('%Y-%m-%d %H:%M:%S', $interval['beg']),
										strftime('%Y-%m-%d %H:%M:%S', $interval['end']),
										$this->_table);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}
}

?>
