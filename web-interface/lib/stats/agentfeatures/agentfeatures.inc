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

xivo_stats::required(array('abstract','abstract.inc'),true);

class xivo_stats_agentfeatures extends xivo_stats_abstract
{
	var $_dso			= null;
	var $_name			= 'agentfeatures';
	var $_filter		= false;
	var $_origin		= false;
	var $_origin_list	= false;
	var $_identity		= false;

	public function __construct(&$stats,&$dso)
	{
		parent::__construct(&$stats);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_dso = &$dso;

		$this->_load_config();
		$this->_identity = &$this->_stats->get_identity($this->_name);
	}

	function _prepare($data)
	{
		$this->_identity->_prepare_identity($data);

		$data['id'] = (int) $data['id'];
		$data['commented'] = (bool) $data['commented'];

		return($data);
	}

	function get_by_number($num)
	{
		return($this->_dso->get_by_number($num));
	}

	function search($value,$disable=null,$order=null,$limit=null)
	{
		if(($list = $this->_dso->search($value,$disable,$order,$limit)) === false)
			return(false);

		$nb = count($list);

		$r = array();

		for($i = 0;$i < $nb;$i++)
			$r[] = $this->_prepare($list[$i]);

		if(isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function get_all_assoc()
	{
		if(($list = $this->_dso->get_all_assoc()) === false)
			return(false);

		foreach($list as $key => &$r)
			$list[$key] = $this->_prepare($r);

		if(empty($list) === true)
			$list = false;

		return($list);
	}

	function get_all_wherein($id,$where,$order=null,$limit=null)
	{
		if(($list = $this->_dso->get_all_wherein($id,$where,$order,$limit)) === false)
			return(false);

		foreach($list as $key => &$r)
			$list[$key] = $this->_prepare($r);

		if(empty($list) === true)
			$list = false;

		return($list);
	}
}

?>
