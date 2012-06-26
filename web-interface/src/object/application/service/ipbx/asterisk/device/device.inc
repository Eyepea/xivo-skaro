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
dwho::load_class('dwho_http');

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_device extends xivo_application_asterisk_abstract
{
	var $_dso					= null;
	protected $_devicefeatures 	= false;
	protected $_provddevice 	= false;
	protected $_provdplugin 	= false;
	protected $_provdconfig 	= false;
	protected $_sccpdevice		= false;
	protected $_prodv_exist_list = array();

	public function __construct(&$service,&$dso,$param=array())
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_devicefeatures = &$this->_service->get_module('devicefeatures')) === false
		|| ($this->_linefeatures = &$this->_service->get_module('linefeatures')) === false
		|| ($this->_sccpdevice = &$this->_service->get_module('sccpdevice')) === false
		|| ($_XOBJ = &dwho_gct::get('xivo_object')) === false
		|| ($this->_provddevice = &$_XOBJ->get_module('provddevice')) === false
		|| ($this->_provdplugin = &$_XOBJ->get_module('provdplugin')) === false
		|| ($this->_provdconfig = &$_XOBJ->get_module('provdconfig')) === false)
			return(false);

		return(true);
	}

	public function update_by_ip($ip)
	{
		if(($device = $this->_provddevice->get_device_by_ip($ip)) === false)
			return(false);

		$deviceid = $device['id'];

		$act = 'add';
		if(($devicefeatures = $this->_devicefeatures->get_where(array('deviceid' => $deviceid))) !== false
		&& $this->get($devicefeatures['id'],null,true) !== false)
			$act = 'edit';

		$this->_update_device($act,$device,true);

		if ($act === 'add')
		{
			$this->get($this->_return['devicefeatures'],null,true);
			return((int) $this->_return['devicefeatures']);
		}

		return((int) $devicefeatures['id']);
	}

	public function update()
	{
		$ret = &$this->_prodv_exist_list;
		if (($provd_devices = $this->_provddevice->get_all()) === false
		|| ($nb = count($provd_devices)) === 0)
			return($this->_prodv_exist_list);

		for($i=0;$i<$nb;$i++)
		{
			$ref = &$provd_devices[$i];
			$deviceid = $ref['id'];
			$ret[$deviceid] = true;

			$act = 'add';
			if(($devicefeatures = $this->_devicefeatures->get_where(array('deviceid' => $deviceid))) !== false
			&& $this->get($devicefeatures['id'],null,true) !== false)
			{
				if ((isset($ref['ip'])
					&& $devicefeatures['ip'] !== $ref['ip'])
				|| (isset($ref['mac'])
					&& $devicefeatures['mac'] !== $ref['mac'])
				|| (isset($ref['vendor'])
					&& $devicefeatures['vendor'] !== $ref['vendor'])
				|| (isset($ref['model'])
					&& $devicefeatures['model'] !== $ref['model'])
				|| (isset($ref['plugin'])
					&& $devicefeatures['plugin'] !== $ref['plugin'])
				|| (isset($ref['config'])
					&& $devicefeatures['config'] !== $ref['config'])
				|| (isset($ref['configured'])
					&& $devicefeatures['configured'] !== $ref['configured']))
					$act = 'edit';
				else
					continue;
			}

			$this->_update_device($act,$ref);
		}

		return($this->_prodv_exist_list);
	}

	private function _update_device($method, $data, $reconfigure=false)
	{
		switch($method)
		{
			case 'add':
				$act_set = 'set_add';
				$act = 'add';
				break;
			case 'edit':
				$act_set = 'set_edit';
				$act = 'edit';
				break;
			default:
				return(false);
		}

		$deviceid = $data['id'];
		$arr = array();
		$arr['devicefeatures'] = $data;
		$arr['devicefeatures']['deviceid'] = $deviceid;
		if($reconfigure === true && $data['config'] !== $deviceid)
			$this->_provddevice->eval_config_device($deviceid);

		if($this->$act_set($arr) === false
		|| $this->$act() === false)
		{
			dwho_report::push('error',
				dwho_i18n::babelfish('error_during_'.$act.'_device',array($deviceid)),
				'error_device_'.$act);
		}
		elseif(isset($data['plugin'])
		&& preg_match('/'.XIVO_SRE_IPBX_AST_PROTO_SCCP.'/', $data['plugin']) === 1)
			$this->_sccpdevice->init_device($data['mac']);

		return(true);
	}

	public function get($id,$disable=null,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['devicefeatures'] = $this->_devicefeatures->get($id,$disable)) === false)
			return(false);

		$this->_origin['devicefeatures'] = $this->_devicefeatures->get_origin();

		if($nocomponents === true)
			return($this->_info);

		$this->get_deviceprovd($this->_info['devicefeatures']['deviceid']);
		$this->get_capabilities();
		$this->get_config();

		return($this->_info);
	}

	public function get_nb($arr=null,$disable=null,$initialized=null)
	{
		return($this->_dso->get_nb($arr,$disable,$initialized));
	}

	public function get_deviceprovd($deviceid)
	{
		$this->_info['deviceprovd'] = $this->_provddevice->get($deviceid);
		$this->_origin['deviceprovd'] = $this->_provddevice->get_origin();
		return($this->_info['deviceprovd']);
	}

	public function get_capabilities()
	{
		$this->_info['capabilities'] = false;

		if (isset($this->_info['deviceprovd']['plugin']) === false
		|| isset($this->_info['deviceprovd']['model']) === false
		|| ($plugin = $this->_info['deviceprovd']['plugin']) === null
		|| ($rs = $this->_provdplugin->get($plugin)) === false
		|| ($info = $rs['info']) === null
		|| isset($info['capabilities']) === false
		|| ($nb = count($info['capabilities'])) === 0)
			return(false);

		$r = array();
		foreach ($info['capabilities'] as $k => $v)
		{
			if(preg_match('/'.$this->_info['deviceprovd']['model'].'/', $k) === 0)
				continue;
			$r = $v;
			break;
		}

		$this->_info['capabilities'] = $r;
	}

	public function get_capabilities_by_plugin($pluginid)
	{
		if (isset($this->_info['deviceprovd']) === false
		|| $this->_info['deviceprovd'] === false
		|| ($rs = $this->_provdplugin->get($pluginid)) === false
		|| ($info = $rs['info']) === null
		|| isset($info['capabilities']) === false
		|| ($nb = count($info['capabilities'])) === 0)
			return(false);

		foreach ($info['capabilities'] as $k => $v)
		{
			if(isset($this->_info['deviceprovd']['model']) === false
			|| preg_match('/'.$this->_info['deviceprovd']['model'].'/', $k) === 0)
				continue;
			return($v);
		}
		return(false);
	}

	public function get_config()
	{
		$this->_info['config'] = false;
		$this->_info['deviceconfig'] = false;

		if (isset($this->_info['devicefeatures'], $this->_info['devicefeatures']['deviceid']) === false
		|| ($deviceconfig = $this->_provdconfig->get($this->_info['devicefeatures']['deviceid'])) === false
		|| isset($deviceconfig['raw_config']) === false)
			return(false);

		$this->_info['config'] = $deviceconfig['raw_config'];
		$this->_info['deviceconfig'] = $deviceconfig;
	}

	public function mode_autoprov($synchronize=false)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$id = $this->_info['devicefeatures']['id'];
		$deviceid = $this->_info['devicefeatures']['deviceid'];
		$mac = $this->_info['devicefeatures']['mac'];
		$plugin = $this->_info['devicefeatures']['plugin'];

		if (($confid = $this->_provdconfig->autocreate()) === false
		|| $this->_provddevice->update_configid($deviceid,$confid,$synchronize) === false
		|| $this->_linefeatures->reset_device($id) === false
		|| $this->remove_all_line() === false)
			return(false);
		elseif(preg_match('/'.XIVO_SRE_IPBX_AST_PROTO_SCCP.'/',$plugin) === 1)
			$this->_sccpdevice->init_device($mac,'');

		return(true);
	}

	public function remove_all_line()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false
		|| ($globalconfig = $this->_provdconfig->get($this->_info['devicefeatures']['deviceid'])) === false
		|| isset($globalconfig['raw_config']) === false)
			return(false);

		$raw_config = &$globalconfig['raw_config'];
		unset($raw_config['sip_lines']);
		unset($raw_config['funckeys']);
		if($this->_provdconfig->edit($globalconfig['id'],$globalconfig) === false)
		{
			dwho_report::push('error', 'Can\'t remove line from config: '.$globalconfig['id']);
			return(false);
		}
		return(true);
	}

	public function remove_line($line_num, $all=false, $synchronize=false)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false
		|| ($globalconfig = $this->_provdconfig->get($this->_info['devicefeatures']['deviceid'])) === false
		|| isset($globalconfig['raw_config']) === false)
			return(false);

		$raw_config = &$globalconfig['raw_config'];

		if (isset($raw_config['sip_lines']) === true
		&& isset($raw_config['sip_lines'][$line_num]) === true)
		{
			unset($raw_config['sip_lines'][$line_num]);
			if (empty($raw_config['sip_lines']) === true)
			{
				unset($raw_config['sip_lines']);
				unset($raw_config['funckeys']);
				$this->mode_autoprov($synchronize);
			}
			if($this->_provdconfig->edit($globalconfig['id'],$globalconfig) === false)
			{
				dwho_report::push('error', 'Can\'t remove line from config: '.$globalconfig['id']);
				return(false);
			}
		}
		return(true);
	}

	public function associate_line($idlinefeatures,$iduserfeatures,$synchronize=false)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$appline = &$this->_service->get_application('line');
		$userfeatures = &$this->_service->get_module('userfeatures');

		$id = $this->_info['devicefeatures']['id'];
		$deviceid = $this->_info['devicefeatures']['deviceid'];

		if($this->_provddevice->update_config_from_line($deviceid,$iduserfeatures,$synchronize) === false)
			return(false);

		$this->_linefeatures->edit($idlinefeatures,array('device' => $id));

		return(true);
	}

	public function get_elements()
	{
		$r = array();
		$r['devicefeatures'] = $this->_devicefeatures->get_element();
		$r['config'] = $this->_provdconfig->get_element();

		return($r);
	}

	public function get_devices_search($search,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_devices('search',$disable,$search,$order,$limit,$assoc,$initialized));
	}

	public function get_devices_list($disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_devices('list',$disable,null,$order,$limit,$assoc,$initialized));
	}

	private function _get_devices($action,$disable=null,$search='',$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$initialized,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_dso->get_all($disable,$initialized,$order,$limit);
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$devicefeatures = dwho_array_startswith_key($ref,'devicefeatures.',true);
			$devicefeatures = $this->_devicefeatures->_prepare($devicefeatures);
			$r[$devicefeatures['id']]['devicefeatures'] = $devicefeatures;

			$r[$devicefeatures['id']]['provdexist'] = false;
			if (isset($this->_prodv_exist_list[$devicefeatures['deviceid']]) === true)
				$r[$devicefeatures['id']]['provdexist'] = true;

			#$r[$devicefeatures['id']]['capabilities'] = $this->get_capabilities_by_plugin($devicefeatures['plugin']);

			$linefeatures = dwho_array_startswith_key($ref,'linefeatures.',true);
			$r[$devicefeatures['id']]['linefeatures'] = false;
			if ($linefeatures['id'] !== null) {
				$linefeatures = $this->_linefeatures->_prepare($linefeatures);
				$r[$devicefeatures['id']]['linefeatures'] = $linefeatures;
			}
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	public function set_add($arr)
	{
		return($this->_set('add',$arr));
	}

	public function set_edit($arr)
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr));
	}

	private function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('devicefeatures',$arr) === false)
			return(false);

		$this->set_devicefeatures($arr['devicefeatures']);

		if (dwho_issa('config',$arr) === true)
			$this->set_config($arr['config']);

		if (isset($arr['configdevice']) === true
		&& $arr['configdevice'] !== null
		&& empty($arr['configdevice']) === false)
			$this->set_configdevice($arr['configdevice']);

		if($this->get_errnb() > 0)
			$r = false;
		else
			$r = true;

		return($r);
	}

	function set_devicefeatures($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('devicefeatures',null);
			$this->_set_error('devicefeatures','invalid data');
			return(false);
		}

		if(($rs = $this->_devicefeatures->chk_values($arr)) === false)
		{
			$this->_set_result('devicefeatures',$this->_devicefeatures->get_filter_result());
			$this->_set_error('devicefeatures',$this->_devicefeatures->get_filter_error());
			return(false);
		}

		$this->_set_result('devicefeatures',$rs);

		return(true);
	}

	function set_config($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('config',null);
			$this->_set_error('config','invalid data');
			return(false);
		}

		if(($rs = $this->_provdconfig->chk_values($arr)) === false)
		{
			$this->_set_result('config',$this->_provdconfig->get_filter_result());
			$this->_set_error('config',$this->_provdconfig->get_filter_error());
			return(false);
		}

		$this->_set_result('config',$rs);

		return(true);
	}

	function set_configdevice($configdeviceid)
	{
		if(dwho_has_len($configdeviceid) === false)
		{
			$this->_set_result('configdevice',null);
			$this->_set_error('configdevice','invalid data');
			return(false);
		}

		if ($this->_provdconfig->get($configdeviceid) === false)
		{
			$this->_set_result('configdevice',$this->_provdconfig->get_filter_result());
			$this->_set_error('configdevice',$this->_provdconfig->get_filter_error());
			return(false);
		}

		$this->_set_result('configdevice',$configdeviceid);
	}

	function add($method='local')
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$devicefeaturesid = null;

		if($this->get_errnb() > 0
		|| ($devicefeaturesid = $this->add_devicefeatures($method)) === false)
		{
			$r = false;
			if($devicefeaturesid !== null)
				$this->_reverse_add();
		}

		$this->_status = '';

		return($r);
	}

	function add_devicefeatures($method)
	{
		if(($rs = $this->get_result('devicefeatures')) === null
		|| $rs === false)
			return(false);

		switch ($method)
		{
			case 'provd':
				if(($rs = $this->_provddevice->chk_values($rs)) === false)
					$this->_set_error('devicefeatures',$this->_provddevice->get_filter_error());

				if($this->get_errnb() > 0)
					return false;

				$deviceid = $this->_provddevice->add($rs);

				if ($this->_add_config($deviceid) === false
				|| $this->_add_configdevice($deviceid) === false)
					return(false);

				return(true);

				break;
			default:
			case 'local':
				$this->_return['devicefeatures'] = $this->_devicefeatures->add($rs);
				return($this->_return['devicefeatures']);
		}

	}

	function _add_config($deviceid)
	{
		if(($rs = $this->get_result('config')) === null)
			return($rs);

		return($this->_provddevice->update_rawconfig($deviceid,$rs));
	}

	function _add_configdevice($deviceid)
	{
		if(($rs = $this->get_result('configdevice')) === null)
			return($rs);

		return($this->_provdconfig->update_parents_ids($deviceid,'add',$rs));
	}

	function _reverse_add()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'devicefeatures':
					$this->_devicefeatures->delete($val);
					break;
			}
		}

		return(true);
	}

	function edit($method='local')
	{
		$this->_status = 'edit';
		$this->_return = array();

		if(is_array($this->_info) === false
		|| empty($this->_info) === true
		|| $this->get_errnb() > 0
		|| ($this->edit_devicefeatures($method)) === false
		|| ($this->edit_config()) === false
		|| ($this->edit_configdevice()) === false)
		{
			$this->_status = '';
			return(false);
		}

		$this->_status = '';
		return(true);
	}

	function edit_devicefeatures($method)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false
		|| ($rs = $this->get_result('devicefeatures')) === null)
			return(false);

		switch ($method)
		{
			case 'provd':
				if(dwho_issa('deviceprovd',$this->_info) === false)
					return(false);

				$arr = $this->_info['deviceprovd'];
				foreach($this->_info['deviceprovd'] as $k => &$v)
				{
					if (isset($rs[$k]) === false)
						continue;
					elseif($rs[$k] !== $v
					&& empty($rs[$k]) === false)
						$arr[$k] = $rs[$k];
				}

				$this->_return['devicefeatures'] = $this->_provddevice->edit($this->_info['devicefeatures']['deviceid'],$arr);
				break;
			default:
			case 'local':
				$this->_return['devicefeatures'] = $this->_devicefeatures->edit($this->_info['devicefeatures']['id'],$rs);
		}

		return($this->_return['devicefeatures']);
	}

	function edit_config()
	{
		if(($rs = $this->get_result('config')) === null)
			return($rs);

		if (($this->_return['config'] = $this->_provddevice->update_rawconfig(
			$this->_info['devicefeatures']['deviceid'],$rs)) === false)
			return(false);

		return($this->_return['config']);
	}

	function edit_configdevice()
	{
		if(($rs = $this->get_result('configdevice')) === null)
			return($rs);

		$deviceid = $this->_info['devicefeatures']['deviceid'];
		$configdevice = isset($this->_info['deviceconfig']['configdevice']) ?
			$this->_info['deviceconfig']['configdevice'] : null;

		if ($configdevice !== $rs)
		{
			if($configdevice === null)
				$this->_provdconfig->update_parents_ids($deviceid,'add',$rs);
			else
			{
				$this->_provdconfig->update_parents_ids($deviceid,'del',$configdevice);
				$this->_provdconfig->update_parents_ids($deviceid,'add',$rs);
			}
		}
		return(true);
	}

	function _reverse_edit($devicefeaturesid=0)
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'edit'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'devicefeatures':
					if(isset($this->_origin['devicefeatures']) === false
					|| $this->_origin['devicefeatures'] === false)
						$this->delete_devicefeatures();
					else
						$this->_devicefeatures->edit_origin($this->_origin['devicefeatures']);
					break;
			}
		}
		return(true);
	}

	function delete()
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();

		if($this->delete_devicefeatures() === false
		|| $this->reset_linefeatures() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	function delete_devicefeatures()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$this->_provdconfig->delete($this->_info['devicefeatures']['config']);
		$this->_provdconfig->delete($this->_info['devicefeatures']['deviceid']);
		$this->_provddevice->delete($this->_info['devicefeatures']['deviceid']);
		$this->_sccpdevice->delete_by_mac($this->_info['devicefeatures']['mac']);
		$r = $this->_devicefeatures->delete($this->_info['devicefeatures']['id']);

		if (isset($this->_info['config'])
		&& isset($this->_info['config']['protocol'])
		&& $this->_info['config']['protocol'] == 'SCCP'){
			$this->_sccpdevice->delete_by_mac($this->_info['devicefeatures']['mac']);
		}

		if($this->_status === 'delete')
			$this->_return['devicefeatures'] = $r;

		return($r);
	}

	function reset_linefeatures()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$r = $this->_linefeatures->reset_device($this->_info['devicefeatures']['id']);

		return($r);
	}

	function _reverse_delete()
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'delete'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'devicefeatures':
					if(isset($this->_origin['devicefeatures']) === true
					&& $this->_origin['devicefeatures'] !== false)
						$this->_devicefeatures->add_origin($this->_origin['devicefeatures']);
					break;
			}
		}

		return(true);
	}

	function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if($this->enable_devicefeatures() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return($r);
	}

	function disable()
	{
		$r = true;

		$this->_status = 'disable';
		$this->_return = array();

		if($this->disable_devicefeatures() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return(true);
	}

	function enable_devicefeatures()
	{
		return($this->_enable_disable_devicefeatures(false));
	}

	function disable_devicefeatures()
	{
		return($this->_enable_disable_devicefeatures(true));
	}

	function _enable_disable_devicefeatures($disable=false)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_devicefeatures->enable($this->_info['devicefeatures']['id']);
		else
			$r = $this->_devicefeatures->disable($this->_info['devicefeatures']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['devicefeatures'] = $r;

		return($r);
	}

	function _reverse_enable_disable()
	{
		if(($this->_status !== 'enable' && $this->_status !== 'disable') === true
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		$disable = $this->_status === 'enable';

		$this->_status = '';

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'devicefeatures':
					$this->_enable_disable_devicefeatures($disable);
					break;
			}
		}

		return(true);
	}

	private function _prepare_import($arr)
	{
		if (is_array($arr) === false)
			return(false);

		return($arr);
	}

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data)) === false
		|| $this->set_add($arr) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}

	function edit_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data)) === false
		|| $this->set_edit($arr) === false
		|| $this->edit() === false)
			return(false);

		return(true);
	}
}

?>
