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

dwho::load_class('dwho_network');
dwho::load_class('dwho_json');

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_dundi extends xivo_service_asterisk_abstract
{
	var $_dso		        = null;
	var $_name		        = 'dundi';
	var $_filter	        = false;
	var $_origin	        = false;
	var $_identity	        = false;
	private $_dundi_type	= array('peers','mappings');

	public function __construct(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;
		
		$this->_load_config();
	}
	
	function edit($id, $rs)
	{
		$rs = array_merge($this->get(1), $rs);
		$rs = $this->chk_values($rs,true);

		return(parent::edit($id, $rs));
	}
	
	public function list_server()
	{
		xivo::load_class('xivo_server',XIVO_PATH_OBJECT,null,false);
		$_SVR = new xivo_server();
		
		if (($list = $_SVR->get_all(null,true,array('name' => SORT_ASC))) === false)
			return(false);
			
		return($list);
	}
	
	public function list_peers($serverid)
	{
		return($this->_remote_list('peers',$serverid));
	}
	
	public function list_mappings($serverid)
	{
		return($this->_remote_list('mappings',$serverid));
	}
	
	private function _remote_list($type,$serverid)
	{
	    if(dwho_has_len($serverid) === false
		|| in_array($type,$this->_dundi_type) === false)
			return(false);
			
		xivo::load_class('xivo_server',XIVO_PATH_OBJECT,null,false);
		$_SVR = new xivo_server();
		
		if($_SVR->get($serverid) === false)
			return(false);
		
		$method = $_SVR->method();
		
		if(($data = $_SVR->request_get('/service/ipbx/json.php/'.$method.'/dundi/'.$type.'/')) === false)
			return(false);
			
		return($data);
	}
}

?>
