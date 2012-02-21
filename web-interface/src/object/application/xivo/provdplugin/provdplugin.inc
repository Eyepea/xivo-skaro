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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','xivo.inc'),true);

class xivo_application_xivo_object_provdplugin extends xivo_application_xivo_object_abstract
{
	protected $_commonconf 		= false;
	protected $_provdplugin		= false;
	protected $_conf			= array();

	public function __construct(&$xobj,$param=array(),$components=true)
	{
		$this->xivo_application_xivo_object_abstract(&$xobj);

		if(($this->_commonconf = &$this->_xobj->get_module('commonconf')) === false
		|| ($this->_provdplugin = &$this->_xobj->get_module('provdplugin')) === false)
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
		return($this->_provdplugin->get($id));
	}
	
	public function get_plugin_list($search='',$order=null,$limit=null,$assoc=false)
	{
		$this->_cnt = 0;
		
		if (($list_installed = $this->_provdplugin->get_plugin_installed($search,$order)) === false)
			$list_installed = array();
		
		if (($list_installable = $this->_provdplugin->get_plugin_installable($search,$order)) === false)
			$list_installable = array();
			
		$list_old_pni = array_diff_key($list_installed, $list_installable);	
		$list_installable = array_merge($list_installable,$list_old_pni);
		
		ksort($list_installable);
			
		$list = array();
		foreach ($list_installable as $k => &$v) 
		{			
			if (isset($list_installed[$k]) === true)
			{
				$v['version'] = $list_installed[$k]['version'];
				$v['type'] = 'installed';
			}
			array_push($list, $v);
		}
		
		/*
		if (($list_installed = $this->_provdplugin->get_plugin_installed($search,$order,null)) === false)
			$list_installed = array();
		
		if (($list_installable = $this->_provdplugin->get_plugin_installable($search,$order,null,true)) === false)
			$list_installable = array();
		
		$plugins = array();
		$plugins['list'] = $list_installable;
		$plugins['slt'] = dwho_array_intersect_key($list_installed,$plugins['list'],'name');
		$plugins['info'] = false;

		if($plugins['slt'] !== false)
		{
			$plugins['info'] = dwho_array_copy_intersect_key($list_installed,$plugins['slt'],'name');
			$plugins['list'] = dwho_array_diff_key($plugins['list'],$plugins['slt']);
		}
		
		$list = array_merge($plugins['info'],$plugins['list']);
		$list = array_values($list);
		*/	
		$this->_cnt = $total = count($list);
		for($i=0;$i<$total;$i++)
		{
			if ($i >= $limit[0] && $i <= ($limit[0]+$limit[1]))
				continue;
			unset($list[$i]);
		}
		
		$list = array_values($list);
		
		return($list);
	}
}

?>
