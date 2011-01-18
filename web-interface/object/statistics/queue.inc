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
		
		$nb_data = count($data);
		for ($i=0;$i<$nb_data;$i++)
		{
			$key = $data[$i];
			switch ($axetype)
			{
				case 'day':
					$key_data = $this->get_list_by_type();
					$key = $key['key'];
					$interval = $this->_xs->get_interval();
					$date = dwho_date_parse_from_format('Y-m-d H:i:s',$interval['dbeg']);
					$dip = array();
					$dip['dbeg'] = date('Y-m-d H:i:s',mktime($key,0,0,$date['month'],$date['day'],$date['year']));
					$dip['dend'] = date('Y-m-d H:i:s',mktime($key+1,0,0,$date['month'],$date['day'],$date['year']));
					$this->_xs->_interval_process = $dip;
					break;
				case 'week':
					$key_data = $this->get_list_by_type();
					$key = $key['key'];
					$interval = $this->_xs->get_interval();
					$date = dwho_date_parse_from_format('Y-m-d H:i:s',$interval['dbeg']);
					$week = date('W',mktime(0,0,0,$date['month'],$date['day'],$date['year']));
					$day_process = $this->_xs->get_day_from_week_by_name_day($date['year'],$week,$key);
					if (is_null($day_process) === true)
						break;
					$dip = array();
					$dip['dbeg'] = $day_process.' 00:00:01';
					$dip['dend'] = $day_process.' 23:59:59';
					$this->_xs->_interval_process = $dip;
					break;
				case 'month':
					$key_data = $this->get_list_by_type();
					$key = $key['key'];
					$interval = $this->_xs->get_interval();
					$date = dwho_date_parse_from_format('Y-m-d H:i:s',$interval['dbeg']);
					$day_process = mktime(0,0,0,$date['month'],$key,$date['year']);
					$dip['dbeg'] = date('Y-m-d',$day_process).' 00:00:01';
					$dip['dend'] = date('Y-m-d',$day_process).' 23:59:59';
					$this->_xs->_interval_process = $dip;
					break;
				case 'year':
					$key_data = $this->get_list_by_type();
					$key = $key['key'];
					$interval = $this->_xs->get_interval();
					$date = dwho_date_parse_from_format('Y-m-d H:i:s',$interval['dbeg']);
					$day_process = mktime(0,0,0,$key+1,0,$date['year']);
					$dip['dbeg'] = date('Y-m',$day_process).'-01 00:00:01';
					$dip['dend'] = date('Y-m',$day_process).'-31 23:59:59';
					$this->_xs->_interval_process = $dip;
					break;
				case 'type':
				default:
					$key_data = $key;
			}
			
			$this->init_result($key);
			
			$enterqueue = $this->eval_count_data($key_data,'ENTERQUEUE');			
			$this->update_result(array($key,'presented'),$enterqueue);
			
			$connect = $this->eval_count_data($key_data,'CONNECT');
			$this->update_result(array($key,'answered'),$connect);
					
			$field = $this->eval_field_queue_log('CONNECT','holdtime');
			$sum = $this->eval_sum_data($key_data,'CONNECT',$field);
			$this->update_result(array($key,'total_time_waiting'),$sum);
			
			$keyobject = array_shift($this->_xs->get_list_by_type());
			
			if (isset($this->_data_custom['qos']) === true
			&& isset($this->_data_custom['qos'][$keyobject]) === true
			&& ($stats_qos = (int) $this->_data_custom['qos'][$keyobject]['stats_qos']) !== 0)
			{
				$field = $this->eval_field_queue_log('CONNECT','holdtime');
				$qos = $this->eval_count_data($key_data,'CONNECT',"$field<'$stats_qos'");
				$this->update_result(array($key,'qos'),$qos);
			}
			
			$abandon = $this->eval_count_data($key_data,'ABANDON');
			$this->update_result(array($key,'abandoned'),$abandon);
			
			$exitempty = $this->eval_count_data($key_data,'EXITEMPTY');
			$this->update_result(array($key,'rerouted_on_hungup'),$exitempty);
			$exitwithtimeout = $this->eval_count_data($key_data,'EXITWITHTIMEOUT');
			$this->update_result(array($key,'rerouted_on_hungup'),$exitwithtimeout);
			
			$this->update_result(array($key,'rerouted_on_guide'),0);
			
			$transfer = $this->eval_count_data($key_data,'TRANSFER');
			$this->update_result(array($key,'rerouted_on_number'),0);
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