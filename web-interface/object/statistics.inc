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
	private	$_listtype			= array('queue','agent','period','incall');
	private	$_listconftype		= array('queue','group','agent','user','incall');
	private	$_listmethod		= array('DB','PHP');
	public 	$_debug				= array();
	public 	$_error				= array();
	public 	$_queue_log_conf	= array();
	public 	$_queue_log 		= array();
	public 	$_conf		 		= array('stats_conf' => array(),
										'queue'		=> array(),
										'group'		=> array(),
										'agent'		=> array(),
										'user'		=> array(),
										'incall'	=> array());
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

		$year = date('Y',$dend);
		$month = date('m',$dend);
		// Init last day for the month
		$dend = $this->get_lastday_for_month($year,$month);

		if ($dend > time())
		    $dend = time();

		if (isset($conf['default_delta']) === true)
		{
		    // Choose this day because interval is set to 0
			if ($conf['default_delta'] == 0)
				$dbeg = $dend = time();
			else
				$dbeg = strtotime($conf['default_delta'], $dend);
		}
		// initialize dbeg at -1 day by default
		else
			$dbeg = strtotime('-1 day', $dend);

		$conf = $this->_conf['stats_conf'];

		$i=0;
		while ($i<6)
        {
            $dayname = strtolower(date('l',$dbeg));
            if (isset($conf[$dayname]) === true
            && $conf[$dayname] === true)
                break;
            $dbeg = strtotime('-1 day',$dbeg);
            $i++;
        }

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
		$this->_conf['stats_conf'] = $conf['stats_conf'];
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

	public function get_full_conf()
	{
		if (($stats_conf = $this->get_conf()) === false)
			return(false);

		$conf = $this->_conf;
		$conf['stats_conf'] = $stats_conf;
		return($conf);
	}

	public function get_conf()
	{
		$this->push_debug("get_conf()");
		if (empty($this->_conf['stats_conf']) === true)
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
		$loadconf['default_delta'] = $statsconf['default_delta'];
		$loadconf['dcreate'] =  $statsconf['dcreate'];
		$loadconf['dupdate'] =  $statsconf['dupdate'];
		$loadconf['dgenercache'] =  $statsconf['dgenercache'];
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
			$tmp['identity'] = dwho_i18n::babelfish($dayname);
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
			$tmp['identity'] = dwho_i18n::babelfish($this->_listmonth[intval($month)-1]);
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

	private function normalize_incall($arr,$type)
	{
		if (is_array($arr) === false
		|| isset($arr['id']) === false
		|| isset($arr['exten']) === false
		|| isset($arr['identity']) === false
		|| isset($arr['context']) === false
		|| isset($arr['commented']) === false)
			return(false);

		if (((bool) $arr['commented']) === true)
			return(false);

		$rs = array();
		$rs['id'] = (int) $arr['id'];
		// clean identity context
		$rs['identity'] =  preg_replace('/@[a-z-_]+/i','',$arr['identity']);
		$rs['context'] = $arr['context'];

		switch ($type)
		{
			case 'incall':
				$rs['key'] = $arr['exten'];
				$rs['keyfile'] = 'incall-'.$arr['id'];
				$tmp = array();
				array_push($tmp, $arr['exten']);
				$rs['keydata'] = $tmp;
				$rs['type'] = 'incall';
				break;
			default:
				return(false);
		}
		return($rs);
	}

	private function normalize_agent($arr,$type)
	{
		if (is_array($arr) === false
		|| isset($arr['id']) === false
		|| isset($arr['fullname']) === false
		|| isset($arr['identity']) === false
		|| isset($arr['number']) === false
		|| isset($arr['context']) === false
		|| isset($arr['commented']) === false)
			return(false);

		if (((bool) $arr['commented']) === true)
			return(false);

		$rs = array();
		$rs['id'] = (int) $arr['id'];
		$rs['fullname'] = $arr['fullname'];
		// clean identity context
		$rs['identity'] =  preg_replace('/@[a-z-_]+/i','',$arr['identity']);
		$rs['number'] = $arr['number'];
		$rs['context'] = $arr['context'];

		switch ($type)
		{
			case 'user':
				if (isset($arr['protocol']) === false)
					return(false);
				$rs['key'] = $arr['protocol'].'/'.$arr['name'];
				$rs['keyfile'] = 'user-'.$arr['id'];
				$tmp = array();
				array_push($tmp, $arr['protocol'].'/'.$arr['name']);
				array_push($tmp, strtoupper($arr['protocol']).'/'.$arr['name']);
				$rs['keydata'] = $tmp;
				$rs['type'] = 'user';
				break;
			case 'agent':
				$rs['key'] = 'agent/'.$arr['number'];
				$rs['keyfile'] = 'agent-'.$arr['id'];
				$tmp = array();
				array_push($tmp, $arr['number']);
				array_push($tmp,'agent/'.$arr['number']);
				array_push($tmp,'Agent/'.$arr['number']);
				$rs['keydata'] = $tmp;
				$rs['type'] = 'agent';
				break;
			default:
				return(false);
		}
		return($rs);
	}

	private function normalize_queue($arr,$type)
	{
		if (is_array($arr) === false
		|| isset($arr['id']) === false
		|| isset($arr['name']) === false
		|| isset($arr['number']) === false
		|| isset($arr['context']) === false
		|| isset($arr['stats_qos']) === false)
			return(false);

		$rs = array();
		$rs['id'] = (int) $arr['id'];
		$rs['name'] = $arr['name'];
		$rs['number'] = $arr['number'];
		$rs['context'] = $arr['context'];
		$rs['keydata'] = array($arr['name']);
		$rs['qos'] = $arr['stats_qos'];

		switch ($type)
		{
			case 'queue':
				$rs['identity'] =  $arr['displayname'];
				$rs['key'] = 'queue/'.$arr['name'];
				$rs['keyfile'] = 'queue-'.$arr['id'];
				$rs['type'] = 'queue';
				break;
			case 'group':
				if (isset($arr['displayname']) === false)
				    $rs['identity'] =  $arr['name'];
				else
				    $rs['identity'] =  $arr['displayname'];
				if (isset($arr['group_qos']) === false)
					return(false);
				$rs['key'] = 'group/'.$arr['number'];
				$rs['keyfile'] = 'group-'.$arr['id'];
				$rs['type'] = 'group';
				break;
			default:
				return(false);
		}
		return($rs);
	}

	public function get_list_by_type($type)
	{
		$this->push_debug("get_list_by_type()",array($type));
		switch ($type)
		{
			case 'incall':
				$ls_incall = array();
				if ($this->_conf['incall'] === false)
					return(false);

				if (empty($this->_objectkey) === true
				|| $this->_objectkey === 0
				|| $this->_objectkey === null)
				{
					if($this->_conf['incall'] !== false)
					{
						$incall = array_values($this->_conf['incall']);
						$nb = count($incall);
						for($i=0;$i<$nb;$i++)
						{
							$ref = &$incall[$i];
							if (($rs = $this->normalize_incall($ref,'incall')) === false)
								continue;
							array_push($ls_incall, $rs);
						}
					}
				}
				elseif (empty($this->_objectkey) === false
				&& preg_match('/([a-z]+)-([0-9]+)/',$this->_objectkey,$out) === 1)
				{
					$key = $out[1];
					$id = $out[2];

					switch ($key)
					{
						case 'incall':
							if ($this->_conf['incall'] !== false)
							{
								$listincall = $this->_conf['incall'];
								while ($listincall)
								{
									$incall = array_shift($listincall);
									if ((int) $id === (int) $incall['id']
									&& ($rs = $this->normalize_incall($incall,$key)) !== false)
									{
										array_push($ls_incall, $rs);
										break;
									}
								}
							}
							break;
						default:
							return($ls_incall);
					}
				}
				return($ls_incall);
				break;
			case 'agent':
				$ls_agent = array();

				if ($this->_conf['agent'] === false
				&& $this->_conf['user'] === false)
					return(false);

				if (empty($this->_objectkey) === true
				|| $this->_objectkey === 0
				|| $this->_objectkey === null)
				{
					if($this->_conf['agent'] !== false)
					{
						$agent = array_values($this->_conf['agent']);
						$nb = count($agent);
						for($i=0;$i<$nb;$i++)
						{
							$ref = &$agent[$i];
							if (($rs = $this->normalize_agent($ref,'agent')) === false)
								continue;
							array_push($ls_agent, $rs);
						}
					}

					if ($this->_conf['user'] !== false)
					{
						$user = array_values($this->_conf['user']);
						$nb = count($user);
						for($i=0;$i<$nb;$i++)
						{
							$ref = &$user[$i];
							if (($rs = $this->normalize_agent($ref,'user')) === false)
								continue;
							array_push($ls_agent, $rs);
						}
					}
				}
				elseif (empty($this->_objectkey) === false
				&& preg_match('/([a-z]+)-([0-9]+)/',$this->_objectkey,$out) === 1)
				{
					$key = $out[1];
					$id = $out[2];

					switch ($key)
					{
						case 'user':
							if ($this->_conf['user'] !== false)
							{
								$listuser = $this->_conf['user'];
								while ($listuser)
								{
									$user = array_shift($listuser);
									if ((int) $id === (int) $user['id']
									&& ($rs = $this->normalize_agent($user,$key)) !== false)
									{
										array_push($ls_agent, $rs);
										break;
									}
								}
							}
							break;
						case 'agent':
							if (empty($this->_conf['agent']) === false)
							{
								$listagent = $this->_conf['agent'];
								while ($listagent)
								{
									$agent = array_shift($listagent);
									if ((int) $id === (int) $agent['id']
									&& ($rs = $this->normalize_agent($agent,$key)) !== false)
									{
										array_push($ls_agent, $rs);
										break;
									}
								}
							}
							break;
						default:
							return($ls_agent);
					}
				}
				return($ls_agent);
				break;
			case 'period':
			case 'queue':
				$ls_queue = array();
				if ($this->_conf['queue'] === false
				&& $this->_conf['group'] === false)
					return(false);

				if (empty($this->_objectkey) === true
				|| $this->_objectkey === 0
				|| $this->_objectkey === null)
				{
					if($this->_conf['queue'] !== false)
					{
						$queue = array_values($this->_conf['queue']);
						$nb = count($queue);
						for($i=0;$i<$nb;$i++)
						{
							$ref = &$queue[$i];
							if (($rs = $this->normalize_queue($ref,'queue')) === false)
								continue;
							array_push($ls_queue, $rs);
						}
					}

					if($this->_conf['group'] !== false)
					{
						$group = array_values($this->_conf['group']);
						$nb = count($group);
						for($i=0;$i<$nb;$i++)
						{
							$ref = &$group[$i];
							if (($rs = $this->normalize_queue($ref,'group')) === false)
								continue;
							array_push($ls_queue, $rs);
						}
					}
				}
				elseif (empty($this->_objectkey) === false
				&& preg_match('/([a-z]+)-([0-9]+)/',$this->_objectkey,$out) === 1)
				{
					$key = $out[1];
					$id = $out[2];

					switch ($key)
					{
						case 'queue':
							if ($this->_conf['queue'] !== false)
							{
								$listqueue = $this->_conf['queue'];
								while ($listqueue)
								{
									$queue = array_shift($listqueue);
									if ((int) $id === (int) $queue['id']
									&& ($rs = $this->normalize_queue($queue,$key)) !== false)
									{
										array_push($ls_queue, $rs);
										break;
									}
								}
							}
							break;
						case 'group';
							if ($this->_conf['group'] !== false)
							{
								$listgroup = $this->_conf['group'];
								while ($listgroup)
								{
									$group = array_shift($listgroup);
									if ((int) $id === (int) $group['id']
									&& ($rs = $this->normalize_queue($group,$key)) !== false)
									{
										array_push($ls_queue, $rs);
										break;
									}
								}
							}
							break;
						default:
							return($ls_queue);
					}
				}
				return($ls_queue);
				break;
			default:
				return(false);
		}
	}

	public function has_type()
	{
		$rs = array();
		$nb = count($this->_listconftype);
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$this->_listconftype[$i];
			$rs[$ref] = true;
			if (isset($this->_conf[$ref]) === false
			|| $this->_conf[$ref] === false)
				$rs[$ref] = false;
		}

		return($rs);
	}

	public function get_object_list()
	{
		$this->push_debug("get_object_list()");
		$objrestore = $this->_objectkey;
		$this->_objectkey = 0;
		switch ($this->_type)
		{
			case 'incall':
				$rs = ($this->get_incall_list());
				break;
			case 'agent':
				$rs = ($this->get_agent_list());
				break;
			case 'period':
			case 'queue':
				$rs = ($this->get_queue_list());
				break;
			default:
				$rs = (false);
		}
		$this->_objectkey = $objrestore;
		return($rs);
	}

	public function get_incall_list()
	{
		$this->push_debug("get_incall_list()");
		if (($list = $this->get_list_by_type('incall')) === false)
			return(false);

		asort($list);
		return($list);
	}

	public function get_queue_list()
	{
		$this->push_debug("get_queue_list()");
		if (($list = $this->get_list_by_type('queue')) === false)
			return(false);

		#asort($list);
		return($list);
	}

	public function get_agent_list()
	{
		$this->push_debug("get_agent_list()");
		if (($list = $this->get_list_by_type('agent')) === false)
			return(false);

		asort($list);
		return($list);
	}

	public function generate_cache($idconf,$dbeg,$dend,$type,$idtype=null)
	{
		$this->set_idconf($idconf);
		$this->load_conf();

		if(($conf = $this->get_conf()) === false
		|| ((is_numeric($dbeg) === true
			&& strlen($dbeg) === 10) === false)
		|| ((is_numeric($dend) === true
			&& strlen($dend) === 10) === false))
				dwho_report::push('error','ERR: Invalid data for gener_cache()');

		if(is_null($idtype) === false)
			$this->_objectkey = $idtype;

		if(($list = $this->get_list_by_type($type)) === false
		|| empty($list) === true)
			dwho_report::push('error','ERR: Invalid list for gener_cache()');

		if (dwho_report::has('error') === true)
			die(dwho_report::get_message('error'));

		$this->_interval = array();
		$this->_interval['beg'] = $dbeg;
		$this->_interval['end'] = $dend;

		if (($rs = $this->generate_cache_for_type($type,$list)) === false)
			dwho_report::push('error','ERR: Invalid type for gener_cache()');

		if (dwho_report::has('error') === true)
			die(dwho_report::get_message('error'));

		$this->update_date_genercache();

		return($rs);
	}

	private function generate_cache_for_type($type,$list)
	{
		switch ($type)
		{
			case 'agent':
			case 'user':
				return($this->generate_cache_for_agent($list));
				break;
			case 'queue':
			case 'group':
				return($this->generate_cache_for_queue($list));
				break;
			case 'period':
				return($this->generate_cache_for_period($list));
				break;
			case 'incall':
				return($this->generate_cache_for_incall($list));
				break;
			default:
				return(false);
		}
	}

	private function generate_cache_for_incall($listincall)
	{
		if(xivo::load_class('xivo_statistics_incall',
			XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics',
			'incall',false) === false)
			die('Can\'t load xivo_statistics_incall object');

		$stats_incall = new xivo_statistics_incall(&$this);

		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];

		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = $this->get_listmonth_for_interval($dbeg,$dend);

		while($listincall)
		{
			$incall = array_shift($listincall);
			$keyfile = $incall['keyfile'];
			$keydata = $incall['keydata'];
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
					$stats_incall->parse_log($keydata,$day);
				}
				$this->save_cache($stats_incall->_result,$keyfile,$year,$month);
				$stats_incall->_result = array();
			}
		}
		unset($stats_incall,$full_interval,$data_listmonth);
		return(true);
	}

	private function generate_cache_for_queue($listqueue)
	{
		if(xivo::load_class('xivo_statistics_queue',
			XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics',
			'queue',false) === false)
			die('Can\'t load xivo_statistics_queue object');

		$stats_queue = new xivo_statistics_queue(&$this);

		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];

		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = $this->get_listmonth_for_interval($dbeg,$dend);

		while($listqueue)
		{
			$queue = array_shift($listqueue);
			$keyfile = $queue['keyfile'];
			$keydata = $queue['keydata'];
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
					$stats_queue->parse_log($keydata,$day);
				}
				$this->save_cache($stats_queue->_result,$keyfile,$year,$month);
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
			$keyfile = $agent['keyfile'];
			$keydata = $agent['keydata'];
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
					$stats_agent->parse_log($keydata,$day);
				}
				$this->save_cache($stats_agent->_result,$keyfile,$year,$month);
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
			$keyfile = $queue['keyfile'];
			$keydata = $queue['keydata'];
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
					$stats_period->parse_log($keydata,$day);
				}
				$this->save_cache($stats_period->_result,$keyfile,$year,$month,'period');
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
		if (is_null($type) === true
		&& ($type = $this->_type) === '')
			return(false);

		if (is_null($idconf) === true
		&& ($idconf = $this->get_idconf()) === false)
			return(false);

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
			if (dwho_file::is_d_x($cachedir) === false
			&& mkdir($cachedir,0775,true) === false)
				dwho_report::push('error','ERR: Can\'t create dir: '.$cachedir);
		}

		if (dwho_file::is_d_w($cachedir) === false)
			dwho_report::push('error','ERR: Not writable cache dir: '.$cachedir);

		if (dwho_report::has('error') === true)
			die(dwho_report::get_message('error'));

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
			dwho_report::push('error','ERR: Not writable cache dir: '.$dir);

		$file = $dir.DWHO_SEP_DIR.$year.$month.'.db';

		if (dwho_file::is_f($file) === false
		&& touch($file) === false)
			dwho_report::push('error','ERR: Can\'t create file: '.$file);

		if (dwho_report::has('error') === true)
			die(dwho_report::get_message('error'));

		#if (($rs = file_put_contents($file, json_encode($data),LOCK_EX)) === false)
		if (($rs = dwho_file::put_contents($file,json_encode($data))) === false)
			$rs = 'error';

		#echo "save data to $file => ",dwho_byte_to($rs)," write. \n";

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
		$keyfile = $object['keyfile'];
		$objectkey = $object['keyfile'];

		$this->_type = $type;
		$this->_objectkey = $objectkey;
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
				echo "$report -- mode erase enabled >> creation required: ";
				echo " in progress......... ";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$objectkey);
				while (!$rs)
					usleep(1);
				echo "  finished \n";
			}

			if (dwho_file::is_f_r($filemonth) === false)
			{
				echo "$report -- not exist >> creation required: ";
				echo " in progress......... \n";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$objectkey);
				while (!$rs)
					usleep(1);
				echo "  finished \n";
			}
			else
			{
				echo "$report -- already exist >> check if is up to date: ";

				if(date('m') !== $month
				&& $lastdayformonth === $lastdayforcache)
				{
					echo "Yes. continue.\n";
					continue;
				}
				echo "No.  update in progress......  ";
				$rs = $this->generate_cache($idconf,$dbeg,$dend,$type,$objectkey);
				while (!$rs)
					usleep(1);
				echo "  finished \n";
			}
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

	public function get_data_cel($type,$value,$event,$field=null,$addwhere=null)
	{
		$this->push_debug("get_data_cel()",array($type,$value,$event,$field,$addwhere));

		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($cel = &$_SRE->get_module('ipbx','cel')) === false)
			return(false);

		$interval = $this->_interval_process;

		if ((isset($interval['beg']) === false
			|| empty($interval['beg']) === true
			|| strlen($interval['beg']) !== 10)
		|| (isset($interval['end']) === false
			|| empty($interval['end']) === true
			|| strlen($interval['end']) !== 10))
			return(false);

		$datetime = array();
		$datetime['beg'] = date('Y-m-d H:i:s',$interval['beg']);
		$datetime['end'] = date('Y-m-d H:i:s',$interval['end']);

		switch ($type)
		{
			case 'count':
				return($cel->count_stats($this->_type,$value,$event,$datetime,$addwhere));
				break;
			case 'sum':
				return($cel->sum_stats($this->_type,$value,$event,$field,$datetime,$addwhere));
				break;
			default:
				return(false);
		}
	}

	public function get_data_queue_log($type,$value,$event,$field=null,$addwhere=null)
	{
		$this->push_debug("get_data_queue_log()",array($type,$value,$event,$field,$addwhere));
		if (($modqueue_log = &$this->_ipbx->get_module('queue_log')) === false)
			return(false);

		$interval = $this->_interval_process;

		if ((isset($interval['beg']) === false
			|| empty($interval['beg']) === true
			|| strlen($interval['beg']) !== 10)
		|| (isset($interval['end']) === false
			|| empty($interval['end']) === true
			|| strlen($interval['end']) !== 10))
			return(false);

		$datetime = array();
		$datetime['beg'] = date('Y-m-d H:i:s',$interval['beg']);
		$datetime['end'] = date('Y-m-d H:i:s',$interval['end']);

		switch ($type)
		{
			case 'count':
				return($modqueue_log->count_stats($this->_type,$value,$event,$datetime,$addwhere));
				break;
			case 'sum':
				return($modqueue_log->get_sum_stats($this->_type,$value,$event,$field,$datetime,$addwhere));
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

	public function eval_pos_data_queue_log_conf($queue_log_entry,$event,$type)
	{
		$this->push_debug("eval_field_queue_log_conf()",array($queue_log_entry,$event,$type));
		if (($queue_log_conf = $this->_queue_log_conf) === false)
			return(false);

		if (isset($queue_log_conf[$event]) === false
		|| in_array($type,$queue_log_conf[$event]) === false)
			return(0);

		$pos = 0;
		$nb = count($queue_log_conf[$event]);
		for ($i=0;$i<$nb;$i++)
			if ($queue_log_conf[$event][$i] === $type)
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

	protected function push_debug($key,$var=null)
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
