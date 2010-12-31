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


class xivo_statistics_queue
{
	
	private $_queue_log_conf= array();
	private $_queue_log 	= array();
	private $_data_custom 	= array();
	private $_counter	 	= array();
	public	$_result 		= array();
	
	public function __construct()
	{
		if(($this->_queue_log_conf = &dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queue_log configuration',E_USER_ERROR);		
	}
	
	public function set_queue_log($queue_log)
	{
		$this->_queue_log = $queue_log;
	}
	
	public function set_data_custom($key,$data)
	{
		$this->_data_custom[$key] = $data;
	}
	
	public function parse_log()
	{
		$res = &$this->_result;
	
		if (isset($res['queue']) === false)
			$res['queue'] = array();
			
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
			
			if (isset($res['queue'][$queuename]) === false)
			{
				$data_process = &$res['queue'][$queuename];
				$data_process = array();
				$data_process['presented'] = array();
				$data_process['presented']['type'] = 'int';
				$data_process['presented']['result'] = 0;
				$data_process['answered'] = array();
				$data_process['answered']['type'] = 'int';
				$data_process['answered']['result'] = 0;
				$data_process['abandoned'] = array();
				$data_process['abandoned']['type'] = 'int';
				$data_process['abandoned']['result'] = 0;
				$data_process['deterred'] = array();
				$data_process['deterred']['type'] = 'int';
				$data_process['deterred']['result'] = 0;
				$data_process['rerouted'] = array();
				$data_process['rerouted']['type'] = 'int';
				$data_process['rerouted']['result'] = 0;
				$data_process['home_rated'] = array();
				$data_process['home_rated']['type'] = 'percent';
				$data_process['home_rated']['result'] = 0;
				$data_process['qos'] = array();
				$data_process['qos']['type'] = 'int';
				$data_process['qos']['result'] = 0;
			}
			
			switch ($event)
			{			
				# ENTERQUEUE(url|callerid)
				case 'ENTERQUEUE':
					$this->update_result($queuename,1,'presented');
					break;
				# CONNECT(holdtime|bridgedchanneluniqueid) 
				case 'CONNECT':
					$this->update_result($queuename,1,'answered');
					if (isset($this->_data_custom['qos']) === true
					&& isset($this->_data_custom['qos'][$queuename]) === true
					&& ($stats_qos = (int) $this->_data_custom['qos'][$queuename]['stats_qos']) !== 0)
					{
						$holdtime = (int) $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
						if ($holdtime << $stats_qos)
							$this->update_result($queuename,1,'qos');
					}
					break;		
				# TRANSFER(extension|context|holdtime|calltime) 
				case 'TRANSFER':
					$this->update_result($queuename,1,'rerouted');
					break;
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->update_result($queuename,1,'abandoned');
					break;
				default:
			}			
		}			
	}

	private function eval_data_queue_log($queue_log_entry,$event,$type)
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

	private function eval_during_time($agent,$event,$eventstart,$eventend,$time,$type)
	{			
		if (isset($this->_counter[$agent]) === false)
		{
			$this->_counter[$agent] = array();
			$this->_counter[$agent][$eventstart] = 0;
			$this->_counter[$agent]['c'] = 0;
		}
			
		$counter = &$this->_counter[$agent];
		
		$timearr = explode('.',$time);
		$timeprocess = dwho_change_date_format($timearr[0],'Y-m-d H:i:s','U');
			
		switch ($event)
		{
			case $eventstart:
					
				if (false
				&& $counter['c'] === 1
				&& $counter[$event] !== 0)
				{
					$diff = $timeprocess - $counter[$event];
					$this->update_result($agent,$diff,$type);
				}
				$counter['c'] = 1;
				$counter[$event] = $timeprocess;
				break;
			case $eventend:				
				$diff = $timeprocess - $counter[$eventstart];
		
				$this->update_result($agent,$diff,$type);
				
				$counter['c'] = 0;
				$counter[$eventstart] = 0;
				break;
			default:
		}
	}
	
	private function update_result($queuename,$str,$type,$operator='+')
	{
		$res = &$this->_result;
		if (isset($res['queue'][$queuename]) === false
		|| isset($res['queue'][$queuename][$type]) === false)
			return(false);
			
		$res = &$res['queue'][$queuename][$type]['result'];
			
		switch($operator)
		{
			case '+':
				$res += $str;
				break;
			case '-':
				$res -= $str;
				break;
			default:
		}
		return(true);
	}

}

?>