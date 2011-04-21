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

	public function __construct(&$xobj,$param=array(),$components=true)
	{
		$this->xivo_application_xivo_object_abstract(&$xobj);

		if(($this->_commonconf = &$this->_xobj->get_module('commonconf')) === false
		|| ($this->_provdconfig = &$this->_xobj->get_module('provdconfig')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	public function load_components()
	{
		$this->_components = true;

		return(true);
	}
	
	public function get($id,$nocomponents=null)
	{
		$this->_info = $this->_provdconfig->get($id);
		
		return($this->_info);
	}
	
	public function get_config_list($search='',$order=null,$limit=null,$assoc=false)
	{
		$list = $this->_provdconfig->get_configs('list',$search,$order,$limit,$assoc);
		
		return($list);
	}

	public function get_elements()
	{
		$r = $this->_provdconfig->get_supp_elements();
		$r['config'] = $this->_provdconfig->get_element();
		
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

	private  function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('config',$arr) === false)
			return(false);

		$this->set_config($arr['config']);

		return(($this->get_errnb() < 1));
	}

	public function set_config($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('config',null);
			$this->_set_error('config','invalid data');
			return(false);
		}
		
		dwho_var_dump($arr);

		if(($rs = $this->_provdconfig->chk_values($arr)) === false)
		{
			$this->_set_result('config',$this->_provdconfig->get_filter_result());
			$this->_set_error('config',$this->_provdconfig->get_filter_error());
			return(false);
		}

		$this->_set_result('config',$rs);

		return(true);
	}
}

?>
