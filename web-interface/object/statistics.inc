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

class xivo_statistics
{
	
	private	$_regex		 		= array('datetime'	=> '/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',
										'date'		=> '/^(\d{4})-(\d{2})-(\d{2})$/',
										'time'		=> '/^(\d{2}):(\d{2}):(\d{2})$/');	
	private	$_xobj		 		= null;	
	private	$_ipbx		 		= null;	
	public 	$_queue_log_conf	= array();
	public 	$_queue_log 		= array();
	public 	$_conf		 		= array();
	public 	$_statsconfsess		= array();
	public 	$_period	 		= array('period1'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0),
										'period2'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0),
										'period3'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0),
										'period4'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0),
										'period5'	=> array(
											'exp'	=> '',
											'beg'	=> 0,
											'end'	=> 0)
										);
	public 	$_interval			= array('dbeg'	=> '',
										'dend'	=> '');
	private	$_ls_method			= array('DB','PHP');
	public 	$_method			= 'DB';
	public	$_type		 		= '';	
	
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
		
		$this->load_interval();
		
		$this->load_conf();
			
		if ($this->_method === 'PHP')
			$this->load_queuelog();
		
		if(($this->_queue_log_conf = &dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queuelog configuration',E_USER_ERROR);
	}
	
	public function set_type($type)
	{			
		$this->_type = $type;
	}
	
	public function set_method($method)
	{ 
		if (in_array($method,$this->_ls_method) === false)
			return(false);
			
		$this->_method = $method;
	}
	
	public function set_idconf($confid,$reloadconf=false)
	{	
		$this->_statsconfsess['id'] = (int) $confid;
		
		if ($reloadconf !== false)
		{
			$this->load_interval();
			$this->load_conf();
			if ($this->_method === 'PHP')
				$this->load_queuelog();
		}
	}
	
	public function set_interval($dbeg,$dend)
	{ 		
		if (preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$dbeg) !== 1
		|| preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$dend) !== 1)
			return(false);
			
		$this->_interval['dbeg'] = $dbeg;
		$this->_interval['dend'] = $dend;
		$this->_statsconfsess['_interval'] = $this->_interval;
	}
	
	public function get_interval()
	{	
		if (isset($this->_statsconfsess['_interval']) === false
		|| ($interval = $this->_statsconfsess['_interval']) === 0)
			return(false);
		
		return($interval);
	}
	
	public function set_calendar($arr)
	{
		$datecal = $arr;
		$dbeg = $datecal['dbeg'];
		$hbeg = $datecal['hbeg'];
		$dend = $datecal['dend'];
		$hend = $datecal['hend'];
		
		$resbeg = '';
		$resend = '';
		
		if (preg_match('/^(\d{4})-(\d{2})-(\d{2})$/',$dbeg) === 1
		&& preg_match('/^(\d{4})-(\d{2})-(\d{2})$/',$dend) === 1
		&& preg_match('/^(\d{0,2})[:]{0,1}(\d{0,2})$/',$hbeg,$outhbeg) === 1
		&& preg_match('/^(\d{0,2})[:]{0,1}(\d{0,2})$/',$hend,$outhend) === 1)
		{
			$resbeg .= $dbeg.' ';
			$resend .= $dend.' ';
		
			if (dwho_empty($outhbeg[1]) === true)
				$reshbeg = '00:00';
			elseif (dwho_empty($outhbeg[2]) === true)
			{
				if (strlen($outhbeg[1]) === 1)
					$reshbeg = '0'.$outhbeg[1].':00';
				else
					$reshbeg = $outhbeg[1].':00';
			}
			else 
				$reshbeg = $outhbeg[1].':'.$outhbeg[2];
				
			$resbeg .= $reshbeg;
				
			if (dwho_empty($outhend[1]) === true)
				$reshend = '23:59';
			elseif (dwho_empty($outhend[2]) === true)
			{
				if (strlen($outhend[1]) === 1)
					$reshend = '0'.$outhend[1].':59';
				else
					$reshend = $outhend[1].':59';
			}
			else 
				$reshend = $outhend[1].':'.$outhend[2];
				
			$resend .= $reshend;
		
			$resbeg .= ':01';
			$resend .= ':59';
		}
		$this->set_interval($resbeg,$resend);
	}
	
	public function get_infocal()
	{	
		if (($interval = $this->get_interval()) === false
		|| is_array($interval) === false)
			return(false);
			
		$infocal = array();
		$dbeg = $interval['dbeg'];
		$dend = $interval['dend'];
		
		$infocal['dbeg'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','Y-m-d');
		$infocal['hbeg'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','H:i');
		$infocal['dend'] = dwho_change_date_format($dend,'Y-m-d H:i:s','Y-m-d');
		$infocal['hend'] = dwho_change_date_format($dend,'Y-m-d H:i:s','H:i');
		
		return($infocal);
	}
	
	public function get_idconf()
	{	
		if (isset($this->_statsconfsess['id']) === false
		|| ($confid = $this->_statsconfsess['id']) === 0)
			return(false);
		
		return($confid);
	}
	
	public function get_conf()
	{	
		$statsconf = $this->_conf['stats_conf'];
		
		if (is_null($statsconf) === true)
			return(false);

		$workweek = array();
		$workweek['monday'] = $statsconf['monday'];
		$workweek['tuesday'] = $statsconf['tuesday'];
		$workweek['wednesday'] = $statsconf['wednesday'];
		$workweek['thursday'] = $statsconf['thursday'];
		$workweek['friday'] = $statsconf['friday'];
		$workweek['saturday'] = $statsconf['saturday'];
		$workweek['sunday'] = $statsconf['sunday'];

		$loadconf = array();
		$loadconf['id'] = $statsconf['id'];
		$loadconf['name'] = $statsconf['name'];
		$loadconf['hour_start'] = $statsconf['hour_start'];
		$loadconf['hour_end'] = $statsconf['hour_end'];
		$loadconf['workweek'] = $workweek;
		$loadconf['periods'] = $this->_period;
		
		return($loadconf);
	}
	
	private function load_interval()
	{
		if (($interval = $this->get_interval()) === false)
			return(false);
		
		$this->_interval = $interval;
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
	
	public function get_list_by_type()
	{		
		switch ($this->_type)
		{
			case 'agent':
				$agent = array_values($this->_conf['agent']);
				$nb_agent = count($this->_conf['agent']);
					
				$ls_agent = array();
				for($i=0;$i<$nb_agent;$i++)
				{
					$number = (string) $agent[$i]['number'];
					if (isset($ls_agent[$i]) === false)
						$ls_agent[$i] = array();
					
					array_push($ls_agent[$i],$number);
					array_push($ls_agent[$i],'agent/'.$number);
					array_push($ls_agent[$i],'Agent/'.$number);
				}
		
				$data = $ls_agent;
				break;
			case 'queue':
				$queue = array_values($this->_conf['queue']);
				$nb_queue = count($this->_conf['queue']);
				
				$ls_queuename = array();
				for($i=0;$i<$nb_queue;$i++)
					array_push($ls_queuename,$queue[$i]['name']);
			
				$data = $ls_queuename;
				break;
			default:
				return(false);
		}
		return($data);
	}
	
	private function load_queuelog()
	{
		if (($appqueue_log = &$this->_ipbx->get_application('queue_log')) === false)
			return(false);
			
		$data = $this->get_list_by_type();
		$conf = $this->get_conf();
		
		if (is_null($conf) === true)
			return(false);
			
		$conf['interval'] = $this->_interval;

		$this->_queue_log = $appqueue_log->get_queue_logs_stats($conf,$this->_type,$data);
		
		return(true);
	}
	
	public function get_queue_list()
	{			
		if (($appqueue = &$this->_ipbx->get_application('queue')) === false)
			return(false);
		
		$list_queue = $appqueue->get_queues_list(null,'name');
		
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
		
		$list_agent = $appagent->get_agentfeatures(null,'name');
		
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
	
	public function db_eval_data($type,$value,$event,$field=null,$addwhere=null)
	{
		if (($appqueue_log = &$this->_ipbx->get_application('queue_log')) === false)
			return(false);
			
		$conf = $this->get_conf();		
		
		if (is_null($conf) === true)
			return(false);
			
		$conf['interval'] = $this->_interval;
			
		switch ($type)
		{
			case 'count':
				return($appqueue_log->count_queue_logs_stats($conf,$this->_type,$value,$event,$addwhere));
				break;
			case 'sum':
				return($appqueue_log->sum_queue_logs_stats($conf,$this->_type,$value,$event,$field,$addwhere));
				break;
			default:
				return(false);
		}
	}

	public function eval_field_queue_log($event,$type)
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
			
		return('data'.$pos);
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
	
}
