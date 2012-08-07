<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
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

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'date.inc'));

class xivo_stats_lib
{
	private	$_sts 				= false;
	public	$_xobj 				= false;
	private	$_cache_path 		= '';
	private	$_regex		 		= array('datetime'	=> '/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/',
										'unixtime'	=> '/^(\d{10})$/',
										'date'		=> '/^(\d{4})-(\d{2})-(\d{2})$/',
										'time'		=> '/^(\d{2}):(\d{2}):(\d{2})$/');
	private	$_listday			= array('monday','tuesday','wednesday','thursday','friday','saturday','sunday');
	private	$_listmonth			= array('january','february','march','april','may','june','july','august','september','october','november','december');
	private	$_listaxetype		= array('type','day','week','month','year');
	private	$_listtype			= array('agent',);
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
	public 	$_type		 		= '';

	public function __construct()
	{
		if(dwho_issa('_statsconf',$_SESSION) === false)
			$_SESSION['_statsconf'] = array();

		$this->_sts = &dwho_gct::get('xivo_stats');
		$this->_xobj = &dwho_gct::get('xivo_object');
		$this->_statsconfsess = &$_SESSION['_statsconf'];
		$this->_statsconfsess['_date_process'] = null;

		if(($this->_queue_log_conf = dwho_gat::load_get('queue_log',DWHO_PATH_CONF)) === false)
			trigger_error('Failed to load queuelog configuration',E_USER_ERROR);
	}

	public function load_component()
	{
		if ($this->load_conf() === false)
			return(false);

		return(true);
	}

	private function load_conf()
	{
		if (($idconf = $this->get_idconf()) === false)
			return(false);

		$appstats_conf = $this->_xobj->get_application('stats_conf');

		$_USR = &dwho_gct::get('_USR');

		$userid = false;
		if (isset($_USR->_info['meta']) === true
		&& $_USR->_info['meta'] === 'admin')
			$userid = $_USR->_info['id'];

		if (($conf = $appstats_conf->get($idconf,null,$userid)) === false
		|| is_array($conf) === false
		|| isset($conf['stats_conf']) === false)
			return(false);

		return($this->init_conf($conf));
	}

