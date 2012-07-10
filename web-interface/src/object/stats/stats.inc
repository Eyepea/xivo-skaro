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
	private	$_listtype			= array('queue','agent','period',); # 'incall'
	private	$_listconftype		= array('queue','group','agent','user','incall');
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

		return(dwho_date::build_full_date_interval($dbeg,$dend,$hour_start,$hour_end));
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
		|| isset($arr['stats_qos']) === false)
			return(false);

		$rs = array();
		$rs['id'] = (int) $arr['id'];
		$rs['name'] = $arr['name'];
		$rs['number'] = $arr['number'];
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
		if (($list = $this->get_list_by_type('incall')) === false)
			return(false);

		#asort($list);
		return($list);
	}

	public function get_queue_list()
	{
		if (($list = $this->get_list_by_type('queue')) === false)
			return(false);

		#asort($list);
		return($list);
	}

	public function get_agent_list()
	{
		if (($list = $this->get_list_by_type('agent')) === false)
			return(false);

		#asort($list);
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
		$this->_sts->load_ressource('incall');
		$stats_incall = new stats_ressource_incall(&$this);

		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];

		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = dwho_date::get_listmonth_for_interval($dbeg,$dend);

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
		$this->_sts->load_ressource('queue');
		$stats_queue = new stats_ressource_queue(&$this);

		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];

		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = dwho_date::get_listmonth_for_interval($dbeg,$dend);

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
		$this->_sts->load_ressource('agent');
		$stats_agent = new stats_ressource_agent(&$this);

		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];

		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = dwho_date::get_listmonth_for_interval($dbeg,$dend);

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
		$this->_sts->load_ressource('period');
		$stats_period = new stats_ressource_period(&$this);

		$dbeg = $this->_interval['beg'];
		$dend = $this->_interval['end'];

		$full_interval = $this->build_full_date_interval($dbeg,$dend);
		$data_listmonth = dwho_date::get_listmonth_for_interval($dbeg,$dend);

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

		while(($dir_process = array_shift($listdir)))
		{
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
			$lastday = date('d',dwho_date::get_lastday_for_month($confyear,$confmonth));
			$dendcache = strtotime("$confyear-$confmonth-$lastday");
		}
		elseif (is_null($dbeg) === false
		&& is_null($dend) === true)
		{
			$dbegcache = dwho_date::all_to_unixtime($dbeg);
			$dendcache = time();
		}
		elseif (is_null($dbeg) === false
		&& is_null($dend) === false)
		{
			$dbegcache = dwho_date::all_to_unixtime($dbeg);
			$dendcache = dwho_date::all_to_unixtime($dend);
		}
		else
			return(false);

		$listconfmonth = dwho_date::get_listmonth_for_interval($dbegcache,$dendcache);

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

				if(date('Ym') !== ($year.$month)
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
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($modcel = &$_SRE->get_module('ipbx','cel')) === false)
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
				return($modcel->count_stats($this->_type,$value,$event,$datetime,$addwhere));
				break;
			case 'sum':
				return($modcel->sum_stats($this->_type,$value,$event,$field,$datetime,$addwhere));
				break;
			default:
				return(false);
		}
	}

	public function get_data_queue_log($type,$value,$event,$field=null,$addwhere=null)
	{
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($modqlog = &$_SRE->get_module('ipbx','queue_log')) === false)
			return(false);

		$interval = $this->_interval_process;

		if ((isset($interval['beg']) === false
			|| empty($interval['beg']) === true
			|| strlen($interval['beg']) !== 10)
		|| (isset($interval['end']) === false
			|| empty($interval['end']) === true
			|| strlen($interval['end']) !== 10))
			return(false);

		/*
		 * FIXME do not necessary
		 *
		if (preg_match('/^([+-]{1})([0-9]{4})|(EST)$/',strftime('%z'),$out) !== 0)
		{
			$val = (int) substr($out[2],0 ,2);
			$unit = ($val > 1) ? 'hours' : 'hour';
			$operator = ($out[1] === '+') ? '-' : '+';
			$interval['beg'] = strtotime("$operator $val $unit",$interval['beg']);
			$interval['end'] = strtotime("$operator $val $unit",$interval['end']);
		}
		*/

		$datetime = array();
		$datetime['beg'] = date('Y-m-d H:i:s',$interval['beg']);
		$datetime['end'] = date('Y-m-d H:i:s',$interval['end']);

		switch ($type)
		{
			case 'count':
				return($modqlog->count_stats($this->_type,$value,$event,$datetime,$addwhere));
				break;
			case 'sum':
				return($modqlog->get_sum_stats($this->_type,$value,$event,$field,$datetime,$addwhere));
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

	public function eval_pos_data_queue_log_conf($queue_log_entry,$event,$type)
	{
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

}

?>
