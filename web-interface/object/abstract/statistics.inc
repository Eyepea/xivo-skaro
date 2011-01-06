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

class xivo_statistics_abstract
{
	
	private	$_xobj		 		= null;	
	private	$_ipbx		 		= null;	
	public 	$_queue_log_conf	= array();
	public 	$_queue_log 		= array();
	public 	$_data_custom 		= array();
	public 	$_counter	 		= array();
	public 	$_conf		 		= array();
	public 	$_statsconfsess		= array();
	public 	$_period	 		= array('period1'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period2'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period3'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period4'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											),
										'period5'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0,
											));
	public		$_result 			= array();
	
	public function __construct(&$xobj,&$ipbx)
	{
		if (is_object($xobj) === false
		|| is_object($ipbx) === false)
			return(false);
		
		$this->_xobj = &$xobj;
		$this->_ipbx = &$ipbx;
		
		if(dwho_issa('_statsconf',$_SESSION) === false)
			$_SESSION['_statsconf'] = array();
			
		$this->_statsconfsess = &$_SESSION['_statsconf'];
		
		if($this->load_conf() === false)
			trigger_error('Failed to statistics configuration',E_USER_ERROR);
			
		if($this->load_queuelog() === false)
			trigger_error('Failed to load queuelog data',E_USER_ERROR);
		
		if(($this->_queue_log_conf = &dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queuelog configuration',E_USER_ERROR);
	}
	
	public function set_idconf($confid,$reloadconf=false)
	{	
		$this->_statsconfsess['id'] = (int) $confid;
		if ($reloadconf !== false)
			$this->load_conf();
	}
	
	public function get_idconf()
	{	
		if (isset($this->_statsconfsess['id']) === false
		|| ($confid = $this->_statsconfsess['id']) === 0)
			return(false);
		
		return($confid);
	}
	
	private function load_conf()
	{
		if (($confid = $this->get_idconf()) === false)
			return(false);
			
		$appstats_conf = $this->_xobj->get_application('stats_conf');

		if (($conf = $appstats_conf->get($confid)) === false
		|| is_array($conf) === false
		|| isset($conf['stats_conf']) === false)
			return(false);
		
		$this->_conf = $conf;
		$this->init_conf();
	}
	
	private function init_conf()
	{		
		$conf = $this->_conf;
		
		$stats_conf = $conf['stats_conf'];
		
		for($i=1;$i<6;$i++)
		{
			if (isset($stats_conf['period'.$i]) === false)
				continue;
				
			$this->_period['period'.$i]['exp'] = $stats_conf['period'.$i];
			
			if (preg_match('/([0-9]+)[-]{1}([0-9]+)/',$stats_conf['period'.$i],$out) === 1)
			{
				$this->_period['period'.$i]['beg'] = (int) $out[1];
				$this->_period['period'.$i]['end'] = (int) $out[2];
			}			
		}
		
		return(true);
	}
	
	private function load_queuelog()
	{
		if (($appqueue_log = &$this->_ipbx->get_application('queue_log')) === false)
			return(false);
		
		$queue = array_values($this->_conf['queue']);
		$nb_queue = count($this->_conf['queue']);
		$agent = array_values($this->_conf['agent']);
		$nb_agent = count($this->_conf['agent']);
		
		$ls_queuename = array();
		for($i=0;$i<$nb_queue;$i++)
			array_push($ls_queuename,$queue[$i]['name']);
			
		$ls_agent = array();
		for($i=0;$i<$nb_agent;$i++)
		{
			array_push($ls_agent,'agent/'.$agent[$i]['number']);
			array_push($ls_agent,'Agent/'.$agent[$i]['number']);
		}
			
		$dstart = '';
		$dend = '';	

		$this->_queue_log = $appqueue_log->get_queue_logs_stats($dstart,$dend,$ls_agent,$ls_queuename);
		
		return(true);
	}
	
	public function get_queue_list()
	{			
		if (($appqueue = &$this->_ipbx->get_application('queue')) === false)
			return(false);
		
		$list_queue = $appqueue->get_queues_list();
		
		$queue = array_values($list_queue);
		$nb_queue = count($queue);
				
		$res = array();
		for($i=0;$i<$nb_queue;$i++)
		{
			if (array_key_exists($queue[$i]['id'],$this->_conf['queue']) === true)
				array_push($res,$queue[$i]);
		}
		
		return($res);
	}
	
	public function get_agent_list()
	{			
		if (($appagent = &$this->_ipbx->get_application('agent')) === false)
			return(false);
		
		$list_agent = $appagent->get_agentfeatures();
		
		$agent = array_values($list_agent);
		$nb_agent = count($agent);
				
		$res = array();
		for($i=0;$i<$nb_agent;$i++)
		{
			if (array_key_exists($agent[$i]['id'],$this->_conf['agent']) === true)
				array_push($res,$agent[$i]);
		}
		
		return($res);
	}
	
	public function set_data_custom($key,$data)
	{
		$this->_data_custom[$key] = $data;
	}

	public function eval_data_queue_log($queue_log_entry,$event,$type)
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

	public function eval_during_time($key,$eventprocess,$eventstart,$eventend,$time)
	{			
		if (isset($this->_counter[$key]) === false)
			$this->_counter[$key] = array();
			
		if (isset($this->_counter[$key][$eventstart]) === false)
		{
			$this->_counter[$key][$eventstart] = array();
			$this->_counter[$key][$eventstart]['start'] = 0;
			$this->_counter[$key][$eventstart]['token'] = 0;
			$this->_counter[$key][$eventstart]['total'] = 0;
		}
					
		$counter = &$this->_counter[$key][$eventstart];
		$timearr = explode('.',$time);
		
		if (preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$timearr[0]) !== 1)
			return(false);
			
		$timeprocess = (int) dwho_change_date_format($timearr[0],'Y-m-d H:i:s','U');
		
		$rs = 0;
		switch ($eventprocess)
		{
			case $eventstart:
				if ($counter['token'] === 1
				&& $counter['start'] !== 0)
					$rs = ($timeprocess - $counter['start']);	
				$counter['token'] = 1;
				$counter['start'] = $timeprocess;		
				break;
			case $eventend:
				if ($counter['token'] === 0)
					continue;
				$rs = ($timeprocess - $counter['start']);					
				$counter['token'] = 0;
				$counter['start'] = 0;
				break;
			default:
		}
		
		$counter['total'] += $rs;
		
		return($rs);
	}
	
	public function update_result($var,$str,$operator='+')
	{
		if (($res = call_user_func_array(array($this,'eval_result_var'), $var)) === null
		|| isset($res['result']) === false)
			return(false);
		 		
		$result = $res['result'];
			
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
				
		$this->set_result_var($result,$var);
		
		return(true);
	}
	
	private function set_result_var($result,$arr)
	{	
		$var = &$this->_result;
		
		for($i = 0;$i < count($arr);$i++)
		{
			$key = $arr[$i];
			if (isset($var[$key]) === true)
				$var = &$var[$key];
		}
		
		$var['result'] = $result;	
	}
	
	private function eval_result_var() 
	{	
		if(($argc = func_num_args()) === 0)
			return(null);
	
		$name = (string) func_get_arg(0);
	
		if (isset($this->_result[$name]) === true)
			$var = $this->_result;
		else
			return(null);
	
		$ref = $var[$name];
	
		if($argc === 1)
			return($ref);
		else if(is_array($var[$name]) === false)
			return(null);
	
		for($i = 1;$i < $argc;$i++)
		{
			$key = func_get_arg($i);
	
			if(dwho_ak($key,$ref) === false)
			        return(null);
	
			$ref = $ref[$key];
		}
	
		return($ref);	
	}
	
}