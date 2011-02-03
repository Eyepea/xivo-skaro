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
	private	$_cache_path 		= '';
	private	$_regex		 		= array('datetime'	=> '/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',
										'unixtime'	=> '/^(\d{10})$/',
										'date'		=> '/^(\d{4})-(\d{2})-(\d{2})$/',
										'time'		=> '/^(\d{2}):(\d{2}):(\d{2})$/');	
	private	$_listday			= array('monday','tuesday','wednesday','thursday','friday','saturday','sunday');
	private	$_listmonth			= array('january','february','march','april','may','june','july','august','september','october','november','december');
	private	$_listaxetype		= array('type','day','week','month','year');
	private	$_listtype			= array('queue','agent','period');
	private	$_listmethod		= array('DB','PHP');
	public 	$_debug				= array();
	public 	$_error				= array();
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
	public 	$_interval			= array();
	public 	$_interval_process	= array();
	public 	$_date_process		= array('dbeg'	=> null,
										'dend'	=> null);
	public 	$_objectkey			= 0;
	public 	$_idconf			= 0;
	public 	$_axetype			= 'type';
	public 	$_method			= 'DB';
	public	$_type		 		= '';
	
	public function __construct(&$xobj,&$ipbx)
	{
		if (is_object($xobj) === false
		|| is_object($ipbx) === false)
			return(false);
		
		if(dwho_issa('_statsconf',$_SESSION) === false)
			$_SESSION['_statsconf'] = array();
			
		$this->_statsconfsess = &$_SESSION['_statsconf'];
		
		$this->_xobj = &$xobj;
		$this->_ipbx = &$ipbx;
		
		if(($this->_queue_log_conf = dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queuelog configuration',E_USER_ERROR);
	}
	
	public function load_component()
	{
		$this->push_debug("load_component()");
		
		if ($this->load_conf() === false)
			return(false);
			
		if ($this->_method === 'PHP')
			$this->load_queuelog();
	}
	
	private function load_conf()
	{
		$this->push_debug("load_conf()");	
		if (($idconf = $this->get_idconf()) === false)
			return(false);
			
		$appstats_conf = $this->_xobj->get_application('stats_conf');

		if (($conf = $appstats_conf->get($idconf)) === false
		|| is_array($conf) === false
		|| isset($conf['stats_conf']) === false)
			return(false);
		
		return($this->init_conf($conf));
	}
	
	private function init_cal($conf)
	{			
		$dbeg = $this->all_to_unixtime($conf['dbegcache']);
		$dend = $this->all_to_unixtime($conf['dendcache']);
		$dbeg = strtotime('-1 month', $dend);
		
		$infocal = array();
		$infocal['dbeg'] 	= date('Y-m-d',$dbeg);
		$infocal['dend'] 	= date('Y-m-d',$dend);
		$infocal['dday'] 	= date('Y-m-d',$dbeg);
		$infocal['dweek'] 	= date('Y-m-d',$dbeg);
		$infocal['dmonth'] 	= date('Y-m',$dbeg);
		$infocal['dyear'] 	= date('Y',$dbeg);
		
		$this->_date_process = $infocal;
		$this->_statsconfsess['_date_process'] = $infocal;
		return(true);
	}
	
	private function init_conf($conf)
	{		
		$this->push_debug("init_conf()");
		$this->_conf = $conf;
		
		$stats_conf = $conf['stats_conf'];
		
		$this->init_cal($stats_conf);
		
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
			elseif (preg_match('/([0-9]+)[-]{0,1}/',$stats_conf['period'.$i],$out) === 1)
			{
				$this->_period['period'.$i]['beg'] = (int) $out[1];
				$this->_period['period'.$i]['end'] = null;
			}
		}
		return(true);
	}	
	
	public function set_idconf($idconf,$reloadconf=false)
	{	
		$this->push_debug("set_idconf()",array($idconf,$reloadconf));
		if (is_numeric($idconf) === false)
			return(false);
		$this->_idconf = (int) $idconf;
		$this->_statsconfsess['_id'] = (int) $idconf;
		
		if ($reloadconf !== false)
			$this->load_component();
		return(true);
	}
		
	public function get_idconf()
	{	
		$this->push_debug("get_idconf()");
		if ($this->_idconf !== 0)
			$idconf = $this->_idconf;
		elseif(isset($this->_statsconfsess['_id']) === false
		|| ($idconf = $this->_statsconfsess['_id']) === 0)
			return(false);
		
		return($idconf);
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
		$loadconf['dcreate'] = $statsconf['dcreate'];
		$loadconf['dupdate'] = $statsconf['dupdate'];
		$loadconf['dgenercache'] = $statsconf['dgenercache'];
		$loadconf['dbegcache'] = $statsconf['dbegcache'];
		$loadconf['dendcache'] = $statsconf['dendcache'];		
		$loadconf['workweek'] = $workweek;
		$loadconf['periods'] = $this->_period;
		$loadconf['objectkey'] = $this->_objectkey;
		
		return($loadconf);
	}
	
	public function global_init($arr)
	{
		$this->push_debug("global_init()",$arr);
		
		if (isset($arr['confid']) === true)
			$this->set_idconf($arr['confid'],true);
		
		$this->load_component();			
			
		$this->_objectkey = 0;
		$this->set_axetype('type');
		
		if (isset($arr['key']) === true
		&& isset($arr['axetype']) === true
		&& $arr['axetype'] !== 'type')
			$this->_objectkey = $arr['key'];
		
		if (isset($arr['axetype']) === true)
			$this->set_axetype($arr['axetype']);
		
		$this->set_datecal($arr);
	}
	
	public function set_type($type)
	{			
		$this->push_debug("set_type()",$type);
		$this->_type = $type;
	}
	
	public function set_method($method)
	{ 
		$this->push_debug("set_method()",$method);
		if (in_array($method,$this->_listmethod) === false)
			return(false);
			
		$this->_method = $method;
	}
	
	public function set_axetype($axetype)
	{
		$this->push_debug("set_axetype()",$axetype);
		if (in_array($axetype,$this->_listaxetype) === false)
			return(false);
			
		$this->_axetype = $axetype;
		$this->_statsconfsess['_axetype'] = $this->_axetype;
	}
	
	public function get_objectkey()
	{
		return($this->_objectkey);
	}
	
	public function get_axetype()
	{
		return($this->_axetype);
	}
	
	public function get_list_axetype()
	{
		$this->push_debug("get_list_axetype()");
		return($this->_listaxetype);
	}
	
	public function get_listtype()
	{
		return($this->_listtype);
	}
	
	public function get_interval()
	{
		return($this->_interval);
	}
	
	private function isvalid_interval($dip)
	{
		$this->push_debug("isvalid_interval()",array($dip));
		if (is_array($dip) === true
		&& isset($dip['beg']) === true
		&& isset($dip['end']) === true
		&& preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$dip['beg']) === 1
		&& preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',$dip['end']) === 1)
			return(true);
			
		return(false);
	}
		
	public function build_full_date_interval($dbeg,$dend)
	{
		$this->push_debug("build_full_interval()",array($dbeg,$dend));
		$rs = array();
					
		$hour_start = '00:00:01';
		$hour_end = '23:59:59';
							
		if (($conf = $this->get_conf()) !== false
		&& isset($conf['hour_start']) === true
		&& isset($conf['hour_end']) === true)
		{
			$hour_start = $conf['hour_start'];
			$hour_end = $conf['hour_end'];
		}
		
		$listday = $this->get_listday_for_interval($dbeg,$dend);
		$listidx = array_keys($listday);
		while($listidx)
		{
			$index = array_shift($listidx);
			$key = $listday[$index]['key'];
			$day_process = $listday[$index]['time'];
			$dip = array();
			$dip['beg'] = strtotime(date('Y-m-d',$day_process).' '.$hour_start);
			$dip['end'] = strtotime(date('Y-m-d',$day_process).' '.$hour_end);
			$rs[$key] = $dip;
		}		
		return($rs);
	}
		
	public function set_datecal($arr)
	{
		$this->push_debug("set_datecal()",$arr);
		
		if(($conf = $this->get_conf()) === false)
			return(false);
			
		$this->init_cal($conf);
		
		$infocal = $this->_statsconfsess['_date_process'];
	
		$axtetype = $this->get_axetype();
		switch ($axtetype)
		{
			case 'day':
				if (isset($arr['dday']) === true)
				{
					$infocal['dday'] = $arr['dday'];
					$time = strtotime($infocal['dday']);
					$dbeg = mktime(0,0,1,date('m',$time),date('d',$time),date('Y',$time));
					$dend = mktime(23,59,59,date('m',$time),date('d',$time),date('Y',$time));
					$infocal['dbeg'] = date('Y-m-d',$dbeg);
					$infocal['dend'] = date('Y-m-d',$dend);
				}
				break;
			case 'week':
				if (isset($arr['dweek']) === true)
				{
					$infocal['dweek'] = $arr['dweek'];
					$time = $this->all_to_unixtime($infocal['dweek']);
					$date = $this->get_week_range($time);
					$infocal['dbeg'] = date('Y-m-d',$date['beg']);
					$infocal['dend'] = date('Y-m-d',$date['end']);
				}
				break;
			case 'month':
				if (isset($arr['dmonth']) === true)
				{
					$infocal['dmonth'] = $arr['dmonth'];
					$time = $this->all_to_unixtime($infocal['dmonth']);
					$date = $this->get_month_range($time);
					$infocal['dbeg'] = date('Y-m-d',$date['beg']);
					$infocal['dend'] = date('Y-m-d',$date['end']);
				}
				break;
			case 'year':
				if (isset($arr['dyear']) === true)
				{
					$infocal['dyear'] = $arr['dyear'];
					$time = $this->all_to_unixtime($infocal['dyear']);
					$date = $this->get_year_range($time);
					$infocal['dbeg'] = date('Y-m-d',$date['beg']);
					$infocal['dend'] = date('Y-m-d',$date['end']);
				}
				break;
			case 'type':
			default:		
				if (isset($arr['dbeg']) === true
				&& isset($arr['dend']) === true)
				{
					$infocal['dbeg'] = $arr['dbeg'];
					$infocal['dend'] = $arr['dend'];
				}
		}
		$this->_date_process = $infocal;
		$this->_statsconfsess['_date_process'] = $infocal;
	}
	
	public function all_to_unixtime($str)
	{
		$rs = time();	
		if (preg_match($this->_regex['datetime'],$str) === 1)
			$rs = (int) strtotime($str);
		elseif (preg_match($this->_regex['unixtime'],$str) === 1)
			$rs = (int) $str;
		elseif (preg_match($this->_regex['date'],$str) === 1)
			$rs = (int) strtotime($str);
		elseif (preg_match('/^(\d{4})-(\d{2})$/',$str) === 1)
			$rs = (int) strtotime($str.'-01');
		elseif (preg_match('/^(\d{4})$/',$str) === 1)
			$rs = (int) strtotime($str.'-01-01');
			
		return($rs);
	}
	
	public function get_datecal()
	{			
		$this->push_debug("get_infocal()");
		return($this->_date_process);
	}
		
	public function get_year_range($date)
	{
		$date = $this->all_to_unixtime($date);
		$year = date('Y',$date);
		$firstday = mktime(0, 0, 0, 1, 1, $year);
		$lastday = $this->get_lastday_for_month($year,12);
		$rs = array();
		$rs['beg'] = $firstday;
		$rs['end'] = $lastday;		
		return($rs);
	}
		
	public function get_month_range($date)
	{
		$date = $this->all_to_unixtime($date);
		$month = date('m',$date);
		$year = date('Y',$date);
		$firstday = mktime(0, 0, 0, $month, 1, $year);
		$lastday = mktime(23, 59, 59, $month + 1, 0, $year);
		$rs = array();
		$rs['beg'] = $firstday;
		$rs['end'] = $lastday;		
		return($rs);
	}
		
	public function get_week_range($date)
	{
		$date = $this->all_to_unixtime($date);
		$week = date('W',$date);
		$year = date('Y',$date);
		$rs = array();
		$rs['beg'] = strtotime("{$year}-W{$week}-1");
		$rs['end'] = strtotime("{$year}-W{$week}-7");		
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
			$tmp['identity'] = dwho_i18n::babelfish('hour-opt',$i);
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
		foreach ($this->_listday as $dayname)
		{
			if (isset($workweek[$dayname]) === true
			&& $workweek[$dayname] === false)
				continue;
				
			$tmp = array();
			$tmp['identity'] =  dwho_i18n::babelfish($dayname);
			$tmp['name'] = $dayname;
			$tmp['key'] = $dayname;
			
			$rs[$dayname] = $tmp;
		}
		return($rs);
	}
	
	public function get_lastday_for_month($year,$month)
	{		
		if (preg_match('/^(\d{4})-(\d{2})$/',"$year-$month") === 1)
			return(mktime(23, 59, 59, $month+1, 0, $year));
			
		return(false);
	}
	
	public function get_listday_for_month($year,$month)
	{
		$this->push_debug("get_listday_for_month()",array($year,$month));
		if(($conf = $this->get_conf()) === false)
			return(false);
		
		$workweek = $conf['workweek'];
		
		#$lastday = strtotime('-1 day',strtotime('+1 month',strtotime($month.'/01/'.$year)));
		$lastday = mktime(23, 59, 59, $month + 1, 0, $year);
		
		$rs = array();
		for ($i=1;$i<=date('d',$lastday);$i++)
		{
			$time = mktime(0,0,0,$month,$i,$year);
			$daynumber = date('d',$time);
			$monthnumber = date('m',$time);
			$dayname = strtolower(date('l',$time));
			if ($workweek[$dayname] === false)
				continue;
				
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish($dayname.'-opt',$i);
			$tmp['index'] = (int) $year.$monthnumber.$daynumber;
			$tmp['dayname'] = $dayname;
			$tmp['day'] = $daynumber;
			$tmp['name'] = $dayname;
			$tmp['key'] = $daynumber;
			$tmp['time'] = (int) $time;
				
			array_push($rs,$tmp);	
		}
		return($rs);
	}
	
	public function get_listday_for_interval($dbeg,$dend)
	{
		$this->push_debug("get_listday_for_interval()",array($dbeg,$dend));
		if(($conf = $this->get_conf()) === false
		|| (strlen($dbeg) !== 10
			&& strlen($dend) !== 10))
			return(false);
				
		$workweek = $conf['workweek'];
		
		$day_process = strtotime('-1 day',$dbeg);
		$listday = array();
		while ($day_process < ((int) $dend))
		{
			$day_process = strtotime('+1 day',$day_process);	
			$dayname = strtolower(date('l',$day_process));
			$daynumber = date('d',$day_process);
			$month = date('m',$day_process);
			$year = date('Y',$day_process);
			
			if (isset($workweek[$dayname]) === false
			 || $workweek[$dayname] === false)
				continue;
			
			$tmp = array();
			$tmp['identity'] =  dwho_i18n::babelfish($dayname);
			$tmp['key'] = (int) ($year.$month.$daynumber);
			$tmp['day'] = $daynumber;
			$tmp['dayname'] = $dayname;
			$tmp['time'] = (int) $day_process;
			$listday[$tmp['key']] = $tmp;
		}		
		return($listday);
	}
	
	public function get_listmonth_for_interval($dbeg,$dend)
	{
		$this->push_debug("get_listmonth_for_interval()",array($dbeg,$dend));
			
		$dbeg = $this->all_to_unixtime($dbeg);
		$dend = $this->all_to_unixtime($dend);
		
		$month_process = $dbeg;
		#$month_process = strtotime('-1 month',$dbeg);
		#$month_process = mktime(0, 0, 0, date('m',$month_process), 1, date('Y',$month_process));
		$listmonth = array();
		while ($month_process <= ((int) $dend))	
		{
			$dayname = strtolower(date('l',$month_process));
			$month = date('m',$month_process);
			$year = date('Y',$month_process);
			
			$tmp = array();
			$tmp['key'] = (int) ($year.$month);
			$tmp['time'] = (int) $month_process;					
			array_push($listmonth,$tmp);
			$month_process = strtotime('+1 month',$month_process);	
		}		
		return($listmonth);
	}
	
	public function get_listmonth()
	{
		$this->push_debug("get_listmonth()");		
		$rs = array();
		for ($i=0;$i<=11;$i++)
		{				
			$tmp = array();
			$tmp['identity'] = dwho_i18n::babelfish($this->_listmonth[$i]);
			$tmp['name'] = $this->_listmonth[$i];
			$tmp['key'] = $i+1;
				
			array_push($rs,$tmp);
		}		
		return($rs);
	}
	
	public function get_day_from_week_by_name_day($year,$week,$nameday)
	{
		$this->push_debug("get_day_from_week_by_name_day()",array($year,$week,$nameday));
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
	
	public function get_list_by_type($type)
	{
		$this->push_debug("get_list_by_type()");			
		$data = array();
		switch ($type)
		{
			case 'agent':
				$ls_agent = array();
				if (((int) $this->_objectkey) === 0)
				{
					asort($this->_conf['agent']);
					$agent = array_values($this->_conf['agent']);
					$nb_agent = count($this->_conf['agent']);
					for($i=0;$i<$nb_agent;$i++)
					{
						$number = (string) $agent[$i]['number'];
						if (isset($ls_agent[$i]) === false)
							$ls_agent[$i] = array();
						
						$tmp = array();
						array_push($tmp,$number);
						array_push($tmp,'agent/'.$number);
						array_push($tmp,'Agent/'.$number);
						$key = array();
						$key['identity'] = $tmp;
						$key['name'] = $tmp;
						$key['key'] = $tmp;
						$key['id'] = (int) $agent[$i]['id'];
						$key['number'] = (int) $number;
						$ls_agent[$i] = $key;
					}
				}
				elseif(($id = ((int) $this->_objectkey)) !== 0)	
				{
					if (($appagent = &$this->_ipbx->get_application('agent')) === false
					|| ($agent = $appagent->get($id)) === false)
						break;
					$tmp = array();
					array_push($tmp,$agent['agentfeatures']['number']);
					array_push($tmp,'agent/'.$agent['agentfeatures']['number']);
					array_push($tmp,'Agent/'.$agent['agentfeatures']['number']);
					$key = array();
					$key['identity'] = $tmp;
					$key['name'] = $tmp;
					$key['key'] = $tmp;
					$key['id'] = (int) $agent['agentfeatures']['id'];
					$key['number'] = (int) $agent['agentfeatures']['number'];
					array_push($ls_agent,$key);
				}
				$data = $ls_agent;
				break;
			case 'period':
			case 'queue':
				$ls_queuename = array();
				if (((int) $this->_objectkey) === 0
				&& isset($this->_conf['queue']) === true)
				{
					asort($this->_conf['queue']);
					$queue = array_values($this->_conf['queue']);	
					$nb_queue = count($this->_conf['queue']);			
					for($i=0;$i<$nb_queue;$i++)
					{
						$tmp = array();
						$tmp['identity'] = array($queue[$i]['name']);
						$tmp['name'] = array($queue[$i]['name']);
						$tmp['key'] = array($queue[$i]['name']);
						$tmp['id'] = (int) $queue[$i]['id'];
						array_push($ls_queuename,$tmp);
					}
				}
				elseif(($id = ((int) $this->_objectkey)) !== 0)	
				{					
					if (($appqueue = &$this->_ipbx->get_application('queue')) === false
					|| ($queue = $appqueue->get($id)) === false)
						break;					
					$tmp = array();
					$tmp['identity'] = array($queue['queuefeatures']['name']);
					$tmp['name'] = array($queue['queuefeatures']['name']);
					$tmp['key'] = array($queue['queuefeatures']['name']);
					$tmp['id'] = (int) $queue['queuefeatures']['id'];
					array_push($ls_queuename,$tmp);
				}
				$data = $ls_queuename;
				break;
			default:
				return(false);
		}
		return($data);
	}
	
	public function get_object_list()
	{
		$this->push_debug("get_object_list()");
		switch ($this->_type)
		{
			case 'agent':
				return($this->get_agent_list());
				break;
			case 'period':
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
	
	public function generate_cache($idconf,$dbeg,$dend,$type,$idtype=null)
	{		
		$this->set_idconf($idconf);
		$this->load_conf();
		
		if(($conf = $this->get_conf()) === false
		|| (is_numeric($dbeg) === true
			&& strlen($dbeg) === 10) === false
		|| (is_numeric($dend) === true
			&& strlen($dend) === 10) === false)
			return(false);
			
		if(is_null($idtype) === false)
			$this->_objectkey = $idtype;
		
		if(($list = $this->get_list_by_type($type)) === false)
			return(false);
		
		#$this->_interval = $this->build_full_date_interval($dbeg,$dend);
		$this->_interval = array();
		$this->_interval['beg'] = $dbeg;
		$this->_interval['end'] = $dend;
		
		$rs = $this->generate_cache_for_type($type,$list);		
		$this->update_date_genercache();
		
		return($rs);
	}
	
	private function generate_cache_for_type($type,$list)
	{
		switch ($type)
		{
			case 'agent':
				return($this->generate_cache_for_agent($list));
				break;
			case 'queue':
				return($this->generate_cache_for_queue($list));
				break;
			case 'period':
				return($this->generate_cache_for_period($list));
				break;
			default:
				return(false);
		}
	}
	
	private function generate_cache_for_queue($listqueue)
	{		
		if(xivo::load_class('xivo_statistics_queue',
			XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics',
			'queue',false) === false)
			die('Can\'t load xivo_statistics_queue object');
		
		$stats_queue = new xivo_statistics_queue(&$this);
		if (($appqueue = &$this->_ipbx->get_application('queue')) === false
		|| ($queue_qos = $appqueue->get_qos()) === false)
			return(false);
		$stats_queue->set_data_custom('qos',$queue_qos);
		
		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];
		
		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = $this->get_listmonth_for_interval($dbeg,$dend);
		
		while($listqueue)
		{
			$queue = array_shift($listqueue);			
			$queuekey = $queue['key'][0];
			$listmonth = $data_listmonth;
			while($listmonth)
			{
				$key = array_shift($listmonth);
				$key = $key['key'];
				$year = substr($key,0,4);
				$month = substr($key,4,2);
				$listday = $this->get_listday_for_month($year,$month);
				while($listday)
				{
					$day = array_shift($listday);
					if (strlen(($day = $day['key'])) === 1)
						$day = '0'.$day;
					if (isset($full_interval[$year.$month.$day]) === false)
						continue;
					$this->_interval_process = $full_interval[$year.$month.$day];
					$stats_queue->parse_log($queuekey,$day);
				}
				$this->save_cache($stats_queue->_result,$queuekey,$year,$month);
				$stats_queue->_result = array();
			}
		}
		unset($stats_queue,$full_interval,$data_listmonth);
		return(true);
	}
	
	private function generate_cache_for_agent($listagent)
	{		
		if(xivo::load_class('xivo_statistics_agent',
			XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics',
			'agent',false) === false)
			die('Can\'t load xivo_statistics_agent object');
				
		$stats_agent = new xivo_statistics_agent(&$this);		
	
		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];
		
		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = $this->get_listmonth_for_interval($dbeg,$dend);
		while($listagent)
		{
			$agent = array_shift($listagent);
			$agent_number = $agent['number'];
			$agent_key = $agent['key'];
			$listmonth = $data_listmonth;
			while($listmonth)
			{
				$key = array_shift($listmonth);
				$key = $key['key'];
				$year = substr($key,0,4);
				$month = substr($key,4,2);
				$listday = $this->get_listday_for_month($year,$month);
				while($listday)
				{
					$day = array_shift($listday);
					if (strlen(($day = $day['key'])) === 1)
						$day = '0'.$day;
					if (isset($full_interval[$year.$month.$day]) === false)
						continue;
					$this->_interval_process = $full_interval[$year.$month.$day];
					$stats_agent->parse_log($agent_key,$day);
				}
				$this->save_cache($stats_agent->_result,$agent_number,$year,$month);
				$stats_agent->_result = array();
			}
		}
		unset($stats_agent,$full_interval,$data_listmonth);
		return(true);
	}
	
	private function generate_cache_for_period($listqueue)
	{
		if(xivo::load_class('xivo_statistics_period',
			XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics',
			'period',false) === false)
			die('Can\'t load xivo_statistics_period object');
		
		$stats_period = new xivo_statistics_period(&$this);
		
		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];
		
		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = $this->get_listmonth_for_interval($dbeg,$dend);
		while($listqueue)
		{
			$queue = array_shift($listqueue);				
			$queuekey = $queue['key'][0];
			$listmonth = $data_listmonth;
			while($listmonth)
			{
				$key = array_shift($listmonth);
				$key = $key['key'];
				$year = substr($key,0,4);
				$month = substr($key,4,2);
				$listday = $this->get_listday_for_month($year,$month);
				while($listday)
				{
					$day = array_shift($listday);
					if (strlen(($day = $day['key'])) === 1)
						$day = '0'.$day;
					if (isset($full_interval[$year.$month.$day]) === false)
						continue;
					$this->_interval_process = $full_interval[$year.$month.$day];
					$stats_period->parse_log($queuekey,$day);
				}
				$this->save_cache($stats_period->_result,$queuekey,$year,$month,'period');
				$stats_period->_result = array();
			}
		}
		unset($stats_period,$full_interval,$data_listmonth);
		return(true);
	}

	public function has_cache_type($key=null,$type=null)
	{
		if (is_null($type) === true)
			$type = $this->_type;
			
		$basecache = DWHO_PATH_CACHE_STATS.DWHO_SEP_DIR.'cache';
		
		$dir = $basecache.DWHO_SEP_DIR.
					$this->get_idconf().DWHO_SEP_DIR.
					$type;
		
		if (is_null($key) === false)
			$dir .= DWHO_SEP_DIR.$key;
		
		if (dwho_file::is_d_r($dir) === false)
			return(false);
			
		return(true);
	}

	public function get_cache($key,$year,$month,$type=null,$idconf=null)
	{
		if (is_null($type) === true)
			$type = $this->_type;	
		if (is_null($idconf) === true)
			$idconf = $this->get_idconf();
		
		if (($dir = $this->build_dir_for_cache($idconf,$type,$key)) === false)
			return(false);
		
		$file = $dir.DWHO_SEP_DIR.$year.$month.'.db';		
		
		if (dwho_file::is_r($file) === false
		|| ($infos = dwho_file::get_info($file)) === false
		|| ($f = fopen($file,'rb')) === false)
			return(false);
		
		$data = '';
		while(feof($f) === false)
		    $data .= fread($f,$infos['size']);
		fclose($f);

		$res = json_decode($data,true);

		return($res);
	}

	public function get_cache_day($key,$year,$month,$day,$type=null,$idconf=null)
	{
		if (($arr = $this-> get_cache($key,$year,$month,$type,$idconf)) === false
		|| isset($arr[$day]) === false)
			return(false);

		return($arr[$day]);
	}
	
	public function get_list_file_for_cache($idconf=null,$type=null,$key=null)
	{
		if (($dir = $this->build_dir_for_cache($idconf,$type,$key)) === false
		|| ($r = dwho_file::read_d($dir,'',FILE_R_OK)) === false)
		    return(false);
		
	    sort($r);
		return($r);
	}
	
	private function build_dir_for_cache($idconf=null,$type=null,$key=null,$cachedir=null)
	{		
		if (is_null($cachedir) === true)
			$cachedir = DWHO_PATH_CACHE_STATS;
			
		$dir = dwho_file::joinpath($cachedir,'cache');
		
		if (is_null($idconf) === false)
			$dir .= DWHO_SEP_DIR.$idconf;
				
		if (is_null($type) === false)
			$dir .= DWHO_SEP_DIR.$type;
			
		if (is_null($key) === false)
			$dir .= DWHO_SEP_DIR.$key;
			
		if (dwho_file::is_d_rx($dir) === false)
			return(false);
			
		return($dir);
	}
	
	private function init_path_cache($idconf=null,$type=null,$key=null,$cachedir=null)
	{
		if (is_null($type) === true)
			$type = $this->_type;
		
		if (is_null($idconf) === true)
			$idconf = $this->get_idconf();
		
		$listdir = array('cache',$idconf,$type);
		
		if(is_null($key) === false)
			array_push($listdir,$key);
			
		if (is_null($cachedir) === true)
			$cachedir = DWHO_PATH_CACHE_STATS;
		
		while($listdir)
		{
			$dir_process = array_shift($listdir);
			$cachedir .= DWHO_SEP_DIR.$dir_process;
			if (dwho_file::is_d_w($cachedir) === false
			&& mkdir($cachedir,0775,true) === false)
				$this->push_error('ERR: Can\'t create dir: '.$cachedir);
		}
		
		if (dwho_file::is_d_w($cachedir) === false)
			$this->push_error('ERR: Not valid cache dir: '.$cachedir);
			
		if ($this->has_error() === true)
			die(var_dump($this->get_error()));
			
		$this->_cache_path = $cachedir;
		return(true);
	}

	private function save_cache($data,$key,$year,$month,$type=null,$erase=false,$cachedir=null)
	{
		if (is_null($type) === true)
			$type = $this->_type;
			
		$this->init_path_cache($this->get_idconf(),$type,$key,$cachedir);
			
		$dir = $this->build_dir_for_cache($this->get_idconf(),$type,$key,$cachedir);
			
		if (dwho_file::is_d_w($dir) === false)
			$this->push_error('ERR: Can\'t create cache file in: '.$dir);
		
		$file = $dir.DWHO_SEP_DIR.$year.$month.'.db';
			
		if (dwho_file::is_f($file) === false
		&& touch($file) === false)
			$this->push_error('ERR: Can\'t create file: '.$file);
			
		if ($this->has_error() === true)
			die(var_dump($this->get_error()));
		
		if (($rs = file_put_contents($file, json_encode($data),LOCK_EX)) === false)
			$rs = 'error';
			
		print("save data to $file => $rs \n");
		
		#return(dwho_file::put_contents($file,json_encode($data)));
		return($rs);
	}
	
	private function update_date_genercache()
	{
		if (($appstats_conf = &$this->_xobj->get_application('stats_conf')) === false)
			return(false);
		$appstats_conf->update_date_genercache($this->get_idconf());
	}
	
	public function update_cache($idconf,$type,$object,$erase=false,$dbeg=null,$dend=null)
	{		
		$keyfile = $object['key'][0];
		$idtype = $object['id'];
				
		$this->_type = $type;
		$this->_objectkey = $idtype;
		$this->init_path_cache($idconf,$type,$keyfile);
		$conf = $this->get_conf();
	
		if (($conf['dendcache']) == 0)
		{
			$confyear = date('Y');
			$confmonth = date('m');
			$indexconf = (int) ($confyear.$confmonth);
		}
		else 
		{
			$indexconf = (int) str_replace('-','',$conf['dendcache']);
			$confyear = substr($indexconf,0,4);
			$confmonth = substr($indexconf,4,2);
		}
		
		$dirkey = $this->build_dir_for_cache($idconf,$type,$keyfile);
		
		if (is_null($dbeg) === true
		&& is_null($dend) === true)
		{
			$dbegcache = strtotime($conf['dbegcache'].'-01');
			$lastday = date('d',$this->get_lastday_for_month($confyear,$confmonth));
			$dendcache = strtotime("$confyear-$confmonth-$lastday");
		}
		elseif (is_null($dbeg) === false
		&& is_null($dend) === true)
		{
			$dbegcache = $this->all_to_unixtime($dbeg);
			$dendcache = time();
		}
		elseif (is_null($dbeg) === false
		&& is_null($dend) === false)
		{
			$dbegcache = $this->all_to_unixtime($dbeg);
			$dendcache = $this->all_to_unixtime($dend);
		}
		else
			return(false);
		
		$listconfmonth = $this->get_listmonth_for_interval($dbegcache,$dendcache);
		
		while($listconfmonth)
		{
			$confmonth = array_shift($listconfmonth);
			$index = (int) $confmonth['key'];			
			$filemonth = $dirkey.DWHO_SEP_DIR.$index.'.db';
			$year = substr($index,0,4);
			$month = substr($index,4,2);
			$report = "-- ".$conf['name']." -- $type -- $keyfile -- $year-$month";
			
			$lastdayforcache = $this->get_lastday_for_cache_file($idconf,$type,$keyfile,$year,$month);
			// get lastday for month from conf available day.
			if (($listday = $this->get_listday_for_month($year,$month)) === false
			|| count($listday) === 0
			|| is_array(($dayfm = array_pop($listday))) === false)
				continue;
				
			$lastdayformonth = (string) $dayfm['key'];
			
			$dbeg = mktime(0,0,1,$month,1,$year);
			$dend = mktime(23,59,59,$month,$lastdayformonth,$year);
			
			if ($erase !== false)
			{
				echo "$report -- mode erase enabled >> creation required \n";
				echo "$report >> create in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$idtype);
				while (!$rs)
					usleep(1);
				echo "$report >> creation finished \n";
			}
			
			if (dwho_file::is_f_r($filemonth) === false)
			{
				echo "$report -- not exist >> creation required \n";
				echo "$report >> create in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$idtype);
				while (!$rs)
					usleep(1);
			}
			else
			{
				echo "$report -- already exist >> check if is up to date \n";
				
				if($lastdayformonth === $lastdayforcache)
				{
					echo "month $index is up to date \n";
					continue;
				}
				echo "month $index is not up to date \n";
				echo "$report >> update in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$idtype);
				while (!$rs)
					usleep(1);
			}
		}
		return(true);
	}
	
	public function update_cache_graphic($idconf,$type,$object,$erase=false,$dbeg=null,$dend=null)
	{		
		require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'pchart.inc'));
		
		$pChart = new pChart;
		var_dump($pChart);
		
		$keyfile = $object['key'][0];
		$idtype = $object['id'];
				
		$this->_type = $type;
		$this->_objectkey = $idtype;
		$this->init_path_cache($idconf,$type,$keyfile,DWHO_PATH_CACHE_PCHART);
		$dirkey = $this->build_dir_for_cache($idconf,$type,$keyfile,DWHO_PATH_CACHE_PCHART);
		$conf = $this->get_conf();
		
		var_dump($dirkey);
	
		if (($conf['dendcache']) == 0)
		{
			$confyear = date('Y');
			$confmonth = date('m');
			$indexconf = (int) ($confyear.$confmonth);
		}
		else 
		{
			$indexconf = (int) str_replace('-','',$conf['dendcache']);
			$confyear = substr($indexconf,0,4);
			$confmonth = substr($indexconf,4,2);
		}		
		
		if (is_null($dbeg) === true
		&& is_null($dend) === true)
		{
			$dbegcache = strtotime($conf['dbegcache'].'-01');
			$lastday = date('d',$this->get_lastday_for_month($confyear,$confmonth));
			$dendcache = strtotime("$confyear-$confmonth-$lastday");
		}
		elseif (is_null($dbeg) === false
		&& is_null($dend) === true)
		{
			$dbegcache = $this->all_to_unixtime($dbeg);
			$dendcache = time();
		}
		elseif (is_null($dbeg) === false
		&& is_null($dend) === false)
		{
			$dbegcache = $this->all_to_unixtime($dbeg);
			$dendcache = $this->all_to_unixtime($dend);
		}
		else
			return(false);
		
		$listconfmonth = $this->get_listmonth_for_interval($dbegcache,$dendcache);
		
		while($listconfmonth)
		{
			$confmonth = array_shift($listconfmonth);
			$index = (int) $confmonth['key'];			
			$filemonth = $dirkey.DWHO_SEP_DIR.$index.'.db';
			$year = substr($index,0,4);
			$month = substr($index,4,2);
			$report = "-- ".$conf['name']." -- $type -- $keyfile -- $year-$month";
			
			var_dump($report);
			
			/*
			$lastdayforcache = $this->get_lastday_for_cache_file($idconf,$type,$keyfile,$year,$month);
			// get lastday for month from conf available day.
			if (($listday = $this->get_listday_for_month($year,$month)) === false
			|| count($listday) === 0
			|| is_array(($dayfm = array_pop($listday))) === false)
				continue;
				
			$lastdayformonth = (string) $dayfm['key'];
			
			$dbeg = mktime(0,0,1,$month,1,$year);
			$dend = mktime(23,59,59,$month,$lastdayformonth,$year);
			
			if ($erase !== false)
			{
				echo "$report -- mode erase enabled >> creation required \n";
				echo "$report >> create in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$idtype);
				while (!$rs)
					usleep(1);
				echo "$report >> creation finished \n";
			}
			
			if (dwho_file::is_f_r($filemonth) === false)
			{
				echo "$report -- not exist >> creation required \n";
				echo "$report >> create in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$idtype);
				while (!$rs)
					usleep(1);
			}
			else
			{
				echo "$report -- already exist >> check if is up to date \n";
				
				if($lastdayformonth === $lastdayforcache)
				{
					echo "month $index is up to date \n";
					continue;
				}
				echo "month $index is not up to date \n";
				echo "$report >> update in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$idtype);
				while (!$rs)
					usleep(1);
			}
			*/
		}
		return(true);
	}
	
	private function get_lastday_for_cache_file($idconf,$type,$key,$year,$month)
	{
		if (($listday = $this->get_cache($key,$year,$month,$type,$idconf)) === false
		|| is_array($listday) === false
		|| count($listday) === 0)
			return(false);
			
		return((string) array_pop(array_keys($listday)));
	}
	
	public function db_eval_data($type,$value,$event,$field=null,$addwhere=null)
	{
		$this->push_debug("db_eval_data()",array($type,$value,$event,$field,$addwhere));
		if (($appqueue_log = &$this->_ipbx->get_application('queue_log')) === false)
			return(false);
		
		$interval = $this->_interval_process;
		
		if ((isset($interval['beg']) === false
			|| empty($interval['beg']) === true
			|| strlen($interval['beg']) !== 10)
		|| (isset($interval['end']) === false
			|| empty($interval['end']) === true
			|| strlen($interval['end']) !== 10))
			return(false);
				
		$timestamp = array();
		$timestamp['beg'] = date('Y-m-d H:i:s',$interval['beg']);
		$timestamp['end'] = date('Y-m-d H:i:s',$interval['end']);
			
		switch ($type)
		{
			case 'count':
				return($appqueue_log->count_queue_logs_stats($this->_type,$value,$event,$timestamp,$addwhere));
				break;
			case 'sum':
				return($appqueue_log->sum_queue_logs_stats($this->_type,$value,$event,$field,$timestamp,$addwhere));
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

	private function eval_during_time($key,$eventprocess,$eventstart,$eventend,$time)
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
		
		$timeprocess = $this->all_to_unixtime($timearr[0]);
		
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

	public function push_error($error, $key=null)
	{
		if (is_array($error) === true)
			$this->_error = array_merge($this->_error, $error);
		elseif (is_null($key) === false
		&& is_scalar($error) === true)
			$this->_error[$key] = $error;
		elseif(is_null($key) === true
		&& is_scalar($error) === true)
			array_push($this->_error, $error);
		
		return(false);
	}

	public function get_error()
	{
		return($this->_error);
	}

	public function has_error() 
	{
		if (empty($this->_error) === true)
			return(false);

		return(true);
	}
	
	public function push_debug($key,$var=null)
	{
		if (isset($this->_debug[$key]) === true)
			$this->_debug[$key.'{'.uniqid().'}'] = $var;
		else
			$this->_debug[$key] = $var;
	}

	public function get_debug() 
	{
		return($this->_debug);
	}
	
}

?>
