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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk','abstract.inc'),true);

class xivo_application_service_asterisk_agentmember_abstract extends xivo_application_service_asterisk_abstract
{
	var $_agentfeatures	= false;
	var $_agentinfo		= array();
	var $_agentorigin	= array();
	var $_defgroup		= XIVO_SRE_IPBX_AST_AGENT_GROUP_DEFAULT;

	function xivo_application_service_asterisk_agentmember_abstract(&$service)
	{
		$this->xivo_application_service_asterisk_abstract(&$service);

		if(($this->_agentfeatures = &$this->_service->get_module('agentfeatures')) === false)
			return(false);

		return($this->load_init());
	}

	function load_init()
	{
		$this->_reset_info();
		$this->_reset();

		return(true);
	}

	function _reset_agentinfo()
	{
		$this->_agentorigin = array();
	}

	function _reset_info()
	{
		$this->_reset_agentinfo();
		return(parent::_reset_info());
	}

	function get($agentgroupid)
	{
		$this->_info = false;
		$this->_origin = false;

		if(($agentgroupid = dwho_ulongint($agentgroupid)) === 0)
			return(false);

		$where = array();
		$where['numgroup'] = $agentgroupid;

		if(($this->_info = $this->_agentfeatures->get_all_where($where)) !== false)
			$this->_origin = $this->_agentfeatures->get_origin_list();

		return($this->_info);
	}

	function set($list)
	{
		$this->_reset();

		if(is_array($list) === false)
			return(false);

		$list = array_values($list);

		if(($nb = count($list)) === 0)
			return(null);

		$this->_reset_agentinfo();

		$tmp = $reslist = array();

		for($i = 0;$i < $nb;$i++)
		{
			$aid = &$list[$i];

			if(($rs = $this->_get_agent($aid)) === false)
			{
				$this->_set_error('wrong agent');
				continue;
			}
			else if(isset($tmp[$aid]) === true)
				continue;

			$tmp[$aid] = 1;
			$reslist[] = $rs['agentfeatures'];
		}

		if($this->get_errnb() > 0 || isset($reslist[0]) === false)
		{
			$this->_set_result(false);
			return(false);
		}

		$this->_set_result($reslist);
		return(true);
	}

	function _get_agent($id,$disable=null)
	{
		$info = array();

		if(($info['agentfeatures'] = $this->_agentfeatures->get($id,$disable)) === false)
			return(false);

		$id = $info['agentfeatures']['id'];

		$this->_agentinfo[$id] = $info;

		$this->_agentorigin[$id]['agentfeatures'] = $this->_agentfeatures->get_origin();
		return($info);
	}

	function save($agentgroupid)
	{
		$rs = false;

		if(($agentgroupid = dwho_ulongint($agentgroupid)) === 0
		|| ($rs = $this->get_result()) === null
		|| $rs === false)
			return($rs);

		$this->_return = $info = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$aid = $rs[$i]['id'];

			if(isset($this->_agentorigin[$aid]) === false)
				return(false);
			else if($agentgroupid === (string) $rs[$i]['numgroup'])
			{
				$this->_return[$aid] = true;
				continue;
			}

			$info['numgroup'] = $agentgroupid;

			$origin = $this->_agentorigin[$aid];

			$this->_return[$aid] = array();
			$return = &$this->_return[$aid];

			if(($return['agenfeatures'] = $this->_agentfeatures->edit($aid,$info)) === false)
				return(false);
		}

		if($agentgroupid === (string) $this->_defgroup
		|| ($r = $this->_save_in_defgroup()) === null)
			$r = true;

		return($r);
	}

	function _save_in_defgroup()
	{
		if(is_array($this->_origin) === false
		|| ($nb = count($this->_origin)) === 0)
			return(null);

		$info = array();
		$info['numgroup'] = $this->_defgroup;

		for($i = 0;$i < $nb;$i++)
		{
			$aid = $this->_origin[$i]['id'];

			if(isset($this->_return[$aid]) === true
			|| $this->_get_agent($aid) === false
			|| isset($this->_agentorigin[$aid]) === false)
				continue;

			$origin = $this->_agentorigin[$aid];

			$this->_return[$aid] = array();
			$return = &$this->_return[$aid];

			if(($return['agentfeatures'] = $this->_agentfeatures->edit($aid,$info)) === false)
				return(false);
		}

		return(true);
	}

	function delete()
	{
		$this->_return = array();
		$this->_reset_agentinfo();

		return($this->_save_in_defgroup());
	}

	function reverse_save($status)
	{
		if($status !== 'add' && $status !== 'edit')
			return(false);

		return($this->_reverse());
	}

	function reverse_delete($status)
	{
		if($status !== 'delete')
			return(false);

		return($this->_reverse());
	}

	function _reverse()
	{
		if(is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if(is_array($val) === false || isset($this->_agentorigin[$key]) === false)
				continue;

			$ref = &$this->_agentorigin[$key];

			if(isset($val['agentfeatures'],$ref['agentfeatures']) === true
			&& $val['agentfeatures'] !== false)
				$this->_agentfeatures->edit_origin($ref['agentfeatures']);

		}

		return(true);
	}
}

?>
