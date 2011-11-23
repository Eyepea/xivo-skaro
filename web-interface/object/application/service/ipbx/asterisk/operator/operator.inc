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

class xivo_application_service_asterisk_operator extends xivo_application_asterisk_abstract
{
	private		$_dso			= null;
	private		$_operator		= false;
	private		$_trunkfeatures	= false;
	private 	$_operator_destination	= false;
	private 	$_operator_trunk	= false;
	protected 	$_trunklist 	= false;

	public function __construct(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_operator = &$this->_service->get_module('operator')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function load_components()
	{
		$this->_components = true;

		if(($this->_operator_destination = &$this->_service->get_module('operator_destination')) === false
		|| ($this->_operator_trunk = &$this->_service->get_module('operator_trunk')) === false
		|| ($this->_trunkfeatures = &$this->_service->get_module('trunkfeatures')) === false)
			return(false);

		return(true);
	}

	public function get($id,$disable=null,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['operator'] = $this->_operator->get($id)) === false)
			return(false);

		$this->_origin['operator'] = $this->_operator->get_origin();

		if($this->_components === false)
			return($this->_info);

		$this->_get_destination();
		$this->_get_trunk(false,false);

		return($this->_info);
	}

	public function get_nb($arr=null,$disable=null)
	{
		if(is_array($arr) === false)
			$arr = array();

		return($this->_operator->get_nb($arr,$disable));
	}

	private function _get_destination()
	{
		$this->_info['destination'] = false;
		$this->_origin['destination'] = false;

		$where = array();
		$where['operator_id'] = $this->_info['operator']['id'];

		if($this->_operator_destination === false
		|| ($this->_info['destination'] = $this->_operator_destination->get_all_where($where)) === false
		|| isset($this->_info['destination'][0]) === false)
			return(false);

		$this->_origin['destination'] = $this->_operator_destination->get_origin_list();

		return($this->_info['destination']);
	}

	private function _get_trunk($fullinfo=false,$assoc)
	{
		$this->_info['trunk'] = false;
		$this->_origin['trunk'] = false;

		$where = array();
		$where['operator_id'] = $this->_info['operator']['id'];

		if($this->_operator_trunk === false
		|| ($rs = $this->_operator_trunk->get_all_where($where)) === false)
			return(false);

		if(($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$trunk_id = (int) $rs[$i]['trunk_id'];
			$r[$trunk_id] = $rs[$i];

			$ref = &$r[$trunk_id];

			if (($tf = $this->_trunkfeatures->get($trunk_id)) === false)
				continue;

			if (((bool) $fullinfo) === true)
			{
				if(($apptrunk = &$this->_service->get_application('trunk',
							    array('protocol' => $tf['protocol']))) === false
				|| ($trunk = $apptrunk->get($trunk_id)) === false)
					$ref = $tf;
				$ref = $trunk;
			}
			else
				$ref = $tf;
		}

		if((bool) $assoc === false)
			$r = array_values($r);

		$this->_info['trunk'] = $r;

		$this->_origin['trunk'] = $this->_operator_trunk->get_origin_list();

		return($this->_info['trunk']);
	}

	public function get_elements()
	{
		$r = array();

		$r['operator'] = $this->_operator->get_element();
		$r['destination'] = $this->_operator_destination->get_element();
		$r['trunk'] = $this->_operator_trunk->get_element();

		return($r);
	}

	public function get_operator_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_operator('search',$search,$disable,$order,$limit,$assoc));
	}

	public function get_operator_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_operator('list',null,$disable,$order,$limit,$assoc));
	}

	private function _get_operator($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
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

			$ref = $this->_operator->_prepare($ref);

			$this->_info['operator']['id'] = $rs[$i]['id'];
			$ref['trunk'] = $this->_get_trunk(true,$assoc);
			$ref['destination'] = $this->_get_destination();
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
		|| dwho_issa('operator',$arr) === false)
			return(false);

		$this->_set_operator($arr['operator']);

		if (isset($arr['trunk']) === true)
			$this->_set_trunk($arr['trunk']);

		if(isset($arr['destination']) === true)
			$this->_set_destination($arr['destination']);

		return(($this->get_errnb() < 1));
	}

	private function _set_operator($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('operator',null);
			$this->_set_error('operator','invalid data');
			return(false);
		}
		else if(($rs = $this->_operator->chk_values($arr)) === false)
		{
			$this->_set_result('operator',$this->_operator->get_filter_result());
			$this->_set_error('operator',$this->_operator->get_filter_error());
			return(false);
		}

		$this->_set_result('operator',$arr);

		return(true);
	}

	private function _set_trunk($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('trunk',null);
			$this->_set_error('trunk','invalid data');
			return(false);
		}

		$error = $reslist = array();
		$errnb = 0;

		for($i = 0;$i < count($arr);$i++)
		{
			$ref = &$arr[$i];
			if(($tf = $this->_trunkfeatures->get($ref)) === false
			|| empty($tf) === true
			|| ($apptrunk = &$this->_service->get_application('trunk',
						    array('protocol' => $tf['protocol']))) === false
			|| ($rs = $apptrunk->get($ref)) === false)
			{
				$errnb++;
				$error[$i] = 'bad_trunk';
			}
			else
			{
				$rs['id'] = $ref;
				array_push($reslist,$rs);
			}
		}
		$this->_set_result('trunk',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('trunk',$error);
			return(false);
		}

		return(true);
	}

	function _set_destination($arr)
	{
		if(is_array($arr) === false
		|| $this->_operator_destination === false
		|| ($operator = $this->get_result('operator')) === false)
			return(false);

		$reslist = $error = array();
		$errnb = 0;

		foreach($arr as $key => $list)
		{
			for($i = 0;$i < count($list);$i++)
			{
				if ($arr[$key][$i] === '')
					$reslist[$i][$key] = '';
				else
					$reslist[$i][$key] = $arr[$key][$i];
			}
		}

		if(empty($reslist) === true)
		{
			$this->_set_result('destination',false);
			$this->_set_error('destination','empty');
			return(false);
		}

		array_pop($reslist);

		for($i = 0;$i < count($reslist);$i++)
		{
			$ref = &$reslist[$i];
			if($this->_operator_destination->chk_values($ref) === false)
			{
				$errnb++;
				$error[$i] = $this->_operator_destination->get_filter_error();
			}
		}
		$this->_set_result('destination',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_error('destination',$error);
			return(false);
		}

		return(true);
	}

	function add()
	{
		$this->_status = 'add';
		$this->_return = array();
		$operatorid = null;

		if($this->get_errnb() > 0
		|| ($operatorid = $this->add_operator()) === false
		|| $this->add_trunk() === false
		|| $this->add_destination() === false)
		{
			if($operatorid !== null)
				$this->_reverse_add();

			$this->_status = '';
			return(false);
		}

		$this->_status = '';

		return(true);
	}

	function add_operator()
	{
		if(($rs = $this->get_result('operator')) === null
		|| $rs === false)
			return(false);

		$this->_return['operator'] = $this->_operator->add($rs);

		return($this->_return['operator']);
	}

	function add_trunk()
	{
		if(($rs = $this->get_result('trunk')) === null || $rs === false)
			return(false);

		$this->_return['trunk'] = array();

		$arr = array();
		$arr['operator_id'] = (int) $this->_return['operator'];

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$arr['trunk_id'] = (int) $ref['id'];
			if (($ret = $this->_operator_trunk->add($arr)) === false)
			{
				dwho_report::push('error','error during create trunk');
				return(false);
			}

			$this->_return['trunk'][] = $ret;
		}

		if(isset($this->_return['trunk'][0]) === false)
			$this->_return['trunk'] = false;

		return(true);
	}

	function add_destination()
	{
		if(($rs = $this->get_result('destination')) === null || $rs === false)
			return($rs);

		$this->_return['destination'] = array();

		$arr = array();
		$arr['operator_id'] = (int) $this->_return['operator'];

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$arr = array_merge($arr,$ref);
			if (($ret = $this->_operator_destination->add($arr)) === false)
			{
				dwho_report::push('error','error during create destination '.$ref['name']);
				return(false);
			}

			$this->_return['destination'][] = $ret;
		}

		if(isset($this->_return['destination'][0]) === false)
			$this->_return['destination'] = false;

		return(true);
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
				case 'operator':
					$this->_operator->delete($val);
					break;
				case 'destination':
					if(is_array($val) === false)
						continue;

					foreach($val as $opdval)
						$this->_operator_destination->delete($opdval);
					break;
				case 'trunk':
					if(is_array($val) === false)
						continue;

					foreach($val as $optval)
						$this->_operator_trunk->delete($optval);
					break;
			}
		}

		return(true);
	}

	function edit()
	{
		$this->_status = 'edit';
		$this->_return = array();

		if(is_array($this->_info) === false
		|| empty($this->_info) === true
		|| $this->get_errnb() > 0
		|| $this->edit_operator() === false
		|| $this->edit_destination() === false
		|| $this->edit_trunk() === false)
		{
			$this->_status = '';
			return(false);
		}

		$this->_status = '';

		return(true);
	}

	public function edit_operator()
	{
		if($this->_info['operator'] === false
		|| ($rs = $this->get_result('operator')) === null
		|| $rs === false)
			return(false);

		$return = false;

		if (($return = $this->_operator->edit($this->_info['operator']['id'],$rs)) === false)
			return(false);

		$this->_return['operator'] = $this->_info['operator']['id'];

		return($return);
	}

	public function edit_destination()
	{
		if($this->_info['destination'] === false)
			return($this->add_destination());

		$this->_return['destination'] = $this->_delete_destination($this->_return['operator']);

		return($this->add_destination());
	}

	public function edit_trunk()
	{
		if($this->_info['trunk'] === false)
			return($this->add_trunk());

		$this->_return['trunk'] = $this->_delete_trunk($this->_return['operator']);

		return($this->add_trunk());
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
				case 'operator':
					if(isset($this->_origin['operator']) === false
					|| $this->_origin['operator'] === false)
						$this->delete_operator();
					else
						$this->_operator->edit_origin($this->_origin['operator']);
					break;
				case 'destination':
					if(dwho_issa('operator',$this->_info) === false)
						continue;

					$this->_delete_destination($this->_info['operator']['id']);

					if(isset($this->_origin['destination']) === true
					&& $this->_origin['destination'] !== false)
						$this->_operator_destination->add_origin_list($this->_origin['destination']);
					break;
				case 'trunk':
					if(dwho_issa('operator',$this->_info) === false)
						continue;

					$this->_delete_trunk($this->_info['operator']['id']);

					if(isset($this->_origin['trunk']) === true
					&& $this->_origin['trunk'] !== false)
						$this->_operator_trunk->add_origin_list($this->_origin['trunk']);
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

		if($this->delete_operator() === false
		|| $this->_delete_destination($this->_info['operator']['id']) === false
		|| $this->_delete_trunk($this->_info['operator']['id']) === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function delete_operator()
	{
		if(dwho_issa('operator',$this->_info) === false)
			return(false);

		$r = $this->_operator->delete($this->_info['operator']['id']);

		if($this->_status === 'delete')
			$this->_return['operator'] = $r;

		return($r);
	}

	private function _delete_destination($operatorid)
	{
		if(dwho_issa('destination',$this->_info) === false)
			return(null);
		else if(dwho_issa('operator',$this->_info) === false
		|| is_scalar($operatorid) === false
		|| $this->_operator_destination === false)
			return(false);

		$where = array();
		$where['operator_id'] = $operatorid;

		$r = $this->_operator_destination->delete_where($where);

		if($this->_status === 'delete')
			$this->_return['destination'] = $r;

		return($r);
	}

	private function _delete_trunk($operatorid)
	{
		if(dwho_issa('trunk',$this->_info) === false)
			return(null);
		else if(dwho_issa('operator',$this->_info) === false
		|| is_scalar($operatorid) === false
		|| $this->_operator_trunk === false)
			return(false);

		$where = array();
		$where['operator_id'] = $operatorid;

		$r = $this->_operator_trunk->delete_where($where);

		if($this->_status === 'delete')
			$this->_return['trunk'] = $r;

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
