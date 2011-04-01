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

class xivo_application_service_asterisk_dundipeer_sql extends xivo_application_abstract_datastorage_sql
{
//	var $_table = array('dundipeer' => '', 'dundipeerchange' => '');
/*
	function get_all($disable=null,$order=null,$limit=null,$value=null)
	{
		$this->_dso->new_select($this->_table['dundipeer']);
		$this->_dso->leftjoin($this->_table['dundipeerchange'],
			$this->_table['dundipeer'].'.id = '.$this->_table['dundipeerchange'].'.dundipeer_id',
			null,
			array('number' => 'COUNT('.$this->_table['dundipeerchange'].'.seconds)')
		);

		$this->_dso->new_group('id'          ,$this->_table['dundipeer']);
		$this->_dso->add_group('name'        ,$this->_table['dundipeer']);
		$this->_dso->add_group('description' ,$this->_table['dundipeer']);
		$this->_dso->add_group('commented'   ,$this->_table['dundipeer']);

		$this->_dso->new_order($order,null,$this->_table['dundipeer']);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_group();
		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_distinct_count_singlecolumn(
							null,
							'id',
							$this->_table['dundipeer'])) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}
*/
}

?>
