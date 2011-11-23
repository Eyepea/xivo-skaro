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
	var $_dso			= null;
	var $_devicefeatures = false;
	var $_provddevice 	= false;
	var $_provdplugin 	= false;
	var $_provdconfig 	= false;

	public function __construct(&$service,&$dso,$param=array(),$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_devicefeatures = &$this->_service->get_module('devicefeatures')) === false
		|| ($this->_linefeatures = &$this->_service->get_module('linefeatures')) === false
		|| ($_XOBJ = &dwho_gct::get('xivo_object')) === false
		|| ($this->_provddevice = &$_XOBJ->get_module('provddevice')) === false
		|| ($this->_provdplugin = &$_XOBJ->get_module('provdplugin')) === false
		|| ($this->_provdconfig = &$_XOBJ->get_module('provdconfig')) === false
		|| $this->load_init($param) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	public function load_init($param=array())
	{
		$this->_reset_info();
		$this->_reset_params();
		$this->_reset();

		return(true);
	}

	public function load_components()
	{
		$this->_components = true;

		return(true);
	}

	public function update()
	{
		$ret = array();
		if (($listd = $this->_provddevice->get_device_list('')) === false
		|| is_array($listd) === false
		|| ($nb = count($listd)) === 0)
			return($ret);

		for($i=0;$i<$nb;$i++)
		{
			$ref = &$listd[$i];
			$deviceid = $ref['id'];
			$ret[$deviceid] = false;

			if((int) $this->get_nb(array('deviceid' => $deviceid)) === 0)
			{
				if(isset($ref['mac']) === true
				&& ($devicefeatures = $this->_devicefeatures->get_where(array('mac' => $ref['mac']))) !== false
				&& $this->get_by_deviceid($devicefeatures['deviceid']) !== false)
				{
					$act_set = 'set_edit';
					$act = 'edit';
				}
				else
				{
					$act_set = 'set_add';
					$act = 'add';
				}
			}
			elseif($this->get_by_deviceid($deviceid,null,false) !== false)
			{
				$act_set = 'set_edit';
				$act = 'edit';
			}
			else
			{
				dwho_report::push('error','error during update device: '.$deviceid);
				continue;
			}

			$ret[$deviceid] = true;

			unset($ref['id']);
			$arr = array();
			$arr['devicefeatures'] = $ref;
			$arr['devicefeatures']['deviceid'] = $deviceid;

			$this->_provddevice->eval_config_device($deviceid);

			if($this->$act_set($arr) === false
			|| $this->$act() === false)
			{
				dwho_report::push('error',
					dwho_i18n::babelfish('error_during_'.$act.'_device',array($deviceid)),
					'error_device_'.$act);
				foreach($this->get_error() as $k => $v)
				{
					if (is_array($v))
						foreach($v as $kk => $vv)
							dwho_report::push('error',$kk.': '.$vv,'error_device_'.$act);
					else
						dwho_report::push('error',$k.': '.$v,'error_device_'.$act);
				}
			}
		}

		return($ret);
	}

	public function get($id,$disable=null,$nocomponents=null,$where=null)
	{
		$this->_info = $this->_origin = array();

		if (is_array($where) === true)
		{
			if(($this->_info['devicefeatures'] = $this->_devicefeatures->get_where($where)) === false)
				return(false);
		}
		else
		{
			if(($this->_info['devicefeatures'] = $this->_devicefeatures->get($id,$disable)) === false)
				return(false);
		}

		$this->_origin['devicefeatures'] = $this->_devicefeatures->get_origin();

		if($this->_components === false)
			return($this->_info);

		$this->get_deviceprovd($this->_info['devicefeatures']['deviceid']);
		$this->get_capabilities();
		$this->get_config();

		return($this->_info);
	}

	public function get_by_deviceid($deviceid,$disable=null,$nocomponents=null)
	{
		$w = array();
		$w['deviceid'] = $deviceid;
		if (is_null($disable) === false)
			$w['commented'] = true;

		return($this->get(0,$disable,$nocomponents,$w));
	}

	public function get_by_ip($ip,$disable=null,$nocomponents=null)
	{
		$w = array();
		$w['ip'] = $ip;
		if (is_null($disable) === false)
			$w['commented'] = true;

		return($this->get(0,$disable,$nocomponents,$w));
	}

	public function get_by_mac($mac,$disable=null,$nocomponents=null)
	{
		$w = array();
		$w['mac'] = $mac;
		if (is_null($disable) === false)
			$w['commented'] = true;

		return($this->get(0,$disable,$nocomponents,$w));
	}

	public function get_nb($arr=null,$disable=null,$initialized=null)
	{
		return($this->_dso->get_nb($arr,$disable,$initialized));
	}

	public function get_deviceprovd($deviceid)
	{
		$this->_info['deviceprovd'] = $this->_provddevice->get($deviceid);
		$this->_origin['deviceprovd'] = $this->_provddevice->get_origin();
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

		if (($confid = $this->_provdconfig->autocreate()) === false
		|| $this->_provddevice->update_configid($deviceid,$confid,$synchronize) === false
		|| $this->_linefeatures->reset_device($id) === false)
			return(false);

		return(true);
	}

	public function update_config($idlinefeatures,$synchronize=false)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$appline = &$this->_service->get_application('line');
		$userfeatures = &$this->_service->get_module('userfeatures');

		$id = $this->_info['devicefeatures']['id'];
		$deviceid = $this->_info['devicefeatures']['deviceid'];

		if(($rs = $appline->get($idlinefeatures)) === false
		|| ($rs['userfeatures'] = $userfeatures->get($rs['linefeatures']['iduserfeatures'])) === false
		|| $this->_provddevice->update_config_from_line($rs,$deviceid,$synchronize) === false)
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

		if (($listupdate = $this->update()) === false)
			dwho_report::push('error',dwho_i18n::babelfish('error_during_update'));

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
			$devicefeatures = $this->_devicefeatures->_prepare($ref);
			$devicefeatures['provdexist'] = false;
			$devicefeatures['capabilities'] = $this->get_capabilities_by_plugin($devicefeatures['plugin']);
			if (isset($listupdate[$devicefeatures['deviceid']]) === true)
				$devicefeatures['provdexist'] = true;
			$r[$devicefeatures['id']] = $devicefeatures;
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

				$this->_return['devicefeatures'] = $this->_provddevice->add($rs);
				break;
			default:
			case 'local':
				$this->_return['devicefeatures'] = $this->_devicefeatures->add($rs);
		}

		return($this->_return['devicefeatures']);
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
		$this->_provddevice->delete($this->_info['devicefeatures']['deviceid']);
		$r = $this->_devicefeatures->delete($this->_info['devicefeatures']['id']);

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
