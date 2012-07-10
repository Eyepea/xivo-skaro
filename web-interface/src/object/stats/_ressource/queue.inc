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

	protected	$_field	= array('presented'				=> array('type' => 'int'),
								'enterqueue'			=> array('type' => 'int'),
								'connect'				=> array('type' => 'int'),
								'abandon'				=> array('type' => 'int'),
								'deterred_on_close'		=> array('type' => 'int'),
								'deterred_on_saturation'=> array('type' => 'int'),
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
		$this->_table = 'queue_log';
		$this->_type = 'queue';
		$this->_xs->set_type($this->_type);
	}

	public function parse_log($key_data,$key)
	{
		$queue_id = 0;
		if (preg_match('/queue-([0-9]+)/', $this->_xs->_objectkey, $out) === 1)
			$queue_id = (int) $out[1];

		$this->init_result($key);

		$enterqueue = $this->eval_count_data($key_data,'ENTERQUEUE');
		$this->update_result(array($key,'enterqueue'),$enterqueue);
		$this->update_result(array($key,'presented'),$enterqueue);

		$connect = $this->eval_count_data($key_data,'CONNECT');
		$this->update_result(array($key,'connect'),$connect);
		$this->update_result(array($key,'presented'),$connect);

		$field = $this->eval_field_queue_log('CONNECT','holdtime');
		$sum = $this->eval_sum_data($key_data,'CONNECT',$field);
		$this->update_result(array($key,'total_time_waiting'),$sum);

		$queue = $this->_xs->get_list_by_type('queue');
		$stats_qos = array_shift($queue);
		$stats_qos = $stats_qos['qos'];

		$field = $this->eval_field_queue_log('CONNECT','holdtime');
		$qos = $this->eval_count_data($key_data,'CONNECT',array('<', array($field, $stats_qos)));
		$this->update_result(array($key,'qos'),$qos);

		$closed = $this->eval_count_data($key_data,'CLOSED');
		$this->update_result(array($key,'deterred_on_close'),$closed);
		$this->update_result(array($key,'presented'),$closed);

		#$full = $this->eval_count_data($key_data,'FULL');
		$full = $this->_stat_queue_periodic->get_event_full($this->_xs->_interval_process, $queue_id);
		$this->update_result(array($key,'deterred_on_saturation'), $full);

		$abandon = $this->eval_count_data($key_data,'ABANDON');
		$this->update_result(array($key,'abandon'),$abandon);
		$this->update_result(array($key,'presented'),$abandon);

		$exitempty = $this->eval_count_data($key_data,'EXITEMPTY');
		$this->update_result(array($key,'rerouted_on_hungup'),$exitempty);
		$this->update_result(array($key,'presented'),$exitempty);
		$exitwithtimeout = $this->eval_count_data($key_data,'EXITWITHTIMEOUT');
		$this->update_result(array($key,'rerouted_on_hungup'),$exitwithtimeout);
		$this->update_result(array($key,'presented'),$exitwithtimeout);

		$rerouteguide = $this->eval_count_data($key_data,'REROUTEGUIDE');
		$this->update_result(array($key,'rerouted_on_guide'),$rerouteguide);
		$this->update_result(array($key,'presented'),$exitwithtimeout);

		$reroutenumber = $this->eval_count_data($key_data,'REROUTENUMBER');
		$this->update_result(array($key,'rerouted_on_number'),$reroutenumber);
		$this->update_result(array($key,'presented'),$reroutenumber);
		$transfer = $this->eval_count_data($key_data,'TRANSFER');
		$this->update_result(array($key,'rerouted_on_number'),$transfer);
		$this->update_result(array($key,'presented'),$transfer);

		return($this->_result);
	}

}

?>
