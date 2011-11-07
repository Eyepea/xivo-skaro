<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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

class stats_ressource_general
{

	public     $_table		= 'queue_log';
	public     $_field	    = array();
	private    $_queue_log	= false;
	private    $_result	    = array();
	private    $_xs         = false;
	private    $_sts        = false;

	public function __construct()
	{
	}

	public function set_xs(&$_XS)
	{
		$this->_xs = $_XS;
		$this->_sts = &dwho_gct::get('xivo_stats');
	}

	public function get_result()
	{
		return($this->_result);
	}

	public function parse_log($type,$conf)
	{
		$result = &$this->_result;
		if (isset($result[$type]) === false)
			$result[$type] = array();
		$rest = &$result[$type];
		if (isset($rest[$conf]) === false)
			$rest[$conf] = array();
		$res = &$rest[$conf];

		switch ($type)
		{
			case 'queue':
				if($this->_sts->load_ressource('queue') === false)
					die('Can\'t load stats_ressource_queue object');

				$stats_queue = new stats_ressource_queue(&$this->_xs);
				$rs = $stats_queue->get_data();
				break;
			case 'agent':
				if($this->_sts->load_ressource('agent') === false)
					die('Can\'t load stats_ressource_agent object');

				$stats_agent = new stats_ressource_agent(&$this->_xs);
				$rs = $stats_agent->get_data();
				break;
		}
		while ($rs)
		{
			$l = array_shift($rs);
			$lkey = array_keys($l);
			while ($l)
			{
				$datakey = array_shift($lkey);
				$data = array_shift($l);
				if (isset($data['type']) === false)
					continue;
				if (isset($res[$datakey]) === true)
					$res[$datakey] = ($res[$datakey] + $data);
				else
					$res[$datakey] = ($data);
			}
		}

		return($result);
	}

}

?>