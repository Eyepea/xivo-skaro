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

	protected 	$_table                = '';
	public	 	$_xs                   = null;
	public	 	$_sts                  = null;
	public 		$_data_custom          = array();
	public 		$_counter              = array();
	public		$_result               = array();
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
		return($this->_xs->get_object_list('queue'));
	}

	public function get_agent_list()
	{
		return($this->_xs->get_object_list('agent'));
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

	protected function _build_hours_for_day($hour, $daytime)
	{
		$year = date('Y', $daytime);
		$month = date('m', $daytime);
		$day = date('d' ,$daytime);
		$interval = array();
		$interval['beg'] = mktime($hour, 0, 0, $month, $day, $year);
		$interval['end'] = mktime($hour+1, 0, -1, $month, $day, $year);
		return($interval);
	}

	protected function _build_interval_days_for_month($year, $month)
	{
		$interval = array();
		$interval['beg'] = mktime(0, 0, 1, $month, 1, $year);
		$interval['end'] = mktime(23, 59, 59, $month, 31, $year);
		return($interval);
	}

	protected function _build_interval_full_day($dbeg, $dend)
	{
		$interval = array();
		$interval['beg'] = mktime(00, 00, 01, date('m', $dbeg), date('d' ,$dbeg), date('Y', $dbeg));
		$interval['end'] = mktime(23, 59, 59, date('m', $dend), date('d' ,$dend), date('Y', $dend));
		return($interval);
	}

	public function get_data()
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

		$obj_process = $this->_xs->get_object_process();
		if ($axetype !== 'type' && !$obj_process)
			return;

		$interval = $this->_build_interval_full_day($dbeg, $dend);

		$this->_build_stat($obj_process, "total", $interval);

		switch ($axetype)
		{
			case 'day':
				$key_data = $this->_xs->get_listhour();
				foreach ($key_data as $data)
					$this->_build_stat($obj_process, $data['key'], $this->_build_hours_for_day($data['key'], $dbeg));
				break;
			case 'week':
			case 'month':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $key => $interval)
					$this->_build_stat($obj_process, $key, $interval);
				break;
			case 'year':
				$key_data = dwho_date::get_listmonth();
				foreach ($key_data as $data)
					$this->_build_stat($obj_process, $data['key'], $this->_build_interval_days_for_month(date('Y', $dbeg), $data['key']));
				break;
			case 'type':
				$key_data = $this->get_list_by_type();
				foreach ($key_data as $data)
					$this->_build_stat($data, $data['keyfile'], $interval);
				break;
		}
	}

}
