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

class xivo_stats_ressource_abstract
{

	protected 	$_table		 		= '';
	protected 	$_type		 		= '';
	public	 	$_xs		 		= null;
	public	 	$_sts		 		= null;
	public 		$_data_custom 		= array();
	public 		$_counter	 		= array();
	public		$_result 			= array();
	protected	$_stat_queue_periodic  = null;
	protected	$_stat_call_on_queue   = null;
	protected	$_queuefeatures        = null;
	protected	$_stat_queue           = null;
	protected	$_stat_agent           = null;

	public function __construct(&$_XS)
	{
		$this->_xs = &$_XS;
		$this->_sts = &dwho_gct::get('xivo_stats');
		$_SRE = dwho_gct::get('xivo_service');
		$ipbx = &$_SRE->get('ipbx');
		$this->_stat_queue_periodic = $ipbx->get_module('stat_queue_periodic');
		$this->_stat_call_on_queue = $ipbx->get_module('stat_call_on_queue');
		$this->_queuefeatures = $ipbx->get_module('queuefeatures');
		$this->_stat_queue = $ipbx->get_module('stat_queue');
		$this->_stat_agent = $ipbx->get_module('stat_agent');
	}

	public function set_data_custom($key,$data)
	{
		$this->_data_custom[$key] = $data;
	}

	public function get_list_by_type()
	{
		return($this->_xs->get_list_by_type($this->_type));
	}

	public function get_queue_list()
	{
		return($this->_xs->get_queue_list());
	}

	public function get_agent_list()
	{
		return($this->_xs->get_agent_list());
	}

	public function get_incall_list()
	{
		return($this->_xs->get_incall_list());
	}

	public function eval_count_data($value,$event,$addwhere=null)
	{
		return($this->get_data_queue_log('count',$value,$event,null,$addwhere));
	}

	public function eval_sum_data($value,$event,$field,$addwhere=null)
	{
		return($this->get_data_queue_log('sum',$value,$event,$field,$addwhere));
	}

	private function get_data_queue_log($type,$value,$event,$field=null,$addwhere=null)
	{
		switch ($this->_table)
		{
			case 'cel':
				return($this->_xs->get_data_cel($type,$value,$event,$field,$addwhere));
				break;
			case 'queue_log':
			default:
				return($this->_xs->get_data_queue_log($type,$value,$event,$field,$addwhere));
		}
	}

	public function eval_field_queue_log($event,$type)
	{
		return($this->_xs->eval_field_queue_log($event,$type));
	}

	public function eval_data_queue_log($queue_log_entry,$event,$type)
	{
		return($this->_xs->eval_pos_data_queue_log_conf($queue_log_entry,$event,$type));
	}

	protected function init_result($key)
	{
		$res = &$this->_result;

		if (is_array($key) === true
				&& isset($key['value']) === true)
			$key = $key['value'];

		if (isset($res[$key]) === false)
		{
			$data_process = &$res[$key];
			$data_process = array();

			foreach ($this->_field as $k => $field)
			{
				$data_process[$k] = array();
				if (isset($field['type']))
					$data_process[$k]['type'] = $field['type'];
				$data_process[$k]['result'] = 0;
			}
		}
	}

	private function _build_hour_for_day($key, $time)
	{
		$dip = array();
		$year = date('Y', $time);
		$month = date('m', $time);
		$day = date('d' ,$time);
		$dip['beg'] = mktime($key, 0, 0, $month, $day, $year);
		$dip['end'] = mktime($key+1, 0, -1, $month, $day, $year);
		return $dip;
	}

	public function get_rows()
	{
		$days = $this->full_itl;
		$rs = array();
		foreach ($days as $day => $data)
		{
			$tmp = array();
			$dayname = strtolower( date('l', strtotime($day)) );
			$tmp['identity'] = dwho_i18n::babelfish($dayname);
			$tmp['name'] = $dayname;
			$tmp['key'] = (int) $day;
			$tmp['day'] = date('d', strtotime($day));
			$tmp['month'] = date('m', strtotime($day));
			$tmp['year'] = date('Y', strtotime($day));
			$rs[$day] = $tmp;
		}
		return($rs);
	}

