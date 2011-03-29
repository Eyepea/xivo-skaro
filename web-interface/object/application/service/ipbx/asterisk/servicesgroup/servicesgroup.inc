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

class xivo_application_service_asterisk_servicesgroup extends xivo_application_asterisk_abstract
{
	private		$_dso				= null;
	private		$_servicesgroup		= false;
	private		$_servicesgroup_user	= false;
	private 	$_userfeatures		= false;
	private 	$_user				= false;

	public function __construct(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_servicesgroup = &$this->_service->get_module('servicesgroup')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function load_components()
	{
		$this->_components = true;

		if(($this->_servicesgroup_user = &$this->_service->get_module('servicesgroup_user')) === false
		|| ($this->_userfeatures = &$this->_service->get_module('userfeatures')) === false
		|| ($this->_user = &$this->_service->get_application('user',null,false)) === false)
			return(false);

		return(true);
	}

	public function get($id,$disable=null,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['servicesgroup'] = $this->_servicesgroup->get($id)) === false)
			return(false);

		$this->_origin['servicesgroup'] = $this->_servicesgroup->get_origin();

		if($this->_components === false)
			return($this->_info);

		$this->_get_user();

		return($this->_info);
	}

	public function get_nb($arr=null,$disable=null)
	{
		if(is_array($arr) === false)
			$arr = array();

		return($this->_servicesgroup->get_nb($arr,$disable));
	}

	private function _get_user($assoc=false)
	{
		$this->_info['user'] = false;
		$this->_origin['user'] = false;

		$where = array();
		$where['servicesgroup_id'] = $this->_info['servicesgroup']['id'];

		if($this->_servicesgroup_user === false
		|| ($rs = $this->_servicesgroup_user->get_all_where($where)) === false)
			return(false);

		if(($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$user_id = (int) $rs[$i]['userfeatures_id'];
			$r[$user_id] = $rs[$i];

			$ref = &$r[$user_id];

			if (($tf = $this->_userfeatures->get($user_id)) === false)
				continue;

			$ref = $tf;
		}

		if((bool) $assoc === false)
			$r = array_values($r);

		$this->_info['user'] = $r;

		$this->_origin['user'] = $this->_servicesgroup_user->get_origin_list();

		return($this->_info['user']);
	}

	public function get_elements()
	{
		$r = array();

		$r['servicesgroup'] = $this->_servicesgroup->get_element();
		$r['user'] = $this->_servicesgroup_user->get_element();

		return($r);
	}

	public function get_servicesgroup_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_servicesgroup('search',$search,$disable,$order,$limit,$assoc));
	}

	public function get_servicesgroup_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_servicesgroup('list',null,$disable,$order,$limit,$assoc));
	}

	private function _get_servicesgroup($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			default:
				$rs = $this->_dso->get_all($disable,$order,$limit);
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = $identity = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$rs[$i]['id']] = $rs[$i];

			$ref = &$r[$rs[$i]['id']];

			$ref = $this->_servicesgroup->_prepare($ref);

			$this->_info['servicesgroup']['id'] = $rs[$i]['id'];
			#$ref['user'] = $this->_get_user(true);
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	public function set_add($arr)
	{
		return($this->_set('add',$arr));
	}

	public function set_edit($arr)
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr));
	}

	private function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('servicesgroup',$arr) === false)
			return(false);

		$this->_set_servicesgroup($arr['servicesgroup']);

		if (isset($arr['user']) === true)
			$this->_set_user($arr['user']);

		return(($this->get_errnb() < 1));
	}

	private function _set_servicesgroup($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('servicesgroup',null);
			$this->_set_error('servicesgroup','invalid data');
			return(false);
		}
		else if(($rs = $this->_servicesgroup->chk_values($arr)) === false)
		{
			$this->_set_result('servicesgroup',$this->_servicesgroup->get_filter_result());
			$this->_set_error('servicesgroup',$this->_servicesgroup->get_filter_error());
			return(false);
		}

		$this->_set_result('servicesgroup',$arr);

		return(true);
	}

	private function _set_user($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('user',null);
			$this->_set_error('user','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if(($userfeatures = $this->_userfeatures->get($ref)) === false)
			{
				$errnb++;
				$error[$i] = 'bad_user';
			}
			else
			{
				$rs['id'] = (int) $ref;
				$rs['protocol'] = $userfeatures['protocol'];
				$rs['protocolid'] = (int) $userfeatures['protocolid'];
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('user',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('user',$error);
			return(false);
		}

		return(true);
	}

	public function add()
	{
		$this->_status = 'add';
		$this->_return = array();
		$servicesgroupid = null;

		if($this->get_errnb() > 0
		|| ($servicesgroupid = $this->add_servicesgroup()) === false
		|| $this->add_user() === false)
		{
			if($servicesgroupid !== null)
				$this->_reverse_add();

			$this->_status = '';
			return(false);
		}

		$this->_status = '';

		return(true);
	}

	public function add_servicesgroup()
	{
		if(($rs = $this->get_result('servicesgroup')) === null
		|| $rs === false)
			return(false);

		$this->_return['servicesgroup'] = $this->_servicesgroup->add($rs);

		return($this->_return['servicesgroup']);
	}

	public function add_user()
	{
		if(($rs = $this->get_result('user')) === null || $rs === false)
			return(false);

		$this->_return['user'] = array();

		$servicesgroup = $this->get_result('servicesgroup');
		$wac = array();
		$wac['accountcode'] = $servicesgroup['accountcode'];

		$arr = array();
		$arr['servicesgroup_id'] = (int) $this->_return['servicesgroup'];

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$arr['userfeatures_id'] = (int) $ref['id'];
			if (($ret = $this->_servicesgroup_user->add($arr)) === false
			|| ($user = $this->_service->get_module('user'.$ref['protocol'])) === false
			|| $user->edit($ref['protocolid'],$wac) === false)
			{
				dwho_report::push('error','error during proccess user');
				return(false);
			}

			$this->_return['user'][] = $ret;
		}

		if(isset($this->_return['user'][0]) === false)
			$this->_return['user'] = false;

		return(true);
	}

	private function _reverse_add()
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
				case 'servicesgroup':
					$this->_servicesgroup->delete($val);
					break;
				case 'user':
					if(is_array($val) === false)
						continue;

					foreach($val as $optval)
						$this->_servicesgroup_user->delete($optval);
					break;
			}
		}

		return(true);
	}

	public function edit()
	{
		$this->_status = 'edit';
		$this->_return = array();

		if(is_array($this->_info) === false
		|| empty($this->_info) === true
		|| $this->get_errnb() > 0
		|| $this->edit_servicesgroup() === false
		|| $this->edit_user() === false)
		{
			$this->_status = '';
			return(false);
		}

		$this->_status = '';

		return(true);
	}

	public function edit_servicesgroup()
	{
		if($this->_info['servicesgroup'] === false
		|| ($rs = $this->get_result('servicesgroup')) === null
		|| $rs === false)
			return(false);

		$return = false;

		if (($return = $this->_servicesgroup->edit($this->_info['servicesgroup']['id'],$rs)) === false)
			return(false);

		$this->_return['servicesgroup'] = $this->_info['servicesgroup']['id'];

		return($return);
	}

	public function edit_user()
	{
		if ($this->_status === 'edit'
		&& $this->_info['user'] === false
		&& $this->get_result('user') === null)
			return(true);
		elseif($this->_info['user'] === false)
			return($this->add_user());

		$this->_return['user'] = $this->_delete_user($this->_return['servicesgroup']);

		return($this->add_user());
	}

	private function _reverse_edit()
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
				case 'servicesgroup':
					if(isset($this->_origin['servicesgroup']) === false
					|| $this->_origin['servicesgroup'] === false)
						$this->delete_servicesgroup();
					else
						$this->_servicesgroup->edit_origin($this->_origin['servicesgroup']);
					break;
				case 'user':
					if(dwho_issa('user',$this->_info) === false)
						continue;

					$this->_delete_user($this->_info['servicesgroup']);

					if(isset($this->_origin['user']) === true
					&& $this->_origin['user'] !== false)
						$this->_servicesgroup_user->add_origin_list($this->_origin['user']);
					break;
			}
		}

		return(true);
	}

	public function delete()
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();

		if($this->delete_servicesgroup() === false
		|| $this->_delete_user($this->_info['servicesgroup']) === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function delete_servicesgroup()
	{
		if(dwho_issa('servicesgroup',$this->_info) === false)
			return(false);

		$r = $this->_servicesgroup->delete($this->_info['servicesgroup']);

		if($this->_status === 'delete')
			$this->_return['servicesgroup'] = $r;

		return($r);
	}

	private function _delete_user($servicesgroupid)
	{
		if(dwho_issa('user',$this->_info) === false)
			return(null);
		else if(dwho_issa('servicesgroup',$this->_info) === false
		|| is_scalar($servicesgroupid) === false
		|| $this->_servicesgroup_user === false)
			return(false);

		$where = array();
		$where['servicesgroup_id'] = $servicesgroupid;

		$r = $this->_servicesgroup_user->delete_where($where);

		$servicesgroup = $this->get_result('servicesgroup');
		$wac = array();
		$wac['accountcode'] = null;

		$rs = $this->_info['user'];

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$arr['userfeatures_id'] = (int) $ref['id'];
			if (($user = $this->_service->get_module('user'.$ref['protocol'])) === false
			|| $user->edit($ref['protocolid'],$wac) === false)
			{
				dwho_report::push('error','error during proccess user');
				return(false);
			}
		}

		if($this->_status === 'delete')
			$this->_return['user'] = $r;

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

	function edit_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_edit($data) === false
		|| $this->edit() === false)
			return(false);

		return(true);
	}
}

?>
