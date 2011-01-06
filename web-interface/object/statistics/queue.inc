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

class xivo_statistics_queue extends xivo_statistics_abstract
{
	
	private	$_field	= array('presented'				=> array('type' => 'int'),
							'answered'				=> array('type' => 'int'),
							'abandoned'				=> array('type' => 'int'),
							'deterred_on_close'		=> array('type' => 'int'),
							'deterred_on_saturation'=> array('type' => 'int'),
							'rerouted_on_hungup'	=> array('type' => 'int'),
							'rerouted_on_guide'		=> array('type' => 'int'),
							'rerouted_on_number'	=> array('type' => 'int'),
							'total_time_waiting'	=> array('type' => 'int'),
							'home_rated'			=> array('type' => 'percent'),
							'qos'					=> array('type' => 'int'));
	
	public function __construct(&$_XOBJ,&$ipbx)
	{
		parent::__construct(&$_XOBJ,&$ipbx);
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
				
				foreach ($this->_field as $k => $field)
				{
					$data_process[$k] = array();
					$data_process[$k]['type'] = $field['type'];
					$data_process[$k]['result'] = 0;
				}
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
				# EXITEMPTY(position|origposition|waittime)
				case 'EXITEMPTY':
					$this->update_result(array($queuename,'rerouted_on_hungup'),1);
					break;					 
				# EXITWITHTIMEOUT(position)
				case 'EXITWITHTIMEOUT':
					$this->update_result(array($queuename,'rerouted_on_guide'),1);
					break;
				# TRANSFER(extension|context|holdtime|calltime) 
				case 'TRANSFER':
					$this->update_result(array($queuename,'rerouted_on_number'),1);
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