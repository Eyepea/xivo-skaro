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

class xivo_object_stats_conf_xivouser extends xivo_object_abstract
{
	var $_dso			= null;
	var $_name			= 'stats_conf_xivouser';
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
		$data['stats_conf_id'] = (int) $data['stats_conf_id'];
		$data['user_id'] = (int) $data['user_id'];

		return($data);
	}

	public function add($arr,$id=0)
	{
		if(is_array($arr) === false)
			return(false);

		return(parent::add($arr,$id));
	}

	public function edit($id,$arr)
	{
		if(is_array($arr) === false)
			return(false);

		return(parent::edit($id,$arr));
	}
}

?>
