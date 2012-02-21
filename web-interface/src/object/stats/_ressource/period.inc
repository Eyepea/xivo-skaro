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

	public function parse_log($key_data,$key)
	{
		$this->init_result($key);

		foreach($this->_xs->_period as $k => $v)
		{
			if (($v['beg']) === 0
			&& ($v['end']) === 0)
				continue;

			$operator = 'BETWEEN';
			if (is_null($v['end']) === true)
				$operator = '>';

			$field = $this->eval_field_queue_log('CONNECT','holdtime');
			$connect = $this->eval_count_data($key_data,'CONNECT',array($operator, array($field,$v['beg'],$v['end'])));
			$this->update_result(array($key,'connect',$k),$connect);

			$field = $this->eval_field_queue_log('ABANDON','waittime');
			$abandon = $this->eval_count_data($key_data,'ABANDON',array($operator, array($field,$v['beg'],$v['end'])));
			$this->update_result(array($key,'abandon',$k),$abandon);
		}
	}

}

?>