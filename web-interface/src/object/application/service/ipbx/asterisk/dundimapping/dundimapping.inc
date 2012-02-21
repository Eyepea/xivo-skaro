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

class xivo_application_service_asterisk_dundimapping extends xivo_application_asterisk_abstract
{
	var $_dundimapping		   = false;

	function xivo_application_service_asterisk_dundimapping(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_dundimapping = &$this->_service->get_module('dundimapping')) === false)
			return(false);

		return(true);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['dundimapping'] = $this->_dundimapping->get($id,$disable)) === false)
			return(false);
		
		$this->_origin['dundimapping'] = $this->_dundimapping->get_origin();

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_elements()
	{
		$r = array();
		$r['dundimapping'] = $this->_dundimapping->get_element();

		return($r);
	}

	function get_dundimapping_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_dundimapping('search',$search,$disable,$order,$limit,$assoc));
	}

	function get_dundimapping_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_dundimapping('list',null,$disable,$order,$limit,$assoc));
	}

	function _get_dundimapping($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				//$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_dundimapping->get_all($disable,true,$order,$limit);
		}

		$this->_cnt = $this->_dundimapping->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$rs[$i]['id']] = $rs[$i];

			$ref = &$r[$rs[$i]['id']];

			$dundimapping = array();
			$ref = array_merge($ref,$this->_dundimapping->_prepare($dundimapping));

			$ref['description'] = $ref['description'];
			$ref['commented']   = (bool) $ref['commented'];

			$arr = array();
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

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
		|| dwho_issa('dundimapping',$arr) === false)
			return(false);

		$this->set_dundimapping($arr['dundimapping']);

		return(($this->get_errnb() < 1));
	}

	function set_dundimapping($arr)
	{
		$r = true;
		$arr['commented'] = false;

		if(($rs = $this->_dundimapping->chk_values($arr)) === false)
		{
			$r = false;
			$rs = $this->_dundimapping->get_filter_result();
			$this->_set_error('dundimapping', $this->_dundimapping->get_filter_error());
		}

		$this->_set_result('dundimapping',$rs);
		return($r);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$dundimappingid = null;

		if($this->get_errnb() > 0
		|| ($dundimappingid = $this->add_dundimapping()) === false)
		{
			$r = false;

			if($dundimappingid !== null)
				$this->_reverse_add($dundimappingid);
		}

		$this->_status = '';

		return($r);
	}

	function add_dundimapping()
	{
		if(($rs = $this->get_result('dundimapping')) === null
		|| $rs === false)
			return(false);

		return(($this->_return['dundimapping'] = $this->_dundimapping->add($rs)));
	}

	function _reverse_add($dundimappingid)
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| ($dundimappingid = dwho_ulongint($dundimappingid)) === 0
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'dundimapping':
					$this->_dundimapping->delete($dundimappingid);
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
		|| $this->edit_dundimapping() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	function edit_dundimapping()
	{
		if(dwho_issa('dundimapping',$this->_info) === false
		|| ($rs = $this->get_result('dundimapping')) === null
		|| $rs === false)
			return(false);

		$rs['commented'] = $this->_info['dundimapping']['commented'];
		$this->_return['dundimapping'] = $this->_dundimapping->edit($this->_info['dundimapping']['id'], $rs);

		return($this->_return['dundimapping']);
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
				case 'dundimapping':
					if(isset($this->_origin['dundimapping']) === false
					|| $this->_origin['dundimapping'] === false)
						$this->delete_dundimapping();
					else
						$this->_dundimapping->edit_origin($this->_origin['dundimapping']);
					break;
			}
		}

		return(true);
	}

	function delete($id)
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();
		$this->_info['dundimapping'] = array('id' => $id);

		if($this->delete_dundimapping() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';
		return($r);
	}

	function delete_dundimapping()
	{
		if(dwho_issa('dundimapping',$this->_info) === false)
			return(false);

		$r = $this->_dundimapping->delete($this->_info['dundimapping']['id']);

		if($this->_status === 'delete')
			$this->_return['dundimapping'] = $r;

		return($r);
	}

	function enable($id)
	{
		$r = true;
		$this->_status = 'enable';
		$this->_return = array();
		$this->_info['dundimapping'] = array('id' => $id);

		if($this->enable_dundimapping() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function disable($id)
	{
		$r = true;
		$this->_status = 'disable';
		$this->_return = array();
		$this->_info['dundimapping'] = array('id' => $id);

		if($this->disable_dundimapping() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function enable_dundimapping()
	{
		return($this->_enable_disable_dundimapping(false));
	}

	function disable_dundimapping()
	{
		return($this->_enable_disable_dundimapping(true));
	}

	function _enable_disable_dundimapping($disable=false)
	{
		if(dwho_issa('dundimapping',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_dundimapping->enable($this->_info['dundimapping']['id']);
		else
			$r = $this->_dundimapping->disable($this->_info['dundimapping']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['dundimapping'] = $r;

		return($r);
	}

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_add($data) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}
}
?>
