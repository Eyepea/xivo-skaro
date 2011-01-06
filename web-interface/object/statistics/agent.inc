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
	
	private	$_field	= array('logintime'			=> array('type' => 'time'),
							'holdtime'			=> array('type' => 'time'),
							'calltime'			=> array('type' => 'time'),
							'ringtime'			=> array('type' => 'time'),
							'pausetime'			=> array('type' => 'time'),
							'connect'			=> array('type' => 'int'),
							'completeagent'		=> array('type' => 'int'),
							'completecaller'	=> array('type' => 'int'),
							'ringnoanswer'		=> array('type' => 'int'),
							'transfer'			=> array('type' => 'int'),
							'abandon'			=> array('type' => 'int'),
							'traitmenttime'		=> array('type' => 'time'));
		
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
			
			if (isset($res[$agent]) === false)
			{
				$data_process = &$res[$agent];
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