	private function _build_total($queue_id, $dbeg, $dend)
	{
		$year = date('Y', $dend);
		$month = date('m', $dend);
		$day = date('d' ,$dend);
		$interval = array();
		$interval['beg'] = $dbeg;
		$interval['end'] = mktime(23, 59, 59, $month, $day, $year);
		$this->build_stat($queue_id, "total", $interval);
	}

	public function get_data_queue()
	{
		$axetype = $this->_xs->get_axetype();

		if (($itl = $this->_xs->get_datecal()) === false
		|| is_null($itl['dbeg']) === true)
			return(false);

		$dbeg = strtotime($itl['dbeg']);
		$dend = strtotime($itl['dend']);

		$this->_stat_queue_periodic->set_dso_param('hour_itl',$this->_xs->get_dip_hour());
		$this->_stat_queue_periodic->set_dso_param('days',$this->_xs->get_valid_list_day());
		$this->_stat_call_on_queue->set_dso_param('hour_itl',$this->_xs->get_dip_hour());
		$this->_stat_call_on_queue->set_dso_param('days',$this->_xs->get_valid_list_day());

		if (preg_match('/queue-([0-9]+)/', $this->_xs->_objectkey, $out) === 1)
		{
			$queuefeatures_id = (int) $out[1];
			$this->_build_total($queuefeatures_id, $dbeg, $dend);
		}

		switch ($axetype)
		{
			case 'day':
				$key_data = $this->_xs->get_listhour();
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$key = $key_full_data['key'];
					$this->build_stat($queuefeatures_id, $key, $this->_build_hour_for_day($key, $dbeg));
				}
				break;
			case 'week':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $date => $date_itl)
					$this->build_stat($queuefeatures_id, $date, $date_itl);
				break;
			case 'month':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $date => $date_itl)
					$this->build_stat($queuefeatures_id, $date, $date_itl);
				break;
			case 'year':
				$key_data = dwho_date::get_listmonth();
				while ($key_data)
				{
					$key_full_data = array_shift($key_data);
					$key = $key_full_data['key'];
					$dip = array();
					$dip['beg'] = mktime(0,0,1,$key,1,date('Y', $dbeg));
					$dip['end'] = mktime(23,59,59,$key,31,date('Y', $dbeg));
					$this->build_stat($queuefeatures_id, $key, $dip);
				}
				break;
			case 'type':
				$key_data = $this->get_list_by_type();
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$keyfile = $key_full_data['keyfile'];

					preg_match('/queue-([0-9]+)/', $keyfile, $out);
					$queuefeatures_id = (int) $out[1];

					$dip = array();
					$dip['beg'] = $dbeg;
					$dip['end'] = $dend;
					$this->build_stat($queuefeatures_id, $keyfile, $dip);
				}
				break;
			default:
		}
	}

	public function get_data()
	{
		$axetype = $this->_xs->get_axetype();

		if (($itl = $this->_xs->get_datecal()) === false
		|| is_null($itl['dbeg']) === true)
			return(false);

		$dbeg = strtotime($itl['dbeg']);
		$dend = strtotime($itl['dend']);

		if (($full_list_day = dwho_date::get_listday_for_interval($dbeg,$dend)) === false
		|| ($data_listmonth = dwho_date::get_listmonth_for_interval($dbeg,$dend)) === false)
			return(false);

		$data = $this->get_list_by_type();

		if (empty($data) === true)
			return(false);

		$data = array_shift($data);
		$key_data_arr = $data['keydata'];
		$keyfile = $data['keyfile'];

		switch ($axetype)
		{
			case 'day':
				$key_data = $this->_xs->get_listhour();
				$date = dwho_date::all_to_unixtime($itl['dday']);
				$year = date('Y',$date);
				$month = date('m',$date);
				$day = date('d',$date);
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$key = $key_full_data['key'];
					$dip = array();
					$dip['beg'] = mktime($key,0,0,$month,$day,$year);
					$dip['end'] = mktime($key+1,0,-1,$month,$day,$year);
					$this->_xs->_interval_process = $dip;
					$this->parse_log($key_data_arr,$key);
				}
				break;
			case 'week':
				$key_data = dwho_date::get_listday_for_interval($dbeg,$dend);
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$dayname = $key_full_data['dayname'];

					$this->init_result($dayname);
					$key = $key_full_data['key'];

					$year = date('Y',$key_full_data['time']);
					$month = date('m',$key_full_data['time']);
					$day = date('d',$key_full_data['time']);

					$dip = array();
					$dip['beg'] = mktime(0,0,1,$month,$day,$year);
					$dip['end'] = mktime(23,59,59,$month,$day,$year);

					if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
							|| is_null($month_data) === true)
						continue;
					$listdaynum = array_keys($month_data);
					while($listdaynum)
					{
						$day = array_shift($listdaynum);

						$index = (int) ($year.$month.$day);
						if ($index !== $key_full_data['key'])
							continue;

						if (isset($full_list_day[$year.$month.$day]) === false)
							continue;

						$this->eval_update_result($month_data[$day],$dayname);
					}
				}
				break;
			case 'month':
				$date = dwho_date::all_to_unixtime($itl['dmonth']);
				$year = date('Y',$date);
				$month = date('m',$date);
				$day = date('d',$date);
				if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
						|| is_null($month_data) === true)
					break;

				$this->_result = $month_data;
				break;
			case 'year':
				$key_data = dwho_date::get_listmonth();

				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$monthnum = $key_full_data['key'];

					$this->init_result($monthnum);
					$listmonth = $data_listmonth;
					while($listmonth)
					{
						$key = array_shift($listmonth);
						$key = $key['key'];
						$year = substr($key,0,4);
						$month = substr($key,4,2);

						if (((int) $month) != ((int) $monthnum))
							continue;

						$dip = array();
						$dip['beg'] = mktime(0,0,1,$monthnum,1,$year);
						$dip['end'] = mktime(23,59,59,$monthnum,31,$year);

						if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
								|| is_null($month_data) === true)
							continue;

						$listdaynum = array_keys($month_data);
						while($listdaynum)
						{
							$day = array_shift($listdaynum);
							if (isset($full_list_day[$year.$month.$day]) === false)
								continue;

							// update result for day data
							$this->eval_update_result($month_data[$day],$monthnum);
						}
					}
				}
				break;
			case 'type':
			default:
				$key_data = $this->get_list_by_type();

				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$keyfile = $key_full_data['keyfile'];

					$this->init_result($keyfile);
					$listmonth = $data_listmonth;
					while($listmonth)
					{
						$key = array_shift($listmonth);
						$key = $key['key'];
						$year = substr($key,0,4);
						$month = substr($key,4,2);

						if (($month_data = $this->_xs->get_cache($keyfile,$year,$month)) === false
								|| is_null($month_data) === true)
							continue;
						$listdaynum = array_keys($month_data);
						while($listdaynum)
						{
							$day = array_shift($listdaynum);

							if (isset($full_list_day[$year.$month.$day]) === false)
								continue;

							// update result for day data
							$this->eval_update_result($month_data[$day],$keyfile);
						}
					}
				}
		}
		return($this->_result);
	}

	private function eval_update_result($data_to_eval,$key)
	{
		$listfield = array_keys($data_to_eval);
		while($listfield)
		{
			$field = array_shift($listfield);
			if(isset($data_to_eval[$field]['result']) === true
					&& $data_to_eval[$field]['result'] !== 0)
				$this->update_result(array($key,$field),$data_to_eval[$field]['result']);
			elseif(isset($data_to_eval[$field]['result']) === false
					&& count($data_to_eval[$field]) >> 2)
			{
				$listssfield = array_keys($data_to_eval[$field]);
				while($listssfield)
				{
					$ssfield = array_shift($listssfield);
					if($data_to_eval[$field][$ssfield]['result'] !== 0)
						$this->update_result(array($key,$field,$ssfield),$data_to_eval[$field][$ssfield]['result']);
				}
			}
		}
	}

	protected function update_result($var,$str,$operator='+')
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
			case '=':
				$result = $str;
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