	private function init_cal($conf)
	{
		$dbeg = dwho_date::all_to_unixtime($conf['dbegcache']);
		$dend = dwho_date::all_to_unixtime($conf['dendcache']);

		$year = date('Y',$dend);
		$month = date('m',$dend);
		// Init last day for the month
		$dend = dwho_date::get_lastday_for_month($year,$month);

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
		$this->_conf = $conf;
		$this->_conf['stats_conf'] = $conf['stats_conf'];
		$stats_conf = $conf['stats_conf'];

		if (empty($stats_conf['timezone']) === false)
			date_default_timezone_set($stats_conf['timezone']);

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

	public function get_dip_hour()
	{
		if(($conf = $this->get_conf()) === false)
			return(false);

		$hour_start = explode(':',$conf['hour_start']);
		$hour_end = explode(':',$conf['hour_end']);
		$dip_hour = array();
		$dip_hour['beg'] = (int) $hour_start[0];
		$dip_hour['end'] = (int) $hour_end[0];
		return($dip_hour);
	}

	public function get_valid_list_day()
	{
		if(($conf = $this->get_conf()) === false)
			return(false);

		$workweek = $conf['workweek'];
		$rs = array();
		if ($workweek['sunday'])
			$rs[] = 0;
		if ($workweek['monday'])
			$rs[] = 1;
		if ($workweek['tuesday'])
			$rs[] = 2;
		if ($workweek['wednesday'])
			$rs[] = 3;
		if ($workweek['thursday'])
			$rs[] = 4;
		if ($workweek['friday'])
			$rs[] = 5;
		if ($workweek['saturday'])
			$rs[] = 6;
		return($rs);
	}

	public function get_conf()
	{
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
		$loadconf['timezone'] = $statsconf['timezone'];
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
		$this->_type = $type;
	}

	public function set_axetype($axetype)
	{
		if (in_array($axetype,$this->_listaxetype) === false)
			return(false);

		$this->_axetype = $axetype;
		$this->_statsconfsess['_axetype'] = $this->_axetype;
	}

	public function get_objectkey()
	{
		return($this->_objectkey);
	}

	public function get_object_process()
	{
		$list = $this->get_list_by_type($this->_type);
		$id_process = 0;
		if (preg_match('/[a-z]-([0-9]+)/', $this->_objectkey, $out) === 1)
			$id_process = (int) $out[1];
		$nb = count($list);
		for($i=0; $i<$nb; $i++)
		{
			$ref = &$list[$i];
			if ($ref['id'] == $id_process)
				return($ref);
		}
		return(false);
	}

	public function get_axetype()
	{
		return($this->_axetype);
	}

	public function get_list_axetype()
	{
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

	public function build_full_date_interval($dbeg,$dend)
	{
		$hour_start = $hour_end = null;

		if (($conf = $this->get_conf()) !== false
		&& isset($conf['hour_start']) === true
		&& isset($conf['hour_end']) === true)
		{
			$hour_start = $conf['hour_start'];
			$hour_end = $conf['hour_end'];
		}

		return(dwho_date::build_full_date_interval($dbeg,$dend,$hour_start,$hour_end,$conf['workweek']));
	}

	public function get_datecal()
	{
		return($this->_date_process);
	}

	public function set_datecal($arr)
	{
		if(($conf = $this->get_conf()) !== false)
			$this->init_cal($conf);

		$infocal = $this->_statsconfsess['_date_process'];

		$axtetype = $this->get_axetype();

		$infocal = dwho_date::set_infocal($this->get_axetype(),$arr);

		$this->_date_process = $infocal;
		$this->_statsconfsess['_date_process'] = $infocal;
	}

	public function get_listhour()
	{
		if(($conf = $this->get_conf()) === false)
			return(false);

		$hour_start = explode(':',$conf['hour_start']);
		$hour_end = explode(':',$conf['hour_end']);

		return(dwho_date::get_listhour($hour_start[0],$hour_end[0]));
	}

	public function get_listday_for_week()
	{
		if(($conf = $this->get_conf()) === false)
			return(false);

		return(dwho_date::get_listday_for_week($conf['workweek']));
	}

	public function get_listday_for_month($year,$month)
	{
		if(($conf = $this->get_conf()) === false)
			return(false);

		return(dwho_date::get_listday_for_month($year,$month,$conf['workweek']));
	}

	private function normalize_agent($arr)
	{
		if (is_array($arr) === false
		|| isset($arr['id']) === false
		|| isset($arr['fullname']) === false
		|| isset($arr['identity']) === false
		|| isset($arr['number']) === false
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
		$rs['key'] = 'agent/'.$arr['number'];
		$rs['keyfile'] = 'agent-'.$arr['id'];
		$tmp = array();
		array_push($tmp, $arr['number']);
		array_push($tmp,'agent/'.$arr['number']);
		array_push($tmp,'Agent/'.$arr['number']);
		$rs['keydata'] = $tmp;
		$rs['type'] = 'agent';

		return($rs);
	}

	private function normalize_queue($arr)
	{
		if (is_array($arr) === false
		|| isset($arr['id']) === false
		|| isset($arr['name']) === false
		|| isset($arr['number']) === false
		|| isset($arr['stats_qos']) === false)
			return(false);

		$rs = array();
		$rs['id'] = (int) $arr['id'];
		$rs['name'] = $arr['name'];
		$rs['number'] = $arr['number'];
		$rs['keydata'] = array($arr['name']);
		$rs['qos'] = $arr['stats_qos'];
		$rs['identity'] =  $arr['displayname'];
		$rs['key'] = 'queue/'.$arr['name'];
		$rs['keyfile'] = 'queue-'.$arr['id'];
		$rs['type'] = 'queue';
		return($rs);
	}

	public function get_list_by_type($type)
	{
		$rs = array();
		switch ($type)
		{
			case 'agent':
				$agents = array_values($this->_conf['agent']);
				$nb_agents = count($agents);
				for($i=0; $i<$nb_agents; $i++)
				{
					$agent = &$agents[$i];
					array_push($rs, $this->normalize_agent($agent));
				}
				break;
			case 'period':
			case 'queue':
				$queues = array_values($this->_conf['queue']);
				$nb_queues = count($queues);
				for($i=0; $i<$nb_queues; $i++)
				{
					$queue = &$queues[$i];
					array_push($rs, $this->normalize_queue($queue));
				}
				break;
			default:
				$rs = false;
		}
		return($rs);
	}

	public function get_object_list($type=null)
	{
		if (!$type)
			$type = $this->_type;
		$rs = array();
		switch ($type)
		{
			case 'agent':
				$rs = $this->get_list_by_type('agent');
				break;
			case 'queue':
			case 'period':
				$rs = $this->get_list_by_type('queue');
				break;
			default:
				$rs = false;
		}
		return($rs);
	}

}

?>
