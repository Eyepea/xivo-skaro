<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2012  Avencall
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


class xivo_application_service_asterisk_agentglobalparams extends xivo_application_asterisk_abstract
{

	var $_conf		= array();
	var $_filter		= false;
	var $_name		= 'agentglobalparams';
	var $_agentglobalparams	= false;


	function xivo_application_service_asterisk_agentglobalparams(&$service,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(($this->_agentglobalparams = &$this->_service->get_module('agentglobalparams')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		$this->_load_config();
	}

	function _load_config()
	{
		return(parent::_load_config(dirname(__FILE__)));
	}

	function get_elements()
	{
		return($this->get_element());
	}

	function get_options($category)
	{
		return $this->_agentglobalparams->get_options($category);
	}
	function save_agent_global_params($options)
	{

		if(($rs = $this->chk_values($options)) === false)
		{
			$this->_set_result('agentglobalparams',$this->_agentglobalparams->get_filter_result());
			$this->_set_error('agentglobalparams',$this->_agentglobalparams->get_filter_error());
			return(false);
		}
		$this->_set_result('agentglobalparams',$this->_agentglobalparams->save_agent_global_params($rs,"agents"));
		return true;
	}

}

?>