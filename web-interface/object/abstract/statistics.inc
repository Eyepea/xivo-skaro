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

class xivo_statistics_abstract
{
	
	public	 	$_xs		 		= null;
	public 		$_data_custom 		= array();
	public 		$_counter	 		= array();
	public		$_result 			= array();
	
	public function __construct(&$_XS)
	{
		$this->_xs = &$_XS;
		$this->_xs->set_type($this->_type);
	}
		
	public function set_method($method)
	{ 
		$this->_xs->set_method($method);
	}
	
	public function set_data_custom($key,$data)
	{
		$this->_data_custom[$key] = $data;
	}
	
	public function get_list_by_type()
	{
		return($this->_xs->get_list_by_type($this->_type));
	}
	
	public function get_queue_list()
	{			
		return($this->_xs->get_queue_list());
	}
	
	public function get_agent_list()
	{			
		return($this->_xs->get_agent_list());
	}
	
	public function db_eval_data($type,$value,$event,$field=null,$addwhere=null)
	{
		return($this->_xs->db_eval_data($type,$value,$event,$field,$addwhere));
	}
	
	public function eval_count_data($value,$event,$addwhere=null)
	{
		return($this->db_eval_data('count',$value,$event,null,$addwhere));
	}
	
	public function eval_sum_data($value,$event,$field,$addwhere=null)
	{
		return($this->db_eval_data('sum',$value,$event,$field,$addwhere));
	}

	public function eval_field_queue_log($event,$type)
	{			
		return($this->_xs->eval_field_queue_log($event,$type));
	}

	public function eval_data_queue_log($queue_log_entry,$event,$type)
	{			
		return($this->_xs->eval_data_queue_log($queue_log_entry,$event,$type));
	}
	
	protected function init_result($key)
	{
		$res = &$this->_result;
		
		if (is_array($key) === true
		&& isset($key['value']) === true)
			$key = $key['value'];
			
		if (isset($res[$key]) === false)
		{
			$data_process = &$res[$key];
			$data_process = array();
			
			foreach ($this->_field as $k => $field)
			{
				$data_process[$k] = array();
				$data_process[$k]['type'] = $field['type'];
				$data_process[$k]['result'] = 0;
			}
		}
	}

