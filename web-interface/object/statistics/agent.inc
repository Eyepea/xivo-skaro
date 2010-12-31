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

class xivo_statistics_agent
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
	
		if (isset($res['agent']) === false)
			$res['agent'] = array();
			
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
			
			if (isset($res['agent'][$agent]) === false)
			{
				$data_process = &$res['agent'][$agent];
				$data_process = array();
				$data_process['logintime'] = array();
				$data_process['logintime']['type'] = 'time';
				$data_process['logintime']['result'] = 0;
				$data_process['holdtime'] = array();
				$data_process['holdtime']['type'] = 'time';
				$data_process['holdtime']['result'] = 0;
				$data_process['calltime'] = array();
				$data_process['calltime']['type'] = 'time';
				$data_process['calltime']['result'] = 0;
				$data_process['ringtime'] = array();
				$data_process['ringtime']['type'] = 'time';
				$data_process['ringtime']['result'] = 0;
				$data_process['pausetime'] = array();
				$data_process['pausetime']['type'] = 'time';
				$data_process['pausetime']['result'] = 0;
				$data_process['connect'] = array();
				$data_process['connect']['type'] = 'int';
				$data_process['connect']['result'] = 0;
				$data_process['completeagent'] = array();
				$data_process['completeagent']['type'] = 'int';
				$data_process['completeagent']['result'] = 0;
				$data_process['completecaller'] = array();
				$data_process['completecaller']['type'] = 'int';
				$data_process['completecaller']['result'] = 0;
				$data_process['ringnoanswer'] = array();
				$data_process['ringnoanswer']['type'] = 'int';
				$data_process['ringnoanswer']['result'] = 0;
				$data_process['transfer'] = array();
				$data_process['transfer']['type'] = 'int';
				$data_process['transfer']['result'] = 0;
				$data_process['abandon'] = array();
				$data_process['abandon']['type'] = 'int';
				$data_process['abandon']['result'] = 0;
			}
			
			switch ($event)
			{
				# AGENTLOGIN(channel)				
				# AGENTLOGOFF(channel|logintime)
				case 'AGENTLOGIN':
				case 'AGENTLOGOFF':
					if (TRUE)
					{
						$this->eval_during_time($agent,$event,'AGENTLOGIN','AGENTLOGOFF',$time,'logintime');
					}
					elseif($event === 'AGENTLOGOFF')
					{					
						$logintime = $this->eval_data_queue_log($queue_log,'AGENTLOGOFF','logintime');
						$this->increment_time_agent($agent,$logintime,'logintime');
					}
					break;
				# CONNECT(holdtime|bridgedchanneluniqueid) 
				case 'CONNECT':
					$holdtime = $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
					$this->increment_time_agent($agent,$holdtime,'holdtime');
					$this->increment_time_agent($agent,1,'connect');
					break;
				# COMPLETEAGENT(holdtime|calltime|origposition) 
				case 'COMPLETEAGENT':
					$calltime = $this->eval_data_queue_log($queue_log,'COMPLETEAGENT','calltime');
					$this->increment_time_agent($agent,$calltime,'calltime');
					$holdtime = $this->eval_data_queue_log($queue_log,'COMPLETEAGENT','holdtime');
					$this->increment_time_agent($agent,$holdtime,'holdtime');
					$this->increment_time_agent($agent,1,'completeagent');
					break;
				# COMPLETECALLER(holdtime|calltime|origposition) 
				case 'COMPLETECALLER':
					$calltime = $this->eval_data_queue_log($queue_log,'COMPLETECALLER','calltime');
					$this->increment_time_agent($agent,$calltime,'calltime');
					$holdtime = $this->eval_data_queue_log($queue_log,'COMPLETECALLER','holdtime');
					$this->increment_time_agent($agent,$holdtime,'holdtime');
					$this->increment_time_agent($agent,1,'completecaller');
					break;
				# RINGNOANSWER(ringtime)
				case 'RINGNOANSWER':
					$ringtime = $this->eval_data_queue_log($queue_log,'RINGNOANSWER','ringtime');
					$this->increment_time_agent($agent,$ringtime,'ringtime');
					$this->increment_time_agent($agent,1,'ringnoanswer');
					break;			
				# TRANSFER(extension|context|holdtime|calltime) 
				case 'TRANSFER':
					$this->increment_time_agent($agent,1,'transfer');
					break;
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->increment_time_agent($agent,1,'abandon');
					break;
				# PAUSE()
				# UNPAUSE()
				case 'PAUSE':
				case 'UNPAUSE':
					$this->eval_during_time($agent,$event,'PAUSE','UNPAUSE',$time,'pausetime');
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
					$this->increment_time_agent($agent,$diff,$type);
				}
				$counter['c'] = 1;
				$counter[$event] = $timeprocess;
				break;
			case $eventend:				
				$diff = $timeprocess - $counter[$eventstart];
		
				$this->increment_time_agent($agent,$diff,$type);
				
				$counter['c'] = 0;
				$counter[$eventstart] = 0;
				break;
			default:
		}
	}
	
	private function increment_time_agent($agent,$str,$type,$operator='+')
	{
		$res = &$this->_result;		
		if (isset($res['agent'][$agent]) === false
		|| isset($res['agent'][$agent][$type]) === false)
			return(false);
			
		$result = &$res['agent'][$agent][$type]['result'];
			
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
		return(true);
	}

}

?>