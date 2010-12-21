<?php

#
# XiVO Web-Interface
# Copyright (C) 2009-2010  Proformatique <technique@proformatique.com>
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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','xivo.inc'),true);

class xivo_application_xivo_object_stats_conf extends xivo_application_xivo_object_abstract
{
	var $_stats_conf	= false;
	var $_queuefeatures	= false;

	public function __construct(&$xobj,&$dso,$param=null,$components=true)
	{		
		parent::__construct(&$xobj);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_stats_conf = &$this->_xobj->get_module('stats_conf')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	public function load_components()
	{
		$this->_components = true;

		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($this->_queuefeatures = &$_SRE->get_module('ipbx','queuefeatures')) === false)
			return(false);

		return(true);
	}

	public function get($id,$disable=null)
	{
		if(($r = $this->_dso->get($id)) === false)
			return(false);

		$r['id'] = (int) $r['id'];
		$r['disable'] = (bool) $r['disable'];
		$r['monday'] = (bool) $r['monday'];
		$r['tuesday'] = (bool) $r['tuesday'];
		$r['wednesday'] = (bool) $r['wednesday'];
		$r['thursday'] = (bool) $r['thursday'];
		$r['friday'] = (bool) $r['friday'];
		$r['saturday'] = (bool) $r['saturday'];
		$r['sunday'] = (bool) $r['sunday'];
			
		if(empty($r) === true)
			return(false);
		
		$this->_info['stats_conf'] = $r;
			
		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	public function get_nb($arr=null,$disable=null)
	{
		return($this->_stats_conf->get_nb($arr,$disable));
	}

	public function get_elements()
	{
		$r = array();
		$r['stats_conf'] = $this->_stats_conf->get_element();

		return($r);
	}

	public function get_stats_conf_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_entities('search',$search,$disable,$order,$limit,$assoc));
	}

	public function get_stats_conf_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_stats_conf('list',null,$disable,$order,$limit,$assoc));
	}

	public function _get_stats_conf($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$order,$limit);
				$this->_cnt = $this->_dso->get_cnt();
				break;
			case 'list':
			default:
				$action = 'list';
				$rs = $this->_dso->get_all($disable,$order,$limit);
				$this->_cnt = $this->_dso->get_cnt();				
		}

		if($rs === false 
		|| ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$i] = $rs[$i];
			$ref = &$r[$i];
			$ref['disable'] = (bool) $ref['disable'];
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

	public function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('stats_qos',$arr) === false
		|| dwho_issa('stats_conf',$arr) === false
		|| dwho_issa('workhour_start',$arr) === false
		|| dwho_issa('workhour_end',$arr) === false)
			return(false);
    
    	$workhour_start = $arr['workhour_start'];
    	$workhour_end = $arr['workhour_end'];
    	
    	if ($workhour_start['h'] === '00')
			$this->_set_error('workhour_start','h',('empty'));
    	
    	if ($workhour_end['h'] === '00')
			$this->_set_error('workhour_end','h',('empty'));
    
    	$arr['stats_conf']['hour_start'] = $workhour_start['h'].':'.$workhour_start['m'];
    	$arr['stats_conf']['hour_end'] = $workhour_end['h'].':'.$workhour_end['m'];

		$this->set_stats_qos($arr['stats_qos']);
		$this->set_stats_conf($arr['stats_conf']);

		return(($this->get_errnb() < 1));
	}

	public function set_stats_qos($arr) {
		
		if(is_array($arr) === false)
		{
			$this->_set_result('stats_qos',null);
			$this->_set_error('stats_qos','invalid data');
			return(false);
		}

		$this->_set_result('stats_qos',$arr);

		return(true);
		
	}

	public function set_stats_conf($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('stats_conf',null);
			$this->_set_error('stats_conf','invalid data');
			return(false);
		}

		$arr['disable'] = false;

		if(($rs = $this->_stats_conf->chk_values($arr)) === false)
		{
			$this->_set_result('stats_conf',$this->_stats_conf->get_filter_result());
			$this->_set_error('stats_conf',$this->_stats_conf->get_filter_error());
			return(false);
		}

		$this->_set_result('stats_conf',$rs);

		return(true);
	}

	public function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();

		if(($this->_dso->get_stats_conf_name_already_exist($this->_result['stats_conf']['name'])) === false)
		{
			$this->_set_error('stats_conf',array('name' => 'already_exist'));
			return(false);
		}

		if($this->get_errnb() > 0
		|| $this->add_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function add_stats_conf()
	{
		if(($rs = $this->get_result('stats_conf')) === null
		|| $rs === false)
			return(false);

		$this->_return['stats_conf'] = $this->_stats_conf->add($rs);

		return($this->_return['stats_conf']);
	}

	public function edit()
	{
		$r = true;

		$this->_status = 'edit';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| $this->edit_stats_conf() === false
		|| $this->edit_queuefeatures() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	public function edit_queuefeatures()
	{		
		if(($rs = $this->get_result('stats_qos')) === null
		|| $rs === false
		|| is_array($rs) === false)
			return(false);
			
		$this->_return['queuefeatures'] = true;
			
		foreach ($rs as $id => $stats_qos) {
			
			if (($this->_queuefeatures->edit($id,array('stats_qos' => $stats_qos))) === false)
				$this->_return['queuefeatures'] = false;
		
		}

		return($this->_return['queuefeatures']);
	}

	public function edit_stats_conf()
	{
		if(dwho_issa('stats_conf',$this->_info) === false
		|| ($rs = $this->get_result('stats_conf')) === null
		|| $rs === false)
			return(false);

		$rs['disable'] = $this->_info['stats_conf']['disable'];

		$this->_return['stats_conf'] = $this->_stats_conf->edit($this->_info['stats_conf']['id'],$rs);

		return($this->_return['stats_conf']);
	}

	public function _reverse_edit()
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
				case 'stats_conf':
					if(isset($this->_origin['stats_conf']) === false
					|| $this->_origin['stats_conf'] === false)
						$this->delete_stats_conf();
					else
						$this->_stats_conf->edit_origin($this->_origin['stats_conf']);
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

		if($this->delete_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function delete_all()
	{
		return($this->_dso->delete_all());
	}

	public function delete_stats_conf()
	{
		if(dwho_issa('stats_conf',$this->_info) === false)
			return(false);

		$r = $this->_stats_conf->delete($this->_info['stats_conf']['id']);

		if($this->_status === 'delete')
			$this->_return['stats_conf'] = $r;

		return($r);
	}

	public function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if($this->enable_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function disable()
	{
		$r = true;

		$this->_status = 'disable';
		$this->_return = array();

		if($this->disable_stats_conf() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	public function enable_stats_conf()
	{
		return($this->_enable_disable_stats_conf(false));
	}

	public function disable_stats_conf()
	{
		return($this->_enable_disable_stats_conf(true));
	}

	public function _enable_disable_stats_conf($disable=false)
	{
		if(dwho_issa('stats_conf',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_stats_conf->enable($this->_info['stats_conf']['id']);
		else
			$r = $this->_stats_conf->disable($this->_info['stats_conf']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['stats_conf'] = $r;

		return($r);
	}

	public function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_add($data) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}

	public function edit_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_edit($data) === false
		|| $this->edit() === false)
			return(false);

		return(true);
	}
}

?>
