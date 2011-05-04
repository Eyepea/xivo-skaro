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

xivo_object::required(array('abstract','provd.inc'),true);

class xivo_object_provddevice extends xivo_object_provd_abstract
{
	protected $_name 		= 'provddevice';
	protected $_base_url 	= '/provd/dev_mgr';	
	protected $_provdconfig	= false;
	
	public function __construct(&$xobj,$param=array())
	{
		if(($this->_provdconfig = $xobj->get_module('provdconfig')) === false)
			return(false);
			
		$this->_load_config(true);
		$this->_load_init();
	}
	
	public function get($str)
	{
		$this->reset();
		$uri = $this->_build_uri(array('devices',$str));
		
		if (($rs = $this->request_get($uri)) === false
		|| $this->_status_code !== 200
		|| empty($rs['device']) === true)
			return(false);
			
		return($rs['device']);
	}
	
	public function get_device_list($search='',$assoc=false)
	{
		return($this->_get_devices('list',$search,$assoc));
	}
	
	private function _get_devices($type,$search='',$assoc=false)
	{
		$this->reset();
		
		switch ($type)
		{
			default:
			case 'list':
				$uri = $this->_build_uri(array('devices'));
		}
			
		#$this->set_order($order);			
		#$this->set_limit($limit);
		
		if (($rs = $this->request_get($uri)) === false
		|| ($rs = $rs['devices']) === false
		|| ($nb = count($rs)) === 0)
			return(false);
			
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$rs[$i];
			
			if ($search !== ''
			&& preg_match('/'.$search.'/', $ref['name']) === 0
			&& preg_match('/'.$search.'/', $ref['description']) === 0)
				unset($rs[$i]);
		}

		if((bool) $assoc === false)
			return(array_values($rs));

