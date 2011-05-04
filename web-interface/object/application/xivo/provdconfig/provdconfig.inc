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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','xivo.inc'),true);

class xivo_application_xivo_object_provdconfig extends xivo_application_xivo_object_abstract
{
	protected $_commonconf 		= false;
	protected $_provdconfig		= false;
	protected $_conf			= array();
	protected $_param			= array('internal'	=> false);

	public function __construct(&$xobj,$param=array(),$components=true)
	{
		$this->xivo_application_xivo_object_abstract(&$xobj);

		if(($this->_commonconf = &$this->_xobj->get_module('commonconf')) === false
		|| ($this->_provdconfig = &$this->_xobj->get_module('provdconfig')) === false
		|| $this->load_init($param) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	public function load_init($param=array())
	{
		$this->_reset_info();
		$this->_reset_params();
		$this->_reset();

		if(is_array($param) === true
		&& isset($param['internal']) === true)
			$this->_param['internal'] = (bool) $param['internal'];

		return(true);
	}

	public function load_components()
	{
		$this->_components = true;

		return(true);
	}
	
	/**
	 * NOTE: internal can take 3 values:
	 *	- false : don't search in internal config
	 *	- true  : search ONLY in internal config
	 *	- null  : search in BOTH internal and non-internal config
	 */
	public function get($id,$internal=false,$nocomponents=null)
	{
		if (($this->_info['config'] = $this->_provdconfig->get($id)) === false)
			return(false);
		
		return($this->_info);
	}
	
	public function get_config_list($search='',$order=null,$limit=null,$assoc=false,$internal=false,$type=null)
	{
		$list = $this->_provdconfig->get_configs('list',$search,$order,$limit,$assoc,$internal,$type);
		
		return($list);
	}

	public function get_elements()
	{
		$r = $this->_provdconfig->get_supp_elements();
		$r['config'] = $this->_provdconfig->get_element();
		
		return($r);
	}

	public function set_add($arr,$type='')
	{
		return($this->_set('add',$arr,$type));
	}

	public function set_edit($arr,$type='')
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr,$type));
	}

	private function _set($action,$arr,$type='')
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('config',$arr) === false)
			return(false);

		$this->set_config($arr['config'],$type);

		return(($this->get_errnb() < 1));
	}

	public function set_config($arr,$type='')
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('config',null);
			$this->_set_error('config','invalid data');
			return(false);
		}
		
		switch ($type)
		{
			case 'registrar':		
				$arr['parent_ids'] = array();
				$arr['raw_config'] = array();
				if(($rs = $this->_provdconfig->chk_confregistrar($arr)) === false)
				{
					dwho_report::push('error', 'fail to create config');
					return(false);
				}
				break;
			case 'network':
				break;
			default:
				if(($rs = $this->_provdconfig->chk_values($arr)) === false)
				{
					$this->_set_result('config',$this->_provdconfig->get_filter_result());
					$this->_set_error('config',$this->_provdconfig->get_filter_error());
					return(false);
				}
		}

		$this->_set_result('config',$rs);

		return(true);
	}

	public function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$configid = null;

		if($this->get_errnb() > 0
		|| ($configid = $this->add_config()) === false)
		{
			$r = false;
			if($configid !== null)
				$this->_reverse_add();
		}

		$this->_status = '';

		return($r);
	}

	public function add_config()
	{
		if(($rs = $this->get_result('config')) === null
		|| $rs === false)
			return(false);	
		
		$this->_return['config'] = $this->_provdconfig->add($rs);
		
		return($this->_return['config']);
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
				case 'config':
					$this->_provdconfig->delete($val);
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
		|| ($this->edit_config()) === false)
		{
			$this->_status = '';
			return(false);
		}

		$this->_status = '';
		return(true);
	}

	function edit_config()
	{
		if(dwho_issa('config',$this->_info) === false
		|| ($rs = $this->get_result('config')) === null)
			return(false);
			
		$this->_return['config'] = $this->_provdconfig->edit($this->_info['config']['id'],$rs);
		
		return($this->_return['config']);
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
				case 'config':
					if(isset($this->_origin['config']) === false
					|| $this->_origin['config'] === false)
						$this->delete_config();
					else
						$this->_provdconfig->edit_origin($this->_origin['config']);
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

		if($this->delete_config() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	public function delete_config()
	{
		if(dwho_issa('config',$this->_info) === false)
			return(false);

		$r = $this->_provdconfig->delete($this->_info['config']['id']);

		if($this->_status === 'delete')
			$this->_return['config'] = $r;

		return($r);
	}

	private function _reverse_delete()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'delete'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'config':
					break;
			}
		}

		return(true);
	}
}

?>
