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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'abstract','statistics.inc'));

class xivo_statistics_queue extends xivo_statistics_abstract
{

	protected	$_field	= array('presented'				=> array('type' => 'int'),
								'enterqueue'			=> array('type' => 'int'),
								'connect'				=> array('type' => 'int'),
								'abandon'				=> array('type' => 'int'),
								'rerouted_on_hungup'	=> array('type' => 'int'),
								'rerouted_on_guide'		=> array('type' => 'int'),
								'rerouted_on_number'	=> array('type' => 'int'),
								'total_time_waiting'	=> array('type' => 'int'),
								'home_rated'			=> array('type' => 'percent'),
								'qos'					=> array('type' => 'int')
							);

	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_method = 'DB';
		$this->_table = 'queue_log';
		$this->_type = 'queue';
		$this->_xs->set_type($this->_type);
	}

	public function parse_log($key_data,$key)
	{
		if ($this->_xs->get_conf() === false)
			return(false);
		switch ($this->_xs->_method)
		{
			case 'DB':
				return($this->parse_log_db($key_data,$key));
				break;
			case 'PHP':
				return($this->parse_log_php());
				break;
			default:
				return(false);
		}
	}

	private function parse_log_db($key_data,$key)
	{
		$this->init_result($key);

		$enterqueue = $this->eval_count_data($key_data,'ENTERQUEUE');
		$this->update_result(array($key,'enterqueue'),$enterqueue);
		$this->update_result(array($key,'presented'),$enterqueue);

		$connect = $this->eval_count_data($key_data,'CONNECT');
		$this->update_result(array($key,'connect'),$connect);

		$field = $this->eval_field_queue_log('CONNECT','holdtime');
		$sum = $this->eval_sum_data($key_data,'CONNECT',$field);
		$this->update_result(array($key,'total_time_waiting'),$sum);

		$abandon = $this->eval_count_data($key_data,'ABANDON');
		$this->update_result(array($key,'abandon'),$abandon);

		$field = $this->eval_field_queue_log('ABANDON','waittime');
		$sum = $this->eval_sum_data($key_data,'ABANDON',$field);
		$this->update_result(array($key,'total_time_waiting'),$sum);

		$exitempty = $this->eval_count_data($key_data,'EXITEMPTY');
		$this->update_result(array($key,'rerouted_on_hungup'),$exitempty);

		$exitwithtimeout = $this->eval_count_data($key_data,'EXITWITHTIMEOUT');
		$this->update_result(array($key,'rerouted_on_hungup'),$exitwithtimeout);

		$rerouteguide = $this->eval_count_data($key_data,'REROUTEGUIDE');
		$this->update_result(array($key,'rerouted_on_guide'),$rerouteguide);
		$this->update_result(array($key,'presented'),$rerouteguide);

		$reroutenumber = $this->eval_count_data($key_data,'REROUTENUMBER');
		$this->update_result(array($key,'rerouted_on_number'),$reroutenumber);
		$this->update_result(array($key,'presented'),$reroutenumber);

		$transfer = $this->eval_count_data($key_data,'TRANSFER');
		$this->update_result(array($key,'rerouted_on_number'),$transfer);

		$queue = $this->_xs->get_list_by_type('queue');
		$stats_qos = array_shift($queue);
		$stats_qos = $stats_qos['qos'];

		$field = $this->eval_field_queue_log('CONNECT','holdtime');
		$qos = $this->eval_count_data($key_data,'CONNECT',array('<', array($field, $stats_qos)));
		$this->update_result(array($key,'qos'),$qos);


		return($this->_result);
	}

	private function parse_log_php()
	{
		$nb_ql = count($this->_queue_log);
		for ($u=0;$u<$nb_ql;$u++)
		{
			$queue_log = &$this->_queue_log[$u];

			foreach ($queue_log as $k => $clean)
				$queue_log[$k] = trim($clean);

			$time 		= $queue_log['time'];
			$callid 	= $queue_log['callid'];
			$queuename 	= $queue_log['queuename'];
			$agent 		= strtolower($queue_log['agent']);
			$event 		= $queue_log['event'];

			$this->init_result($queuename);

			switch ($event)
			{
				# ENTERQUEUE(url|callerid)
				case 'ENTERQUEUE':
					$this->update_result(array($queuename,'presented'),1);
					break;
				# CONNECT(holdtime|bridgedchanneluniqueid)
				case 'CONNECT':
					$this->update_result(array($queuename,'answered'),1);

					$holdtime = (int) $this->eval_data_queue_log($queue_log,'CONNECT','holdtime');
					$this->update_result(array($queuename,'total_time_waiting'),$holdtime);

					if (isset($this->_data_custom['qos']) === true
					&& isset($this->_data_custom['qos'][$queuename]) === true
					&& ($stats_qos = (int) $this->_data_custom['qos'][$queuename]['stats_qos']) !== 0
					&& $holdtime << $stats_qos)
						$this->update_result(array($queuename,'qos'),1);
					break;
				# ABANDON(positionorig|positionwaittime)
				case 'ABANDON':
					$this->update_result(array($queuename,'abandoned'),1);
					break;
				# EXITEMPTY(position|origposition|waittime)
				case 'EXITEMPTY':
					$this->update_result(array($queuename,'rerouted_on_hungup'),1);
					break;
				# EXITWITHTIMEOUT(position)
				case 'EXITWITHTIMEOUT':
					$this->update_result(array($queuename,'rerouted_on_guide'),1);
					break;
				# TRANSFER(extension|context|holdtime|calltime)
				case 'TRANSFER':
					$this->update_result(array($queuename,'rerouted_on_number'),1);
					break;
				default:
			}
		}
	}

}

?>