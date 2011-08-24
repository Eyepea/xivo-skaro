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
dwho::load_class('dwho_file');

xivo_object::required(array('abstract','abstract.inc'),true);

abstract class xivo_object_provd_abstract extends xivo_object_abstract
{
	protected 	$_curl			= null;
	protected 	$_uri			= null;
	protected 	$_url			= array();
	protected 	$_status_code	= 0;
	protected 	$_response		=  array('header' 		=> '',
				                         'body' 		=> '',
				                         'curl_error' 	=> '',
				                         'http_code' 	=> '',
			                        	 'last_url' 	=> '');
	protected 	$_curl_opt		= array();
	protected 	$_limit			= array();
	protected 	$_order			= array();
	protected 	$_filter		= false;
	protected 	$_origin		= false;
	protected 	$_origin_list	= false;

	protected function _load_init()
	{
		$this->_set_configuration();

		$this->_url = array('scheme' => 'http',
				    'host' => $this->_conf['provd']['host'],
				    'port' => $this->_conf['provd']['port']);

		$this->_uri = new dwho_uri();
		$this->_curl = new dwho_curl();
	}

	protected function _set_configuration()
	{
		$_XOBJ = &dwho_gct::get('xivo_object');
		$appprovisionning = &$_XOBJ->get_application('provisioning');
		$ref = $appprovisionning->get(1);

		$this->_conf['provd'] = array();

		if(isset($ref['net4_ip_rest']) === true)
		{
			if(dwho_network::valid_host($ref['net4_ip_rest'],
						    (DWHO_NETWORK_HOST_IPV4_DOTDEC | DWHO_NETWORK_HOST_HOSTNAME)) === true)
				$this->_conf['provd']['host'] = $ref['net4_ip_rest'];
			else
				dwho_report::push('warning','Invalid option net4_ip_rest for conf provisioning');
		}

		if(isset($ref['rest_port']) === true)
		{
			if(dwho_network::valid_port_number($ref['rest_port']) === true)
				$this->_conf['provd']['port'] = (int) $ref['rest_port'];
			else
				dwho_report::push('warning','Invalid option rest_port for conf provisioning');
		}

		if(isset($ref['private']) === true)
			$this->_conf['provd']['private'] = (bool) $ref['private'];

		if(isset($ref['username']) === true)
		{
			if(empty($ref['username']) === false)
				$this->_conf['provd']['user'] = $ref['username'];
			else
				dwho_report::push('warning','Invalid option username for conf provisioning');
		}

		if(isset($ref['password']) === true)
		{
			if(empty($ref['password']) === false)
				$this->_conf['provd']['pass'] = $ref['password'];
			else
				dwho_report::push('warning','Invalid option password for conf provisioning');
		}

		if(isset($ref['secure']) === true)
			$this->_conf['provd']['secure'] = (bool) $ref['secure'];

		if(isset($ref['connect_timeout']) === true)
		{
			if(dwho_is_uint($ref['connect_timeout']) === true)
				$this->_conf['provd']['connect_timeout'] = $ref['connect_timeout'];
			else
				dwho_report::push('warning','Invalid option connect_timeout for conf provisioning');
		}
		else
			$this->_conf['provd']['connect_timeout'] = 30;

		if(isset($ref['timeout']) === true)
		{
			if(dwho_is_uint($ref['timeout']) === true)
				$this->_conf['provd']['timeout'] = $ref['timeout'];
			else
				dwho_report::push('warning','Invalid option timeout for conf provisioning');
		}
		else
			$this->_conf['provd']['timeout'] = 60;

		return(true);
	}

	protected function reset()
	{
		$this->_limit = array();
		$this->_order = array();
	}

	protected function _set_curl_opt($key,$value)
	{
		if (is_array($this->_curl_opt) === false)
			return(false);

		$this->_curl_opt[$key] = $value;

		return(true);
	}

	public function _build_uri($arr)
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

	protected function _split_top_parentheses($str)
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

	protected function _create()
	{
		$opt = array('connect_timeout'	=> $this->_conf['provd']['connect_timeout'],
					'timeout'			=> $this->_conf['provd']['timeout'],
					'header'			=> true,
					'returntransfer'	=> true,
					#'writefunction'	=> array($this,'header'),
					#'followlocation'	=> true,
					#'httpheader'		=> array(dwho_json::get_header()));
					'httpheader'		=> array('Content-Type: application/vnd.proformatique.provd+json'));

		if(is_array($this->_curl_opt) === true
		&& empty($this->_curl_opt) === false)
			$opt = array_merge($opt, $this->_curl_opt);

		if(((bool) $this->_conf['provd']['private']) === true
		&& ($user = $this->_conf['provd']['user']) !== ''
		&& ($pass = $this->_conf['provd']['pass']) !== '')
			$opt = array_merge($opt, array('httpauth' => CURLAUTH_DIGEST,
				'userpwd' => $user.':'.$pass));

		if(((bool) $this->_conf['provd']['secure']) === true)
		{
			$ssl = array(CURLOPT_PROTOCOLS	=> CURLPROTO_HTTPS,
					CURLOPT_SSL_VERIFYHOST	=> 0,
					CURLOPT_SSL_VERIFYPEER 	=> 0,
					CURLOPT_SSLVERSION 		=> 3);

			$opt = array_merge($opt, $ssl);
		}

		return($this->_curl->load(null,$opt,false));
	}

