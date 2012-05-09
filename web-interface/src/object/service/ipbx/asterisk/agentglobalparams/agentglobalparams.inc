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

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_agentglobalparams extends xivo_service_asterisk_abstract
{
	var $_dso	= null;
	var $_name	= 'agentglobalparams';
	var $_filter	= false;
	var $_origin	= false;

	function xivo_service_asterisk_agentglobalparams(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}

	function _prepare($data)
	{
		$nb = count($data);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$info = &$data[$i];
			$r[$info['option_name']] = $info['option_value'];
		}
		return $r;
	}

	function get_options($category)
	{
		if(isset($this->_origin) === true)
			$this->_origin = false;

		$where = array();
		$where['category'] = $category;

		if (($list = $this->_dso->get_all_where($where,null,false)) === false)
			return false;

		return($this->_prepare($list));
	}

	function save_agent_global_params($options,$category)
	{

		foreach ($options as $option_name => $option_value) {
			$where['category'] = $category;
			$where['option_name'] = $option_name;
			$option['category'] = $category;
			$option['option_name'] = $option_name;
			$option['option_value'] = $option_value;
			$this->edit_where($where, $option);
		}
		return $options;
	}

}

?>
