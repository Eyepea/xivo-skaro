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

class xivo_application_service_asterisk_pickup extends xivo_application_asterisk_abstract
{
	var $_pickup		   = false;
	var $_pickupmember = false;

	function xivo_application_service_asterisk_pickup(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_pickup = &$this->_service->get_module('pickup')) === false)
			return(false);
		else if(($this->_pickupmember = &$this->_service->get_module('pickupmember')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function load_components()
	{
		$this->_components = true;

		return(true);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['pickup'] = $this->_pickup->get($id,$disable)) === false)
			return(false);

		$this->_info['members'] = $this->_pickupmember->get_all_where(array('pickupid' => $id, 'category'=>'member'));
		$this->_info['pickups'] = $this->_pickupmember->get_all_where(array('pickupid' => $id, 'category'=>'pickup'));

		$this->_origin['pickup'] = $this->_pickup->get_origin();

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_elements()
	{
		$r = array();
		$r['pickup'] = $this->_pickup->get_element();

		return($r);
	}

	function get_pickups_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_pickups('search',$search,$disable,$order,$limit,$assoc));
	}

	function get_pickups_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_pickups('list',null,$disable,$order,$limit,$assoc));
	}

	function _get_pickups($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_pickup->get_all();
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$rs[$i]['id']] = $rs[$i];

			$ref = &$r[$rs[$i]['id']];

			$pickup = array();
			$pickup['name'] = $ref['name'];

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

	function get_result_for_display()
	{
		$r = $this->get_result();

		if(is_array($r) === false)
			$r = array();

		if(dwho_issa('pickup',$r) === false)
			$r['pickup'] = array();

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
		|| dwho_issa('pickup',$arr) === false)
			return(false);

		$this->set_pickup($arr['pickup']);
		$this->set_pickup_members($arr['pickup']['members']);

		return(($this->get_errnb() < 1));
	}

	function set_pickup($arr, $dialaction)
	{
		$r = true;
		$arr['commented'] = false;

		if(($rs = $this->_pickup->chk_values($arr)) === false)
		{
			$r = false;
			$rs = $this->_pickup->get_filter_result();
			$this->_set_error('pickup', $this->_pickup->get_filter_error());
		}

		$this->_set_result('pickup',$rs);

		return($r);
	}

	function set_pickup_members($arr)
	{
		$errs = array();
		$members = array();
		foreach($arr as $rs)
		{
			if(($rs = $this->_pickupmember->chk_values($rs)) === false)
			{
				$errs[] = $this->_pickupmember->get_filter_error();
			}
			$members[] = $rs;
		}

		$this->_set_result('members',$members);
		return true;
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$pickupid = null;

		if($this->get_errnb() > 0
			|| ($pickupid = $this->add_pickup()) === false
		|| $this->add_pickup_members($pickupid) === false)
		{
			$r = false;

			if($pickupid !== null)
				$this->_reverse_add($pickupid);
		}

		$this->_status = '';

		return($r);
	}

	function add_pickup()
	{
		if(($rs = $this->get_result('pickup')) === null
		|| $rs === false)
			return(false);

		if(($id = $this->_pickup->_dso->get_empty()) === false)
		{
			dwho_report::push('error', 'max_pickup_groups');
			return(false);
		}
		$rs['id'] = $id;

		if($this->_pickup->add($rs) === false)
			return false;

		return(($this->_return['pickup'] = $id));
	}

	function add_pickup_members($pickupid)
	{
		foreach($this->get_result('members') as $rs)
		{
			$rs['pickupid'] = $pickupid;
			$ret = $this->_pickupmember->add($rs);
		}

		return true;
	}

	//TODO
	function _reverse_add($pickupid)
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| ($pickupid = dwho_ulongint($pickupid)) === 0
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'pickup':
					$this->_pickup->delete($pickupid);
					break;
				case 'dialaction':
					$this->_dialaction->reverse_add();
					break;
				case 'contextmember':
					$this->_contextmember->reverse_add();
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
		|| $this->edit_pickup() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	function edit_pickup()
	{
		if(dwho_issa('pickup',$this->_info) === false
		|| ($rs = $this->get_result('pickup')) === null
		|| $rs === false)
			return(false);

		$rs['commented'] = $this->_info['pickup']['commented'];
		$this->_return['pickup'] = true;

		if($this->_pickup->edit($this->_info['pickup']['id'], $rs) == false
		|| $this->edit_pickup_members($this->_info['pickup']['id']) == false)
		{
			$this->_return['pickup'] = false;
		}

		return($this->_return['pickup']);
	}


	function edit_pickup_members($pickupid)
	{
		$this->_pickupmember->delete_where(array('pickupid' => $pickupid));

		foreach($this->get_result('members') as $rs)
		{
			$rs['pickupid'] = $pickupid;
			$this->_pickupmember->add($rs);
		}

		return true;
	}

	// TODO
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
				case 'pickup':
					if(isset($this->_origin['pickup']) === false
					|| $this->_origin['pickup'] === false)
						$this->delete_pickup();
					else
						$this->_pickup->edit_origin($this->_origin['pickup']);
					break;
				case 'dialaction':
					$this->_dialaction->reverse_edit($this->_status);
					break;
				case 'contextmember':
					$this->_contextmember->reverse_edit($this->_status);
					break;
			}
		}

		return(true);
	}

	// TODO
	function delete()
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();

		if($this->delete_pickup() === false
		|| $this->delete_pickup_members() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';
		return($r);
	}

	function delete_pickup()
	{
		if(dwho_issa('pickup',$this->_info) === false)
			return(false);

		$r = $this->_pickup->delete($this->_info['pickup']['id']);

		if($this->_status === 'delete')
			$this->_return['pickup'] = $r;

		return($r);
	}

	function delete_pickup_members()
	{
		$r = $this->_pickupmember->delete_where(array('pickupid' => $this->_info['pickup']['id']));
		return $r;
	}


	//TODO
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
				case 'pickup':
					if(isset($this->_origin['pickup']) === true
					&& $this->_origin['pickup'] !== false)
						$this->_pickup->add_origin($this->_origin['pickup']);
					break;
				case 'dialaction':
					$this->_dialaction->add_origin_list();
					break;
				case 'contextmember':
					$this->_contextmember->add_origin_list();
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

		if($this->enable_pickup() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function disable()
	{
		$r = true;
		$this->_status = 'disable';
		$this->_return = array();

		if($this->disable_pickup() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function enable_pickup()
	{
		return($this->_enable_disable_pickup(false));
	}

	function disable_pickup()
	{
		return($this->_enable_disable_pickup(true));
	}

	function _enable_disable_pickup($disable=false)
	{
		if(dwho_issa('pickup',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_pickup->enable($this->_info['pickup']['id']);
		else
			$r = $this->_pickup->disable($this->_info['pickup']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['pickup'] = $r;

		return($r);
	}

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_add(array('pickup' => $data)) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}
}
?>
