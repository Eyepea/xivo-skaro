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

class xivo_service_asterisk_queue_log_postgresql extends xivo_service_asterisk_abstract_sql
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

	public function stats_sum_by_type($type,$value,$event,$fieldsum,$interval=null,$addwhere=null)
	{			
		$this->_cnt = 0;		
		
		$s = microtime(true);

		$field = array((object) ('SUM(cast("'.$fieldsum.'" as int))'));
		
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
		$this->_dso->andwhere('"'.$fieldsum.'" ~ \'^[0-9]+$\'');
			
		if (is_null($addwhere) === false)
		{
			$type = $addwhere[0];
			$value = $addwhere[1];		
			switch ($type)
			{
				case 'BETWEEN':
					$cast = '';
					if (is_numeric($value[1]) === true
					&& is_numeric($value[2]) === true)
						$cast = '::int';
					$this->_dso->andwhere('"'.$this->_table.'"."'.$value[0].'"'.$cast.' BETWEEN '.$value[1].' AND '.$value[2]);
					break;
				case '<':
					$cast = '';
					if (is_numeric($value[1]) === true)
						$cast = '::int';
					$this->_dso->andwhere('"'.$this->_table.'"."'.$value[0].'"'.$cast.' < '.$value[1]);
					break;
			}
		}
	
		if (is_null($interval) === false)
		{
			if(isset($interval['beg']) === true
			&& isset($interval['end']) === true)
			{
				#$this->_dso->where('"'.$this->_table.'"."time"::timestamp BETWEEN \''.$interval['beg'].'\'::timestamp AND \''.$interval['end'].'\'::timestamp');
				$this->_dso->wherebetween('time',$interval['beg'],$interval['end'],$this->_table);
				#$this->_dso->wheredatetime('time',$interval['dbeg'],$interval['dend'],$this->_table,'datetime');
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
				return(false);
		}
		
		$r = $this->_dso->select_singlecolumn();
		
		#print ($this->_dso->get_select().'<br>');
		#var_dump(dwho_second_to((microtime(true) - $s),2));

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}
	
	public function stats_count_by_type($type,$value,$event,$interval=null,$addwhere=null)
	{			
		$this->_cnt = 0;		
		
		$s = microtime(true);

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
			case 'period':
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
		{
			$type = $addwhere[0];
			$value = $addwhere[1];		
			switch ($type)
			{
				case 'BETWEEN':
					$cast = '';
					if (is_numeric($value[1]) === true
					&& is_numeric($value[2]) === true)
						$cast = '::int';
					$this->_dso->andwhere('"'.$this->_table.'"."'.$value[0].'"'.$cast.' BETWEEN '.$value[1].' AND '.$value[2]);
					break;
				case '<':
				case '>':
				case '=':
					$cast = '';
					if (is_numeric($value[1]) === true)
						$cast = '::int';
					$this->_dso->andwhere('"'.$this->_table.'"."'.$value[0].'"'.$cast.' '.$type.' '.$value[1]);
					break;
			}
		}
		
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
		
		#print ($this->_dso->get_select().'<br>');
		#var_dump(dwho_second_to((microtime(true) - $s),2));

		return($this->_cnt);
	}

	public function stats($conf,$type,$data)
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

		$r = $this->_dso->select_all();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}
}

?>