	public function get_data()
	{
		$axetype = $this->_xs->get_axetype();
		
		if (($itl = $this->_xs->get_datecal()) === false)
			return(false);
			
		if (is_null($itl['dbeg']) === true)
			return(false);
		
		$dbeg = strtotime($itl['dbeg']);
		$dend = strtotime($itl['dend']);
		
		if (($full_list_day = $this->_xs->get_listday_for_interval($dbeg,$dend)) === false
		|| ($data_listmonth = $this->_xs->get_listmonth_for_interval($dbeg,$dend)) === false)
			return(false);		
		
		$data = $this->get_list_by_type();

		if (empty($data) === true)
			return(false);
			
		$data = array_shift($data);				
		$keyfile = $data['key'][0];		
		$key_field = 'key';
		
		switch ($axetype)
		{
			case 'day':
				$key_data = $this->_xs->get_listhour();			
				$key_field = 'key';	
				$date = $this->_xs->all_to_unixtime($itl['dday']);
				$year = date('Y',$date);
				$month = date('m',$date);
				$day = date('d',$date);
				
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$key = $key_full_data[$key_field];
					$dip = array();	
					$dip['beg'] = mktime($key,0,0,$month,$day,$year);
					$dip['end'] = mktime($key+1,0,0,$month,$day,$year);
					$this->_xs->_interval_process = $dip;
					$this->parse_log($keyfile,$key);
				}
				break;
			case 'week':
				$key_data = $this->_xs->get_listday_for_interval($dbeg,$dend);
				$key_field = 'dayname';
				
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$k = $key_full_data[$key_field];
											
					$this->init_result($k);
					$listmonth = $data_listmonth;
					while($listmonth)
					{
						$key = array_shift($listmonth);
						$key = $key['key'];
						$year = substr($key,0,4);
						$month = substr($key,4,2);
						
						if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
						|| is_null($month_data) === true)
							continue;
						
						$listdaynum = array_keys($month_data);
						while($listdaynum)
						{
							$day = array_shift($listdaynum);
							
							$index = (int) ($year.$month.$day);
							if ($index !== $key_full_data['key'])
								continue;					
						
							if (isset($full_list_day[$year.$month.$day]) === false)
								continue;
							
							// update result for day data
							$this->eval_update_result($month_data[$day],$k);
						}
					}
				}
				break;
			case 'month':
				$date = $this->_xs->all_to_unixtime($itl['dmonth']);
				$year = date('Y',$date);
				$month = date('m',$date);		
				
				if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
				|| is_null($month_data) === true)
					break;
					
				$this->_result = ($month_data);
				break;
			case 'year':
				$key_field = 'key';
				$key_data = $this->_xs->get_listmonth();
				
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$k = $key_full_data[$key_field];
						
					$this->init_result($k);
					$listmonth = $data_listmonth;
					while($listmonth)
					{
						$key = array_shift($listmonth);
						$key = $key['key'];
						$year = substr($key,0,4);
						$month = substr($key,4,2);
						
						if (((int) $month) != ((int) $k))
							continue;
						
						if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
						|| is_null($month_data) === true)
							continue;
						
						$listdaynum = array_keys($month_data);
						while($listdaynum)
						{
							$day = array_shift($listdaynum);
						
							if (isset($full_list_day[$year.$month.$day]) === false)
								continue;
							
							// update result for day data
							$this->eval_update_result($month_data[$day],$k);
						}
					}
				}
				break;
			case 'type':
			default:
				$key_data = $this->get_list_by_type();
				$key_field = 'key';
				
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$keyfile = $key_full_data[$key_field][0];
						
					$this->init_result($keyfile);
					$listmonth = $data_listmonth;
					while($listmonth)
					{
						$key = array_shift($listmonth);
						$key = $key['key'];
						$year = substr($key,0,4);
						$month = substr($key,4,2);
						
						if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
						|| is_null($month_data) === true)
							continue;
						$listdaynum = array_keys($month_data);
						while($listdaynum)
						{
							$day = array_shift($listdaynum);
						
							if (isset($full_list_day[$year.$month.$day]) === false)
								continue;
							
							// update result for day data
							$this->eval_update_result($month_data[$day],$keyfile);
						}
					}
				}
		}
	}
	
	private function eval_update_result($data_to_eval,$key)
	{							
		$listfield = array_keys($data_to_eval);
		while($listfield)
		{
			$field = array_shift($listfield);
			if(isset($data_to_eval[$field]['result']) === true
			&& $data_to_eval[$field]['result'] !== 0)
				$this->update_result(array($key,$field),$data_to_eval[$field]['result']);						
			elseif(isset($data_to_eval[$field]['result']) === false
			&& count($data_to_eval[$field]) >> 2)
			{
				$listssfield = array_keys($data_to_eval[$field]);
				while($listssfield)
				{
					$ssfield = array_shift($listssfield);
					if($data_to_eval[$field][$ssfield]['result'] !== 0)
						$this->update_result(array($key,$field,$ssfield),$data_to_eval[$field][$ssfield]['result']);
				}	
			}
		}
	}
	
	protected function update_result($var,$str,$operator='+')
	{
		if (($res = call_user_func_array(array($this,'eval_result_var'), $var)) === null
		|| isset($res['result']) === false)
			return(false);
		 		
		$result = $res['result'];
			
		switch($operator)
		{
			case '+':
				$result += $str;
				break;
			case '-':
				$result -= $str;
				break;
			default:
		}
				
		$this->set_result_var($result,$var);
		
		return(true);
	}
	
	private function set_result_var($result,$arr)
	{	
		$var = &$this->_result;
		
		for($i = 0;$i < count($arr);$i++)
		{
			$key = $arr[$i];
			if (isset($var[$key]) === true)
				$var = &$var[$key];
		}
		
		$var['result'] = $result;	
	}
	
	private function eval_result_var() 
	{	
		if(($argc = func_num_args()) === 0)
			return(null);
	
		$name = (string) func_get_arg(0);
	
		if (isset($this->_result[$name]) === true)
			$var = $this->_result;
		else
			return(null);
	
		$ref = $var[$name];
	
		if($argc === 1)
			return($ref);
		else if(is_array($var[$name]) === false)
			return(null);
	
		for($i = 1;$i < $argc;$i++)
		{
			$key = func_get_arg($i);
	
			if(dwho_ak($key,$ref) === false)
			        return(null);
	
			$ref = $ref[$key];
		}
	
		return($ref);	
	}
	
}
