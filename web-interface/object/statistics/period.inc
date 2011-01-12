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
	
	public		$_field		= array();
	
	public function __construct(&$_XOBJ,&$ipbx)
	{
		parent::__construct(&$_XOBJ,&$ipbx);
		$this->_method = 'SQL';
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