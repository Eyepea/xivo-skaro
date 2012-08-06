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

class stats_ressource_period extends xivo_stats_ressource_abstract
{

	public		$_field		= array();

	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_table = 'queue_log';
		$this->_type = 'period';
		$this->_xs->set_type($this->_type);
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

			foreach($this->_xs->_period as $k => $v)
			{
				if(isset($data_process['connect'][$k]) === false)
				{
					$data_process['connect'][$k] = array();
					$data_process['connect'][$k]['type'] = 'int';
					$data_process['connect'][$k]['result'] = 0;
					$data_process['abandon'][$k] = array();
					$data_process['abandon'][$k]['type'] = 'int';
					$data_process['abandon'][$k]['result'] = 0;
				}
			}
		}

		return(true);
	}

	public function get_data_period()
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
					$this->_build_stat($queuefeatures_id, $key, $this->_build_hour_for_day($key, $dbeg));
				}
				break;
			case 'week':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $date => $date_itl)
					$this->_build_stat($queuefeatures_id, $date, $date_itl);
				break;
			case 'month':
				$this->full_itl = $this->_xs->build_full_date_interval($dbeg, $dend);
				foreach ($this->full_itl as $date => $date_itl)
					$this->_build_stat($queuefeatures_id, $date, $date_itl);
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
					$this->_build_stat($queuefeatures_id, $key, $dip);
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
					$this->_build_stat($queuefeatures_id, $keyfile, $dip);
				}
				break;
		}
	}

	protected function _build_stat($queuefeatures_id, $key, $interval)
	{
		$queuefeatures_name = $this->_queuefeatures->name_from_id($queuefeatures_id);
		if (!$queuefeatures_name)
			return;

		$queue_id = $this->_stat_queue->id_from_name($queuefeatures_name);
		if (!$queue_id)
			return;

		foreach($this->_xs->_period as $k => $interval_wt)
		{
			if (($interval_wt['beg']) === 0
			&& ($interval_wt['end']) === 0)
				continue;

			$answered = $this->_stat_call_on_queue->get_count_wait_time_by_period('answered', $interval, $queue_id, $interval_wt);
			$this->_result[$key]['connect'][$k]['result'] = $answered;

			$abandoned = $this->_stat_call_on_queue->get_count_wait_time_by_period('abandoned', $interval, $queue_id, $interval_wt);
			$this->_result[$key]['abandon'][$k]['result'] = $abandoned;
		}
	}

}

?>