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

xivo_object::required(array('abstract','provd.inc'),true);

class xivo_object_provdconfig extends xivo_object_provd_abstract
{
	protected $_name 			= 'provdconfig';
	protected $_base_url 		= '/provd/cfg_mgr';
	protected $_internal 		= array('base','autoprov');
	protected $_confdefault 	= false;
	protected $_phonefunckey 	= false;
	protected $_extenumbers  	= false;
	protected $_devicefeatures 	= false;
	protected $_groupfeatures	= false;
	protected $_linefeatures  	= false;
	protected $_meetmefeatures	= false;
	protected $_queuefeatures	= false;
	protected $_callfiltermember    = false;
	protected $_callfilter      = false;
	protected $_appsip 	        = false;

	public function __construct(&$xobj,$param=array())
	{
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($ipbx = &$_SRE->get('ipbx')) === false
		|| ($this->_extenumbers = &$ipbx->get_module('extenumbers')) === false
		|| ($this->_devicefeatures = &$ipbx->get_module('devicefeatures')) === false
		|| ($this->_groupfeatures = &$ipbx->get_module('groupfeatures')) === false
		|| ($this->_linefeatures = &$ipbx->get_module('linefeatures')) === false
		|| ($this->_meetmefeatures = &$ipbx->get_module('meetmefeatures')) === false
		|| ($this->_queuefeatures = &$ipbx->get_module('queuefeatures')) === false
		|| ($this->_userfeatures = &$ipbx->get_module('userfeatures')) === false
		|| ($this->_phonefunckey = &$ipbx->get_module('phonefunckey')) === false
		|| ($this->_callfiltermember = &$ipbx->get_module('callfiltermember')) === false
		|| ($this->_callfilter = &$ipbx->get_module('callfilter')) === false
		|| ($this->_appsip = &$ipbx->get_apprealstatic('sip')) === false)
			return(false);

		$this->_load_config(true);
		$this->_load_init();
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
		if (is_array($this->_confdefault) === true)
			return($this->_confdefault);
		elseif ($this->_confdefault === false
		&& ($confdefault = $this->get('default')) === false
		&& $this->eval_required_config(null,true) === false)
		{
			dwho_report::push('error', 'fatal error: config default not exist.');
			return(false);
		}

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
			case 'device':
				$q = dwho_json::encode(array('X_type' => 'device'));
				break;
			case 'all':
			default:
				$w = array('$nin' => array('registrar','device'));
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

		if (isset($arr['deletable']) === false)
			$arr['deletable'] = true;

		$uri = $this->_build_uri(array('configs'));
		$data['config'] = $arr;
		$rs = $this->request_post($uri,$data);

		if($this->_status_code !== 201)
		{
			dwho_report::push('error', 'fail to create config');
			return(false);
		}

