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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'abstract','statistics.inc'));

class xivo_statistics_period extends xivo_statistics_abstract
{
	
	public		$_type		= 'period';
	public		$_field		= array();
	
	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_method = 'DB';
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
					
			foreach($this->_xs->_period as $k => $v)
			{
				if(isset($data_process['connect'][$k]) === false)
				{
					$data_process['connect'][$k] = array();
					$data_process['connect'][$k]['type'] = 'int';
					$data_process['connect'][$k]['result'] = 0;
					$data_process['abandon'][$k] = array();
					$data_process['abandon'][$k]['type'] = 'int';
					$data_process['abandon'][$k]['result'] = 0;
				}
			}
		}
		
		return(true);
	}
		
	public function parse_log($key_data,$key)
	{
		if ($this->_xs->get_conf() === false)
			return(false);
		switch ($this->_xs->_method)
		{
			case 'DB':
				return($this->parse_log_db($key_data,$key));
				break;
			case 'PHP':
				return($this->parse_log_php());
				break;
			default:
				return(false);
		}
	}
		
	private function parse_log_db($key_data,$key)
	{
		$this->init_result($key);
		
		foreach($this->_xs->_period as $k => $v)
		{
			if (($v['beg']) === 0
			&& ($v['end']) === 0)
				continue;
				
			$operator = 'BETWEEN';
			if (is_null($v['end']) === true)
				$operator = '>';
			
			$field = $this->eval_field_queue_log('CONNECT','holdtime');
			$connect = $this->eval_count_data($key_data,'CONNECT',array($operator, array($field,$v['beg'],$v['end'])));
			$this->update_result(array($key,'connect',$k),$connect);
		
			$field = $this->eval_field_queue_log('ABANDON','waittime');
			$abandon = $this->eval_count_data($key_data,'ABANDON',array($operator, array($field,$v['beg'],$v['end'])));
			$this->update_result(array($key,'abandon',$k),$abandon);
		}
	}
	
	private function parse_log_php()
	{
		$res = &$this->_result;
			
		$nb_ql = count($this->_queue_log);
		for ($u=0;$u<$nb_ql;$u++)
		{
			$queue_log = &$this->_queue_log[$u];
					
			foreach ($queue_log as $k => $clean)
				$queue_log[$k] = trim($clean);
						
			$time 		= $queue_log['time'];
			$callid 	= $queue_log['callid']; 
			$queuename 	= $queue_log['queuename'];
			$agent 		= strtolower($queue_log['agent']);
			$event 		= $queue_log['event'];
			
			if (isset($res[$queuename]) === false)
			{
				$data_process = &$res[$queuename];
				$data_process = array();
				$data_process['treaties'] = array();
				$data_process['abandon'] = array();
				foreach($this->_period as $k => $v)
				{
					$data_process['treaties'][$k] = array();
					$data_process['treaties'][$k]['type'] = 'int';
					$data_process['treaties'][$k]['result'] = 0;
					$data_process['abandon'][$k] = array();
					$data_process['abandon'][$k]['type'] = 'int';
					$data_process['abandon'][$k]['result'] = 0;
				}
			}
			
			$top = '';
			switch ($event)
			{
				# CONNECT(holdtime|bridgedchanneluniqueid)
				case 'CONNECT':
					$top = 'treaties';
					$holdtime = $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
					break;
				# ENTERQUEUE(url|callerid)
				case 'ENTERQUEUE':
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$top = 'abandon';
					$holdtime = $this->eval_during_time($callid,$event,'ENTERQUEUE','ABANDON',$time);
					break;
				default:
			}
			
			foreach($this->_period as $k => $v)
			{
				$beg = $v['beg'];
				$end = $v['end'];
				
				if ($holdtime > $beg
				&& $holdtime < $end)
					$this->update_result(array($queuename,$top,$k),1);

			}
		}			
	}

}

?>