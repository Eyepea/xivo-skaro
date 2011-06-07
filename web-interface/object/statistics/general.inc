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

class xivo_statistics_general
{

	public     $_table		= 'queue_log';
	public     $_field	    = array();
	private    $_ipbx		= false;
	private    $_queue_log	= false;
	private    $_result	    = array();
	private    $_xs           = false;
		
	public function __construct()
	{
		$this->_method = 'DB';
	}
	
	public function set_xs(&$_XS)
	{
	    $this->_xs = $_XS;
	}
		
	public function parse_log($type,$conf)
	{
		switch ($this->_method)
		{
			case 'DB':
				return($this->parse_log_db($type,$conf));
				break;
			case 'PHP':
				return($this->parse_log_php());
				break;
			default:
				return(false);
		}
	}

	public function get_result()
	{
		return($this->_result);
	}
	
	public function parse_log_db($type,$conf)
	{
	    $result = &$this->_result;
	    if (isset($result[$type]) === false)
	        $result[$type] = array();
	    $rest = &$result[$type];
	    if (isset($rest[$conf]) === false)
	        $rest[$conf] = array();
	    $res = &$rest[$conf];
	    
		switch ($type)
		{
			case 'queue':
                if(xivo::load_class('xivo_statistics_queue',dwho_file::joinpath(XIVO_PATH_OBJECT,'statistics'),'queue',false) === false)
                	die('Can\'t load xivo_statistics_queue object');
                
                $stats_queue = new xivo_statistics_queue(&$this->_xs);
                $rs = $stats_queue->get_data();
				break;
			case 'agent':
                if(xivo::load_class('xivo_statistics_agent',dwho_file::joinpath(XIVO_PATH_OBJECT,'statistics'),'agent',false) === false)
                	die('Can\'t load xivo_statistics_agent object');
                
                $stats_agent = new xivo_statistics_agent(&$this->_xs);
                $rs = $stats_agent->get_data();
				break;
		}
        while ($rs)
        {
             $l = array_shift($rs);
             $lkey = array_keys($l);
             while ($l)
             {
                 $datakey = array_shift($lkey);
                 $data = array_shift($l);
                 if (isset($data['type']) === false)
                     continue;
                 if (isset($res[$datakey]) === true)
                     $res[$datakey] = ($res[$datakey] + $data);
                 else
                     $res[$datakey] = ($data);
             }
         }
                
         return($result);
	}
	
	public function parse_log_php()
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
			
			$this->init_result('total');
			
			switch ($event)
			{
				# ENTERQUEUE(url|callerid)
				case 'ENTERQUEUE':
					$this->update_result(array('total','enterqueue'),1);
					break;
				# AGENTLOGIN(channel)
				case 'AGENTLOGIN':
				# AGENTLOGOFF(channel|logintime)
				case 'AGENTLOGOFF':
					$logintime = 0;
					if (TRUE)
						$logintime = $this->eval_during_time('total',$event,'AGENTLOGIN','AGENTLOGOFF',$time);
					elseif($event === 'AGENTLOGOFF')
						$logintime = $this->eval_data_queue_log($queue_log,'AGENTLOGOFF','logintime');
					$this->update_result(array('total','logintime'),$logintime);
					break;
				# CONNECT(holdtime|bridgedchanneluniqueid)
				case 'CONNECT':
					$holdtime = $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
					$this->update_result(array('total','holdtime'),$holdtime);
					$this->update_result(array('total','traitmenttime'),$holdtime);
					$this->update_result(array('total','connect'),1);
					break;
				# COMPLETEAGENT(holdtime|calltime|origposition)
				case 'COMPLETEAGENT':
					$calltime = $this->eval_data_queue_log($queue_log,'COMPLETEAGENT','calltime');
					$this->update_result(array('total','calltime'),$calltime);
					$this->update_result(array('total','traitmenttime'),$calltime);
					$holdtime = $this->eval_data_queue_log($queue_log,'COMPLETEAGENT','holdtime');
					$this->update_result(array('total','holdtime'),$holdtime);
					$this->update_result(array('total','completeagent'),1);
					break;
				# COMPLETECALLER(holdtime|calltime|origposition)
				case 'COMPLETECALLER':
					$calltime = $this->eval_data_queue_log($queue_log,'COMPLETECALLER','calltime');
					$this->update_result(array('total','calltime'),$calltime);
					$this->update_result(array('total','traitmenttime'),$calltime);
					$holdtime = $this->eval_data_queue_log($queue_log,'COMPLETECALLER','holdtime');
					$this->update_result(array('total','holdtime'),$holdtime);
					$this->update_result(array('total','completecaller'),1);
					break;
				# RINGNOANSWER(ringtime)
				case 'RINGNOANSWER':
					$ringtime = $this->eval_data_queue_log($queue_log,'RINGNOANSWER','ringtime');
					$this->update_result(array('total','ringtime'),$ringtime);
					$this->update_result(array('total','traitmenttime'),$ringtime);
					$this->update_result(array('total','ringnoanswer'),1);
					break;
				# TRANSFER(extension|context|holdtime|calltime)
				case 'TRANSFER':
					$this->update_result(array('total','transfer'),1);
					break;
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->update_result(array('total','abandon'),1);
					break;
				# PAUSE()
				case 'PAUSE':
				# UNPAUSE()
				case 'UNPAUSE':
					$pausetime = $this->eval_during_time('total',$event,'PAUSE','UNPAUSE',$time);
					$this->update_result(array('total','pausetime'),$pausetime);
					$this->update_result(array('total','traitmenttime'),$pausetime);
					break;
				default:
			}
		}
	}

}

?>