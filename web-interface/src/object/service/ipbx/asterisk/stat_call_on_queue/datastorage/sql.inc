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

class xivo_service_asterisk_stat_call_on_queue_sql extends xivo_service_asterisk_abstract_sql
{

	public function queue_count_under_qos($qos, $interval, $queue_id)
	{
		$field = array((object) ('COUNT(status)'));

		$this->_dso->new_select($this->_table, $field);
		$this->_dso->where(array('queue_id' => $queue_id));
		$this->_dso->andwhere(array('status' => 'answered'));
		$this->_dso->andwhere($this->_table.'.waittime <= '.$qos);
		$this->_stat_common_where($interval);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

	public function queue_count_by_period($status, $interval, $queue_id, $interval_wt)
	{
		$field = array((object) ('COUNT(status)'));

		$this->_dso->new_select($this->_table, $field);
		$this->_dso->where(array('queue_id' => $queue_id));
		$this->_dso->andwhere(array('status' => $status));
		$this->_stat_common_where($interval);

		if (is_null($interval_wt['end']))
			$this->_dso->andwhere($this->_table.'.waittime > '.$interval_wt['beg']);
		else
			$this->_dso->andwhere($this->_table.'.waittime BETWEEN '.$interval_wt['beg'].' AND '.$interval_wt['end']);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

	public function queue_wait_time($interval, $queue_id)
	{
		$field = array((object) ('SUM(waittime)'));

		$this->_dso->new_select($this->_table, $field);
		$this->_dso->where(array('queue_id' => $queue_id));
		$this->_stat_common_where($interval);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

	public function agent_conversation_time($interval, $agent_ids)
	{
		$field = array((object) ('SUM(talktime)'));

		$this->_dso->new_select($this->_table, $field);

		$this->_dso->wherein('agent_id',$agent_ids);
		$this->_stat_common_where($interval);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

	public function agent_count_status($status, $interval, $agent_ids)
	{
		$field = array((object) ('COUNT(status)'));

		$this->_dso->new_select($this->_table, $field);

		$this->_dso->wherein('agent_id',$agent_ids);
		$this->_dso->andwhere(array('status' => $status));
		$this->_stat_common_where($interval);

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

}

?>
