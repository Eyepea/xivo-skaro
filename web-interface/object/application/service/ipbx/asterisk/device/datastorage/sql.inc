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

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'application','abstract','datastorage','sql.inc'));

class xivo_application_service_asterisk_device_sql extends xivo_application_abstract_datastorage_sql
{
	var $_table	= array('devicefeatures' => '');

	function get_nb($arr=null,$disable=null,$initialized=null)
	{
		if(is_array($arr) === false)
			$arr = array();

		$this->_dso->new_select($this->_table['devicefeatures']);

		if($disable !== null)
			$arr['commented'] = intval((bool) $disable);

		$this->_dso->andwhere($arr,$this->_table['devicefeatures']);

		if($initialized !== null)
		{
		}

		return(dwho_ulongint($this->_dso->select_count(null,'id',$this->_table['devicefeatures'])));
	}

	function get_all($disable=null,$initialized=null,$order=null,$limit=null,$value=null)
	{
		$this->_cnt = 0;

		$arr = array();

		$this->_dso->new_select($this->_table['devicefeatures']);

		if($disable !== null)
			$arr['commented'] = intval((bool) $disable);

		$this->_dso->andwhere($arr,$this->_table['devicefeatures']);

		$this->_dso->aggregate_where(false,'AND');

		$this->_dso->new_order($order,null,$this->_table['devicefeatures']);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count(null,'id',$this->_table['devicefeatures'])) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function search($value,$disable=null,$initialized=null,$order=null)
	{
		$this->_cnt = 0;

		if(dwho_has_len($value) === false)
			return(false);

		return($this->get_all($disable,$initialized,$order,$limit,$value));
	}
}

?>
