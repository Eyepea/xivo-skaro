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

xivo_service_asterisk::required(array('abstract','datastorage','abstract','sql.inc'),true);

class xivo_service_asterisk_queuefeatures_sql extends xivo_service_asterisk_abstract_sql
{
	var $_unique	= 'name';
	var $_disable	= null;

	function get_by_name($name)
	{
		$this->_dso->new_select($this->_table,'*');

		$this->_dso->where(array('name' => (string) $name));

		$r = $this->_dso->select_single();

		if(empty($r) === true)
			$r = false;

		return($r);
	}

	function get_all_wherein($id,$where,$order=null,$limit=null)
	{
		$this->_dso->new_select($this->_table,'*');

		$this->_dso->wherein('id',$where);

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all('',true,false,'id');

		if(empty($r) === true)
			$r = false;

		return($r);
	}

	function get_all_except($id,$number=false,$order=null,$limit=null)
	{
		$this->_dso->new_select($this->_table,'*');

		if(isset($this->_forcecolumn) === true)
			$this->_dso->where($this->_forcecolumn);

		if(($id = dwho_ulongint($id)) !== 0)
			$this->_dso->andwherenot(array('id' => $id));

		if((bool) $number === true)
			$this->_dso->andwherenot('IFNULL(number,\'\') = \'\'');

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(isset($r[0]) === false)
			$r = false;

		return($r);
	}
}

?>
