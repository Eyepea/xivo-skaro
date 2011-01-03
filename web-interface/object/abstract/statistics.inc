<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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
	
	public 	$_queue_log_conf	= array();
	public 	$_queue_log 		= array();
	public 	$_data_custom 		= array();
	public 	$_counter	 		= array();
	public 	$_conf		 		= array();
	public 	$_period	 		= array('period1'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period2'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period3'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period4'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period5'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											));
	public		$_result 			= array();
	
	public function __construct($conf,$queue_log)
	{
		if ($this->set_conf($conf) === false)
			trigger_error('Failed to statistics configuration',E_USER_ERROR);
		$this->set_queue_log($queue_log);
		if(($this->_queue_log_conf = &dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queue_log configuration',E_USER_ERROR);
	}
	
	private function set_conf($conf)
	{
		if (is_array($conf) === false
		|| isset($conf['stats_conf']) === false)
			return(false);
		
		$this->_conf = $conf;
		
		$stats_conf = $conf['stats_conf'];
		
		for($i=1;$i<6;$i++)
		{
			if (isset($stats_conf['period'.$i]) === false)
				continue;
				
			$this->_period['period'.$i]['exp'] = $stats_conf['period'.$i];
			
			if (preg_match('/([0-9]+)[-]{1}([0-9]+)/',$stats_conf['period'.$i],$out) === 1)
			{
				$this->_period['period'.$i]['beg'] = (int) $out[1];
				$this->_period['period'.$i]['end'] = (int) $out[2];
			}			
		}
		
		return(true);
	}
	
	private function set_queue_log($queue_log)
	{
		$this->_queue_log = $queue_log;
	}
	
	public function set_data_custom($key,$data)
	{
		$this->_data_custom[$key] = $data;
	}

	public function eval_data_queue_log($queue_log_entry,$event,$type)
	{			
		$conf = $this->_queue_log_conf;
		
		if (isset($conf[$event]) === false
		|| in_array($type,$conf[$event]) === false)
			return(0);
			
		$pos = 0;
		$nb = count($conf[$event]);
		for ($i=0;$i<$nb;$i++)
			if ($conf[$event][$i] === $type)
				$pos = $i+1;	
			
		if (isset($queue_log['data']) === true
		&& dwho_empty($queue_log['data']) === false)
		{
			$data = explode($queue_log_entry['data']);
			return($data[$pos]);
		}
		elseif (isset($queue_log_entry['data'.$pos])
		&& dwho_empty($queue_log_entry['data'.$pos]) === false)
		{
			return($queue_log_entry['data'.$pos]);
		}
			
		return(0);		
	}

	public function eval_during_time($key,$event,$eventstart,$eventend,$time)
	{			
		if (isset($this->_counter[$key]) === false)
		{
			$this->_counter[$key] = array();
			$this->_counter[$key][$eventstart] = 0;
			$this->_counter[$key]['c'] = 0;
		}
			
		$counter = &$this->_counter[$key];
		$timearr = explode('.',$time);
		$timeprocess = dwho_change_date_format($timearr[0],'Y-m-d H:i:s','U');
			
		$rs = 0;
		switch ($event)
		{
			case $eventstart:
				if (false
				&& $counter['c'] === 1
				&& $counter[$event] !== 0)
					$rs = ($timeprocess - $counter[$event]);
				$counter['c'] = 1;
				$counter[$event] = $timeprocess;
				break;
			case $eventend:
				$rs = ($timeprocess - $counter[$eventstart]);
				$counter['c'] = 0;
				$counter[$eventstart] = 0;
				break;
			default:
		}
		return($rs);
	}
	
	public function update_result($var,$str,$operator='+')
	{
		/*
		$res = &$this->_result;			
		$res = &$res[$key][$type]['result'];
		*/
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
	
}