	protected function set_limit($limit)
	{
		$this->_limit = array();

		if (is_null($limit) === true
		|| is_array($limit) === false
		|| count($limit) !== 2)
			return(false);

		$this->_limit = $limit;
	}

	protected function set_order($column,$sort='')
	{
		$this->_order = array();

		if (is_null($column) === true
		|| is_array($column) === false)
			return(false);

		$r = array();
		{
			if(empty($column) === true)
				return(false);

			foreach($column as $key => $val)
			{
				$tmp = array();
				$tmp['sort'] = $key;
				$tmp['sort_ord'] = $this->_set_sort($val);
				$r[] = $tmp;
			}

			if (isset($r[0]) === false)
				return(false);
		}

		$this->_order = $r[0];
	}

	private function _set_sort($sort='')
	{
		$sort = strtoupper($sort);

		switch($sort)
		{
			case 'D':
			case 'DESC':
			case SORT_DESC:
				return('DESC');
		}

		return('ASC');
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

	protected function _connect($path,$query=null)
	{
		if (is_null($query) === true)
			$query = array();

		if (empty($this->_limit) === false)
		{
			array_push($query,array('skip',$this->_limit[0]));
			array_push($query,array('limit',$this->_limit[1]));
		}

		if (empty($this->_order) === false)
		{
			if (isset($this->_order['sort']) === true)
				array_push($query,array('sort',$this->_order['sort']));
			if (isset($this->_order['sort_ord']) === true)
				array_push($query,array('sort_ord',$this->_order['sort_ord']));
		}

		if(($uri = $this->build_href($path,$query)) === false
		|| $this->_curl->set_option('url',$uri) === false)
			return(false);

		$response = $this->_curl->connect();
		$this->_response = $this->_curl->decode_response($response);

		return($this->_response);
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

		$rs = $this->request_put($uri,$data);

		if($this->_status_code !== 204)
			return(false);

		return(true);
	}

	public function get_params($uri)
	{
		$rs = $this->request_get($uri);

		if(is_array($rs) === false
		|| $this->_status_code !== 200
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

		$rs = false;
		if(($r = $this->_connect($path,$query)) !== false
		&& $r['body'] !== false)
			$rs = dwho_json::decode(rtrim($r['body']),true);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		if ($this->_status_code === 401)
			dwho_report::push('error','authentification to provd failed');

		return($rs);
	}

	public function request_get($path,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('get',true);

		$rs = false;
		if(($r = $this->_connect($path,$query)) !== false
		&& $r['body'] !== false)
			$rs = dwho_json::decode(rtrim($r['body']),$decode_assoc);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		if ($this->_status_code === 401)
			dwho_report::push('error','authentification to provd failed');

		return($rs);
	}

	public function request_delete($path,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('customrequest','DELETE');
		$this->_curl->set_option('get',true);

		$rs = false;
		if(($r = $this->_connect($path,$query)) !== false)
			$rs = dwho_json::decode(rtrim($r['body']),$decode_assoc);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		if ($this->_status_code === 401)
			dwho_report::push('error','authentification to provd failed');

		return($rs);
	}

	function request_put($path,$data,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('customrequest','PUT');
		$this->_curl->set_option('post',true);
		$this->_curl->set_option('postfields',dwho_json::encode($data));

		$rs = false;
		if(($r = $this->_connect($path,$query)) !== false)
			$rs = dwho_json::decode(rtrim($r['body']),$decode_assoc);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		if ($this->_status_code === 401)
			dwho_report::push('error','authentification to provd failed');

		return($rs);
	}

	function request_post($path,$data,$query=null,$decode_assoc=true)
	{
		$this->_status_code = null;

		if($this->_create() === false)
			return(false);

		$this->_curl->set_option('post',true);
		$this->_curl->set_option('postfields',dwho_json::encode($data));

		$rs = false;
		if(($r = $this->_connect($path,$query)) !== false)
			$rs = dwho_json::decode(rtrim($r['body']),$decode_assoc);

		$this->_status_code = $this->_curl->get_info('http_code');
		$this->_curl->close();

		if ($this->_status_code === 401)
			dwho_report::push('error','authentification to provd failed');

		return($rs);
	}
}

?>