		return($rs);
	}
	
	public function add($arr)
	{
		if (is_array($arr) === false)
			return(false);
		
		$uri = $this->_build_uri(array('devices'));
				
		$this->_set_curl_opt('header', true);
		$this->_set_curl_opt('returntransfer', true);
			
		$data['device'] = $arr;
		
		if (($rs = $this->request_post($uri,$data)) === false
		|| $this->_status_code !== 201
		|| isset($rs['id']) === false)
			return(false);
			
		$this->eval_config_device($arr);
		
		return($rs['id']);
	}
	
	public function edit($id,$arr)
	{
		if (is_array($arr) === false)
			return(false);
			
		$uri = $this->_build_uri(array('devices',$id));
				
		$this->_set_curl_opt('header', true);
		$this->_set_curl_opt('returntransfer', true);
			
		$data['device'] = $arr;
		
		if (($rs = $this->request_put($uri,$data)) === false
		|| $this->_status_code !== 204)
			return(false);
			
		$this->eval_config_device($arr);
			
		return(true);
	}
	
	public function reconfigure($id)
	{		
		$uri = $this->_build_uri(array('reconfigure'));
				
		$this->_set_curl_opt('header', true);
		$this->_set_curl_opt('returntransfer', true);
			
		$data['id'] = $id;
		
		if (($rs = $this->request_post($uri,$data)) === false
		|| $this->_status_code !== 204)
			return(false);
		
		return(true);
	}
	
	public function synchronize($id)
	{		
		$uri = $this->_build_uri(array('synchronize'));
				
		$this->_set_curl_opt('header', true);
		$this->_set_curl_opt('returntransfer', true);
			
		$data['id'] = $id;
		
		############################################
		# return false, bug in provd
		return(false);
		############################################
		
		if (($rs = $this->request_post($uri,$data)) === false)
			return(false);
		
		$decoded = $this->decode_header($rs);
		
		if (isset($decoded['Location']) === false		
		|| $this->request_delete($decoded['Location']) === false)
			return(false);
		
		return(true);
	}
	
	public function delete($id)
	{
		$uri = $this->_build_uri(array('devices',$id));
				
		if (($rs = $this->request_delete($uri)) === false
		|| $this->_status_code !== 204)
			return(false);
			
		return(true);
	}
	
	public function eval_config_device($arr)
	{
		if ($this->_provdconfig === false)
			return(false);
			
		$deviceid = isset($arr['deviceid']) ? $arr['deviceid'] : $arr['id'];
		
		// create config for this device if not exist
		if (($rs = $this->_provdconfig->get($deviceid)) === false)
		{		
			if (($conf = $this->_provdconfig->build_raw_config($deviceid,null,null,true)) === false
			|| $this->_provdconfig->add($conf) === false)
			{
				dwho_report::push('error', 'fail to create config for this device: '.$deviceid);
				return(false);
			}
		}
			
		return(true);
	}
	
	public function update_rawconfig($deviceid,$rawconfig)
	{		
		if (($device = $this->get($deviceid)) === false)
		{
			dwho_report::push('error', 'device not exist: '.$deviceid);
			return(false);
		}
		$conf = $this->_provdconfig->build_raw_config($deviceid,null,$rawconfig);
					
		if (($conf = $this->_provdconfig->build_raw_config($deviceid,null,$rawconfig)) === false
		|| $this->_provdconfig->edit($conf['id'],$conf) === false)
		{
			dwho_report::push('error', 'fail to create config for this device: '.$deviceid);
			return(false);
		}		
		
		if ($this->synchronize($deviceid) === false)
			dwho_report::push('warning', 'fail to synchronize this device: '.$deviceid);
		
		return(true);
	}
	
	public function update_configid($deviceid,$configid)
	{		
		if (($device = $this->get($deviceid)) === false)
		{
			dwho_report::push('error', 'device not exist: '.$deviceid);
			return(false);
		}
		
		if ($this->_provdconfig->get($configid) === false)
		{
			dwho_report::push('error', 'config not exist: '.$configid);
			return(false);
		}
		
		$device['config'] = $configid;
		if($this->edit($deviceid,$device) === false)
		{
			dwho_report::push('error', 'fail to edit device: '.$deviceid);
			return(false);
		}
		
		if ($this->synchronize($deviceid) === false)
			dwho_report::push('warning', 'fail to synchronize this device: '.$deviceid);
		
		return(true);
	}
	
	public function update_config_from_line($arr,$deviceid)
	{
		if ($this->_provdconfig === false
		|| dwho_issa('protocol',$arr) === false
		|| dwho_issa('linefeatures',$arr) === false
		|| dwho_issa('userfeatures',$arr) === false)
			return(false);
		
		$global = $arr['userfeatures'];
		
		$lines = array();
		$lines[$arr['linefeatures']['num']] = array();
		$lines[$arr['linefeatures']['num']]['protocol'] = $arr['protocol'];
		$lines[$arr['linefeatures']['num']]['linefeatures'] = $arr['linefeatures'];
		
		if (($conf = $this->_provdconfig->build_raw_config($deviceid,$lines,$global)) === false)
			return(false);
		
		if ($this->_provdconfig->edit($deviceid,$conf) === false)
		{
			dwho_report::push('error', 'fail to edit config for this device: '.$deviceid);
			return(false);
		}
		
		if($this->update_configid($deviceid,$deviceid) === false)
		{
			dwho_report::push('error', 'fail to edit config device: '.$deviceid);
			return(false);
		}
	}
	
	public function remove_config($deviceid)
	{		
		if (($device = $this->get($deviceid)) === false)
		{
			dwho_report::push('error', 'device not exist: '.$deviceid);
			return(false);
		}
		
		unset($device['config']);
		if($this->edit($deviceid,$device) === false)
		{
			dwho_report::push('error', 'fail to edit device: '.$deviceid);
			return(false);
		}
		
		return(true);
	}
	
	public function remove_config_from_line($deviceid)
	{		
		return($this->remove_config($deviceid));		
	}
}

?>