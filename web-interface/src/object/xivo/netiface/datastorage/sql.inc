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

xivo_object::required(array('abstract','datastorage','sql.inc'),true);

class xivo_object_netiface_sql extends xivo_object_abstract_sql
{
	var $_unique	= array(array('uuid','ifname'));

	function exists_link($ifname, $uuid)
	{
		if(dwho_has_len($ifname) === false
		|| dwho_has_len($uuid)   === false)
			return(null);

		$this->_dso->new_select($this->_table,array('ifname'));

		// Test if exists an alias interface
		$this->_dso->where(array('uuid' => $uuid));
		$this->_dso->andwherebegin('ifname',$ifname.':');

		// Test if exists a vlan-raw-device
		$this->_dso->orwhere(array('uuid' => $uuid));
		$this->_dso->andwhere(array('vlanrawdevice' => $ifname));

		return($this->_dso->select_single());
	}

	function get_voip_iface($uuid)
	{
		$this->_dso->new_select($this->_table);
		$this->_dso->where(array('uuid' => $uuid));
		$this->_dso->where(array('networktype' => 'voip'));

		return($this->_dso->select_single());
	}
}

?>
