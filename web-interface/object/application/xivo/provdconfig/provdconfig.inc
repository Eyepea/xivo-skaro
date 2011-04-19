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
		return($this->_provdconfig->get($id));
	}
	
	public function get_config_list($search='',$order=null,$limit=null,$assoc=false)
	{
		return($this->_provdconfig->get_configs('list',$search,$order,$limit,$assoc));
	}
}

?>
