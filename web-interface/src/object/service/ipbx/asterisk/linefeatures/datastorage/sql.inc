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

class xivo_service_asterisk_linefeatures_sql extends xivo_service_asterisk_abstract_sql
{
	var $_unique	= array(array('protocol','name'),array('protocol','protocolid'));
	var $_param		= array('internal' => 0);

	function _set_param_internal()
	{
		if($this->_param['internal'] !== null)
			$this->_param['internal'] = intval((bool) $this->_param['internal']);

		return($this->_param['internal']);
	}

	function get($arr,$disable=null,$primary=false)
	{
		if(is_array($arr) === false
		&& ($arr = $this->mk_primary_key_value($arr)) === false)
			return(false);

		if(($arr['internal'] = $this->_set_param_internal()) === null)
			unset($arr['internal']);

		return(parent::get($arr,$disable,$primary));
	}

	function get_primary($arr,$disable=null)
	{
		return($this->get($arr,$disable,true));
	}

	function get_nb($arr=null,$disable=null)
	{
		if(is_array($arr) === false)
			$arr = array();

		if(($arr['internal'] = $this->_set_param_internal()) === null)
			unset($arr['internal']);

		return(parent::get_nb($arr,$disable));
	}

	function get_all_wherein($id,$where)
	{
		$this->_dso->new_select($this->_table,'*');

		$this->_dso->wherein('id',$where);

		$r = $this->_dso->select_all('',true,false,'id');

		if(empty($r) === true)
			$r = false;

		return($r);
	}
	
	function user_masterline($userid=null,$deviceid=null)
	{
		$this->_dso->new_select($this->_table);
		if(((int) $userid = dwho_ulongint($userid)) !== 0)
		{
			$this->_dso->where(array('iduserfeatures' => $userid));
			$this->_dso->where(array('line_num' => 0));
			$this->_dso->where(array('rules_order' => 1));
		}
		if(((int) $deviceid = dwho_ulongint($deviceid)) !== 0)
		{
			$this->_dso->where(array('device' => $deviceid));
			$this->_dso->where(array('num' => 1));
		}
		$r = $this->_dso->select_single();
		return($r);
	}

	function search($value,$disable=null,$order=null,$limit=null,$number=false)
	{
		$this->_cnt = 0;

		$number = (bool) $number;

		$this->_dso->new_select($this->_table);
		$this->_dso->orwherecontain('name',$value);

		if($number === false)
			$this->_dso->orwherecontain('context',$value);

		if($this->_dso->aggregate_where() === false)
			return(false);

		$arr = array();

		if($disable !== null && isset($this->_disable) === true)
			$arr[$this->_disable] = intval((bool) $disable);

		if(($internal = $this->_set_param_internal()) !== null)
			$arr['internal'] = $internal;

		if(empty($arr) === false)
			$this->_dso->andwhere($arr);

		if($number === true)
			$this->_dso->andwhere('IFNULL(number,\'\') != \'\'');

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function get_all_except($id,$number=false,$order=null,$limit=null)
	{
		$this->_dso->new_select($this->_table,'*');

		$arr = array();

		if(isset($this->_forcecolumn) === true)
			$arr = $this->_forcecolumn;

		if(($internal = $this->_set_param_internal()) !== null)
			$arr['internal'] = $internal;

		if(empty($arr) === false)
			$this->_dso->where($arr);

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

	function get_all_context($disable=null,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		$this->_dso->new_select($this->_table,'context');

		$arr = array();

		if($disable !== null && isset($this->_disable) === true)
			$arr[$this->_disable] = intval((bool) $disable);

		if(($internal = $this->_set_param_internal()) !== null)
			$arr['internal'] = $internal;

		if(empty($arr) === false)
			$this->_dso->where($arr);

		$this->_dso->new_group('context');
		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_group();
		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function edit($arr,$value,$disable=null)
	{
		if(is_array($arr) === false && ($arr = $this->mk_primary_key_value($arr)) === false)
			return(false);
		else if(($arr['internal'] = $this->_set_param_internal()) === null)
			unset($arr['internal']);

		return(parent::edit($arr,$value,$disable));
	}

	function delete($arr,$disable=null)
	{
		if(is_array($arr) === false
		&& ($arr = $this->mk_primary_key_value($arr)) === false)
			return(false);

		if(($arr['internal'] = $this->_set_param_internal()) === null)
			unset($arr['internal']);

		return(parent::delete($arr,$disable));
	}

	function get_list($disable=null,$order=null,$limit=null)
	{
		$arr = array();

		if(($arr['internal'] = $this->_set_param_internal()) === null)
			$r = parent::get_list($disable,$order,$limit);
		else
			$r = parent::get_list_where($arr,$disable,$order,$limit);

		return($r);
	}

	function get_list_where($arr,$disable=null,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		if(is_array($arr) === false || empty($arr) === true)
			return(false);
		else if(($arr['internal'] = $this->_set_param_internal()) === null)
			unset($arr['internal']);

		return(parent::get_list_where($arr,$disable,$order,$limit));
	}

	function get_all($disable=null,$order=null,$limit=null)
	{
		$arr = array();

		if(($arr['internal'] = $this->_set_param_internal()) === null)
			$r = parent::get_list($disable,$order,$limit,true);
		else
			$r = parent::get_list_where($arr,$disable,$order,$limit,true);

		return($r);
	}

	function get_all_where($arr,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$this->_cnt = 0;

		if(is_array($arr) === false || empty($arr) === true)
			return(false);

		$this->_dso->new_select($this->_table);

		if($disable !== null && isset($this->_disable) === true)
			$arr[$this->_disable] = intval((bool) $disable);

		if(($internal = $this->_set_param_internal()) !== null)
			$arr['internal'] = $internal;

		if(empty($arr) === false)
			$this->_dso->andwhere($arr,$this->_table);
			
		$this->_dso->leftjoin('usersip',
				       $this->_table.'.protocolid = usersip.id',
				       null,
				       'encryption');
		$this->_dso->joinwhere('usersip',array('protocol' => 'sip'));

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
		return(parent::get_list_where($arr,$disable,$order,$limit,true));
	}
}

?>
