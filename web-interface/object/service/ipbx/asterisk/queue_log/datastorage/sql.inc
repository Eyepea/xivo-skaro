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
	
	public function stats_sum_by_type($conf,$type,$value,$event,$fieldsum,$addwhere=null)
	{			
		$this->_cnt = 0;

		# not possible PGSQL: field => function sum(character varying) does not exist
		#$field = array((object) "SUM('$fieldsum')");
		
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
			
		#$this->_dso->andwhere('"time" > \'2010-12-01 00:00:01\'');
		#$this->_dso->andwhere('"time" < \'2010-12-01 23:59:59\'');	
		
		#$this->_dso-> wherebetween('time','2010-12-01 00:00:01','2010-12-01 23:59:59',$this->_table);
			
		#$this->_dso->wheredatetime('time','2010-12-20 00:00:01','2010-12-20 23:59:59',$this->_table,'datetime');
		
		$interval = $conf['interval'];
			
		if (empty($interval['dbeg']) === false)
			$this->_dso-> wherebetween('time',$interval['dbeg'],$interval['dend'],$this->_table);
			#$this->_dso->wheredatetime('time',$interval['dbeg'],$interval['dend'],$this->_table,'datetime');
		
		#print($this->_dso->get_select().'<br>');
		
		$r = $this->_dso->select_singlecolumn();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}
	
	public function stats_count_by_type($conf,$type,$value,$event,$addwhere=null)
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
		
		$interval = $conf['interval'];
		if (empty($interval['dbeg']) === false)
			$this->_dso-> wherebetween('time',$interval['dbeg'],$interval['dend'],$this->_table);
			#$this->_dso->wheredatetime('time',$interval['dbeg'],$interval['dend'],$this->_table,'datetime');
			
		#print($this->_dso->get_select().'<br>');

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
			#$this->_dso->wheredatetime('time',$interval['dbeg'],$interval['dend'],$this->_table,'datetime');
	/*
		$this->_dso->wherein('id','');
		
		$this->_dso->wherecontain('firstname',$value);
		$this->_dso->orwherecontain('lastname',$value);
		$this->_dso->orwherecontain('number',$value);

		if(($concat = $this->_dso->concat(array((object) 'firstname',
							' ',
							(object) 'lastname'))) !== false)
			$this->_dso->orwherecontain((object) $concat,$value,true);

		if($this->_dso->aggregate_where() === false)
			return(false);
	*/
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
