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

class xivo_application_service_asterisk_dundipeer extends xivo_application_asterisk_abstract
{
	var $_dso          = null;
	var $_dundipeer    = false;

	function xivo_application_service_asterisk_dundipeer(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_dundipeer = &$this->_service->get_module('dundipeer')) === false)
			return(false);

		return(true);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['dundipeer'] = $this->_dundipeer->get($id,$disable)) === false)
			return(false);
		
		$this->_origin['dundipeer'] = $this->_dundipeer->get_origin();

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_elements()
	{
		$r = array();
		$r['dundipeer'] = $this->_dundipeer->get_element();

		return($r);
	}

	function get_dundipeer_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_dundipeer('search',$search,$disable,$order,$limit,$assoc));
	}

	function get_dundipeer_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_dundipeer('list',null,$disable,$order,$limit,$assoc));
	}

	function _get_dundipeer($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				//$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_dundipeer->get_all($disable,true,$order,$limit);
		}

		$this->_cnt = $this->_dundipeer->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$rs[$i]['id']] = $rs[$i];

			$ref = &$r[$rs[$i]['id']];
			$ref = $this->_dundipeer->_prepare($ref);
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	/*
	function get_result_for_display()
	{
		$r = $this->get_result();

		if(is_array($r) === false)
			$r = array();

		if(dwho_issa('dundipeer',$r) === false)
			$r['dundipeer'] = array();

		return($r);
	}
*/
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
		|| dwho_issa('dundipeer',$arr) === false)
			return(false);

		$this->set_dundipeer($arr['dundipeer']);

		return(($this->get_errnb() < 1));
	}

	function set_dundipeer($arr)
	{
		$r = true;
		$arr['commented'] = false;

		if(($rs = $this->_dundipeer->chk_values($arr)) === false)
		{
			$r = false;
			$rs = $this->_dundipeer->get_filter_result();
			$this->_set_error('dundipeer', $this->_dundipeer->get_filter_error());
		}

		$this->_set_result('dundipeer',$rs);
		return($r);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$dundipeerid = null;

		if($this->get_errnb() > 0
		|| ($dundipeerid = $this->add_dundipeer()) === false)
		{
			$r = false;

			if($dundipeerid !== null)
				$this->_reverse_add($dundipeerid);
		}

		$this->_status = '';

		return($r);
	}

	function add_dundipeer()
	{
		if(($rs = $this->get_result('dundipeer')) === null
		|| $rs === false)
			return(false);

		return(($this->_return['dundipeer'] = $this->_dundipeer->add($rs)));
	}

	function _reverse_add($dundipeerid)
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| ($dundipeerid = dwho_ulongint($dundipeerid)) === 0
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'dundipeer':
					$this->_dundipeer->delete($dundipeerid);
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
		|| $this->edit_dundipeer() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	function edit_dundipeer()
	{
		if(dwho_issa('dundipeer',$this->_info) === false
		|| ($rs = $this->get_result('dundipeer')) === null
		|| $rs === false)
			return(false);

		$rs['commented'] = $this->_info['dundipeer']['commented'];
		$this->_return['dundipeer'] = $this->_dundipeer->edit($this->_info['dundipeer']['id'], $rs);

		return($this->_return['dundipeer']);
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
				case 'dundipeer':
					if(isset($this->_origin['dundipeer']) === false
					|| $this->_origin['dundipeer'] === false)
						$this->delete_dundipeer();
					else
						$this->_dundipeer->edit_origin($this->_origin['dundipeer']);
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
		$this->_info['dundipeer'] = array('id' => $id);

		if($this->delete_dundipeer() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';
		return($r);
	}

	function delete_dundipeer()
	{
		if(dwho_issa('dundipeer',$this->_info) === false)
			return(false);

		$r = $this->_dundipeer->delete($this->_info['dundipeer']['id']);

		if($this->_status === 'delete')
			$this->_return['dundipeer'] = $r;

		return($r);
	}

	function enable($id)
	{
		$r = true;
		$this->_status = 'enable';
		$this->_return = array();
		$this->_info['dundipeer'] = array('id' => $id);

		if($this->enable_dundipeer() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function disable($id)
	{
		$r = true;
		$this->_status = 'disable';
		$this->_return = array();
		$this->_info['dundipeer'] = array('id' => $id);

		if($this->disable_dundipeer() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function enable_dundipeer()
	{
		return($this->_enable_disable_dundipeer(false));
	}

	function disable_dundipeer()
	{
		return($this->_enable_disable_dundipeer(true));
	}

	function _enable_disable_dundipeer($disable=false)
	{
		if(dwho_issa('dundipeer',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_dundipeer->enable($this->_info['dundipeer']['id']);
		else
			$r = $this->_dundipeer->disable($this->_info['dundipeer']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['dundipeer'] = $r;

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
