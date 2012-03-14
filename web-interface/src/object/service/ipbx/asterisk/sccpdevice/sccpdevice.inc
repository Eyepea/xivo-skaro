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

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_sccpdevice extends xivo_service_asterisk_abstract
{
	var $_dso		= null;
	var $_name		= 'sccpdevice';
	var $_filter	= false;
	var $_origin	= false;

	function xivo_service_asterisk_sccpdevice(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}

	function _prepare($data)
	{
		$data['id'] = (int) $data['id'];

		return($data);
	}

	function add($arr,$id=0)
	{
		if(is_array($arr) === false)
			return(false);

		$name = str_replace(':', '', $arr['name']);
		$name = str_replace('-', '', $name);

		$arr['name'] = 'SEP'.$name;
		$arr['device'] = $arr['name'];

		return(parent::add($arr,$id));
	}

	function edit($id,$arr,$disable=null)
	{
		if(is_array($arr) === false)
			return(false);

		$name = str_replace(':', '', $arr['name']);
		$name = str_replace('-', '', $name);

		if (substr($name, 0, 3) !== 'SEP')
			$arr['name'] = 'SEP'.$name;
		else
			$arr['name'] = $name;
		$arr['device'] = $arr['name'];

		return(parent::edit($id,$arr,$disable));
	}

	function delete_by_mac($mac)
	{
		$arr = array();
		$name = str_replace(':', '', $mac);
		$name = str_replace('-', '', $name);

		if (substr($name, 0, 3) !== 'SEP')
			$arr['name'] = 'SEP'.$name;
		else
			$arr['name'] = $name;

		return(parent::delete_where($arr));
	}
}

?>
