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

dwho::load_class('dwho_uri');
dwho::load_class('dwho_curl');
dwho::load_class('dwho_json');

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'abstract','libdatastorage.inc'));

class xivo_server extends xivo_libdatastorage_abstract
{
	var $_conf		    = array();
	var $_dso		    = null;
	var $_filter		= false;
	var $_origin		= false;
	var $_origin_list	= false;
	private $_curl			= null;
	private $_uri			= null;
	private $_url			= array();
	protected 	$_curl_opt		= array();
	private $_status_code	= 0;
	private $_method	    = '';

	public function __construct()
	{
		$this->_load_config(dirname(__FILE__).DWHO_SEP_DIR.'server');
		$this->_load_dso();
		$this->_uri = new dwho_uri();
		$this->_curl = new dwho_curl();
	}

	function _prepare($data)
	{
		$data['ws_ssl'] = (bool) $data['ws_ssl'];
		$data['cti_ssl'] = (bool) $data['cti_ssl'];
		$data['disable'] = (bool) $data['disable'];
		$data['identity'] = $data['name'].' ('.$data['host'].')';

		$data['url'] = array();

		if($data['ws_ssl'] === true)
			$data['url']['scheme'] = 'https';
		else
			$data['url']['scheme'] = 'http';

		$data['url']['authority'] = array('host'	=> $data['host'],
						  'port'	=> $data['ws_port']);
		
		$this->init_url($data);

		return($data);
	}

	public function add($arr,$id=0)
	{
		if(is_array($arr) === false)
			return(false);
		else if(empty($id) === true || isset($arr['dcreate']) === false)
			$arr['dcreate'] = gmstrftime('%s');

		if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);

		return(parent::add($arr,$id));
	}

	public function edit($id,$arr,$disable=null)
	{
		if(is_array($arr) === false)
			return(false);
		else if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);

		return(parent::edit($id,$arr,$disable));
	}

	private function _load_dso()
	{
		$dso = &dwho_gct::get('DWHO_DSO');
		$type = $dso->get_type();
		$class = 'xivo_server_'.$type;
		$dir = dwho_file::joinpath(XIVO_PATH_OBJECT,'server','datastorage');

		if(xivo::load_class($class,$dir,$type,false) === false)
		{
			trigger_error('Failed to load datastorage '.$type.' for server',E_USER_ERROR);
			return(false);
		}

		$this->_dso = new $class($dso);
		return(true);
	}

	public function method()
	{
		return($this->_method);
	}

	public function init_url($data)
	{
	    $this->_curl_opt = array('connect_timeout'	=> 30,
	    						'timeout'			=> 60,
					        	'httpheader'		=> array(dwho_json::get_header()));
	    
		$this->_url = $data['url'];
		
		$this->_method = 'restricted';
		if ($data['url']['authority']['host'] === '127.0.0.1'
		|| $data['url']['authority']['host'] === 'localhost')
			$this->_method = 'private';
			
		if(dwho_has_len($data['ws_login']) === true
		&& dwho_has_len($data['ws_pass']) === true)
			$this->_curl_opt = array_merge($this->_curl_opt, array('httpauth' => CURLAUTH_BASIC,
				'userpwd' => $data['ws_login'].':'.$data['ws_pass']));
	}

	private function _create()
	{
		return($this->_curl->load(null,$this->_curl_opt,false));
	}

	private function _connect($path,$query=null)
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

	public function last_status_code()
	{
		return($this->_status_code);
	}

	public function request_get($path,$query=null,$decode_assoc=true)
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

	public function request_post($path,$data,$query=null,$decode_assoc=true)
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
