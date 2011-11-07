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

class stats_ressource_agent extends xivo_stats_ressource_abstract
{

	protected		$_field		= array('logintime'		=> array('type' => 'time'),
									'holdtime'			=> array('type' => 'time'),
									'calltime'			=> array('type' => 'time'),
									'ringtime'			=> array('type' => 'time'),
									'pausetime'			=> array('type' => 'time'),
									'traitmenttime'		=> array('type' => 'time'),
									'connect'			=> array('type' => 'int'),
									'completeagent'		=> array('type' => 'int'),
									'completecaller'	=> array('type' => 'int'),
									'ringnoanswer'		=> array('type' => 'int'),
									'transfer'			=> array('type' => 'int'),
									'abandon'			=> array('type' => 'int')
							);

	public function __construct(&$_XS)
	{
		parent::__construct(&$_XS);
		$this->_table = 'queue_log';
		$this->_type = 'agent';
		$this->_xs->set_type($this->_type);
	}

	public function parse_log($key_data,$key)
	{
		$this->init_result($key);

		$val = $this->eval_count_data($key_data,'CONNECT');
		$this->update_result(array($key,'connect'),$val);

		$field = $this->eval_field_queue_log('CONNECT','holdtime');
		$holdtime = $this->eval_sum_data($key_data,'CONNECT',$field);
		$this->update_result(array($key,'holdtime'),$holdtime);
		$this->update_result(array($key,'traitmenttime'),$holdtime);

		$val = $this->eval_count_data($key_data,'TRANSFER');
		$this->update_result(array($key,'transfer'),$val);

		$field = $this->eval_field_queue_log('RINGNOANSWER','ringtime');
		$ringtime = $this->eval_sum_data($key_data,'RINGNOANSWER',$field);
		$this->update_result(array($key,'ringtime'),$ringtime);
		$this->update_result(array($key,'traitmenttime'),$ringtime);
		$val = $this->eval_count_data($key_data,'RINGNOANSWER');
		$this->update_result(array($key,'ringnoanswer'),$val);

		$val = $this->eval_count_data($key_data,'ABANDON');
		$this->update_result(array($key,'abandon'),$val);

		$field = $this->eval_field_queue_log('COMPLETEAGENT','calltime');
		$calltime = $this->eval_sum_data($key_data,'COMPLETEAGENT',$field);
		$this->update_result(array($key,'calltime'),$calltime);
		$this->update_result(array($key,'traitmenttime'),$calltime);

		$field = $this->eval_field_queue_log('COMPLETEAGENT','holdtime');
		$holdtime = $this->eval_sum_data($key_data,'COMPLETEAGENT',$field);
		$this->update_result(array($key,'holdtime'),$holdtime);

		$val = $this->eval_count_data($key_data,'COMPLETEAGENT');
		$this->update_result(array($key,'completeagent'),$val);

		$field = $this->eval_field_queue_log('COMPLETECALLER','calltime');
		$calltime = $this->eval_sum_data($key_data,'COMPLETECALLER',$field);
		$this->update_result(array($key,'calltime'),$calltime);
		$this->update_result(array($key,'traitmenttime'),$calltime);

		$field = $this->eval_field_queue_log('COMPLETECALLER','holdtime');
		$holdtime = $this->eval_sum_data($key_data,'COMPLETECALLER',$field);
		$this->update_result(array($key,'holdtime'),$holdtime);

		$val = $this->eval_count_data($key_data,'COMPLETECALLER');
		$this->update_result(array($key,'completecaller'),$val);

		$field = $this->eval_field_queue_log('AGENTLOGOFF','logintime');
		$logintime = $this->eval_sum_data($key_data,'AGENTLOGOFF',$field);
		$this->update_result(array($key,'logintime'),$logintime);

		$field = $this->eval_field_queue_log('AGENTCALLBACKLOGOFF','logintime');
		$logintime = $this->eval_sum_data($key_data,'AGENTCALLBACKLOGOFF',$field,array('ISNOT', array('data1', '')));
		$this->update_result(array($key,'logintime'),$logintime);

		return($this->_result);
	}

}

?>