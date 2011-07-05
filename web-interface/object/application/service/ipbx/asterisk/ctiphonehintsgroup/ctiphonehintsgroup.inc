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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_ctiphonehintsgroup extends xivo_application_asterisk_abstract
{
	var $_ctiphonehintsgroup = false;
	var $_ctistatus = false;

	function xivo_application_service_asterisk_ctiphonehintsgroup(&$service,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);
		if(($this->_ctiphonehintsgroup = &$this->_service->get_module('ctiphonehintsgroup')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function get_phonehintsgroup_list($order=null,$limit=null,$assoc=false)
	{
		if(($rs = $this->_ctiphonehintsgroup->get_all(null,true,$order,$limit)) === false
		|| ($nb = count($rs)) === 0)
		{
			$this->_cnt = $this->_ctiphonehintsgroup->get_cnt();
			return(false);
		}

		$r = $info = array();
		for($i = 0;$i < $nb;$i++)
		{
			$info['ctiphonehintsgroup'] = $rs[$i];
			$r[$info['ctiphonehintsgroup']['id']] = $info;
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	function get_phonehintsgroup_edit()
	{
		return(false);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		$this->_info['phonehintsgroup'] = $this->_ctiphonehintsgroup->get($id);

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_nb($arr=null,$disable=null)
	{
		return($this->_ctiphonehintsgroup->get_nb($arr,$disable));
	}

	function get_elements()
	{
		$r = array();
		$r['phonehintsgroup'] = $this->_ctiphonehintsgroup->get_element();

		return($r);
	}

	function set_add($arr)
	{
		return($this->_set('add',$arr));
	}

	function set_edit($arr)
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr));
	}

	function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('phonehintsgroup',$arr) === false)
			return(false);

		$this->set_phonehintsgroup($arr['phonehintsgroup']);

		return(($this->get_errnb() < 1));
	}

	function set_phonehintsgroup($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('phonehintsgroup',null);
			$this->_set_error('phonehintsgroup','invalid data');
			return(false);
		}
		else if(($rs = $this->_ctiphonehintsgroup->chk_values($arr)) === false)
		{
			$this->_set_result('phonehintsgroup',$this->_ctiphonehintsgroup->get_filter_result());
			$this->_set_error('phonehintsgroup',$this->_ctiphonehintsgroup->get_filter_error());
			return(false);
		}

		$this->_set_result('phonehintsgroup',$rs);

		return(true);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| ($phonehintsgroupid = $this->add_phonehintsgroup()) === false)
		{
			$r = false;
			if($phonehintsgroupid !== null)
				$this->_reverse_add();
		}

		$this->_status = '';

		return($r);
	}

	function add_phonehintsgroup()
	{
		if(($rs = $this->get_result('phonehintsgroup')) === null
		|| $rs === false)
			return(false);

		$rs['deletable'] = 1;
		$this->_return['phonehintsgroup'] = $this->_ctiphonehintsgroup->add($rs);
		return($this->_return['phonehintsgroup']);
	}

	function _reverse_add()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'phonehintsgroup':
					$this->_ctiphonehintsgroup->delete($val);
					break;
			}
		}

		return(true);
	}

	function edit()
	{
		$r = true;

		$this->_status = 'edit';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| $this->edit_phonehintsgroup() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

    function edit_phonehintsgroup()
    {
        if(dwho_issa('phonehintsgroup',$this->_info) === false
        || ($rs = $this->get_result('phonehintsgroup')) === null
        || $rs === false)
            return(false);

        return(($this->_return['phonehintsgroup'] = $this->_ctiphonehintsgroup->edit($this->_info['phonehintsgroup']['id'],$rs)));
    }

	function _reverse_edit()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'edit'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'phonehintsgroup':
					if(isset($this->_origin['phonehintsgroup']) === false
					|| $this->_origin['phonehintsgroup'] === false)
						$this->delete_phonehintsgroup();
					else
						$this->_ctiphonehintsgroup->edit_origin($this->_origin['phonehintsgroup']);
					break;
			}
		}

		return(true);
	}

	function delete()
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| $this->delete_phonehintsgroup() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	function delete_phonehintsgroup()
	{
		if(dwho_issa('phonehintsgroup',$this->_info) === false
		|| (string) $this->_info['phonehintsgroup']['id'] === '1')
			return(false);

		$r = $this->_ctiphonehintsgroup->delete($this->_info['phonehintsgroup']['id']);

		if($this->_status === 'delete')
			$this->_return['phonehintsgroup'] = $r;

		return($r);
	}

	function _reverse_delete()
	{
		if($this->_status !== 'delete'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'phonehintsgroup':
                    if(isset($this->_origin['phonehintsgroup']) === true
                    && $this->_origin['phonehintsgroup'] !== false)
                        $this->_ctiphonehintsgroup->add_origin($this->_origin['phonehintsgroup']);
					break;
			}
		}

		return(true);
	}

	function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if($this->enable_phonehintsgroup() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return($r);
	}

	function disable()
	{
		$r = true;

		$this->_status = 'disable';
		$this->_return = array();

		if($this->disable_phonehintsgroup() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return(true);
	}

	function enable_phonehintsgroup()
	{
		return($this->_enable_disable_phonehintsgroup(false));
	}

	function disable_phonehintsgroup()
	{
		return($this->_enable_disable_phonehintsgroup(true));
	}

	function _enable_disable_phonehintsgroup($disable=false)
	{
		if(dwho_issa('phonehintsgroup',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_ctiphonehintsgroup->enable($this->_info['phonehintsgroup']['id']);
		else
			$r = $this->_ctiphonehintsgroup->disable($this->_info['phonehintsgroup']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['phonehintsgroup'] = $r;

		return($r);
	}

	function _reverse_enable_disable()
	{
		if(($this->_status !== 'enable' && $this->_status !== 'disable') === true
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		$disable = $this->_status === 'enable';

		$this->_status = '';

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'phonehintsgroup':
					$this->_enable_disable_phonehintsgroup($disable);
					break;
			}
		}

		return(true);
	}
}

?>
