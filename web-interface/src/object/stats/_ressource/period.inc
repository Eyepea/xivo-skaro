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