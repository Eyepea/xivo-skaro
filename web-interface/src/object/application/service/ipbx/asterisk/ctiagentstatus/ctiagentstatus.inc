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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_ctiagentstatus extends xivo_application_asterisk_abstract
{
	var $_ctiagentstatus = false;

	function xivo_application_service_asterisk_ctiagentstatus(&$service,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);
		if(($this->_ctiagentstatus = &$this->_service->get_module('ctiagentstatus')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function get_agentstatus_list($order=null,$limit=null,$assoc=false,$idgroup=1)
	{
	    $w = array();
	    $w['idgroup'] = (int) $idgroup;

		if(($rs = $this->_ctiagentstatus->get_all_where($w,null,true,$order,$limit)) === false
		|| ($nb = count($rs)) === 0)
		{
			$this->_cnt = $this->_ctiagentstatus->get_cnt();
			return(false);
		}

		$r = $info = array();
		for($i = 0;$i < $nb;$i++)
		{
			$info['ctiagentstatus'] = $rs[$i];
			$r[$info['ctiagentstatus']['id']] = $info;
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	function get_agentstatus_edit()
	{
		return(false);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		$this->_info['agentstatus'] = $this->_ctiagentstatus->get($id);

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_nb($arr=null,$disable=null)
	{
		return($this->_ctiagentstatus->get_nb($arr,$disable));
	}

	function get_elements()
	{
		$r = array();
		$r['agentstatus'] = $this->_ctiagentstatus->get_element();

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
		|| dwho_issa('agentstatus',$arr) === false)
			return(false);

		$this->set_agentstatus($arr['agentstatus']);

		return(($this->get_errnb() < 1));
	}

	function set_agentstatus($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('agentstatus',null);
			$this->_set_error('agentstatus','invalid data');
			return(false);
		}
		else if(($rs = $this->_ctiagentstatus->chk_values($arr)) === false)
		{
			$this->_set_result('agentstatus',$this->_ctiagentstatus->get_filter_result());
			$this->_set_error('agentstatus',$this->_ctiagentstatus->get_filter_error());
			return(false);
		}

		$this->_set_result('agentstatus',$rs);

		return(true);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| ($agentstatusid = $this->add_agentstatus()) === false)
		{
			$r = false;
			if($agentstatusid !== null)
				$this->_reverse_add();
		}

		$this->_status = '';

		return($r);
	}

	function add_agentstatus()
	{
		if(($rs = $this->get_result('agentstatus')) === null
		|| $rs === false)
			return(false);

		$this->_return['agentstatus'] = $this->_ctiagentstatus->add($rs);
		return($this->_return['agentstatus']);
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
				case 'agentstatus':
					$this->_ctiagentstatus->delete($val);
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
		|| $this->edit_agentstatus() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

    function edit_agentstatus()
    {
        if(dwho_issa('agentstatus',$this->_info) === false
        || ($rs = $this->get_result('agentstatus')) === null
        || $rs === false)
            return(false);

        return(($this->_return['agentstatus'] = $this->_ctiagentstatus->edit($this->_info['agentstatus']['id'],$rs)));
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
				case 'agentstatus':
					if(isset($this->_origin['agentstatus']) === false
					|| $this->_origin['agentstatus'] === false)
						$this->delete_agentstatus();
					else
						$this->_ctiagentstatus->edit_origin($this->_origin['agentstatus']);
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
		|| $this->delete_agentstatus() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	function delete_agentstatus()
	{
		if(dwho_issa('agentstatus',$this->_info) === false)
			return(false);

		$r = $this->_ctiagentstatus->delete($this->_info['agentstatus']['id']);

		if($this->_status === 'delete')
			$this->_return['agentstatus'] = $r;

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
				case 'agentstatus':
                    if(isset($this->_origin['agentstatus']) === true
                    && $this->_origin['agentstatus'] !== false)
                        $this->_ctiagentstatus->add_origin($this->_origin['agentstatus']);
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

		if($this->enable_agentstatus() === false)
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

		if($this->disable_agentstatus() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return(true);
	}

	function enable_agentstatus()
	{
		return($this->_enable_disable_agentstatus(false));
	}

	function disable_agentstatus()
	{
		return($this->_enable_disable_agentstatus(true));
	}

	function _enable_disable_agentstatus($disable=false)
	{
		if(dwho_issa('agentstatus',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_ctiagentstatus->enable($this->_info['agentstatus']['id']);
		else
			$r = $this->_ctiagentstatus->disable($this->_info['agentstatus']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['agentstatus'] = $r;

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
				case 'agentstatus':
					$this->_enable_disable_agentstatus($disable);
					break;
			}
		}

		return(true);
	}
}

?>
