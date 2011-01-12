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
	
	public		$_type	= 'queue';
	public		$_field	= array('presented'				=> array('type' => 'int'),
								'answered'				=> array('type' => 'int'),
								'abandoned'				=> array('type' => 'int'),
								'deterred_on_close'		=> array('type' => 'int'),
								'deterred_on_saturation'=> array('type' => 'int'),
								'rerouted_on_hungup'	=> array('type' => 'int'),
								'rerouted_on_guide'		=> array('type' => 'int'),
								'rerouted_on_number'	=> array('type' => 'int'),
								'total_time_waiting'	=> array('type' => 'int'),
								'home_rated'			=> array('type' => 'percent'),
								'qos'					=> array('type' => 'int')
							);
	
	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->set_method('DB');
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
		$data = $this->get_list_by_type();
		$nb_data = count($data);
		for ($i=0;$i<$nb_data;$i++)
		{
			$queuename = $data[$i];
			$this->init_result($queuename);
			
			$enterqueue = $this->eval_count_data($queuename,'ENTERQUEUE');			
			$this->update_result(array($queuename,'presented'),$enterqueue);
			
			$connect = $this->eval_count_data($queuename,'CONNECT');
			$this->update_result(array($queuename,'answered'),$connect);			
					
			$field = $this->eval_field_queue_log('CONNECT','holdtime');
			$sum = $this->eval_sum_data($queuename,'CONNECT',$field);
			$this->update_result(array($queuename,'total_time_waiting'),$sum);
			
			if (isset($this->_data_custom['qos']) === true
			&& isset($this->_data_custom['qos'][$queuename]) === true
			&& ($stats_qos = (int) $this->_data_custom['qos'][$queuename]['stats_qos']) !== 0)
			{
				$field = $this->eval_field_queue_log('CONNECT','holdtime');
				$qos = $this->eval_count_data($queuename,'CONNECT',"$field<'$stats_qos'");
				$this->update_result(array($queuename,'qos'),$qos);
			}
			
			$abandon = $this->eval_count_data($queuename,'ABANDON');
			$this->update_result(array($queuename,'abandoned'),$abandon);
			
			$exitempty = $this->eval_count_data($queuename,'EXITEMPTY');
			$this->update_result(array($queuename,'rerouted_on_hungup'),$exitempty);
			$exitwithtimeout = $this->eval_count_data($queuename,'EXITWITHTIMEOUT');
			$this->update_result(array($queuename,'rerouted_on_hungup'),$exitwithtimeout);
			
			$this->update_result(array($queuename,'rerouted_on_guide'),0);
			
			$transfer = $this->eval_count_data($queuename,'TRANSFER');
			$this->update_result(array($queuename,'rerouted_on_number'),0);
		}
	}	
	
	private function parse_log_php()
	{			
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
			
			$this->init_result($queuename);
			
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
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->update_result(array($queuename,'abandoned'),1);
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
				default:
			}			
		}			
	}

}

?>