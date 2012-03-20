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

class xivo_service_asterisk_sccpdevice extends xivo_service_asterisk_abstract
{
	var $_dso		= null;
	var $_name		= 'sccpdevice';
	var $_filter	= false;
	var $_origin	= false;

	function xivo_service_asterisk_sccpdevice(&$sre,&$dso)
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
		$data['id'] = (int) $data['id'];

		return($data);
	}

	function sccp_normalize_mac($mac)
	{
		$var = dwho_network::normalize_macaddr($mac);
		$var = str_replace(':', '', $var);

		$rs = 'SEP'.$var;
		if (substr($var, 0, 3) == 'SEP')
			$rs = $var;

		return((string) $rs);
	}

	function get_by_mac($mac)
	{
		$mac = $this->sccp_normalize_mac($mac);
		if(($rs = $this->_dso->get(array('name' => $mac))) === false)
			return(false);

		return($this->_prepare($rs));
	}

	public function add($arr,$id=0)
	{
		if(is_array($arr) === false)
			return(false);

		$arr['name'] = $this->sccp_normalize_mac($arr['name']);
		$arr['device'] = $arr['name'];

		if (($ret = parent::add($arr,$id)) === false)
			return(false);

		$this->_sre->discuss(array('sccp update config'));

		return($ret);
	}

	public function edit($id,$arr,$disable=null)
	{
		if(is_array($arr) === false)
			return(false);

		$arr['name'] = $this->sccp_normalize_mac($arr['name']);
		$arr['device'] = $arr['name'];

		if (($ret = parent::edit($id,$arr,$disable)) === false)
			return(false);

		$this->_sre->discuss(array('sccp update config'));

		return($ret);
	}

	public function delete_by_mac($mac)
	{
		$arr = array('name' => $this->sccp_normalize_mac($mac));
		if (($ret = parent::delete_where($arr)) === false)
			return(false);

		$this->_sre->discuss(array('sccp update config'));

		return($ret);
	}

	public function init_device($mac,$line=false,$voicemail=false)
	{
		$arr = array();
		$arr['name'] = $this->sccp_normalize_mac($mac);
		$arr['device'] = $arr['name'];
		if ($line !== false)
			$arr['line'] = (string) $line;
		if ($voicemail !== false)
			$arr['voicemail'] = (string) $voicemail;

		if (($info = $this->get_by_mac($mac)) === false)
			$ret = parent::add($arr);
		else
			$ret = parent::edit($info['id'],$arr);

		$this->_sre->discuss(array('sccp update config'));

		return($ret);
	}

	public function update_line($mac,$line,$voicemail=false)
	{
		if (($info = $this->get_by_mac($mac)) === false)
			return(false);

		$arr = array();
		$arr['name'] = $this->sccp_normalize_mac($mac);
		$arr['device'] = $arr['name'];
		$arr['line'] = (string) $line;
		if ($voicemail !== false)
			$arr['voicemail'] = (string) $voicemail;

		$ret = parent::edit($info['id'],$arr);

		$this->_sre->discuss(array('sccp update config'));

		return($ret);
	}
}

?>
