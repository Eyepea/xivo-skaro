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
		
	private	$_xobj		 		= null;	
	private	$_ipbx		 		= null;	
	private	$_regex		 		= array('datetime'	=> '/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',
										'date'		=> '/^(\d{4})-(\d{2})-(\d{2})$/',
										'time'		=> '/^(\d{2}):(\d{2}):(\d{2})$/');	
	private	$_listday			= array('monday','tuesday','wednesday','thursday','friday','saturday','sunday');
	private	$_listmonth			= array('january','february','march','april','may','june','july','august','september','october','november','december');
	private	$_listaxetype		= array('type','day','week','month','year');
	private	$_listmethod		= array('DB','PHP');
	public 	$_debug				= array();
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
	public 	$_interval_process	= array('dbeg'	=> '',
										'dend'	=> '');
	public 	$_objectkey			= 0;
	public 	$_axetype			= 'type';
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
		
		$this->load_component();
		
		if(($this->_queue_log_conf = dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queuelog configuration',E_USER_ERROR);
	}
	
	public function load_component()
	{
		$this->push_debug("load_component()");		
		$this->load_interval();		
		$this->load_conf();
			
		if ($this->_method === 'PHP')
			$this->load_queuelog();		
	}

	private function load_interval()
	{
		$this->push_debug("load_interval()");	
		if (($interval = $this->get_interval()) === false)
			return(false);
		
		$this->_interval = $interval;
		$this->_interval_process = $interval;
		return(true);
	}
	
	private function load_conf()
	{
		$this->push_debug("load_conf()");	
		if (($confid = $this->get_idconf()) === false)
			return(false);
			
		$appstats_conf = $this->_xobj->get_application('stats_conf');

		if (($conf = $appstats_conf->get($confid)) === false
		|| is_array($conf) === false
		|| isset($conf['stats_conf']) === false)
			return(false);
		
		return($this->init_conf($conf));
	}
	
	private function init_conf($conf)
	{		
		$this->push_debug("init_conf()");
		$this->_conf = $conf;
		
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
	
	public function global_init($arr)
	{
		$this->push_debug("global_init( array() )",$arr);		
		
		if (isset($arr['key']) === true
		&& isset($arr['axetype']) === true
		&& $arr['axetype'] !== 'type')
			$this->set_objectkey($arr['key']);
		else
		{
			$this->set_objectkey(0);
			$this->set_axetype('type');
		}
		
		if (isset($arr['axetype']) === true)
			$this->set_axetype($arr['axetype']);
		
		if (isset($arr['datecal']) === true)
			$this->set_calendar($arr['datecal']);
		
		if (isset($arr['confid']) === true)
			$this->set_idconf($arr['confid'],true);		
	}
	
	public function set_objectkey($key)
	{			
		$this->push_debug("set_objectkey( string )",$key);
		$this->_objectkey = $key;
	}
	
	public function get_objectkey()
	{			
		$this->push_debug("get_objectkey( string )");
		return($this->_objectkey);
	}
	
	public function set_type($type)
	{			
		$this->push_debug("set_type( string )",$type);
		$this->_type = $type;
	}
	
	public function set_method($method)
	{ 
		$this->push_debug("set_method( array() )",$method);
		if (in_array($method,$this->_listmethod) === false)
			return(false);
			
		$this->_method = $method;
	}
	
	public function set_idconf($confid,$reloadconf=false)
	{	
		$this->push_debug("set_idconf()",$confid);
		$this->_statsconfsess['_id'] = (int) $confid;
		
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
		$this->push_debug("set_interval()",array($dbeg,$dend));
		if (preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$dbeg) !== 1
		&& preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$dend) !== 1)
			return(false);
		
		$this->_interval['dbeg'] = $dbeg;
		$this->_interval['dend'] = $dend;
		$this->_statsconfsess['_interval'] = $this->_interval;
	}
	
	public function get_interval()
	{	
		$this->push_debug("get_interval()");
		if (isset($this->_statsconfsess['_interval']) === false)
			return(false);
		
		return($this->_statsconfsess['_interval']);
	}
	
	public function get_infocal()
	{			
		$infocal = array();
		$infocal['dbeg'] = $infocal['hbeg'] = $infocal['dend'] = $infocal['hend'] = null;
		$infocal['dday'] = null;
		$infocal['dweek'] = null;
		$infocal['dmonth'] = null;
		$infocal['dyear'] = null;
		
		if (($interval = $this->get_interval()) === false
		|| is_array($interval) === false)
			return($infocal);
		
		switch ($this->get_axtype())
		{
			case 'day':			
				$dbeg = $interval['dbeg'];
				$infocal['dday'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','Y-m-d');
				break;
			case 'week':			
				$dbeg = $interval['dbeg'];
				$infocal['dweek'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','Y-m-d');
				break;
			case 'month':
				$dbeg = $interval['dbeg'];
				$infocal['dmonth'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','Y-m');
				break;
			case 'year':
				$dbeg = $interval['dbeg'];
				$infocal['dyear'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','Y');
				break;
			case 'type':
			default:			
				$dbeg = $interval['dbeg'];
				$dend = $interval['dend'];
				
				$infocal['dbeg'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','Y-m-d');
				$infocal['hbeg'] = dwho_change_date_format($dbeg,'Y-m-d H:i:s','H:i');
				$infocal['dend'] = dwho_change_date_format($dend,'Y-m-d H:i:s','Y-m-d');
				$infocal['hend'] = dwho_change_date_format($dend,'Y-m-d H:i:s','H:i');
		}
		return($infocal);
	}
	
	public function set_calendar($arr)
	{
		$this->push_debug("set_calendar()",$arr);
		switch ($this->get_axtype())
		{
			case 'day':
				if(is_array($arr) === true)
					$dbeg = $arr['dday'];
				elseif($arr === 'default')
					$dbeg = date('Y-m-d');
				else 
					break;
				$this->set_interval($dbeg.' 00:00:01',$dbeg.' 23:59:59');
				break;
			case 'week':
				if(is_array($arr) === true)
					$dbeg = $arr['dweek'];
				elseif($arr === 'default')
					$dbeg = date('Y-m-d');
				$this->set_interval($dbeg.' 00:00:01',$dbeg.' 23:59:59');
				break;
			case 'month':
				if(is_array($arr) === true)
					$dbeg = $arr['dmonth'];
				elseif($arr === 'default')
					$dbeg = date('Y-m');
				$date = dwho_date_parse_from_format('Y-m',$dbeg);
				$lastday = strtotime('-1 second',strtotime('+1 month',strtotime($date['month'].'/01/'.$date['year'].' 00:00:00')));
				$this->set_interval($dbeg.'-01 00:00:01',date('Y-m-d',$lastday).' 23:59:59');
				break;
			case 'year':
				if(is_array($arr) === true)
					$dbeg = $arr['dyear'];
				elseif($arr === 'default')
					$dbeg = date('Y');
				$date = dwho_date_parse_from_format('Y',$dbeg);
				$this->set_interval($dbeg.'-01-01 00:00:01',$dbeg.'31-12 23:59:59');
				break;
			case 'type':
			default:
				$hbeg = $hend = '';	
				if(is_array($arr) === true)
				{
					$dbeg = $arr['dbeg'];
					$dend = $arr['dend'];
					if (isset($arr['hbeg']) === true)
						$hbeg = $arr['hbeg'];
					if (isset($arr['hend']) === true)
						$hend = $arr['hend'];	
				}				
				elseif($arr === 'default')
				{
					$dbeg = date('Y-m-d');
					$dend = date('Y-m-d');
				}
				else 
					break;
				
				$resbeg = '';
				$resend = '';
				
				if (preg_match('/^(\d{4})-(\d{2})-(\d{2})$/',$dbeg) === 1
				&& preg_match('/^(\d{4})-(\d{2})-(\d{2})$/',$dend) === 1
				&& preg_match('/^(\d{0,2})[:]{0,1}(\d{0,2})$/',$hbeg,$outhbeg) === 1
				&& preg_match('/^(\d{0,2})[:]{0,1}(\d{0,2})$/',$hend,$outhend) === 1)
				{
					$resbeg .= $dbeg.' ';
					$resend .= $dend.' ';
					
					if (($conf = $this->get_conf()) !== false
					&& isset($conf['hour_start']) === true
					&& isset($conf['hour_end']) === true)
					{
						$hour_start = $conf['hour_start'];
						$hour_end = $conf['hour_end'];
					}
				
					if (dwho_empty($outhbeg[1]) === true)
					{
						if (isset($hour_start) === false)
							$reshbeg = '00:00:01';
						else
							$reshbeg = $hour_start;
					}
					elseif (dwho_empty($outhbeg[2]) === true)
					{
						if (strlen($outhbeg[1]) === 1)
							$reshbeg = '0'.$outhbeg[1].':00:01';
						else
							$reshbeg = $outhbeg[1].':00:01';
					}
					else 
						$reshbeg = $outhbeg[1].':'.$outhbeg[2].':01';
						
					$resbeg .= $reshbeg;
						
					if (dwho_empty($outhend[1]) === true)
					{
						if (isset($hour_end) === false)
							$reshend = '23:59:59';
						else
							$reshend = $hour_end;
					}
					elseif (dwho_empty($outhend[2]) === true)
					{
						if (strlen($outhend[1]) === 1)
							$reshend = '0'.$outhend[1].':59:59';
						else
							$reshend = $outhend[1].':59:59';
					}
					else 
						$reshend = $outhend[1].':'.$outhend[2].':59';
						
					$resend .= $reshend;				
				}
				$this->set_interval($resbeg,$resend);
		}
	}
	
	public function get_list_axtype()
	{
		$this->push_debug("get_list_axtype()");
		return($this->_listaxetype);
	}
	
	public function set_axetype($axetype)
	{
		$this->push_debug("set_axetype()",$axetype);
		if (in_array($axetype,$this->_listaxetype) === false)
			return(false);
			
		$this->_axetype = $axetype;
		$this->_statsconfsess['_axetype'] = $this->_axetype;
	}
	
	public function get_axtype()
	{	
		$this->push_debug("get_axtype()");
		if (isset($this->_statsconfsess['_axetype']) === false
		|| ($axetype = $this->_statsconfsess['_axetype']) === '')
			return(false);
			
		return($axetype);
	}
	
	public function get_idconf()
	{	
		$this->push_debug("get_idconf()");
		if (isset($this->_statsconfsess['_id']) === false
		|| ($confid = $this->_statsconfsess['_id']) === 0)
			return(false);
		
		return($confid);
	}
	
	public function get_conf()
	{	
		$this->push_debug("get_conf()");		
		if (isset($this->_conf['stats_conf']) === false)
			return(false);
		
		$statsconf = $this->_conf['stats_conf'];

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
		$loadconf['interval'] = $this->_interval;
		$loadconf['periods'] = $this->_period;
		$loadconf['objectkey'] = $this->_objectkey;	
		$loadconf['axetype'] = $this->_axetype;	
		
		return($loadconf);
	}
	
	public function get_interval_process()
	{
		$this->push_debug("get_interval_process()");
		$interval = $this->_interval_process;
		
		if (is_null($interval) === true)
			return(false);
			
		return($interval);		
	}
	
	public function get_hour_range()
	{			
		$this->push_debug("get_hour_range()");
		$interval = $this->get_interval();
		
		if (is_null($interval) === true)
			return(false);
			
		$rs = array();
		$rs['interval'] = $interval;
		return($rs);
		
	}
	
	public function get_week_range()
	{
		$interval = $this->get_interval();
		$date = dwho_date_parse_from_format('Y-m-d H:i:s',$interval['dbeg']);
		$week = date('W',mktime(0,0,0,$date['month'],$date['day'],$date['year']));
		$rs = array();
		$rs['from'] = strtotime("{$date['year']}-W{$week}-1");
		$rs['to'] = strtotime("{$date['year']}-W{$week}-7");		
		return($rs);
	}
	
	public function get_listhour()
	{	
		$this->push_debug("get_listhour()");
		if(($conf = $this->get_conf()) === false)
			return(false);
			
		$hour_start = explode(':',$conf['hour_start']);
		$hour_end = explode(':',$conf['hour_end']);
		
		$rs = array();
		for ($i=0;$i<=24;$i++)
		{
			if ($i < $hour_start[0]
			|| $i > $hour_end[0])
				continue;
				
			$tmp = array();
			$tmp['identity'] = 'hour-opt('.$i.')';
			$tmp['name'] = $i;
			$tmp['key'] = $i;
				
			array_push($rs,$tmp);
		}		
		return($rs);
	}
	
	public function get_listday_for_week()
	{	
		$this->push_debug("get_listday_for_week()");
		if(($conf = $this->get_conf()) === false)
			return(false);
		
		$workweek = $conf['workweek'];
		
		$rs = array();
		foreach ($this->_listday as $day)
		{
			if (isset($workweek[$day]) === true
			&& $workweek[$day] === false)
				continue;
				
			$tmp = array();
			$tmp['identity'] = $day;
			$tmp['name'] = $day;
			$tmp['key'] = $day;
				
			array_push($rs,$tmp);
		}
		return($rs);
	}
	
	public function get_listday_for_month()
	{
		$this->push_debug("get_listday_for_month()");
		if(($conf = $this->get_conf()) === false)
			return(false);
		
		$workweek = $conf['workweek'];
		
		$date = dwho_date_parse_from_format('Y-m-d H:i:s',$this->_interval['dbeg']);		
		$lastday = strtotime('-1 second',strtotime('+1 month',strtotime($date['month'].'/01/'.$date['year'].' 00:00:00')));
		
		$rs = array();
		for ($i=1;$i<=date('d',$lastday);$i++)
		{
			$time = mktime(0,0,0,$date['month'],$i,$date['year']);
			$dayname = strtolower(date('l',$time));
			if ($workweek[$dayname] === false)
				continue;
				
			$tmp = array();
			$tmp['identity'] = $dayname.'-opt('.$i.')';
			$tmp['name'] = $dayname;
			$tmp['key'] = $i;
				
			array_push($rs,$tmp);	
		}
		return($rs);
	}
	
	public function get_listmonth()
	{
		$this->push_debug("get_listmonth()");
		
		$rs = array();
		for ($i=0;$i<=11;$i++)
		{				
			$tmp = array();
			$tmp['identity'] = $this->_listmonth[$i];
			$tmp['name'] = $this->_listmonth[$i];
			$tmp['key'] = $i+1;
				
			array_push($rs,$tmp);
		}		
		return($rs);
	}
	
	public function get_day_from_week_by_name_day($year,$week,$nameday)
	{
		$from = strtotime("{$year}-W{$week}-1");
		$to = strtotime("{$year}-W{$week}-7");
		
		$rs = array();
		for ($i=$from;$i<=$to;$i=strtotime('+1day',$i))
		{
			if (date('l',$i) === ucfirst($nameday))
				return(date('Y-m-d',$i));
		}
		return(null);
	}
	
	public function get_list_by_type()
	{
		$this->push_debug("get_list_by_type()");
		$data = array();
		switch ($this->_type)
		{
			case 'agent':
				$ls_agent = array();
				if (((int) $this->_objectkey) === 0)
				{
					$agent = array_values($this->_conf['agent']);
					$nb_agent = count($this->_conf['agent']);
					for($i=0;$i<$nb_agent;$i++)
					{
						$number = (string) $agent[$i]['number'];
						if (isset($ls_agent[$i]) === false)
							$ls_agent[$i] = array();
						
						array_push($ls_agent[$i],$number);
						array_push($ls_agent[$i],'agent/'.$number);
						array_push($ls_agent[$i],'Agent/'.$number);
					}
				}
				elseif(($id = ((int) $this->_objectkey)) !== 0)	
				{	
					if (($appagent = &$this->_ipbx->get_application('agent')) === false
					|| ($agent = $appagent->get($id)) === false)
						break;
					
					array_push($ls_agent[0],$agent['number']);
					array_push($ls_agent[1],'agent/'.$agent['number']);
					array_push($ls_agent[2],'Agent/'.$agent['number']);
				}
				$data = $ls_agent;
				break;
			case 'queue':
				$ls_queuename = array();
				if (((int) $this->_objectkey) === 0
				&& isset($this->_conf['queue']) === true)
				{
					$queue = array_values($this->_conf['queue']);
					$nb_queue = count($this->_conf['queue']);
					
					for($i=0;$i<$nb_queue;$i++)
						array_push($ls_queuename,$queue[$i]['name']);
				}
				elseif(($id = ((int) $this->_objectkey)) !== 0)	
				{	
					if (($appqueue = &$this->_ipbx->get_application('queue')) === false
					|| ($queue = $appqueue->get($id)) === false)
						break;
					
					array_push($ls_queuename,$queue['queuefeatures']['name']);
				}			
				$data = $ls_queuename;
				break;
			default:
				return(false);
		}
		return($data);
	}
	
	private function load_queuelog()
	{
		$this->push_debug("load_queuelog()");
		if (($appqueue_log = &$this->_ipbx->get_application('queue_log')) === false)
			return(false);
			
		$data = $this->get_list_by_type();
		$conf = $this->get_conf();
		
		if (is_null($conf) === true)
			return(false);
			
		$conf['axetype'] = $this->_axetype;
		$conf['interval'] = $this->_interval_process;

		$this->_queue_log = $appqueue_log->get_queue_logs_stats($conf,$this->_type,$data);
		
		return(true);
	}
	
	public function get_object_list()
	{
		$this->push_debug("get_object_list()");
		switch ($this->_type)
		{
			case 'agent':
				return($this->get_agent_list());
				break;
			case 'queue':
				return($this->get_queue_list());
				break;
			default:
				return(false);
		}
	}
	
	public function get_queue_list()
	{			
		$this->push_debug("get_queue_list()");
		
		if (isset($this->_conf['queue']) === false
		|| ($appqueue = &$this->_ipbx->get_application('queue')) === false)
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
		$this->push_debug("get_agent_list()");
		
		if (isset($this->_conf['agent']) === false
		|| ($appagent = &$this->_ipbx->get_application('agent')) === false)
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
		$this->push_debug("db_eval_data()",array($type,$value,$event,$field,$addwhere));
		if (($appqueue_log = &$this->_ipbx->get_application('queue_log')) === false)
			return(false);
			
		$conf = $this->get_conf();		
		
		if (is_null($conf) === true)
			return(false);
			
		$conf['axetype'] = $this->_axetype;
		$conf['interval'] = $this->_interval_process;
			
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
		$this->push_debug("eval_field_queue_log()",array($event,$type));
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
		$this->push_debug("eval_data_queue_log()",array($queue_log_entry,$event,$type));
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

	public function push_debug($key,$var=null) {

		if (isset($this->_debug[$key]) === true)
			$this->_debug[$key.'{'.uniqid().'}'] = $var;
		else
			$this->_debug[$key] = $var;

	}

	public function get_debug() {

		return($this->_debug);


	}
	
}
