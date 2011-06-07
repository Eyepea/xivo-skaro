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

xivo_object::required(array('abstract','abstract.inc'),true);

class xivo_object_stats_conf extends xivo_object_abstract
{
	var $_dso			= null;
	var $_name			= 'stats_conf';
	var $_filter		= false;
	var $_origin		= false;
	var $_origin_list	= false;

	public function __construct(&$xobj,&$dso)
	{
		parent::__construct(&$xobj);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_dso = &$dso;
	}

	public function _prepare($data)
	{
		$data['id'] = (int) $data['id'];
		$data['hour_start'] = date('H:i',strtotime($data['hour_start']));
		$data['hour_end'] = date('H:i',strtotime($data['hour_end']));
		$data['monday'] = (bool) $data['monday'];
		$data['tuesday'] = (bool) $data['tuesday'];
		$data['wednesday'] = (bool) $data['wednesday'];
		$data['thursday'] = (bool) $data['thursday'];
		$data['friday'] = (bool) $data['friday'];
		$data['saturday'] = (bool) $data['saturday'];
		$data['sunday'] = (bool) $data['sunday'];
		$data['dbegcache'] = date('Y-m',$data['dbegcache']);
		if ($data['dendcache'] != 0)
			$data['dendcache'] = date('Y-m',$data['dendcache']);
		$data['homepage'] = (bool) $data['homepage'];
		$data['disable'] = (bool) $data['disable'];

		return($data);
	}
	
	public function update_date_genercache($id)
	{
		$arr['dgenercache'] = time();
		return(parent::edit($id,$arr,null));
	}

	public function add($arr,$id=0)
	{
		if(is_array($arr) === false)
			return(false);

		if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);
			
		$arr['dcreate'] = time();
		$arr['dbegcache'] = strtotime($arr['dbegcache']);
		if ($arr['dendcache'] !== 0)
			$arr['dendcache'] = strtotime($arr['dendcache']);

		return(parent::add($arr,$id));
	}

	public function edit($id,$arr,$disable=null)
	{
		if(is_array($arr) === false)
			return(false);
		else if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);
			
		$arr['dupdate'] = time();
		$arr['dbegcache'] = strtotime($arr['dbegcache']);
		if ($arr['dendcache'] !== 0)
			$arr['dendcache'] = strtotime($arr['dendcache']);

		return(parent::edit($id,$arr,$disable));
	}
}

?>
