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

class xivo_application_xivo_object_ha extends xivo_application_xivo_object_abstract
{
	var $_sysconfd = false;
	var $_ha = false;

	function xivo_application_xivo_object_ha(&$xobj)
	{
		$this->xivo_application_xivo_object_abstract(&$xobj);

		if(($this->_sysconfd = &$this->_xobj->get_module('sysconfd')) === false
		|| ($this->_ha = &$this->_xobj->get_module('ha')) === false)
			return(false);

		return(true);
	}

	function get()
	{
		if(($res = $this->_sysconfd->request_get('/get_ha_config')) === false
		|| is_array($res) === false)
			return(false);

		return($res);
	}

	function get_elements()
	{
		return($this->_ha->get_element());
	}

	function get_status()
	{
		$status = $this->_sysconfd->request_get('/ha_status');
		if($status === false)
		{ return false; }

		return $status;
	}

	function _set_check($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('ha',null);
			$this->_set_error('ha','invalid data');
			return(false);
		}

		switch($arr['node_type'])
		{
			case 'master':
				break;
			case 'slave':
				break;
		}

		if(($rs = $this->_ha->chk_values($arr)) === false)
		{
			$this->_set_result('ha',$this->_ha->get_filter_result());
			$this->_set_error('ha',$this->_ha->get_filter_error());
			return(false);
		}

		$this->_set_result('ha',$rs);

		return(true);
	}

	function _set_save($arr)
	{
		$query = array();
		$query['node_type'] = $arr['node_type'];
		$query['remote_address'] = $arr['remote_address'];

		if(($res = $this->_sysconfd->request_post('/update_ha_config', $query)) === false
			|| $this->_sysconfd->last_status_code() != 200) {
			return(false);
        }
		return($res);
	}

	function set($arr)
	{
		$this->_reset();

		if(!$this->_set_check(&$arr))
			return false;

		/* TODO
		 *
		 */
		//return;

		if($this->_set_save($arr) === false)
			return false;

		return $this->generate();
	}

	function generate()
	{
	}

	function gen_passphrase($len, $lower=false)
	{
		$pwd = '';
		for($i = 0; $i < $len; $i++)
		{
			$r = mt_rand(0, 35);
			$pwd .= $r < 10?$r:chr($r-10+65);
		}

		if($lower)
			$pwd = strtolower($pwd);

		return $pwd;
	}

}

?>
