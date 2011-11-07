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

xivo_stats::required(array('abstract','datastorage','sql.inc'),true);

class xivo_stats_queue_log_sql extends xivo_stats_abstract_sql
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

		if(isset($arr['dbeg']) === true)
		{
			$dbeg = $arr['dbeg'];
			$len = strlen($dbeg);

			if($len === 4)
				$format = '%Y';
			else if($len === 7)
				$format = '%Y-%m';
			else if($len === 10)
				$format = '%Y-%m-%d';
			else
				$format = '%Y-%m-%d %H:%i:%s';

			if(isset($arr['dend']) === true)
				$dend = $arr['dend'];
			else
				$dend = '';

			$this->_dso->wheredate('eventtime',$dbeg,$dend,null,$format);
			#$this->_dso->wherebetween('eventtime',$arr['beg'],$arr['end']);
		}

		return(true);
	}

	public function stats_sum_by_type($type,$value,$event,$fieldsum,$interval=null,$addwhere=null)
	{
		$this->_cnt = 0;

		$field = array((object) ('SUM("'.$fieldsum.'")'));

		$this->_dso->new_select($this->_table,$field);

		switch ($type)
		{
			case 'agent':
				if (is_array($value) === true)
				{
					if (count($value) === 1)
						$this->_dso->where(array('agent' => $value[0]));
					else
						$this->_dso->wherein('agent',$value);
				}
				else
					$this->_dso->where(array('agent' => $value));
				break;
			case 'period':
			case 'queue':
				if (is_array($value) === true)
				{
					if (count($value) === 1)
						$this->_dso->where(array('queuename' => $value[0]));
					else
						$this->_dso->wherein('queuename',$value);
				}
				else
					$this->_dso->where(array('queuename' => $value));
				break;
			default:
				return(false);
		}

		$this->_dso->andwhere(array('event' => $event));

		if (is_null($addwhere) === false)
			$this->search_add_where($addwhere);

		if (is_null($interval) === false)
		{
			if(isset($interval['beg']) === true
			&& isset($interval['end']) === true)
				$this->_dso->wherebetween('time',$interval['beg'],$interval['end'],$this->_table);
			elseif (($nbinterval = count($interval)) > 2)
			{
				$this->_dso->aggregate_where(false,'AND');
				foreach ($interval as $itl)
					$this->_dso->orwherebetween('time',$itl['beg'],$itl['end'],$this->_table);
				$this->_dso->aggregate_where(false,'AND');
			}
			else
				return(false);
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
				{
					if (count($value) === 1)
						$this->_dso->where(array('agent' => $value[0]));
					else
						$this->_dso->wherein('agent',$value);
				}
				else
					$this->_dso->where(array('agent' => $value));
				break;
			case 'queue':
			case 'period':
				if (is_array($value) === true)
				{
					if (count($value) === 1)
						$this->_dso->where(array('queuename' => $value[0]));
					else
						$this->_dso->wherein('queuename',$value);
				}
				else
					$this->_dso->where(array('queuename' => $value));
				break;
			default:
				return(false);
		}

		$this->_dso->andwhere(array('event' => $event));

		if (is_null($addwhere) === false)
			$this->search_add_where($addwhere);

		if (is_null($interval) === false)
		{
			if(isset($interval['beg']) === true
			&& isset($interval['end']) === true)
			{
				#$this->_dso->where('"'.$this->_table.'"."time"::timestamp BETWEEN \''.$interval['beg'].'\'::timestamp AND \''.$interval['end'].'\'::timestamp');
				$this->_dso->wherebetween('time',$interval['beg'],$interval['end'],$this->_table);
				#$this->_dso->wheredatetime('time',$interval['beg'],$interval['end'],$this->_table,'datetime');
			}
			elseif (($nbinterval = count($interval)) > 2)
			{
				$this->_dso->aggregate_where(false,'AND');

				foreach ($interval as $itl)
				{
					#$this->_dso->orwhere('"'.$this->_table.'"."time"::timestamp BETWEEN \''.$itl['beg'].'\'::timestamp AND \''.$itl['end'].'\'::timestamp');
					$this->_dso->orwherebetween('time',$itl['beg'],$itl['end'],$this->_table);
					#$this->_dso->orwheredatetime('time',$itl['beg'],$itl['end'],$this->_table,'datetime');
				}

				$this->_dso->aggregate_where(false,'AND');
			}
			else
				return(0);
		}

		if(($this->_cnt = $this->_dso->select_count()) === false)
			$this->_cnt = 0;

		return($this->_cnt);
	}

	private function search_add_where($addwhere)
	{
		if(is_array($addwhere) === false)
			return(false);

		$type = $addwhere[0];
		$value = $addwhere[1];
		switch ($type)
		{
			case 'BETWEEN':
				$this->_dso->wherebetween($value[0],$value[1],$value[2],$this->_table);
				break;
			case 'ISNOT':
				$this->_dso->andwherenot(array($value[0] => $value[1]),$this->_table);
				break;
			case '<':
			case '>':
			case '=':
				$this->_dso->andwhere($this->_table.'.'.$value[0].' '.$type.' '.$value[1]);
				break;
		}
	}
}

?>
