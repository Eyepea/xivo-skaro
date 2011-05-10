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

class xivo_object_provdconfig extends xivo_object_provd_abstract
{
	protected $_name 			= 'provdconfig';
	protected $_base_url 		= '/provd/cfg_mgr';
	protected $_internal 		= array('base','autoprov');
	protected $_confdefault 	= false;
	protected $_extenfeatures 	= false;
	protected $_phonefunckey 	= false;
	protected $_extenumbers  	= false;
	protected $_linefeatures  	= false;
	
	public function __construct(&$xobj,$param=array())
	{
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($ipbx = &$_SRE->get('ipbx')) === false
		|| ($this->_extenfeatures = &$ipbx->get_application('extenfeatures')) === false
		|| ($this->_extenumbers = &$ipbx->get_module('extenumbers')) === false
		|| ($this->_linefeatures = &$ipbx->get_module('linefeatures')) === false
		|| ($this->_phonefunckey = &$ipbx->get_module('phonefunckey')) === false)
			return(false);
		
		$this->_load_config(true);
		$this->_load_init();
		$this->get_default();
	}
	
	public function get_supp_elements()
	{
		$dir = dwho_file::joinpath(dirname(__FILE__),'config');
		
		if(($listfile = dwho_file::read_d($dir)) === false
		|| ($nb = count($listfile)) === 0)
			return(false);
			
		$res = array();
		
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$listfile[$i];
			if(($info = dwho_file::get_info($dir.DWHO_SEP_DIR.$ref)) === false
			|| ($conf = dwho_gat::get_file($dir.DWHO_SEP_DIR.$info['filename'])) === false)
				continue;
			
			$res[$info['filename']] = $conf['element'];
		}
		
		return($res);
	}

	public function _prepare($data)
	{
		return($data);
	}
	
	public function get_default()
	{
		$this->_confdefault = false;
		if (($confdefault = $this->get('default')) === false)
			return(false);
		
		return(($this->_confdefault = $confdefault));
	}
	
	public function get($id)
	{
		$this->reset();
		
		if(dwho_has_len($id) === false)
			return(false);
			
		$uri = $this->_build_uri(array('configs',$id));
		$rs = $this->request_get($uri);
		
		if($this->_status_code !== 200
		|| empty($rs['config']) === true)
			return(false);
			
		return($rs['config']);
	}
	
	public function get_configs($mode,$search='',$order=null,$limit=null,$assoc=false,$internal=false,$type=null)
	{
		$this->reset();
		
		switch ($mode)
		{
			default:
			case 'list':
				$uri = $this->_build_uri(array('configs'));
		}
			
		$this->set_order($order);
		$this->set_limit($limit);
		
		$query = array();
		$q = array();
		switch ($type)
		{
			case 'registrar':
				$q = dwho_json::encode(array('X_type' => 'registrar'));
				break;
			case 'network':
				$q = dwho_json::encode(array('X_type' => 'network'));
				break;
			case 'all':
			default:
				$w = array('$nin' => array('registrar','network'));
				$q = dwho_json::encode(array('X_type' => $w));
		}
		array_push($query,array('q64',base64_encode($q)));
		
		$rs = $this->request_get($uri,$query);
		
		if (is_array($rs) === false
		|| ($rs = $rs['configs']) === false
		|| ($nb = count($rs)) === 0)
			return(false);
		
		$this->_cnt = $nb;
			
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$rs[$i];
			
			if (in_array($ref['id'],$this->_internal) === true)
			{
				unset($rs[$i]);
				continue;
			}
			
			if ($search !== ''
			&& preg_match('/'.$search.'/', $ref['id']) === 0)
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
		
		$uri = $this->_build_uri(array('configs'));
		$data['config'] = $arr;
		$rs = $this->request_post($uri,$data);
		
		if($this->_status_code !== 201)
			return(false);
		
		return($rs['id']);
	}
	
	public function edit($id,$arr)
	{
		if (is_array($arr) === false
		|| dwho_has_len($id) === false)
			return(false);
		
		$uri = $this->_build_uri(array('configs',$id));
		$data['config'] = $arr;
		$rs = $this->request_put($uri,$data);
		
		if($this->_status_code !== 204)
			return(false);
			
		return(true);
	}
	
	public function delete($id)
	{
		if(dwho_has_len($id) === false)
			return(false);
			
		$uri = $this->_build_uri(array('configs',$id));
		$rs = $this->request_delete($uri);
		
		if($this->_status_code !== 204)
			return(false);
			
		return(true);
	}
	
	public function add_required_config($config=null)
	{
		$confdefault = false;
		if (is_null($config) === true
		&& ($confdefault = $this->get('default')) === false)
		{
			dwho_report::push('error', 'fail to get default config');
			return(false);
		}
		elseif(is_array($config) === true)
			$confdefault = $config;
		elseif($confdefault === false)
		{
			dwho_report::push('error', 'invalid default config');
			return(false);
		}
		
		if ($this->_add_base($confdefault) === false
		|| $this->_add_autoprov($confdefault) === false)
			return(false);
			
		return(true);
	}
	
	private function _add_base($confregistrar)
	{
		$base = $this->_conf['base'];
		
		if ($this->chk_confregistrar($confregistrar) === false)
			return(false);
		
		$base['X_type'] = 'internal';
		
		$base['raw_config']['ntp_enabled'] = true;
		$base['raw_config']['ntp_ip'] = $confregistrar['proxy_main'];
				
		$base['raw_config']['sip_lines'][1]['proxy_ip'] = $confregistrar['proxy_main'];
		$base['raw_config']['sip_lines'][1]['backup_proxy_ip'] = $confregistrar['proxy_backup'];
		
		$base['raw_config']['sccp_call_managers'][1] = array();
		$base['raw_config']['sccp_call_managers'][1]['ip'] = $confregistrar['proxy_main'];
		$base['raw_config']['sccp_call_managers'][2] = array();
		$base['raw_config']['sccp_call_managers'][2]['ip'] = $confregistrar['proxy_backup'];
		
		if ($this->add($base) === false)
		{
			dwho_report::push('error', 'fail to create base config');
			return(false);
		}
		
		return(true);
	}
	
	private function _add_autoprov($confregistrar)
	{
		$autoprov = $this->_conf['autoprov'];
		
		if ($this->chk_confregistrar($confregistrar) === false)
			return(false);
				
		$autoprov['X_type'] = 'internal';
		$autoprov['raw_config']['sip_lines'][1]['proxy_ip'] = $confregistrar['proxy_main'];
		$autoprov['raw_config']['sip_lines'][1]['backup_proxy_ip'] = $confregistrar['proxy_backup'];
		$autoprov['raw_config']['sip_lines'][1]['registrar_ip'] = $confregistrar['registrar_main'];
		$autoprov['raw_config']['sip_lines'][1]['backup_registrar_ip'] = $confregistrar['registrar_backup'];
		
		$autoprov['raw_config']['sccp_call_managers'][1] = array();
		$autoprov['raw_config']['sccp_call_managers'][1]['ip'] = $confregistrar['proxy_main'];
		$autoprov['raw_config']['sccp_call_managers'][2] = array();
		$autoprov['raw_config']['sccp_call_managers'][2]['ip'] = $confregistrar['proxy_backup'];
		
		if ($this->add($autoprov) === false)
		{
			dwho_report::push('error', 'fail to create autoprov config');
			return(false);
		}
		
		return(true);
	}
	
	public function get_exten($name)
	{
		if($this->_extenfeatures === false
		|| ($rs = $this->_extenfeatures->_get_extenumbers($name)) === false)
			return(false);
			
		$exten = $rs['exten'];
			
		$exten = str_replace('_', '', $exten);
		$exten = str_replace('.', '', $exten);
			
		return($exten);
	}
	
	private function _set_config_var(&$config,$data,$var)
	{
		if (isset($data[$var]) === true
		&& dwho_empty($data[$var]) === false)
			$config[$var] = $data[$var];
		else
			unset($config[$var]);
	}
	
	public function build_raw_config($configid,$lines=null,$raw=null,$protocolname='sip')
	{
		if ($this->_confdefault === false
		&& $this->get_default() === false)
			return(false);
			
		$confdefault = $this->_confdefault;
		
		if (($globalconfig = $this->get($configid)) === false)
		{
			$globalconfig = array();
			$globalconfig['id'] = $configid;
			$globalconfig['parent_ids'] = array();
			$globalconfig['raw_config'] = array('X_key' => '');
			
			$this->add($globalconfig);
		}
			
		$raw_config = &$globalconfig['raw_config'];
		
		switch ($protocolname)
		{
			case 'sip':
			default:
				$raw_config['ntp_enabled'] = true;
				$raw_config['ntp_ip'] = $confdefault['proxy_main'];
					
				$this->_set_config_var($raw_config,$raw,'timezone');
				$this->_set_config_var($raw_config,$raw,'locale');
				$this->_set_config_var($raw_config,$raw,'protocol');
				$this->_set_config_var($raw_config,$raw,'config_encryption_enabled');
				$this->_set_config_var($raw_config,$raw,'sip_proxy_ip');
				$this->_set_config_var($raw_config,$raw,'sip_proxy_port');
				$this->_set_config_var($raw_config,$raw,'sip_backup_proxy_ip');
				$this->_set_config_var($raw_config,$raw,'sip_backup_proxy_port');
				$this->_set_config_var($raw_config,$raw,'sip_registrar_port');
				$this->_set_config_var($raw_config,$raw,'sip_backup_registrar_ip');
				$this->_set_config_var($raw_config,$raw,'sip_backup_registrar_port');
				$this->_set_config_var($raw_config,$raw,'sip_outbound_proxy_ip');
				$this->_set_config_var($raw_config,$raw,'sip_outbound_proxy_port');
				$this->_set_config_var($raw_config,$raw,'sip_dtmf_mode');
				$this->_set_config_var($raw_config,$raw,'sip_srtp_mode');
				$this->_set_config_var($raw_config,$raw,'sip_transport');
				$this->_set_config_var($raw_config,$raw,'sip_servers_root_and_intermediate_certificates');
				$this->_set_config_var($raw_config,$raw,'sip_local_root_and_intermediate_certificates');
				$this->_set_config_var($raw_config,$raw,'sip_local_certificate');
				$this->_set_config_var($raw_config,$raw,'sip_local_key');
				$this->_set_config_var($raw_config,$raw,'sip_subscribe_mwi');
				
				if (is_array($lines) === true
				|| empty($lines) === false
				&& empty($raw_config['sip_lines']) === false)
				{
					$rslines = array();
					$iduserfeatures = false;
					
					if (in_array('base',$globalconfig['parent_ids']) === false)
						array_push($globalconfig['parent_ids'],'base');
						
					foreach ($lines as $num => $val)
					{
						if (dwho_issa('protocol',$val) === false
						|| dwho_issa('linefeatures',$val) === false)
							return(false);
						
						$protocol = $val['protocol'];
						$linefeatures = $val['linefeatures'];
						
						$protolines = array_merge($protocol,$linefeatures);
						if (($confregistrar = $this->get($linefeatures['configregistrar'])) === false)
							$confregistrar = $this->get_default();
						
						if(($siplines = $this->build_raw_config_siplines($protolines,$confregistrar)) === false)
							return(false);
			
						$rslines[$linefeatures['num']] = $siplines;
						
						// getting iduserfeatures from line 1
						if ((int) $num === 1)
							$iduserfeatures = $linefeatures['iduserfeatures'];
					}
					if (isset($raw_config['sip_lines']) === true)
						$raw_config['sip_lines'] = array_replace($raw_config['sip_lines'],$rslines);
					else
						$raw_config['sip_lines'] = $rslines;
					
					// build funckey from masterline
					if ($iduserfeatures !== false
					&& ($rs = $this->_build_funckey($iduserfeatures)) !== false
					&& empty($rs) === false)
						$raw_config['funckeys'] = $this->_build_funckey($iduserfeatures);
					else
						unset($raw_config['funckeys']);
				}
				$raw_config = array_merge($raw_config,$this->_build_exten_config());
		}
		
		return($globalconfig);
	}
	
	private function _build_exten_config()
	{
		$conf = array();
		$conf['exten_dnd'] = $this->get_exten('enablednd');
		$conf['exten_fwd_unconditional'] = $this->get_exten('fwdunc');
		$conf['exten_fwd_no_answer'] = $this->get_exten('fwdrna');
		$conf['exten_fwd_busy'] = $this->get_exten('fwdbusy');
		$conf['exten_fwd_disable_all'] = $this->get_exten('fwdundoall');
		$conf['exten_park'] = $this->get_exten('parkext');
		$conf['exten_pickup_group'] = $this->get_exten('pickupexten');
		$conf['exten_pickup_call'] = $this->get_exten('pickup');
		$conf['exten_voicemail'] = $this->get_exten('vmusermsg');
		
		return($conf);
	}
	
	private function _build_funckey($iduserfeatures)
	{
		$conf = array();

		if(is_object($this->_phonefunckey) === false
		|| is_object($this->_linefeatures) === false)
			return(false);

		$where = array();
		$where['iduserfeatures'] = $iduserfeatures;

		if (($rs = $this->_phonefunckey->get_all_where($where, null,true, array('fknum' => SORT_ASC))) === false
		|| ($nb = count($rs)) === 0)
			return($conf);
		
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
		
			$type = $this->_phonefunckey->get_type($ref['typeextenumbers'],
													$ref['typevalextenumbers'],
													$ref['typeextenumbersright'],
													$ref['typevalextenumbersright']);
								
			$exten = '';
			if (empty($type) === false)
			{
				switch ($type['type'])
				{
					case 'user':
						$where = array();
						$where['iduserfeatures'] = $type['val'];
						if(($linefeatures = $this->_linefeatures->get_all_where($where)) !== false)
							$exten = $linefeatures[0]['number'];
						break;
					default:
						$where = array();
						$where['type'] = $type['type'];
						$where['typeval'] = $type['val'];
						if (($rsexten = $this->_extenumbers->get_where($where)) !== false)
							$exten = $rsexten['exten'];
				}
			}
												
			$conf[$ref['fknum']] = array();
			$conf[$ref['fknum']]['type'] = ($ref['supervision'] === false) ? 'speeddial' : 'blf';
			$conf[$ref['fknum']]['value'] = $exten;
			$conf[$ref['fknum']]['label'] = $ref['label'];
			$conf[$ref['fknum']]['line'] = 1;
		}
		
		return($conf);
	}
	
	public function build_raw_config_siplines($arr,$confregistrar)
	{
		if (is_array($arr) === false
		|| $this->chk_confregistrar($confregistrar) === false)
			return(false);
		
		$conf = array();
		$conf['proxy_ip'] = $confregistrar['proxy_main'];
		
		if(dwho_has_len($confregistrar['proxy_backup']) === true)
			$conf['backup_proxy_ip'] = $confregistrar['proxy_backup'];
		if(dwho_has_len($confregistrar['registrar_main']) === true)
			$conf['registrar_ip'] = $confregistrar['registrar_main'];
		if(dwho_has_len($confregistrar['registrar_backup']) === true)
			$conf['backup_registrar_ip'] = $confregistrar['registrar_backup'];
		
		$conf['username'] = $arr['name'];
		$conf['auth_username'] = $arr['name'];
		$conf['password'] = $arr['secret'];
		
		$calleridname = trim(preg_replace('/<[^<]*>$/','',trim(strval($arr['callerid']))));
		$calleridname = str_replace('"','',str_replace('\"','"',$calleridname));
		$conf['display_name'] = $calleridname;
		
		$conf['number'] = $arr['number'];
		#$conf['dtmf_mode'] = null;
		#$conf['srtp_mode'] = null;
		#$conf['voicemail'] = null;
		
		return($conf);
	}
	
	public function build_raw_config_from_confnetwork($confnetwork)
	{
		$conf = array();
		$conf['vlan_enabled'] = true;
		$conf['vlan_id'] = true;
		$conf['vlan_priority'] = true;
		$conf['vlan_pc_port_id'] = true;
		
		$conf['syslog_enabled'] = true;
		$conf['syslog_ip'] = true;
		$conf['syslog_port'] = true;
		$conf['syslog_level'] = true;
		
		return($conf);
	}
	
	public function chk_confregistrar($arr)
	{
		if (is_array($arr) === false
		|| isset($arr['id'],$arr['registrar_main'],
			$arr['proxy_main'],$arr['displayname']) === false)
		{
			dwho_report::push('error', 'config registrar not valid');
			return(false);
		}
		
		return($arr);
	}
}

?>