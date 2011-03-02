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

class xivo_statistics_cdr 
{
	
	public		$_field		= array('duration'	=> array('type' => 'time'),
									'nb'		=> array('type' => 'int'),
									'max_concurrent_calls'	=> array('type' => 'int'));
	private		$_result	= false;
	private		$_cdr		= false;
		
	public function __construct()
	{
		$this->_type = 'cdr';
		
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($this->_cdr = &$_SRE->get_module('ipbx','cdr')) === false)
			die('Can\'t load cell object');
	}
	
	public function init_result_by_list($arr)
	{
		while($arr)
		{
			$data = array_shift($arr);
			$this->_init_result($data['key']);
		}
	}
	
	private function _init_result($key)
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
	
	public function parse_data($data,$axetype)
	{
		/*
		  'id' => string '59' (length=2)
	      'calldate' => string '2011-02-17 16:03:12' (length=19)
	      'clid' => string '"celine dion" <8001>' (length=20)
	      'src' => string '8001' (length=4)
	      'dst' => string '666' (length=3)
	      'dcontext' => string 'default' (length=7)
	      'channel' => string 'SIP/8001-0000000a' (length=17)
	      'dstchannel' => string '' (length=0)
	      'lastapp' => string 'Read' (length=4)
	      'lastdata' => string 'TOTO' (length=4)
	      'answer' => string '2011-02-17 16:03:12' (length=19)
	      'end' => string '2011-02-17 16:03:17' (length=19)
	      'duration' => string '5' (length=1)
	      'billsec' => string '5' (length=1)
	      'disposition' => string 'ANSWERED' (length=8)
	      'amaflags' => string '3' (length=1)
	      'accountcode' => string '' (length=0)
	      'uniqueid' => string '1297976592.20' (length=13)
	      'userfield' => string '' (length=0)
	      'amaflagsmeta' => string 'documentation' (length=13)
		*/
		while ($data)
		{
			$ref = array_shift($data);
						
			$calldate 	= $ref['calldate'];
			$clid 		= $ref['clid']; 
			$src 		= $ref['src'];
			$duration	= (int) $ref['duration'];
			
			switch ($axetype)
			{
				case 'period':
					$key = (int) date('Ymd',strtotime($calldate));
					break;
				case 'day':
					$key = (int) date('H',strtotime($calldate));
					break;
				case 'week':			
					$key = strtolower(date('l',strtotime($calldate)));
					break;
				case 'month':
					$key = date('d',strtotime($calldate));
					break;
				default:
					continue;
			}
			
			$this->update_result(array($key,'duration'),$duration);			
			$this->update_result(array($key,'nb'),1);
			#max_concurrent_calls
		}
		
		return($this->_result);
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

?>