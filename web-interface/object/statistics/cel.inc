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

class xivo_statistics_cel
{
	
	public		$_field		= array('duration_in'		=> array('type' => 'time'),
									'duration_out'		=> array('type' => 'time'),
									'duration_intern'	=> array('type' => 'time'),
									'duration_total'	=> array('type' => 'time'),
									'nb_in'				=> array('type' => 'int'),
									'nb_out'			=> array('type' => 'int'),
									'nb_intern'			=> array('type' => 'int'),
									'nb_total'			=> array('type' => 'int'),
									'max_concurrent_calls_in'		=> array('type' => 'int'),
									'max_concurrent_calls_out'		=> array('type' => 'int'),
									'max_concurrent_calls_intern'	=> array('type' => 'int'),
									'max_concurrent_calls_total'	=> array('type' => 'int'),
									'top10_call_duration'	=> array('type' => 'top10'));
	private		$_result	= false;
	private		$_cel		= false;
	private		$_trunk		= false;
	private		$_trunklist	= false;
	
	public function __construct()
	{
		$this->_type = 'cel';
		
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($ipbx = &$_SRE->get('ipbx')) === false
		|| ($this->_cel = &$_SRE->get_module('ipbx','cel')) === false
		|| ($this->_trunk = &$ipbx->get_application('trunk')) === false)
			die('Can\'t load cel object');
	}
	
	public function get_trunk_list()
	{
		if (($apptrunk = $this->_trunk) === false)
			return(false);
			
		if ($this->_trunklist !== false)
			return($this->_trunklist);
		
		$list = $apptrunk->get_trunks_list();	
		$rs = array();
		
		$tmp = array();
		$tmp['identity'] = dwho_i18n::babelfish('trunk_intern');
		$tmp['key'] = 'intern';
		$tmp['name'] = 'intern';
		$rs['intern'] = $tmp;
		
		$this->_init_result('intern');
		
		$nb = count($list);	
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$list[$i];
			preg_match('/\(([\w]+)\)/i',$ref['identity'],$out);
			if (empty($out) === true
			|| isset($out[1]) === false)
				continue;
			$trunkname = $out[1].'/'.$ref['name'];
			$tmp = array();
			$tmp['identity'] = $ref['identity'];
			$tmp['key'] = $trunkname;
			$tmp['name'] = $trunkname;
			$rs[$tmp['key']] = $tmp;
			$this->_init_result($trunkname);
		}
		
		$this->_trunklist = $rs;
		return($rs);
	}
	
	public function get_list_call()
	{	
		$arr = array();
		$arr['dbeg'] = date('Y-m-d').' 00:00:01';
		$arr['dend'] = date('Y-m-d').' 23:59:59';
		
		if ($this->_trunk === false		
		|| ($list = $this->_cel->search($arr)) === false)
			return(false);

		$rs = array();
		while($list)
		{
			$ref = array_shift($list);
			$uid = $ref['linkedid'];
			if (isset($rs[$uid]) === false)
				$rs[$uid] = array();
			array_push($rs[$uid], $ref);
		}
		return($rs);
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
		
	public function parse_data($axetype)
	{		
		$data = $this->_build_data($axetype);
		$trunklist = $this->get_trunk_list();
		$data1 = $data;
		while($data1)
		{
			$call = array_shift($data1);			
			$uniqueid = array_shift(array_keys($call));	
			$datacall = array_shift($call);
			$nextdatacall = array_shift($call);
				
			if (isset($datacall['end']) === false)
				continue;
			
			switch ($axetype)
			{
				case 'period':
					$key = (int) date('Ymd',$eventtime);
					break;
				case 'day':				
					$hour = (string) strftime('%H',$eventtime);
					$key = (int) date('H',$eventtime);
					break;
				case 'week':
					$key = strtolower(date('l',$eventtime));
					break;
				case 'month':
					$key = date('d',$eventtime);
					break;
				case 'trunk':
				default:
					if (isset($trunklist[$datacall['trunk']]) === false)
						$key = 'intern';
					else
						$key = $datacall['trunk'];
			}
			
			$this->update_result(array($key,'nb_total'),1);
			
			$duration = (isset($datacall['duration'])) ? $datacall['duration'] : 0;
			$this->update_result(array($key,'duration_total'),$duration);
			
			if (isset($trunklist[$datacall['trunk']]) === false
			&& isset($trunklist[$nextdatacall['trunk']]) === false)
			{
				$this->update_result(array('intern','nb_intern'),1);
				$this->update_result(array('intern','duration_intern'),$duration);
			}
			elseif (isset($trunklist[$datacall['trunk']]) === false
			&& isset($trunklist[$nextdatacall['trunk']]) === true)
			{
				$this->update_result(array($key,'nb_out'),1);
				$this->update_result(array($key,'duration_out'),$duration);
			}
			elseif (isset($trunklist[$datacall['trunk']]) === true
			&& isset($trunklist[$nextdatacall['trunk']]) === false)
			{
				$this->update_result(array($key,'nb_in'),1);
				$this->update_result(array($key,'duration_in'),$duration);
			}
			
			$data2 = $data;
			while($data2)
			{
				$call2 = array_shift($data2);
				$datacall2 = array_shift($call2);
				$nextdatacall2 = array_shift($call2);
				
				if (isset($datacall2['end']) === false)
					continue;
				
				if ($datacall2['start'] === $datacall['start']
				&& $datacall2['end'] === $datacall['end'])
					continue;
				
				if ($datacall2['start'] > $datacall['start']
				&& $datacall2['start'] < $datacall['end'])
				{
					if (isset($trunklist[$datacall2['trunk']]) === false
					&& isset($trunklist[$nextdatacall2['trunk']]) === false)
					{
						$this->update_result(array('intern','max_concurrent_calls_intern'),1);
						$this->update_result(array('intern','max_concurrent_calls_total'),1);
					}
					elseif (isset($trunklist[$datacall2['trunk']]) === false
					&& isset($trunklist[$nextdatacall2['trunk']]) === true)
					{
						$this->update_result(array($key,'max_concurrent_calls_out'),1);
						$this->update_result(array($key,'max_concurrent_calls_total'),1);
					}
					elseif (isset($trunklist[$datacall2['trunk']]) === true
					&& isset($trunklist[$nextdatacall2['trunk']]) === false)
					{
						$this->update_result(array($key,'max_concurrent_calls_in'),1);
						$this->update_result(array($key,'max_concurrent_calls_total'),1);
					}
				}
			}
		}
		return($this->_result);
	}
	
	private function _build_data($axetype)
	{	
		$rs = array();
		$listcall = $this->get_list_call();
		while ($listcall)
		{
			$ticketcall = array_shift($listcall);			
			$token = array();
			$itl = array();			
			$tmp = array();
			while ($ticketcall)
			{
				$call = array_shift($ticketcall);
				
				$eventtime = dwho_date::all_to_unixtime($call['eventtime']);
				$uniqueid = $call['uniqueid'];
				$eventtype = $call['eventtype'];
				$channame = $call['channame'];				
				$trunkname = substr($channame,0,-strlen(strrchr($channame,'-')));
				
				if (isset($token[$uniqueid]) === false)
					$token[$uniqueid] = array();
					
				$ref = &$token[$uniqueid];
				
				if (isset($ref['event']) === false)
					$ref['event'] = array();
					
				$event = &$ref['event'];
				
				if (isset($event[$eventtype]) === false)
					$event[$eventtype] = 0;
					
				$event_cnt = &$event[$eventtype];					
				$event_cnt++;
				
				if (isset($tmp[$uniqueid]) === false)
					$tmp[$uniqueid] = array();
					
				$cc = &$tmp[$uniqueid];				
			
				switch ($axetype)
				{
					case 'period':
						$key = (int) date('Ymd',$eventtime);
						break;
					case 'day':				
						$hour = (string) strftime('%H',$eventtime);
						$key = (int) date('H',$eventtime);
						break;
					case 'week':			
						$key = strtolower(date('l',$eventtime));
						break;
					case 'month':
						$key = date('d',$eventtime);
						break;
					case 'trunk':
					default:
						$key = $trunkname;
				}
				
				switch ($eventtype)
				{
					case 'CHAN_START':
						if ($event_cnt === 1)
						{
							$ref['channame'] = $channame;
							$ref['dstart'] = date('Y-m-d H:i:s',$eventtime);
							$ref['start'] = $eventtime;
							$ref['trunk'] = $trunkname;		
							$ref['from'] = $call['cid_num'];
							$ref['to'] = empty($call['cid_dnid']) ? $call['exten'] : $call['cid_dnid'];	
							$ref['context'] = $call['context'];
							
							$itl['start'] = $eventtime;
							$itl['trunkname'] = $trunkname;
						}
						else
						{
							$ref['dstart'] = date('Y-m-d H:i:s',$eventtime);
							$ref['start'] = $eventtime;	
							$ref['context'] = $call['context'];
						}
						$ref['ringing'] = $eventtime;
						break;
					case 'APP_START':
						break;
					case 'ANSWER':
						$cc['danswer'] = $eventtime;
						break;
					case 'BRIDGE_START':
						$ref['ringing'] = ($eventtime - $ref['ringing']);
						break;
					case 'BRIDGE_END':
						break;
					case 'HANGUP':
						if (isset($cc['danswer']) === true)
							$ref['duration'] = ($eventtime - $cc['danswer']);
						else
							$ref['duration'] = 0;
						break;
					case 'CHAN_END':
						$ref['end'] = $eventtime;
						$ref['dend'] = date('Y-m-d H:i:s',$eventtime);
						$itl['end'] = $eventtime;
						$itl['duration'] = $ref['duration'];
						break;
					default:
				}
			}
			array_push($rs,$token);
		}
		return($rs);
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