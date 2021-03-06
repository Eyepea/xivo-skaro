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

class xivo_service_asterisk_agentgroup_sql extends xivo_service_asterisk_abstract_sql
{
	function get($arr,$disable=null,$delete=null,$primary=false)
	{
		if(is_array($arr) === false
		&& ($arr = $this->mk_primary_key_value($arr)) === false)
			return(false);

		if($delete !== null)
			$arr['deleted'] = intval((bool) $delete);

		return(parent::get($arr,$disable,$primary));
	}

	function get_primary($arr,$disable=null,$delete=null)
	{
		return($this->get($arr,$disable,$delete,true));
	}

	function get_nb($arr=null,$disable=null,$delete=null)
	{
		if(is_array($arr) === false)
			$arr = array();

		if($delete !== null)
			$arr['deleted'] = intval((bool) $delete);

		return(parent::get_nb($arr,$disable));
	}

	function get_last()
	{
		$this->_dso->new_select($this->_table,array('cnt' => (object) 'COUNT(*)',
							    'id' => (object) 'MAX(id)'));

		if(($r = $this->_dso->select_single()) !== false)
			$r = $r['cnt'] > 0 ? $r['id'] : 0;

		return($r);
	}

	function get_free()
	{
		$this->_dso->new_select($this->_table,'id');
		$this->_dso->where(array('deleted' => 1));
		$this->_dso->new_order(array('id' => SORT_ASC));

		$r = $this->_dso->select_one();

		$this->_dso->reset_order();

		return($r);
	}

	function add($arr,$insertid=true)
	{
		if(is_array($arr) === false)
			return(false);
		else if(array_key_exists('deleted',$arr) === true)
			$arr['deleted'] = intval((bool) $arr['deleted']);

		return(parent::add($arr,$insertid));
	}

	function edit($arr,$value,$disable=null,$delete=null)
	{
		if(is_array($value) === false
		|| (is_array($arr) === false && ($arr = $this->mk_primary_key_value($arr)) === false) === true)
			return(false);

		if($delete !== null)
			$arr['deleted'] = intval((bool) $delete);

		if(array_key_exists('deleted',$value) === true)
			$value['deleted'] = intval((bool) $value['deleted']);

		return(parent::edit($arr,$value,$disable));
	}

	function get_list($disable=null,$delete=null,$order=null,$limit=null)
	{
		if($delete === null)
			$r = parent::get_list($disable,$order,$limit);
		else
			$r = parent::get_list_where(array('deleted' => intval((bool) $delete)),
						    $disable,
						    $order,
						    $limit);
		return($r);
	}

	function get_list_where($arr,$disable=null,$delete=null,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		if(is_array($arr) === false || empty($arr) === true)
			return(false);
		else if($delete !== null)
			$arr['deleted'] = intval((bool) $delete);

		return(parent::get_list_where($arr,$disable,$order,$limit));
	}

	function get_all($disable=null,$delete=null,$order=null,$limit=null)
	{
		if($delete === null)
			$r = parent::get_list($disable,$order,$limit,true);
		else
			$r = parent::get_list_where(array('deleted' => intval((bool) $delete)),
						    $disable,
						    $order,
						    $limit,
						    true);
		return($r);
	}

	function get_all_where($arr,$disable=null,$delete=null,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		if(is_array($arr) === false || empty($arr) === true)
			return(false);
		else if($delete !== null)
			$arr['deleted'] = intval((bool) $delete);

		return(parent::get_list_where($arr,$disable,$order,$limit,true));
	}
}

?>
