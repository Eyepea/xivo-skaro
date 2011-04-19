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

abstract class module_provd_abstract
{
	var $_conf			= null;
	var $_curl			= null;
	var $_uri			= null;
	var $_url			= array();
	var $_status_code	= null;
	var $_curl_opt		= array();
	
	public function __construct($conf)
	{		
		$this->_conf = $conf;
		$this->_url = array('scheme' => 'http',
				    'host' => $this->_conf['host'],
				    'port' => $this->_conf['port']);

		$this->_uri = new dwho_uri();
		$this->_curl = new dwho_curl();
	}

	protected function _set_curl_opt($key,$value)
	{		
		if (is_array($this->_curl_opt) === false)
			return(false);

		$this->_curl_opt[$key] = $value;

		return(true);
	}
	
	protected function _build_uri($arr)
	{
		if (is_array($arr) === false
		|| ($nb = count($arr)) === 0)
			return($this->_base_url);
			
		$path = $this->_base_url.'/'.implode('/', $arr);
			
		if ($this->_uri->valid_path($path) === false)
			return(false);
		
		return($path);
	}
	
	public function decode_header($header)
	{
		$ret = array();		
		$fields = explode("\r\n", preg_replace('/\x0D\x0A[\x09\x20]+/', ' ', $header));
		foreach( $fields as $field ) 
		{
			if( preg_match('/([^:]+): (.+)/m', $field, $match) ) 
			{
				$match[1] = preg_replace('/(?<=^|[\x09\x20\x2D])./e', 'strtoupper("\0")', strtolower(trim($match[1])));
				if( isset($ret[$match[1]]) )
					$ret[$match[1]] = array($ret[$match[1]], $match[2]);
				else
					$ret[$match[1]] = trim($match[2]);
			}
		}
		
		return($ret);
	}
	
	public function header($ch, $string)
	{
    	$length = strlen($string); 
		dwho_var_dump($ch);
		dwho_var_dump($string);
		return($length);
	}
	
	function _split_top_parentheses($str)
	{
		$idx = 0;
	    $length = count($str);
	    $result = array();
	    while ($idx < $length)
	    {
	        if ($str[$idx] != '(')
	            dwho_report::push('error',sprintf('invalid character: %s', $str[$idx]));
			$start_idx = $idx;
			$idx += 1;
	        $count = 1;
	        while ($count)
	        {
	            if ($idx >= $length)
	            	dwho_report::push('error',sprintf('unbalanced number of parentheses: %s', $str));
	            $c = $str[$idx];
	            if ($c == '(')
	                $count += 1;
	            elseif ($c == ')')
	                $count -= 1;
	            $idx += 1;
	        }
	        $end_idx = $idx;
	        array_push($result,substr($str,$start_idx+1,$end_idx-1));
	    }
	    return $result;
	}

	private function _create()
	{
		$opt = array('connect_timeout'	=> $this->_conf['connect_timeout'],
					'timeout'			=> $this->_conf['timeout'],
					#'writefunction'	=> array($this,'header'),
					#'followlocation'	=> true,
					#'httpheader'		=> array(dwho_json::get_header()));
					'httpheader'		=> array('Content-Type: text/plain'));
		
		if(is_array($this->_curl_opt) === true
		&& empty($this->_curl_opt) === false)
			$opt = array_merge($opt, $this->_curl_opt);
		
		if (($user = $this->_conf['user']) !== ''
		&& ($pass = $this->_conf['pass']) !== '')
			$opt = array_merge($opt, array('httpauth' => CURLAUTH_DIGEST,
				'userpwd' => $user.':'.$pass));
		
		return($this->_curl->load(null,$opt,false));
	}
	
	public function build_href($path,$query=null)
	{
		if(dwho_has_len($path) === false)
			return(false);

		$url = $this->_url;
		$url['path'] = $path;

		if(is_array($query) === true)
			$url['query'] = $query;

		if(($uri = $this->_uri->build_uri($url)) === false)
			return(false);
			
		return($uri);
	}

	private function _connect($path,$query=null)
	{
		if(($uri = $this->build_href($path,$query)) === false
		|| $this->_curl->set_option('url',$uri) === false)
			return(false);

		return($this->_curl->connect());
	}

	public function last_status_code()
	{
		return($this->_status_code);
	}
	
	public function edit_params($uri,$value)
	{		
		$data = array();
		$data['param'] = array();
		$data['param']['value'] = $value;
		
		if ($this->request_put($uri,$data) === false
		|| $this->_status_code !== 204)
			return(false);
			
		return(true);
	}
	
	public function get_params($uri)
	{		
		if (($rs = $this->request_get($uri)) === false
		|| empty($rs['param']) === true)
			return(false);
			
		return($rs['param']);
	}
	
	public function request_oip($path)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('get',true);

		if(($r = $this->_connect($path,$query)) === false)
			return(false);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		return($r);
	}

	public function request_get($path,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('get',true);

		if(($r = $this->_connect($path,$query)) !== false
		&& $r !== '')
		{
			if (($decoded = dwho_json::decode(rtrim($r),$decode_assoc)) !== null)
			    $r = $decoded;
		}

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		return($r);
	}

	public function request_delete($path,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('customrequest','DELETE');
		$this->_curl->set_option('get',true);

		if(($r = $this->_connect($path,$query)) !== false
		&& $r !== '')
			$r = dwho_json::decode(rtrim($r),$decode_assoc);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		return($r);
	}

	function request_put($path,$data,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('customrequest','PUT');
		$this->_curl->set_option('post',true);
		$this->_curl->set_option('postfields',dwho_json::encode($data));

		if(($r = $this->_connect($path,$query)) !== false
		&& $r !== '')
		{
			if (($decoded = dwho_json::decode(rtrim($r),$decode_assoc)) !== null)
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

		if(($r = $this->_connect($path,$query)) !== false
		&& $r !== '')
		{
			if (($decoded = dwho_json::decode(rtrim($r),$decode_assoc)) !== null)
			    $r = $decoded;
		}

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		return($r);
	}
}

?>