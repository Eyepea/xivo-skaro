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

xivo_service_asterisk::required(array('abstract','datastorage','abstract','sql.inc'),true);

class xivo_service_asterisk_queue_log_sql extends xivo_service_asterisk_abstract_sql
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

	public function search($arr,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		$this->_dso->new_select($this->_table);

		if($this->_search_where($arr) === false)
			return(false);

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	public function _search_where($arr)
	{
		if(is_array($arr) === false)
			return(false);

		return(true);
	}

	public function stats_sum_by_type($type,$value,$event,$fieldsum,$interval=null,$addwhere=null)
	{
		$this->_cnt = 0;

		$this->_dso->new_select($this->_table,array($fieldsum));

		switch ($type)
		{
			case 'agent':
				if (is_array($value) === true)
					$this->_dso->wherein('agent',$value);
				else
					$this->_dso->where(array('agent' => $value));
				break;
			case 'queue':
				if (is_array($value) === true)
					$this->_dso->wherein('queuename',$value);
				else
					$this->_dso->where(array('queuename' => $value));
				break;
			default:
				return(false);
		}

		$this->_dso->andwhere(array('event' => $event));

		if (is_null($addwhere) === false)
			$this->_dso->andwhere($addwhere);

		if (is_null($interval) === false)
		{
			if(isset($interval['dbeg']) === true
			&& isset($interval['dend']) === true)
			{
				$this->_dso->wherebetween('time',$interval['dbeg'],$interval['dend'],$this->_table);
			}
			elseif (($nbinterval = count($interval)) > 2)
			{
				$this->_dso->aggregate_where(false,'AND');
				foreach ($interval as $itl)
					$this->_dso->orwherebetween('time',$itl['dbeg'],$itl['dend'],$this->_table);
				$this->_dso->aggregate_where(false,'AND');
			}
		}

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

	public function stats_count_by_type($type,$value,$event,$interval=null,$addwhere=null)
	{
		$this->_cnt = 0;

		$this->_dso->new_select($this->_table,array('event'));

		switch ($type)
		{
			case 'agent':
				if (is_array($value) === true)
					$this->_dso->wherein('agent',$value);
				else
					$this->_dso->where(array('agent' => $value));
				break;
			case 'queue':
				if (is_array($value) === true)
					$this->_dso->wherein('queuename',$value);
				else
					$this->_dso->where(array('queuename' => $value));
				break;
			default:
				return(false);
		}

		$this->_dso->andwhere(array('event' => $event));

		if (is_null($addwhere) === false)
			$this->_dso->andwhere($addwhere);

		if (is_null($interval) === false)
		{
			if(isset($interval['dbeg']) === true
			&& isset($interval['dend']) === true)
			{
				$this->_dso->wherebetween('time',$interval['dbeg'],$interval['dend'],$this->_table);
			}
			elseif (($nbinterval = count($interval)) > 2)
			{
				$this->_dso->aggregate_where(false,'AND');
				foreach ($interval as $itl)
					$this->_dso->orwherebetween('time',$itl['dbeg'],$itl['dend'],$this->_table);
				$this->_dso->aggregate_where(false,'AND');
			}
		}

		if(($this->_cnt = $this->_dso->select_count()) === false)
			$this->_cnt = 0;

		return($this->_cnt);
	}

	public function stats($conf,$type,$data,$order=null,$limit=null)
	{
		if (is_null($conf) === true)
			return(false);

		$this->_cnt = 0;

		$this->_dso->new_select($this->_table);

		switch ($type)
		{
			case 'agent':
				if (is_array($data) === true)
					$this->_dso->wherein('agent',$data);
				else
					$this->_dso->where(array('agent' => $data));
				break;
			case 'queue':
				if (is_array($data) === true)
					$this->_dso->wherein('queuename',$data);
				else
					$this->_dso->where(array('queuename' => $data));
				break;
			default:
				return(false);
		}

		$interval = $conf['interval'];

		if (empty($interval['dbeg']) === false)
			$this->_dso-> wherebetween('time',$interval['dbeg'],$interval['dend'],$this->_table);

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}
}

?>
