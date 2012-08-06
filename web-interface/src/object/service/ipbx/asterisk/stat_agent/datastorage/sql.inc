<?php

#
# XiVO Web-Interface
# Copyright (C) 2012  Avencall
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

class xivo_service_asterisk_stat_agent_sql extends xivo_service_asterisk_abstract_sql
{

	public function get_id_from_numbers($numbers)
	{
		if (! $numbers)
			return(false);

		$this->_dso->new_select($this->_table,'id');

		foreach($numbers as $number) {
			$this->_dso->orwhere(array('name' => $number));
		}

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			return(false);

		return $r;
	}
}

?>
