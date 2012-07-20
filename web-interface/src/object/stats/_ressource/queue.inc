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

	protected $_field = array('presented'			=> array('type' => 'int'),
				  'connect'			=> array('type' => 'int'),
				  'abandon'			=> array('type' => 'int'),
				  'deterred_on_close'		=> array('type' => 'int'),
				  'deterred_on_saturation'	=> array('type' => 'int'),
				  'joinempty'			=> array('type' => 'int'),
				  'leaveempty'		=> array('type' => 'int'),
				  'timeout'			=> array('type' => 'int'),
				  'average_wait_time'		=> array('type' => 'int'),
				  'home_rated'		=> array('type' => 'percent'),
				  'qos'			=> array('type' => 'percent')
		);

	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_table = 'queue_log';
		$this->_type = 'queue';
		$this->_xs->set_type($this->_type);
	}

	public function build_stat($queue_id, $key, $interval)
	{
		$this->init_result($key);

		$queue = $this->_xs->get_list_by_type('queue');
		$stats_qos = array_shift($queue);
		$stats_qos = $stats_qos['qos'];

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

		$qos = $answered > 0 ? $answered_in_qos / $answered : null;

		$hr_total = $answered + $abandon + $closed + $full + $leaveempty + $joinempty;
		$hr = $hr_total > 0 ? $answered / $hr_total : null;

		$waited_call = $answered + $abandon + $leaveempty + $timeout;
		$awt = $waited_call > 0 ? $total_wait_time / $waited_call : null;

		$this->update_result(array($key, 'presented'), $total, '=');
		$this->update_result(array($key, 'connect'), $answered, '=');
		$this->update_result(array($key, 'average_wait_time'), $awt, '=');
		$this->update_result(array($key, 'qos'), $qos, '=');
		$this->update_result(array($key, 'deterred_on_close'), $closed, '=');
		$this->update_result(array($key, 'deterred_on_saturation'), $full, '=');
		$this->update_result(array($key, 'abandon'), $abandon, '=');
		$this->update_result(array($key, 'joinempty'), $joinempty, '=');
		$this->update_result(array($key, 'leaveempty'), $leaveempty, '=');
		$this->update_result(array($key, 'timeout'), $timeout, '=');
		$this->update_result(array($key, 'home_rated'), $hr, '=');

		return($this->_result);
	}
}

?>
