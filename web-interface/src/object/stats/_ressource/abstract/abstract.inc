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
		$this->_xs->set_type($this->_type);
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
		return($this->get_list_by_type());
	}

	public function get_agent_list()
	{
		return($this->get_list_by_type());
	}

	protected function _build_hour_for_day($key, $time)
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

	protected function _build_total($queue_id, $dbeg, $dend)
	{
		$year = date('Y', $dend);
		$month = date('m', $dend);
		$day = date('d' ,$dend);
		$interval = array();
		$interval['beg'] = $dbeg;
		$interval['end'] = mktime(23, 59, 59, $month, $day, $year);
		$this->_build_stat($queue_id, "total", $interval);
	}

	public function get_data()
	{
		$axetype = $this->_xs->get_axetype();

		if (($itl = $this->_xs->get_datecal()) === false
		|| is_null($itl['dbeg']) === true)
			return(false);

		$dbeg = strtotime($itl['dbeg']);
		$dend = strtotime($itl['dend']);

		if ($dbeg == $dend)
			$dend = strtotime('+1 day', $dend);

		$this->_stat_queue_periodic->set_dso_param('hour_itl',$this->_xs->get_dip_hour());
		$this->_stat_queue_periodic->set_dso_param('days',$this->_xs->get_valid_list_day());
		$this->_stat_call_on_queue->set_dso_param('hour_itl',$this->_xs->get_dip_hour());
		$this->_stat_call_on_queue->set_dso_param('days',$this->_xs->get_valid_list_day());

		$obj_process = $this->_xs->get_object_process();
		if ($axetype !== 'type' && !$obj_process)
			return;

		$this->_build_total($obj_process, $dbeg, $dend);

		switch ($axetype)
		{
			case 'day':
				$key_data = $this->_xs->get_listhour();
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$key = $key_full_data['key'];
					$this->_build_stat($obj_process, $key, $this->_build_hour_for_day($key, $dbeg));
				}
				break;
			case 'week':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $date => $date_itl)
					$this->_build_stat($obj_process, $date, $date_itl);
				break;
			case 'month':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $date => $date_itl)
					$this->_build_stat($obj_process, $date, $date_itl);
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
					$this->_build_stat($obj_process, $key, $dip);
				}
				break;
			case 'type':
				$key_data = $this->get_list_by_type();
				while($key_data)
				{
					$key_full_data = array_shift($key_data);
					$keyfile = $key_full_data['keyfile'];

					$dip = array();
					$dip['beg'] = $dbeg;
					$dip['end'] = $dend;
					$this->_build_stat($key_full_data, $keyfile, $dip);
				}
				break;
		}
	}

}
