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

class xivo_service_asterisk_pickup_sql extends xivo_service_asterisk_abstract_sql
{
	var $_autoincrement	= false;
	var $_unique	= 'name';
	#var $_disable	= null;
	
	function get_empty()
	{
		$this->_dso->new_select($this->_table,array('id'));
		$this->_dso->new_order(array('id' => SORT_ASC));

		$cur = 0;
		foreach($this->_dso->select_all() as $row)
		{
			if(intval($row['id']) > $cur)
				break;

			$cur++;
		}

		return($cur < 64?$cur:false);
	}
	
}

?>
