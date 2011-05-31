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

dwho::load_class('dwho_network');
dwho::load_class('dwho_uri');
dwho::load_class('dwho_curl');
dwho::load_class('dwho_json');

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_dundi extends xivo_service_asterisk_abstract
{
	var $_dso		= null;
	var $_name		= 'dundi';
	var $_filter	= false;
	var $_origin	= false;
	var $_identity	= false;
	var $_curl		= null;
	var $_uri		= null;
	var $_url		= array();
	var $_status_code	= null;

	function xivo_service_asterisk_dundi(&$sre,&$dso)
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
	
	function list_server()
	{
		xivo::load_class('xivo_server',XIVO_PATH_OBJECT,null,false);
		$_SVR = new xivo_server();
		
		if (($list = $_SVR->get_all(null,true,array('name' => SORT_ASC))) === false)
			return(false);
			
		return($list);
	}
	
	function list_peers($serverid)
	{
		xivo::load_class('xivo_server',XIVO_PATH_OBJECT,null,false);
		$_SVR = new xivo_server();
		
		if(dwho_has_len($serverid) === false
		|| ($info = $_SVR->get($serverid)) === false)
			return(false);
		
		$this->_url = $info['url'];
		
		$method = 'restricted';
		if (isset($info['url']['authority']) === true
		&& isset($info['url']['authority']['host']) === true
		&& ($info['url']['authority']['host'] === '127.0.0.1'
			|| $info['url']['authority']['host'] === 'localhost'))
			$method = 'private';
		
		$this->_uri = new dwho_uri();
		$this->_curl = new dwho_curl();
		
		if(($data = $this->request_get('/service/ipbx/json.php/'.$method.'/dundi/peers/')) === false)
			return(false);
			
		return($data);
	}

	function _create()
	{
		return($this->_curl->load(null,
					  array('connect_timeout'	=> 30,
					        'timeout'			=> 60,
					        'httpheader'		=> array(dwho_json::get_header())),
				          false));
	}

	function _connect($path,$query=null)
	{
		if(dwho_has_len($path) === false)
			return(false);

		$url = $this->_url;
		$url['path'] = $path;

		if(is_array($query) === true)
			$url['query'] = $query;

		if(($uri = $this->_uri->build_uri($url)) === false
		|| $this->_curl->set_option('url',$uri) === false)
			return(false);

		return($this->_curl->connect());
	}

	function last_status_code()
	{
		return($this->_status_code);
	}

	function request_get($path,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('get',true);

		if(($r = $this->_connect($path,$query)) !== false)
		{
			$decoded = dwho_json::decode(rtrim($r),$decode_assoc);
			if(!is_null($decoded))
			    $r = $decoded;
		}

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		return($r);
	}

	function request_post($path,$data,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('post',true);
		$this->_curl->set_option('postfields',dwho_json::encode($data));

		if(($r = $this->_connect($path,$query)) !== false)
			$r = dwho_json::decode(rtrim($r),$decode_assoc);

		$this->_status_code = $this->_curl->get_info('http_code');

		$this->_curl->close();

		return($r);
	}
}

?>
