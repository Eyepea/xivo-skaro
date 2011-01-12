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

class xivo_statistics_agent extends xivo_statistics_abstract
{
	
	public		$_type		= 'agent';
	public		$_field	= array('logintime'			=> array('type' => 'time'),
								'holdtime'			=> array('type' => 'time'),
								'calltime'			=> array('type' => 'time'),
								'ringtime'			=> array('type' => 'time'),
								'pausetime'			=> array('type' => 'time'),
								'traitmenttime'		=> array('type' => 'time'),
								'connect'			=> array('type' => 'int'),
								'completeagent'		=> array('type' => 'int'),
								'completecaller'	=> array('type' => 'int'),
								'ringnoanswer'		=> array('type' => 'int'),
								'transfer'			=> array('type' => 'int'),
								'abandon'			=> array('type' => 'int')
						);
		
	public function __construct(&$_XOBJ,&$ipbx)
	{
		parent::__construct(&$_XOBJ,&$ipbx);
		$this->_method = 'DB';
	}
		
	public function parse_log()
	{
		switch ($this->_method)
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
		return(true);
	}
	
	private function parse_log_db()
	{		
		$data = $this->get_list_by_type();
		$nb_data = count($data);
		for ($i=0;$i<$nb_data;$i++)
		{
			$agent = $data[$i];
			
			$agent_num = (int) $agent[0];
			$this->init_result($agent_num);
						
			$val = $this->eval_count_data($agent,'CONNECT');
			$this->update_result(array($agent_num,'connect'),$val);	
					
			$field = $this->eval_field_queue_log('CONNECT','holdtime');
			$holdtime = $this->eval_sum_data($agent,'CONNECT',$field);
			$this->update_result(array($agent_num,'holdtime'),$holdtime);
			$this->update_result(array($agent_num,'traitmenttime'),$holdtime);
			
			$val = $this->eval_count_data($agent,'TRANSFER');
			$this->update_result(array($agent_num,'transfer'),$val);
			
			$field = $this->eval_field_queue_log('RINGNOANSWER','ringtime');
			$ringtime = $this->eval_sum_data($agent,'RINGNOANSWER',$field);
			$this->update_result(array($agent_num,'ringtime'),$ringtime);
			$this->update_result(array($agent_num,'traitmenttime'),$ringtime);
			$val = $this->eval_count_data($agent,'RINGNOANSWER');
			$this->update_result(array($agent_num,'ringnoanswer'),$val);
			
			$val = $this->eval_count_data($agent,'ABANDON');
			$this->update_result(array($agent_num,'abandon'),$val);	
						
			$field = $this->eval_field_queue_log('COMPLETEAGENT','calltime');
			$calltime = $this->eval_sum_data($agent,'COMPLETEAGENT',$field);
			$this->update_result(array($agent_num,'calltime'),$calltime);
			$this->update_result(array($agent_num,'traitmenttime'),$calltime);
			
			$field = $this->eval_field_queue_log('COMPLETEAGENT','holdtime');
			$holdtime = $this->eval_sum_data($agent,'COMPLETEAGENT',$field);
			$this->update_result(array($agent_num,'holdtime'),$holdtime);
			
			$val = $this->eval_count_data($agent,'COMPLETEAGENT');
			$this->update_result(array($agent_num,'completeagent'),$val);
						
			$field = $this->eval_field_queue_log('COMPLETECALLER','calltime');
			$calltime = $this->eval_sum_data($agent,'COMPLETECALLER',$field);
			$this->update_result(array($agent_num,'calltime'),$calltime);
			$this->update_result(array($agent_num,'traitmenttime'),$calltime);
			
			$field = $this->eval_field_queue_log('COMPLETECALLER','holdtime');
			$holdtime = $this->eval_sum_data($agent,'COMPLETECALLER',$field);
			$this->update_result(array($agent_num,'holdtime'),$holdtime);
			
			$val = $this->eval_count_data($agent,'COMPLETECALLER');
			$this->update_result(array($agent_num,'completecaller'),$val);		
						
			$field = $this->eval_field_queue_log('AGENTLOGOFF','logintime');
			$logintime = $this->eval_sum_data($agent,'AGENTLOGOFF',$field);
			$this->update_result(array($agent_num,'logintime'),$logintime);
			
			$field = $this->eval_field_queue_log('AGENTCALLBACKLOGOFF','logintime');
			$logintime = $this->eval_sum_data($agent,'AGENTCALLBACKLOGOFF',$field);
			$this->update_result(array($agent_num,'logintime'),$logintime);
			
			continue;			
			
			if (isset($this->_data_custom['qos']) === true
			&& isset($this->_data_custom['qos'][$queuename]) === true
			&& ($stats_qos = (int) $this->_data_custom['qos'][$queuename]['stats_qos']) !== 0)
			{
				$field = $this->eval_field_queue_log('CONNECT','holdtime');
				$qos = $this->eval_count_data($queuename,'CONNECT',"$field<'$stats_qos'");
				$this->update_result(array($queuename,'qos'),$qos);
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
			
			$this->init_result($agent);
			
			switch ($event)
			{
				# AGENTCALLBACKLOGIN(exten@context) 
				case 'AGENTCALLBACKLOGIN':
				# AGENTCALLBACKLOGOFF(exten@context|logintime|reason)
				case 'AGENTCALLBACKLOGOFF':
					$logintime = $this->eval_during_time($agent,$event,'AGENTCALLBACKLOGIN','AGENTCALLBACKLOGOFF',$time);
					$this->update_result(array($agent,'logintime'),$logintime);
					break;
				# AGENTLOGIN(channel)
				case 'AGENTLOGIN':
				# AGENTLOGOFF(channel|logintime)
				case 'AGENTLOGOFF': 
					$logintime = 0;
					if (TRUE)
						$logintime = $this->eval_during_time($agent,$event,'AGENTLOGIN','AGENTLOGOFF',$time);
					elseif($event === 'AGENTLOGOFF')
						$logintime = $this->eval_data_queue_log($queue_log,'AGENTLOGOFF','logintime');
					$this->update_result(array($agent,'logintime'),$logintime);
					break;
				# CONNECT(holdtime|bridgedchanneluniqueid)
				case 'CONNECT':
					$holdtime = $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
					$this->update_result(array($agent,'holdtime'),$holdtime);
					$this->update_result(array($agent,'traitmenttime'),$holdtime);
					$this->update_result(array($agent,'connect'),1);
					break;
				# COMPLETEAGENT(holdtime|calltime|origposition)
				case 'COMPLETEAGENT':
					$calltime = $this->eval_data_queue_log($queue_log,'COMPLETEAGENT','calltime');
					$this->update_result(array($agent,'calltime'),$calltime);
					$this->update_result(array($agent,'traitmenttime'),$calltime);
					$holdtime = $this->eval_data_queue_log($queue_log,'COMPLETEAGENT','holdtime');
					$this->update_result(array($agent,'holdtime'),$holdtime);
					$this->update_result(array($agent,'completeagent'),1);
					break;
				# COMPLETECALLER(holdtime|calltime|origposition)
				case 'COMPLETECALLER':
					$calltime = $this->eval_data_queue_log($queue_log,'COMPLETECALLER','calltime');
					$this->update_result(array($agent,'calltime'),$calltime);
					$this->update_result(array($agent,'traitmenttime'),$calltime);
					$holdtime = $this->eval_data_queue_log($queue_log,'COMPLETECALLER','holdtime');
					$this->update_result(array($agent,'holdtime'),$holdtime);
					$this->update_result(array($agent,'completecaller'),1);
					break;
				# RINGNOANSWER(ringtime)
				case 'RINGNOANSWER':
					$ringtime = $this->eval_data_queue_log($queue_log,'RINGNOANSWER','ringtime');
					$this->update_result(array($agent,'ringtime'),$ringtime);
					$this->update_result(array($agent,'traitmenttime'),$ringtime);
					$this->update_result(array($agent,'ringnoanswer'),1);
					break;
				# TRANSFER(extension|context|holdtime|calltime)
				case 'TRANSFER':
					$this->update_result(array($agent,'transfer'),1);
					break;
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->update_result(array($agent,'abandon'),1);
					break;
				# PAUSE()
				case 'PAUSE':
				# UNPAUSE()
				case 'UNPAUSE':
					$pausetime = $this->eval_during_time($agent,$event,'PAUSE','UNPAUSE',$time);
					$this->update_result(array($agent,'pausetime'),$pausetime);
					$this->update_result(array($agent,'traitmenttime'),$pausetime);
					break;
				default:
			}
		}
	}

}

?>