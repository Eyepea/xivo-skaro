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
	
	public		$_type		= 'queue';
	public		$_field		= array();
	
	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_method = 'DB';
	}
		
	public function parse_log()
	{
		switch ($this->_xs->_method)
		{
			case 'DB':
				$this->parse_log_db();
				break;
			case 'PHP':
				$this->parse_log_php();
				break;
			default:
				return(false);
		}
	}
	
	private function parse_log_db()
	{
		$axetype = $this->_xs->get_axtype();
		
		switch ($axetype)
		{
			case 'day':
				$data = $this->_xs->get_listhour();
				break;
			case 'week':
				$data = $this->_xs->get_listday_for_week();
				break;
			case 'month':
				$data = $this->_xs->get_listday_for_month();
				break;
			case 'year':
				$data = $this->_xs->get_listmonth();
				break;
			case 'type':
			default:
				$data = $this->get_list_by_type();
		}
					
		$key_data = $this->get_list_by_type();
		$interval = $this->_xs->get_interval();
		
		$nb_data = count($data);
		for ($i=0;$i<$nb_data;$i++)
		{
			$key = $data[$i];
			switch ($axetype)
			{
				case 'day':
				case 'week':
				case 'month':
				case 'year':
					$key = $key['key'];
					if (isset($interval[$key]) === true)
						$this->_xs->_interval_process =  $interval[$key];
					break;
				case 'type':
				default:
					$key_data = $key;
					if (count($interval) === 1)
						$interval = array_shift($interval);
					$this->_xs->_interval_process =  $interval;
			}
		
			$res = &$this->_result;
					
			if (isset($res[$key]) === false)
			{
				$data_process = &$res[$key];
				$data_process = array();
				$data_process['answered'] = array();
				$data_process['abandoned'] = array();
				foreach($this->_xs->_period as $k => $v)
				{
					if(isset($data_process['answered'][$k]) === false)
					{
						$data_process['answered'][$k] = array();
						$data_process['answered'][$k]['type'] = 'int';
						$data_process['answered'][$k]['result'] = 0;
						$data_process['abandoned'][$k] = array();
						$data_process['abandoned'][$k]['type'] = 'int';
						$data_process['abandoned'][$k]['result'] = 0;
					}
					
					if (($pbeg = $v['beg']) === 0
					&& ($pend = $v['end']) === 0)
						continue;
					
					$field = $this->eval_field_queue_log('CONNECT','holdtime');
					$connect = $this->eval_count_data($key_data,'CONNECT',"\"$field\"::int BETWEEN $pbeg AND $pend");
					$this->update_result(array($key,'answered',$k),$connect);
				
					$field = $this->eval_field_queue_log('ABANDON','waittime');
					$abandon = $this->eval_count_data($key_data,'ABANDON',"\"$field\"::int BETWEEN $pbeg AND $pend");
					$this->update_result(array($key,'abandoned',$k),$abandon);
					
				}
			}
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
				$data_process['abandoned'] = array();
				foreach($this->_period as $k => $v)
				{
					$data_process['treaties'][$k] = array();
					$data_process['treaties'][$k]['type'] = 'int';
					$data_process['treaties'][$k]['result'] = 0;
					$data_process['abandoned'][$k] = array();
					$data_process['abandoned'][$k]['type'] = 'int';
					$data_process['abandoned'][$k]['result'] = 0;
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
					$top = 'abandoned';
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