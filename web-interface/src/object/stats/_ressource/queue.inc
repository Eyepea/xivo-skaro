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

class stats_ressource_queue extends xivo_stats_ressource_abstract
{

	protected $_field = array('presented'                 => array(),
								'connect'                 => array(),
								'abandon'                 => array(),
								'deterred_on_close'       => array(),
								'deterred_on_saturation'  => array(),
								'joinempty'               => array(),
								'leaveempty'              => array(),
								'timeout'                 => array(),
								'average_wait_time'       => array(),
								'home_rated'              => array(),
								'qos'                     => array()
		);

	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_type = 'queue';
		$this->_xs->set_type($this->_type);
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

		$queuefeatures_id = 0;
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
			default:
		}
	}

	protected function _build_stat($queuefeatures_id, $key, $interval)
	{
		$queue = $this->_xs->get_list_by_type('queue');
		if (!$queue)
			return;

		$stats_qos = $queue[0]['qos'];

		$queuefeatures_name = $this->_queuefeatures->name_from_id($queuefeatures_id);
		if (!$queuefeatures_name)
			return;

		$queue_id = $this->_stat_queue->id_from_name($queuefeatures_name);
		if (!$queue_id)
			return;

		$total = $this->_stat_queue_periodic->get_event_total($interval, $queue_id);
		$answered = $this->_stat_queue_periodic->get_event_answered($interval, $queue_id);
		$answered_in_qos = $this->_stat_call_on_queue->get_count_under_qos($interval, $queue_id, $stats_qos);
		$closed = $this->_stat_queue_periodic->get_event_closed($interval, $queue_id);
		$full = $this->_stat_queue_periodic->get_event_full($interval, $queue_id);
		$abandon = $this->_stat_queue_periodic->get_event_abandon($interval, $queue_id);
		$joinempty = $this->_stat_queue_periodic->get_event_joinempty($interval, $queue_id);
		$leaveempty = $this->_stat_queue_periodic->get_event_leaveempty($interval, $queue_id);
		$timeout = $this->_stat_queue_periodic->get_event_timeout($interval, $queue_id);
		$total_wait_time = $this->_stat_call_on_queue->get_queue_wait_time($interval, $queue_id);

		$qos = $answered > 0 ? 100 * $answered_in_qos / $answered : null;

		$hr_total = $answered + $abandon + $closed + $full + $leaveempty + $joinempty + $timeout;
		$hr = $hr_total > 0 ? 100 * $answered / $hr_total : null;

		$waited_call = $answered + $abandon + $leaveempty + $timeout;
		$awt = $waited_call > 0 ? $total_wait_time / $waited_call : null;

		$this->_result[$key]['presented']['result'] = $total;
		$this->_result[$key]['connect']['result'] = $answered;
		$this->_result[$key]['average_wait_time']['result'] = $awt;
		$this->_result[$key]['qos']['result'] = $qos;
		$this->_result[$key]['deterred_on_close']['result'] = $closed;
		$this->_result[$key]['deterred_on_saturation']['result'] = $full;
		$this->_result[$key]['abandon']['result'] = $abandon;
		$this->_result[$key]['joinempty']['result'] = $joinempty;
		$this->_result[$key]['leaveempty']['result'] = $leaveempty;
		$this->_result[$key]['timeout']['result'] = $timeout;
		$this->_result[$key]['home_rated']['result'] = $hr;
	}
}

?>
