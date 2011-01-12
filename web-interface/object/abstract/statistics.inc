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
	
	public function get_list_by_type()
	{					
		return($this->_xs->get_list_by_type());
	}
	
	public function get_queue_list()
	{			
		return($this->_xs->get_queue_list());
	}
	
	public function get_agent_list()
	{			
		return($this->_xs->get_agent_list());
	}
	
	public function set_data_custom($key,$data)
	{
		$this->_data_custom[$key] = $data;
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

	public function eval_during_time($key,$eventprocess,$eventstart,$eventend,$time)
	{			
		if (isset($this->_counter[$key]) === false)
			$this->_counter[$key] = array();
			
		if (isset($this->_counter[$key][$eventstart]) === false)
		{
			$this->_counter[$key][$eventstart] = array();
			$this->_counter[$key][$eventstart]['start'] = 0;
			$this->_counter[$key][$eventstart]['token'] = 0;
			$this->_counter[$key][$eventstart]['total'] = 0;
		}
					
		$counter = &$this->_counter[$key][$eventstart];
		$timearr = explode('.',$time);
		
		if (preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$timearr[0]) !== 1)
			return(false);
			
		$timeprocess = (int) dwho_change_date_format($timearr[0],'Y-m-d H:i:s','U');
		
		$rs = 0;
		switch ($eventprocess)
		{
			case $eventstart:
				if ($counter['token'] === 1
				&& $counter['start'] !== 0)
					$rs = ($timeprocess - $counter['start']);	
				$counter['token'] = 1;
				$counter['start'] = $timeprocess;		
				break;
			case $eventend:
				if ($counter['token'] === 0)
					continue;
				$rs = ($timeprocess - $counter['start']);					
				$counter['token'] = 0;
				$counter['start'] = 0;
				break;
			default:
		}
		
		$counter['total'] += $rs;
		
		return($rs);
	}
	
	public function update_result($var,$str,$operator='+')
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
