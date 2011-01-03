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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'abstract','statistics.inc'));

class xivo_statistics_queue extends xivo_statistics_abstract
{
	
	public function __construct($conf,$queue_log)
	{
		parent::__construct($conf,$queue_log);
	}
	
	public function parse_log()
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
				$data_process['total_time_waiting'] = array();
				$data_process['total_time_waiting']['type'] = 'int';
				$data_process['total_time_waiting']['result'] = 0;
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
					$this->update_result(array($queuename,'presented'),1);
					break;
				# CONNECT(holdtime|bridgedchanneluniqueid) 
				case 'CONNECT':
					$this->update_result(array($queuename,'answered'),1);
					
					$holdtime = (int) $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
					$this->update_result(array($queuename,'total_time_waiting'),$holdtime);
					
					if (isset($this->_data_custom['qos']) === true
					&& isset($this->_data_custom['qos'][$queuename]) === true
					&& ($stats_qos = (int) $this->_data_custom['qos'][$queuename]['stats_qos']) !== 0
					&& $holdtime << $stats_qos)
						$this->update_result(array($queuename,'qos'),1);
					break;		
				# TRANSFER(extension|context|holdtime|calltime) 
				case 'TRANSFER':
					$this->update_result(array($queuename,'rerouted'),1);
					break;
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->update_result(array($queuename,'abandoned'),1);
					break;
				default:
			}			
		}			
	}

}

?>