		return($rs['id']);
	}

	public function edit($id,$arr)
	{
		if (is_array($arr) === false
		|| dwho_has_len($id) === false)
			return(false);

		if ($id === 'default'
		|| $id === 'defaultconfigdevice')
			$arr['deletable'] = false;
		elseif (isset($arr['deletable']) === false)
			$arr['deletable'] = true;

		$uri = $this->_build_uri(array('configs',$id));
		$data['config'] = $arr;
		$rs = $this->request_put($uri,$data);

		if($this->_status_code !== 204)
		{
			dwho_report::push('error', 'fail to edit config: '.$id);
			return(false);
		}

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

	public function autocreate()
	{
		$uri = $this->_build_uri(array('autocreate'));
		$rs = $this->request_post($uri,array('' => ''));

		if($this->_status_code !== 201)
		{
			dwho_report::push('error', 'fail to create autocreate config');
			return(false);
		}

		return($rs['id']);
	}

	private function _delete_required_config()
	{
		if ($this->get('default') !== false)
			$this->delete('default');
		if ($this->get('base') !== false)
			$this->delete('base');
		if ($this->get('autoprov') !== false)
			$this->delete('autoprov');
		if ($this->get('defaultconfigdevice') !== false)
			$this->delete('defaultconfigdevice');
	}

	public function rebuild_required_config($confdefault=null)
	{
		if (is_null($confdefault) === true)
			$confdefault = $this->get('default');

		if ($this->_add_base($confdefault) === false
		|| $this->_add_autoprov($confdefault) === false
		|| $this->_add_configdevice($confdefault) === false)
			return(false);

		return(true);
	}

	public function eval_required_config($registrarip=null,$reset=false)
	{
		$confdefault = false;

		if ($reset === true)
		{
			$this->_delete_required_config();
			if (is_null($registrarip) === true)
				$registrarip = $_SERVER['SERVER_ADDR'];
			return($this->eval_required_config($registrarip));
		}

		if (is_null($registrarip) === false)
		{
			if (dwho_network::valid_ipv4($registrarip) === false
			|| $this->_add_default_registrar_config($registrarip) === false
			|| is_array($this->_confdefault) === false)
			{
				dwho_report::push('error', 'fail to create default registrar config');
				return(false);
			}
			$confdefault = $this->_confdefault;
		}
		elseif(($confdefault = $this->get('default')) === false
		|| $this->eval_required_config(null,true) === false
		|| $this->eval_required_config() === false)
		{
			dwho_report::push('error', 'invalid default registrar config');
			return(false);
		}

		if ($this->rebuild_required_config($confdefault) === false)
		{
			dwho_report::push('error', 'Can\'t rebuild config');
			return(false);
		}

		return(true);
	}

	private function _add_default_registrar_config($registrarip)
	{
		$config = array();
		$config['X_type'] = 'registrar';
		$config['id'] = 'default';
		$config['deletable'] = false;
		$config['displayname'] = 'local';
		$config['parent_ids'] = array();
		// required raw_config dict by provd
		$config['raw_config'] = array('X_key' => 'xivo');
		$config['proxy_main'] = $registrarip;
		$config['registrar_main'] = $registrarip;

		if ($this->chk_confregistrar($config) === false
		|| $this->add($config) === false)
		{
			dwho_report::push('error', 'fail to create default registrar config');
			return(false);
		}

		$this->_confdefault = $config;

		return(true);
	}

	private function _add_base($confregistrar)
	{
		$base = $this->_conf['base'];

		if ($this->chk_confregistrar($confregistrar) === false)
			return(false);

		$base['X_type'] = 'internal';
		$base['deletable'] = false;

		$base['raw_config']['ntp_enabled'] = true;
		$base['raw_config']['ntp_ip'] = $confregistrar['proxy_main'];

		$base['raw_config']['X_xivo_phonebook_ip'] = $confregistrar['proxy_main'];

		$base['raw_config']['sip_lines'][1]['proxy_ip'] = $confregistrar['proxy_main'];

		$base['raw_config']['sccp_call_managers'][1] = array();
		$base['raw_config']['sccp_call_managers'][1]['ip'] = $confregistrar['proxy_main'];

		if (empty($confregistrar['proxy_backup']) === false)
		{
			$base['raw_config']['sip_lines'][1]['backup_proxy_ip'] = $confregistrar['proxy_backup'];
			$base['raw_config']['sccp_call_managers'][2] = array();
			$base['raw_config']['sccp_call_managers'][2]['ip'] = $confregistrar['proxy_backup'];
		}

		if (($rs = $this->get('base')) !== false)
			$this->delete('base');
		if (is_array($rs) === true)
			$base['raw_config'] = array_merge($rs['raw_config'],$base['raw_config']);

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

		if(($_SRE = &dwho_gct::get('xivo_service')) !== false
		&& ($ipbx = &$_SRE->get('ipbx')) !== false)
		{
			$appsip = &$ipbx->get_apprealstatic('sip');
			$appgeneralsip = &$appsip->get_module('general');
			if(($rs = $appgeneralsip->get('autocreate_prefix')) === false
			|| isset($rs['general'], $rs['general']['var_val']) === false)
				dwho_report::push('error', 'Can\'t get autocreate_prefix in staticsip table');
			else
				$autoprov['raw_config']['sip_lines'][1]['username'] = $rs['general']['var_val'];
		}

		$autoprov['X_type'] = 'internal';
		$autoprov['deletable'] = false;
		$autoprov['raw_config']['sip_lines'][1]['proxy_ip'] = $confregistrar['proxy_main'];
		$autoprov['raw_config']['sip_lines'][1]['registrar_ip'] = $confregistrar['registrar_main'];

		$autoprov['raw_config']['sccp_call_managers'][1] = array();
		$autoprov['raw_config']['sccp_call_managers'][1]['ip'] = $confregistrar['proxy_main'];

		if (empty($confregistrar['proxy_backup']) === false)
		{
			$autoprov['raw_config']['sip_lines'][1]['backup_registrar_ip'] = $confregistrar['proxy_backup'];
			$autoprov['raw_config']['sip_lines'][1]['backup_proxy_ip'] = $confregistrar['proxy_backup'];
			$autoprov['raw_config']['sccp_call_managers'][2] = array();
			$autoprov['raw_config']['sccp_call_managers'][2]['ip'] = $confregistrar['proxy_backup'];
		}

		if (($rs = $this->get('autoprov')) !== false)
			$this->delete('autoprov');
		if (is_array($rs) === true)
			$autoprov['raw_config'] = array_merge($rs['raw_config'],$autoprov['raw_config']);

		if ($this->add($autoprov) === false)
		{
			dwho_report::push('error', 'fail to create autoprov config');
			return(false);
		}

		return(true);
	}

	private function _add_configdevice($confregistrar)
	{
		if ($this->chk_confregistrar($confregistrar) === false)
			return(false);

		$conf = array();
		$conf['X_type'] = 'device';
		$conf['deletable'] = false;
		$conf['id'] = 'defaultconfigdevice';
		$conf['label'] = 'Default config device';
		$conf['parent_ids'] = array();
		$conf['raw_config'] = array();
		$conf['raw_config']['ntp_enabled'] = true;
		$conf['raw_config']['ntp_ip'] = $confregistrar['proxy_main'];

		if (($rs = $this->get('defaultconfigdevice')) !== false)
			$this->delete('defaultconfigdevice');
		if (is_array($rs) === true)
			$conf['raw_config'] = array_merge($rs['raw_config'],$conf['raw_config']);

		if ($this->add($conf) === false)
		{
			dwho_report::push('error', 'fail to create default config device');
			return(false);
		}

		return(true);
	}

	public function get_exten($name)
	{
		if($this->_extenumbers === false
		|| ($rs = $this->_extenumbers->get_where(array('typeval' => $name))) === false)
			return(null);

		$exten = $rs['exten'];
		$exten = str_replace('_', '', $exten);
		$exten = str_replace('.', '', $exten);

		return($exten);
	}

	private function _set_config_var(&$config,$data,$var,$type=null)
	{
		if (isset($data[$var]) === true
		&& dwho_empty($data[$var]) === false) {
			switch ($type)
			{
				case 'int':
					$rs = (int) ($data[$var]);
					break;
				case 'bool':
					$rs = dwho_bool($data[$var]);
					break;
				case null:
				default:
					$rs = $data[$var];
			}
			$config[$var] = $rs;
		} else {
			unset($config[$var]);
		}
	}

	public function update_parents_ids($configid,$method,$id)
	{
		if (($config = $this->get($configid)) === false) {
			dwho_report::push('error', 'Config not exist: '.$config);
			return(false);
		}

		$parents_ids = &$config['parent_ids'];
		switch ($method)
		{
			case 'add':
			case 'edit':
				if (in_array($id,$parents_ids) === false) {
					array_push($parents_ids,$id);
				}
				$config['configdevice'] = $id;
				break;
			case 'del':
				for ($i=0;$i<count($parents_ids);$i++) {
					if ($id === $parents_ids[$i])
					unset($parents_ids[$i]);
				}
				unset($config['configdevice']);
				break;
		}

		if ($this->edit($configid,$config) === false) {
			dwho_report::push('error', 'fail to update config: '.$configid);
			return(false);
		}

		return(true);
	}

	public function build_raw_config($configid,$lines=null,$raw=null,$protocolname='sip')
	{
		if ($this->_confdefault === false
		&& $this->get_default() === false)
			return(false);

		$confdefault = $this->_confdefault;

		if (($globalconfig = $this->get($configid)) === false) {
			$globalconfig = array();
			$globalconfig['id'] = $configid;
			$globalconfig['configdevice'] = 'defaultconfigdevice';
			$globalconfig['parent_ids'] = array('base','defaultconfigdevice');
			$globalconfig['raw_config'] = array('X_key' => '');

			$this->add($globalconfig);
		}

		if (in_array('base',$globalconfig['parent_ids']) === false) {
			array_push($globalconfig['parent_ids'],'base');
		}

		$raw_config = &$globalconfig['raw_config'];

		if (isset($raw_config['sip_lines']) === true
		&& is_array($raw_config['sip_lines']) === false) {
			$raw_config['sip_lines'] = array();
		}

		if (is_null($raw) === false) {
			$build_raw_config = $this->build_raw_config_device($raw);
			$raw_config = array_merge($raw_config,$build_raw_config);

			foreach ($raw_config as $key => $val) {
				if (substr($key, 0, 5) === 'exten'
				|| $key === 'sip_lines'
				|| isset($build_raw_config[$key]))
					continue;

				unset($raw_config[$key]);
			}
		} else {
			$raw = array();
		}

		$raw_config = array_merge($raw_config,$this->_build_exten_config());

		$funckeys = $this->_init_device_master_line($configid);

		if (empty($funckeys)) {
			unset($raw_config['funckeys']);
		} else {
			$raw_config = array_merge($raw_config,$funckeys);
		}

		if (isset($lines[1])
		&& isset($lines[1]['linefeatures'])
		&& isset($lines[1]['linefeatures']['protocol'])) {
			$protocolname = $lines[1]['linefeatures']['protocol'];
		}

		switch ($protocolname)
		{
			case 'sccp':
				$raw_config['protocol'] = 'SCCP';
				break;
			case 'sip':
			default:
				$raw_config['protocol'] = 'SIP';
				$appgeneralsip = &$this->_appsip->get_module('general');

				$tlsenable = $appgeneralsip->get('tlsenable');
				if (isset($raw['sip_transport']) === true
				&& $raw['sip_transport'] === 'tls'
				&& $tlsenable['general']['var_val'] === 'yes')
				{
					$tlscafile = $appgeneralsip->get('tlscafile');
					$crt = $tlscafile['general']['var_val'];
					$raw['sip_servers_root_and_intermediate_certificates'] =
						file_get_contents($crt);
				}
				else
				{
					unset($raw['sip_srtp_mode'],
					$raw['sip_servers_root_and_intermediate_certificates'],
					$raw_config['sip_transport'],
					$raw_config['sip_servers_root_and_intermediate_certificates'],
					$raw_config['sip_srtp_mode']);
				}

				if (is_array($lines) === true)
				{
					$rslines = $this->_build_lines($lines);
					if (isset($raw_config['sip_lines']) === true) {
						$raw_config['sip_lines'] = array_replace($raw_config['sip_lines'],$rslines);
					} else {
						$raw_config['sip_lines'] = $rslines;
					}
					if (isset($raw_config['sip_lines'][0])) {
						unset($raw_config['sip_lines'][0]);
					}
				}
		}

		return($globalconfig);
	}

	public function rebuild_lines_user($iduserfeatures)
	{
		$w = array('iduserfeatures' => (int) $iduserfeatures);
		if (($list = $this->_linefeatures->get_all_where($w)) === false)
			return(null);

		for($i = 0;$i < $nb;$i++) {
			$ref = &$rs[$i];
			if (dwho_has_len($line['device']) === true
			&& $this->rebuild_device_config($ref['device']) === false)
				return(false);
		}

		return(true);
	}

	public function rebuild_master_line_user($iduserfeatures)
	{
		if (($line = $this->_linefeatures->get_user_masterline($iduserfeatures)) === false)
			return(null);

		if (dwho_has_len($line['device']) === true
		&& $this->rebuild_device_config($line['device']) === false)
			return(false);

		return(true);
	}

	public function rebuild_device_config($deviceid)
	{
		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($ipbx = &$_SRE->get('ipbx')) === false) {
			return(false);
		}

		$rslines = array();
		if (($listline = $this->_linefeatures->get_all_where(array('device' => (string) $deviceid))) !== false
		&& ($device = $this->_devicefeatures->get($deviceid)) !== false) {
			$rs = array();
			while($listline) {
				$line = array_shift($listline);
				$rs['linefeatures'] = $line;
				$modprotocol = $ipbx->get_protocol_module($line['protocol']);
				$rs['protocol'] = $modprotocol->get($line['protocolid']);
				$rslines[$line['num']] = $rs;
			}
		}

		$conf = $this->build_raw_config($device['deviceid'],$rslines);

		if ($this->edit($device['deviceid'],$conf) === false) {
			dwho_report::push('error', 'fail to edit config for this device: '.$device['deviceid']);
			return(false);
		}
		return(true);
	}

	private function _init_device_master_line($deviceid)
	{
		$raw_config = array();

		if (($device = $this->_devicefeatures->get_where(array('deviceid' => $deviceid))) === false
		|| ($masterline = $this->_linefeatures->get_user_masterline(null,$device['id'])) === false
		|| (int) $masterline['iduserfeatures'] === 0) {
			return($raw_config);
		}

		$iduserfeatures = $masterline['iduserfeatures'];

		// build funckey from user masterline
		if ($iduserfeatures !== false
		&& ($rs = $this->_build_funckey($iduserfeatures)) === false) {
			unset($raw_config['funckeys']);
		} else {
			$raw_config['funckeys'] = $rs;
		}

		return($raw_config);
	}

	private function _build_lines($lines)
	{
		$rslines = array();
		foreach ($lines as $num => $val) {
			if (dwho_issa('protocol',$val) === false
			|| dwho_issa('linefeatures',$val) === false) {
				return(false);
			}

			$protocol = $val['protocol'];
			$linefeatures = $val['linefeatures'];

			$protolines = array_merge($protocol,$linefeatures);
			if (($confregistrar = $this->get($linefeatures['configregistrar'])) === false) {
				$confregistrar = $this->get_default();
			}

			if(($siplines = $this->build_raw_config_siplines($protolines,$confregistrar)) === false) {
				return(false);
			}

			$rslines[$linefeatures['num']] = $siplines;
		}
		return($rslines);
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
		|| is_object($this->_linefeatures) === false) {
			return(false);
		}

		$where = array();
		$where['iduserfeatures'] = $iduserfeatures;
		if (($rs = $this->_phonefunckey->get_all_where($where, null,true, array('fknum' => SORT_ASC))) === false
		|| ($nb = count($rs)) === 0) {
			return(false);
		}

		for($i = 0;$i < $nb;$i++) {
			$ref = &$rs[$i];

			$type = $this->_phonefunckey->get_type($ref['typeextenumbers'],
													$ref['typevalextenumbers'],
													$ref['typeextenumbersright'],
													$ref['typevalextenumbersright']);

			$conf[$ref['fknum']] = array();
			$conf[$ref['fknum']]['type'] = ($ref['supervision'] === false) ? 'speeddial' : 'blf';
			$conf[$ref['fknum']]['line'] = 1;
			$label = $ref['label'];
			if($label !== null) {
				$conf[$ref['fknum']]['label'] = $label;
			}

			if(empty($type) === true) {
				$conf[$ref['fknum']]['value'] = $ref['exten'];
				continue;
			}

			$exten = '';
			switch ($type['type'])
			{
				case 'generalfeatures':
					if ($type['val'] === 'parkext')
						$conf[$ref['fknum']]['type'] = 'park';
					$exten = $ref['exten'];
					break;
				case 'user':
					$where = array();
					$where['iduserfeatures'] = $type['val'];
					if(($linefeatures = $this->_linefeatures->get_all_where($where)) !== false)
						$exten = $linefeatures[0]['number'];
					break;
				case 'queue':
					$queue_id = $type['val'];
					$queue = $this->_queuefeatures->get($queue_id);
					$exten = $queue['number'];
					break;
				case 'group':
					$group_id = $type['val'];
					$group = $this->_groupfeatures->get($group_id);
					$exten = $group['number'];
					break;
				case 'meetme':
					$meetme_id = $type['val'];
					$meetme = $this->_meetmefeatures->get($meetme_id);
					$exten = $meetme['confno'];
					break;
				case 'agent':
					if ($ref['progfunckey'] === true) {

						if ($ref['exten'] === null && $ref['typevalextenumbersright'] !== null)
							$typevalright = '*'.$ref['typevalextenumbersright'];

						$where = array('typeval' => 'phoneprogfunckey');
						if (($rsextenmbers = $this->_extenumbers->get_where($where)) === false)
							break;
						$where = array();
						$where['type'] = $ref['typeextenumbers'];
						$where['typeval'] = $ref['typevalextenumbers'];
						if (($extenumleftexten = $this->_extenumbers->get_where($where)) === false)
							break;

						$exten = $this->_phonefunckey->fkey_extension($rsextenmbers['extenbrut'],
								array($ref['iduserfeatures'],
									$extenumleftexten['extenbrut'],
									$typevalright)
								);
					}
					break;
				case 'featuremap':
				case 'extenfeatures':
					$where = array();
					$where['type'] = $type['type'];
					$where['typeval'] = $type['val'];
					if (($rsextenmbers = $this->_extenumbers->get_where($where)) !== false)
						$rsexten = $rsextenmbers['exten'];
					switch($type['val'])
					{
						case 'bsfilter':
							$whereright = array();
							$whereright['type'] = $ref['typeextenumbersright'];
							$whereright['typeval'] = $ref['typevalextenumbersright'];

							switch($ref['typeextenumbersright'])
							{
								case 'user':
									if (($masterline = $this->_linefeatures->get_user_masterline($ref['typevalextenumbersright'])) === false
									|| ($callfiltermember = $this->_callfiltermember->get_where($whereright)) === false)
									{
										dwho_report::push('error', 'error during get master line of user or user not exist in callfitermember');
										break;
									}
									$w = array();
									$w['callfilterid'] = $callfiltermember['callfilterid'];
									$w['bstype'] = ($callfiltermember['bstype'] === 'boss') ? 'secretary' : 'boss';
									$callfilter = $this->_callfiltermember->get_where($w);

									if($w['bstype'] === 'boss')
										$bossmasterline = $this->_linefeatures->get_user_masterline($callfilter['typeval']);
									else
									{
										$bossmasterline = $masterline;
										$masterline = $this->_linefeatures->get_user_masterline($callfilter['typeval']);
									}
							}

							$exten .= $bossmasterline['number'];
							$exten .= '*';
							$exten .= $masterline['number'];
							$exten = str_replace('.', $exten, $rsexten);
							break;
						default:
							if($ref['progfunckey'] === true)
							{
								$where = array('typeval' => 'phoneprogfunckey');
								if (($progfunckey = $this->_extenumbers->get_where($where)) === false)
									break;
								$exten = $this->_phonefunckey->fkey_extension($progfunckey['extenbrut'],
									array($ref['iduserfeatures'],
										$rsexten,
										$ref['exten'])
								);
							}
							else
							{
								$exten = str_replace('.', $ref['typevalextenumbersright'], $rsexten);
							}
					}
			}

			$conf[$ref['fknum']]['value'] = $exten;

		}

		return((empty($conf) ? false : $conf));
	}

	public function build_raw_config_siplines($arr,$confregistrar)
	{
		if (is_array($arr) === false
		|| $this->chk_confregistrar($confregistrar) === false)
			return(false);

		$conf = array();
		$conf['proxy_ip'] = $confregistrar['proxy_main'];
		$conf['username'] = $arr['name'];
		$conf['auth_username'] = $arr['name'];
		$conf['password'] = $arr['secret'];

		$calleridname = trim(preg_replace('/<[^<]*>$/','',trim(strval($arr['callerid']))));
		$calleridname = str_replace('"','',str_replace('\"','"',$calleridname));
		$conf['display_name'] = $calleridname;

		$confregistrar['registrar_ip'] = $confregistrar['registrar_main'];
		$confregistrar['proxy_ip'] = $confregistrar['proxy_main'];
		$confregistrar['backup_registrar_ip'] = $confregistrar['registrar_backup'];
		$confregistrar['backup_proxy_ip'] = $confregistrar['proxy_backup'];

		$this->_set_config_var($conf,$confregistrar,'registrar_ip');
		$this->_set_config_var($conf,$confregistrar,'proxy_ip');
		$this->_set_config_var($conf,$confregistrar,'backup_proxy_ip');
		$this->_set_config_var($conf,$confregistrar,'backup_registrar_ip');
		$this->_set_config_var($conf,$arr,'number');
		$this->_set_config_var($conf,$arr,'dtmf_mode');
		$this->_set_config_var($conf,$arr,'srtp_mode');
		$this->_set_config_var($conf,$arr,'voicemail');

		return($conf);
	}

	public function build_raw_config_device($raw)
	{
		$conf = array();

		$this->_set_config_var($conf,$raw,'X_key');
		$this->_set_config_var($conf,$raw,'_comment');
		$this->_set_config_var($conf,$raw,'timezone');
		$this->_set_config_var($conf,$raw,'locale');
		$this->_set_config_var($conf,$raw,'protocol');
		$this->_set_config_var($conf,$raw,'ntp_enabled','int');
		$this->_set_config_var($conf,$raw,'ntp_ip');
		$this->_set_config_var($conf,$raw,'vlan_enabled','int');
		$this->_set_config_var($conf,$raw,'vlan_id');
		$this->_set_config_var($conf,$raw,'vlan_priority');
		$this->_set_config_var($conf,$raw,'vlan_pc_port_id');
		$this->_set_config_var($conf,$raw,'syslog_enabled','int');
		$this->_set_config_var($conf,$raw,'syslog_ip');
		$this->_set_config_var($conf,$raw,'syslog_port');
		$this->_set_config_var($conf,$raw,'syslog_level');
		$this->_set_config_var($conf,$raw,'config_encryption_enabled','int');
		$this->_set_config_var($conf,$raw,'sip_proxy_ip');
		$this->_set_config_var($conf,$raw,'sip_proxy_port');
		$this->_set_config_var($conf,$raw,'sip_backup_proxy_ip');
		$this->_set_config_var($conf,$raw,'sip_backup_proxy_port');
		$this->_set_config_var($conf,$raw,'sip_registrar_port');
		$this->_set_config_var($conf,$raw,'sip_backup_registrar_ip');
		$this->_set_config_var($conf,$raw,'sip_backup_registrar_port');
		$this->_set_config_var($conf,$raw,'sip_outbound_proxy_ip');
		$this->_set_config_var($conf,$raw,'sip_outbound_proxy_port');
		$this->_set_config_var($conf,$raw,'sip_dtmf_mode');
		$this->_set_config_var($conf,$raw,'sip_srtp_mode');
		$this->_set_config_var($conf,$raw,'sip_transport');
		$this->_set_config_var($conf,$raw,'sip_servers_root_and_intermediate_certificates');
		$this->_set_config_var($conf,$raw,'sip_local_root_and_intermediate_certificates');
		$this->_set_config_var($conf,$raw,'sip_local_certificate');
		$this->_set_config_var($conf,$raw,'sip_local_key');
		$this->_set_config_var($conf,$raw,'sip_subscribe_mwi','int');

		return($conf);
	}

	public function remove_line_from_config($config,$line_num)
	{
		if(dwho_has_len($config) === false
		||dwho_has_len($line_num) === false)
			return(false);

		if (($globalconfig = $this->get($config)) === false)
		{
			dwho_report::push('error', 'config not exist: '.$config);
			return(false);
		}

		$raw_config = &$globalconfig['raw_config'];

		if (isset($raw_config['sip_lines']) === true
		&& isset($raw_config['sip_lines'][$line_num]) === true)
		{
			unset($raw_config['sip_lines'][$line_num]);
			if (empty($raw_config['sip_lines']) === true)
				unset($raw_config['sip_lines']);
			if($this->edit($config,$globalconfig) === false)
			{
				dwho_report::push('error', 'Can\'t remove line from config: '.$config);
				return(false);
			}
		}
		return(true);
	}

	public function chk_confregistrar($arr)
	{
		if (is_array($arr) === false
		|| isset($arr['id'],$arr['registrar_main'],
		$arr['proxy_main'],$arr['displayname']) === false
		|| dwho_network::valid_ipv4($arr['registrar_main']) === false
		|| dwho_network::valid_ipv4($arr['proxy_main']) === false)
		{
			dwho_report::push('error', 'config registrar not valid');
			return(false);
		}

		return($arr);
	}
}

?>