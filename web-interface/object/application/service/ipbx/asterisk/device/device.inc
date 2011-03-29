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
dwho::load_class('dwho_http');

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_device extends xivo_application_asterisk_abstract
{
	var $_dso			= null;
	var $_devicefeatures = false;
	var $_protocolname	= false;
	var $_protocol		= false;
	var $_extensions	= false;
	var $_extenumbers	= false;
	var $_conf			= array();
	var $_param			= array('internal'	=> false);
	var $_servicesgroup = false;
	var $_servicesgroup_user = false;

	public function __construct(&$service,&$dso,$param=array(),$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_devicefeatures = &$this->_service->get_module('devicefeatures')) === false
		|| $this->load_init($param) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function load_init($param=array())
	{
		$this->_reset_info();
		$this->_reset_params();
		$this->_reset();

		return(true);
	}

	function load_components()
	{
		$this->_components = true;

		if(($this->_servicesgroup = &$this->_service->get_application('servicesgroup')) === false
		|| ($this->_servicesgroup_user = &$this->_service->get_module('servicesgroup_user')) === false)
			return(false);

		return(true);
	}

	function _reset()
	{
		$this->_protocolname = false;

		return(parent::_reset());
	}

	function get($id,$disable=null,$where=false,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['device'] = $this->_devicefeatures->get($id,$disable)) === false)
			return(false);

		$this->_origin['device'] = $this->_devicefeatures->get_origin();

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_where($arr,$disable=null,$internal=false)
	{
		return($this->get($arr,$disable,$internal,true));
	}

	function get_nb($arr=null,$disable=null,$initialized=null)
	{
		return($this->_dso->get_nb($arr,$disable,$initialized));
	}

	function get_elements()
	{
		$r = array();

		$r['servicesgroup'] = $this->_servicesgroup->get_element();

		return($r);
	}

	function get_devices_search($search,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_devices('search',$disable,$search,$order,$limit,$assoc,$initialized));
	}

	function get_devices_search_number($search,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_devices('search_number',$disable,$search,$order,$limit,$assoc,$initialized));
	}

	function get_devices_list($disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_devices('list',$disable,null,null,$order,$limit,$assoc,$initialized));
	}

	function _get_devices($action,$disable=null,$search='',$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$initialized,$order,$limit);
				break;
			case 'search_number':
				$rs = $this->_dso->search($search,$disable,$initialized,$order,$limit,'number');
				break;
			case 'list':
			default:
				$rs = $this->_dso->get_all($disable,$initialized,$order,$limit,null,null,null);
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
			$r[$devicefeatures['id']] = $devicefeatures;
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	function set_add($arr)
	{
		return($this->_set('add',$arr));
	}

	function set_edit($arr)
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr));
	}

	function _set($action,$arr)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('protocol',$arr) === false
		|| dwho_issa('devicefeatures',$arr) === false)
			return(false);

		$this->_protocolname = $protocolname;

		if(isset($arr['protocol']['callerid']) === true)
			$arr['protocol']['callerid'] = $this->_service->mk_callerid($arr['protocol']['callerid']);

		if($arr['protocol']['protocol'] == 'sccp')
		{
			$arr['protocol']['number']     = $arr['devicefeatures']['number'];
			if(array_key_exists('musiconhold',$arr['devicefeatures']))
				$arr['protocol']['musicclass'] = $arr['devicefeatures']['musiconhold'];
		}

		$this->set_protocol($arr['protocol'],$protocolname);

		$arr['devicefeatures']['protocol'] = $protocolname;
		$arr['devicefeatures']['protocolid'] = 0;

		if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			$name = $this->get_result_var('protocol','interface');
		else
			$name = $this->get_result_var('protocol','name');

		$vmaction = $action;

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			$arr['voicemail-option'] = 'none';

		if(isset($arr['voicemail-option']) === true)
		{
			switch($arr['voicemail-option'])
			{
				case 'add':
				case 'none':
					$vmaction = $arr['voicemail-option'];
					$arr['devicefeatures']['voicemailid'] = null;
					break;
				case 'search':
					$vmaction = 'edit';
					break;
			}
		}

		$arr['devicefeatures']['name'] = $name;

		$this->set_devicefeatures($action,$arr['devicefeatures']);

		$number = (string) $this->get_result_var('devicefeatures','number');
		$protocolname = (string) $this->get_result_var('devicefeatures','protocol');
		$simultcalls = (int) $this->get_result_var('devicefeatures','simultcalls');
		$musiconhold = (string) $this->get_result_var('devicefeatures','musiconhold');

		$numhaslen = dwho_has_len($number);

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
		  $this->_set_result_var('devicefeatures','voicemailtype',null);

		switch($this->get_result_var('devicefeatures','voicemailtype'))
		{
		  case 'asterisk':
		    break;
		  case 'exchange':
		    if($numhaslen === false)
		      $this->_set_result_var('devicefeatures','voicemailtype',null);
		  default:
		    $vmaction = 'none';
		    $this->_set_result_var('devicefeatures','voicemailid',null);
		    break;
		}

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SIP)
			$this->_set_result_var('protocol','call-limit',(2 * $simultcalls));

		if($this->_protocolname !== XIVO_SRE_IPBX_AST_PROTO_CUSTOM
		&& dwho_has_len($musiconhold) === true)
			$this->_set_result_var('protocol','mohsuggest',$musiconhold);

		if(dwho_issa('group',$arr) === true
		&& dwho_issa('group-select',$arr) === true
		&& $this->set_groupmember($arr['group'],
					  $arr['group-select'],
					  $name,
					  $number,
					  $protocolname) === true
		&& $this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SIP)
		{
			$callgroup = $this->get_result('callgroup');

			if(is_array($callgroup) === true && isset($callgroup[0]) === true)
				$callgroup = implode(',',$callgroup);
			else
				$callgroup = '';

			$this->_set_result_var('protocol','callgroup',$callgroup);
		}

		if(dwho_issa('queue',$arr) === true && dwho_issa('queue-select',$arr) === true)
			$this->set_queuemember($arr['queue'],
					       $arr['queue-select'],
					       $name,
					       $number,
					       $protocolname);

		if(dwho_issa('dialaction',$arr) === true)
			$this->set_dialaction($arr['dialaction']);

		if($this->_errnb === 0 && $numhaslen === true)
		{
			if(($rsusermacro = $this->chk_macro('usermacro',
							    $number,
							    $this->_mk_usermacro_appdata(0))))
				$this->_set_result('usermacro',$rsusermacro);

			$this->set_extenumbers($action,$number);
		}

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
		{
			if($this->get_errnb() > 0)
				$this->_protocolname = $r = false;
			else
				$r = true;

			return($r);
		}

		if($this->_errnb === 0 && $numhaslen === true)
		{
			$callerid = (string) $this->get_result_var('protocol','callerid');
			$callerid = $this->_service->mk_callerid($callerid, $number, $protocolname);
			$this->_set_result_var('protocol','callerid',$callerid);

			$enablehint = (bool) $this->get_result_var('devicefeatures','enablehint') === false;

			if(($hints = $this->set_hints($action,$name,$protocolname,$number,$enablehint)) === false)
				$this->_set_error('hints');

			$this->_set_result('hints',$hints);
		}

		if(dwho_issa('rightcall',$arr) === true)
			$this->set_rightcall($arr['rightcall']);

		if(dwho_issa('voicemail',$arr) === true
		&& dwho_has_len($arr['voicemail'],'mailbox') === true)
		{
			if($vmaction === 'add')
				$arr['voicemail']['context'] = $context;

			if(isset($arr['voicemail']['deletevoicemail']) === false)
				$arr['voicemail']['deletevoicemail'] = 0;

			$this->_set_result_var('protocol','mailbox',$arr['voicemail']['mailbox'].'@'.$context);

			if($vmaction !== 'disable')
			{
				if(dwho_issa('voicemailfeatures',$arr) === true)
					$this->set_voicemail($vmaction,$arr['voicemail'],$arr['voicemailfeatures']);
				else
					$this->set_voicemail($vmaction,$arr['voicemail']);
			}
		}

		if(dwho_issa('phonefunckey',$arr) === true)
			$this->set_phonefunckey($arr['phonefunckey']);

		if(dwho_issa('autoprov',$arr) === true)
			$this->set_autoprov($action,$arr['autoprov'],$protocolname);

		// QUEUESKILLS
		if(dwho_issa('queueskills',$arr) === true)
			$this->set_queueskills($action, $arr['queueskills']);

		if($this->get_errnb() > 0)
			$this->_protocolname = $r = false;
		else
			$r = true;

		// schedule
		if(array_key_exists('schedule_id', $arr))
			$this->_set_result('schedule_id', intval($arr['schedule_id']));

		return($r);
	}

	function set_protocol($arr,$protocolname)
	{
		if(is_array($arr) === false
		|| ($protocol = &$this->_service->get_protocol_module($protocolname)) === false)
		{
			$this->_set_result('protocol',null);
			$this->_set_error('protocol','invalid module');
			return(false);
		}

		if(isset($arr['host-type']) === true)
			$arr['host'] = $arr['host-type'];
		else if(isset($arr['host']) === false)
			$arr['host'] = '';

		if(isset($arr['host-static']) === true && $arr['host'] === 'static')
			$arr['host'] = $arr['host-static'];

		if(($rs = $protocol->chk_values($arr)) === false)
		{
			$this->_set_result('protocol',$protocol->get_filter_result());
			$this->_set_error('protocol',$protocol->get_filter_error());
			return(false);
		}

		if(dwho_issa('allow',$rs) === true)
			$rs['allow'] = implode(',',$rs['allow']);

		$this->_set_result('protocol',$rs);

		return(true);
	}

	function set_devicefeatures($action,$arr)
	{
		if(($action !== 'add' && $action !== 'edit') === true
		|| ($action === 'edit' && dwho_issa('devicefeatures',$this->_origin) === false) === true)
			return(false);
		else if(is_array($arr) === false)
		{
			$this->_set_result('devicefeatures',null);
			$this->_set_error('devicefeatures','invalid data');
			return(false);
		}

		$this->get_musiconhold();

		if(isset($arr['musiconhold']) === true
		&& isset($this->_musiconhold[$arr['musiconhold']]) === false)
			$arr['musiconhold'] = '';

		if($action === 'edit'
		&& isset($arr['profileclient']) === false
		&& isset($arr['enableclient']) === false)
			$arr['profileclient'] = $this->_origin['devicefeatures']['profileclient'];

		$this->get_profileclient_list();

		if(isset($arr['profileclient']) === true
		&& isset($this->_profileclientlist[$arr['profileclient']]) === false)
			$arr['profileclient'] = '';

		if(isset($arr['destunc']) === true
		&& dwho_has_len($arr['destunc']) === false)
			$arr['enableunc'] = false;

		if(isset($arr['destrna']) === true
		&& dwho_has_len($arr['destrna']) === false)
			$arr['enablerna'] = false;

		if(isset($arr['destbusy']) === true
		&& dwho_has_len($arr['destbusy']) === false)
			$arr['enablebusy'] = false;

		if(isset($arr['outcallerid-type']) === true)
			$arr['outcallerid'] = $arr['outcallerid-type'];
		else if(isset($arr['outcallerid']) === false)
			$arr['outcallerid'] = '';

		if(isset($arr['outcallerid-custom']) === true
		&& $arr['outcallerid'] === 'custom')
			$arr['outcallerid'] = $arr['outcallerid-custom'];

		if(($rs = $this->_devicefeatures->chk_values($arr)) === false)
		{
			$this->_set_result('devicefeatures',$this->_devicefeatures->get_filter_result());
			$this->_set_error('devicefeatures',$this->_devicefeatures->get_filter_error());
			return(false);
		}
		else
		{
			if($action === 'edit')
				$id = $this->_origin['devicefeatures']['id'];
			else
				$id = null;

			if($this->_devicefeatures->loginclient_exists($rs['loginclient'],
								    $rs['context'],
								    $id) === true)
			{
				$this->_set_result('devicefeatures',$rs);
				$this->_set_error('devicefeatures','client login exists');
				return(false);
			}
		}

		if(isset($rs['loginclient']) === false
		|| dwho_has_len($rs['loginclient']) === false)
		{
			$rs['enableclient'] = false;
			$rs['passwdclient'] = '';
		}

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM
		|| dwho_has_len($rs['agentid']) === false
		|| is_object($this->_agentfeatures) === false
		|| $this->_agentfeatures->get_primary($rs['agentid']) === false)
			$rs['agentid'] = null;

		$this->_set_result('devicefeatures',$rs);

		return(true);
	}

	function _set_usermacro($action,$devicefeaturesid)
	{
		$rs = false;

		if(($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0
		|| ($rs = $this->get_result('usermacro')) === null
		|| $rs === false)
			return($rs);
		else if(($rsmacro = $this->set_macro($action,
						     'usermacro',
						     $rs['exten'],
						     $this->_mk_usermacro_appdata($devicefeaturesid),
						     $rs['context'])) === false)
		return(false);

		$this->_set_result('usermacro',$rsmacro);

		return(true);
	}

	function set_hints($action,$name,$protocolname,$number,$disable=null)
	{
		if($action !== 'add' && $action !== 'edit')
			return(false);
		else if($action === 'edit' && dwho_issa('hints',$this->_info) !== false)
			return($this->_extensions->chk_hints($name,$protocolname,$number,$disable));

		return($this->_extensions->new_hints($name,$protocolname,$number,$disable));
	}

	function set_groupmember($group,$select,$name,$context='',$number='',$protocolname='')
	{
		return($this->_set_member_type('group',$group,$select,$name,$context,$number,$protocolname));
	}

	function set_queuemember($queue,$select,$name,$context='',$number='',$protocolname='')
	{
		return($this->_set_member_type('queue',$queue,$select,$name,$context,$number,$protocolname));
	}

	function _set_member_type($type,$list,$select,$name,$context='',$number='',$protocolname='')
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| is_array($list) === false
		|| is_array($select) === false
		|| ($module = &$this->_service->get_module($type.'features')) === false
		|| is_object($this->_queuemember) === false)
			return(false);

		$slt = array_values($select);

		if(($nb = count($slt)) === 0)
			return(null);

		$info = array();
		$info['usertype'] = 'user';
		$info['userid'] = 0;
		$info['category'] = $type;

		$key = $type.'member';

		$tmp = $reslist = array();

		if($type === 'group')
		{
			$callgroup = array();
			$info['penalty'] = 0;
		}
		if($type == 'queue')
			$info['skills'] = '';

		for($i = 0;$i < $nb;$i++)
		{
			$qname = &$slt[$i];

			if(isset($tmp[$qname]) === true
			|| isset($list[$qname]) === false
			|| ($chantype = dwho_ak('chantype',$list[$qname],true)) === false
			|| ($interface = $this->mk_interface($name,
							     $chantype,
							     $context,
							     $number,
							     $protocolname)) === false
			|| ($typeid = $module->get_primary(array('name' => $qname))) === false)
				continue;

			$info['queue_name'] = $qname;
			$info['interface'] = $interface['interface'];
			$info['channel'] = $interface['channel'];

			$values = array_merge($list[$qname],$info);

			if(($rs = $this->_queuemember->chk_values($values)) === false)
				continue;
			else if($type === 'queue')
				$rs['queuefeaturesid'] = $typeid;
			else
			{
				$rs['groupfeaturesid'] = $typeid;
				$callgroup[] = $typeid;
			}

			$tmp[$qname] = 1;
			$reslist[] = $rs;
		}

		if(isset($reslist[0]) === false)
		{
			$this->_set_result($key,false);
			$this->_set_error($key,'empty');

			if($type === 'group')
				$this->_set_result('callgroup','');

			return(false);
		}

		$this->_set_result($key,$reslist);

		if($type === 'group')
			$this->_set_result('callgroup',$callgroup);

		return(true);
	}

	function set_voicemail($action,$voicemail,$voicemailfeatures=null)
	{
		if(($action !== 'add' && $action !== 'edit') === true
		|| is_array($voicemail) === false
		|| empty($voicemail) === true
		|| is_object($this->_voicemail) === false)
			return(false);

		$rs = array();
		$rs['voicemail'] = $voicemail;

		if(is_array($voicemailfeatures) === true)
			$rs['voicemailfeatures'] = $voicemailfeatures;

		if($action === 'add')
			$r = $this->_voicemail->set_add($rs);
		else
			$r = $this->_voicemail->set_edit($rs,false);

		if(($voicemailerror = $this->_voicemail->get_error('voicemail')) !== null)
		{
			$this->_set_error('voicemail',$voicemailerror);
			$this->_set_result('voicemail',$this->_voicemail->get_result('voicemail'));
		}
		else $this->_set_result('voicemail',$this->_voicemail->get_result('voicemail'));

		if(($voicemailfeatureserror = $this->_voicemail->get_error('voicemailfeatures')) !== null)
		{
			$this->_set_error('voicemailfeatures',$voicemailfeatureserror);
			$this->_set_result('voicemailfeatures',$this->_voicemail->get_result('voicemailfeatures'));
		}
		else $this->_set_result('voicemailfeatures',$this->_voicemail->get_result('voicemailfeatures'));

		return($r);
	}

	function set_phonefunckey($list)
	{
		if(($list = dwho_group_array('fknum',$list)) === false)
			return(false);

		$reslist = $errlist = $tmp = array();

		$nb = count($list);

		for($i = $j = 0;$i < $nb;$i++)
		{
			$ref = &$list[$i];
			$ref['iddevicefeatures'] = 0;

			if(($val = $this->_phonefunckey->mk_values_array($ref)) === false)
				continue;
			else if(($info = $this->_phonefunckey->chk_values($val)) === false)
			{
				$errlist[$j] = $this->_phonefunckey->get_filter_error();
				$reslist[$j++] = $this->_phonefunckey->get_filter_result();
			}
			else if(isset($tmp[$info['fknum']]) === true)
			{
				$errlist[$j] = 'wrong phonefunckey';
				$reslist[$j++] = $info;
			}
			else
			{
				$tmp[$info['fknum']] = 1;
				$reslist[$j++] = $info;
			}
		}

		$this->_set_result('phonefunckey',$reslist);

		if(empty($errlist) === false)
		{
			$this->_set_error('phonefunckey',$errlist);
			return(false);
		}

		return(true);
	}

	function set_autoprov($action,$arr,$protocolname)
	{
		if(($action !== 'add' && $action !== 'edit') === true
		|| is_array($arr) === false)
			return(false);

		if($action === 'edit' && dwho_issa('autoprov',$this->_info) === true)
		{
			if(dwho_has_len($arr,'modact') === false)
				return(null);

			$modact = $arr['modact'];
			$arr = $this->_info['autoprov'];
			$arr['modact'] = $modact;
			$arr['proto'] = $protocolname;
		}
		else if(dwho_has_len($arr,'vendormodel') === false
		|| dwho_has_len($arr,'macaddr') === false)
			return(null);
		else if(($pos = strpos($arr['vendormodel'],'.')) === false)
			$arr['vendormodel'] = $arr['modact'] = '';
		else
		{
			if(isset($arr['modact']) === false)
				$arr['modact'] = 'prov';

			$arr['iddevicefeatures'] = 0;
			$vendor = substr($arr['vendormodel'],0,$pos);
			$model = substr($arr['vendormodel'],$pos + 1);

			if(($list = $this->get_autoprov_list()) === false)
				return(false);

			if(dwho_issa($vendor,$list) === true
			&& dwho_issa('model',$list[$vendor]) === true
			&& dwho_issa($model,$list[$vendor]['model']) === true)
			{
				$arr['vendor'] = $vendor;
				$arr['model'] = $model;
			}

			if(($macaddr = dwho_network::normalize_macaddr($arr['macaddr'])) !== false
			&& dwho_network::valid_macaddr($macaddr) !== false)
				$arr['macaddr'] = $macaddr;
			else
				$arr['macaddr'] = '';

			$arr['proto'] = $protocolname;
		}

		if(($rs = $this->_autoprov->chk_values($arr)) === false)
		{
			$this->_set_result('autoprov',$this->_autoprov->get_filter_result());
			$this->_set_error('autoprov',$this->_autoprov->get_filter_error());
			return(false);
		}

		$this->_set_result('autoprov',$rs);
		$this->_set_result_var('autoprov','modact',$arr['modact']);

		return(true);
	}

	function set_queueskills($action, $arr)
	{
		if($action !== 'add'
		|| is_array($arr) === false)
			return(false);

		$skills = array();
		foreach($arr as $skill)
		{
			$skills[] = array(
				'userid'    => null,
				'skillid'   => $skill['id'],
				'weight'    => intval($skill['weight'])
			);
		}

		$this->_set_result('queueskills', $skills);

		$appqueue = &$this->_service->get_application('queue');
		if($appqueue->userskills_setadd($skills) === false)
		{
				$this->_set_error('queueskills', $appqueue->userskills_get_error());
				return false;
		}

		return true;
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$devicefeaturesid = null;

		if($this->get_errnb() > 0
		|| $this->_protocolname === false
		|| ($protocolid = $this->add_protocol()) === false
		|| ($devicefeaturesid = $this->add_devicefeatures($protocolid)) === false
		|| $this->update_protocol_setvar($protocolid,$devicefeaturesid) === false
		|| $this->add_usermacro($devicefeaturesid) === false
		|| $this->add_hints() === false
		|| $this->add_extenumbers($devicefeaturesid) === false
		|| $this->add_groupmember($devicefeaturesid) === false
		|| $this->add_queuemember($devicefeaturesid) === false
		|| $this->add_rightcall($devicefeaturesid) === false
		|| $this->add_dialaction($devicefeaturesid) === false
		|| $this->add_contextnummember($devicefeaturesid) === false
		|| $this->add_voicemail($devicefeaturesid) === false
		|| $this->add_phonefunckey($devicefeaturesid) === false
		|| $this->add_phone($devicefeaturesid) === false
		|| $this->add_queueskills($devicefeaturesid) === false
		|| $this->add_schedule_path($devicefeaturesid) === false)
		{
			$r = false;

			if($devicefeaturesid !== null)
				$this->_reverse_add();
		}

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SCCP)
			$this->_service->discuss('sccp reload');

		$this->_status = '';

		return($r);
	}

	function add_protocol()
	{
		if(($rs = $this->get_result('protocol')) === null
		|| ($protocol = &$this->_service->get_protocol_module($this->_protocolname)) === false)
			return(false);

		return(($this->_return['protocol'] = $protocol->add($rs)));
	}

	function add_devicefeatures($protocolid)
	{
		if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($rs = $this->get_result('devicefeatures')) === null
		|| $rs === false)
			return(false);

		$rs['protocolid'] = $protocolid;
		$this->_return['devicefeatures'] = $this->_devicefeatures->add($rs);

		if (isset($rs['servicesgroup_id']) === true
		&& empty($rs['servicesgroup_id']) === false)
		{
			$arr = array();
			$arr['servicesgroup_id'] = (int) $rs['servicesgroup_id'];
			$arr['devicefeatures_id'] = (int) $this->_return['devicefeatures'];
			$this->_servicesgroup_user->add($arr);
		}
		return($this->_return['devicefeatures']);
	}

	function update_protocol_setvar($protocolid,$devicefeaturesid)
	{
		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			return(null);
		else if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0
		|| ($protocol = &$this->_service->get_protocol_module($this->_protocolname)) === false)
			return(false);

		$val = array();
		$val['setvar'] = 'XIVO_USERID='.$devicefeaturesid;

		return($protocol->edit($protocolid,$val));
	}

	function add_usermacro($devicefeaturesid)
	{
		if(($rs = $this->_set_usermacro('add',$devicefeaturesid)) !== true)
			return($rs);

		$ret = parent::add_macro('usermacro');
		return($ret);
	}

	function add_hints()
	{
		if(($rs = $this->get_result('hints')) === null || $rs === false)
			return($rs);

		return(($this->_return['hints'] = $this->_extensions->add_hints($rs)));
	}

	function add_groupmember($devicefeaturesid)
	{
		return($this->_add_member_type('group',$devicefeaturesid));
	}

	function add_queuemember($devicefeaturesid)
	{
		return($this->_add_member_type('queue',$devicefeaturesid));
	}

	function _add_member_type($type,$devicefeaturesid)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| ($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $devicefeaturesid;
			if($type == 'queue')
			{ $rs[$i]['skills'] = $devicefeaturesid; }

			unset($rs[$i]['groupfeaturesid'],$rs[$i]['queuefeaturesid']);

			if($this->_queuemember->add($rs[$i]) === false)
				return(false);

			$ret['queue_name'] = $rs[$i]['queue_name'];
			$ret['interface'] = $rs[$i]['interface'];

			$this->_return[$key][] = $ret;
		}

		if(isset($this->_return[$key][0]) === false)
			$this->_return[$key] = false;

		return(true);
	}

	function add_voicemail($devicefeaturesid)
	{
		if(($voicemailid = dwho_ulongint($this->get_result_var('devicefeatures','voicemailid'))) === 0)
			return($this->_add_voicemail($devicefeaturesid));
		else if(is_object($this->_voicemail) === false
		|| $this->_voicemail->get($voicemailid) === false
		|| ($rs = $this->get_result('voicemail')) === null
		|| $rs === false)
			return($rs);

		return(($this->_return['voicemail'] = $this->_voicemail->edit(false)));
	}

	function _add_voicemail($devicefeaturesid)
	{
		if(($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0
		|| ($rs = $this->get_result('voicemail')) === null
		|| $rs === false)
			return($rs);
		else if(($this->_return['voicemail'] = $this->_voicemail->add()) === true
		&& (($voicemailid = dwho_ulongint($voicemailid = $this->_voicemail->get_return('voicemail'))) === 0
		   || $this->_devicefeatures->edit($devicefeaturesid,array('voicemailid' => $voicemailid)) === false) === true)
			return(false);

		return($this->_return['voicemail']);
	}

	function add_phonefunckey($devicefeaturesid)
	{
		$rs = false;

		if(($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0
		|| ($rs = $this->get_result('phonefunckey')) === null
		|| $rs === false)
			return($rs);

		$context = $this->get_result_var('devicefeatures','context');
		$bsfilter = $this->get_result_var('devicefeatures','bsfilter');

		$id = $this->_return['phonefunckey'] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$ref['iddevicefeatures'] = $devicefeaturesid;

			if(($ref['typeextenumbers'] !== null
			   || $ref['typeextenumbersright'] !== null) === true
			&& $this->_phonefunckey->is_valid($ref['typeextenumbers'],
							  $ref['typevalextenumbers'],
							  $ref['typeextenumbersright'],
							  $ref['typevalextenumbersright'],
							  $ref['iddevicefeatures'],
							  null,
							  $context) === false)
				return(false);
			else if($ref['typeextenumbers'] === 'extenfeatures'
			&& $ref['typevalextenumbers'] === 'bsfilter'
			&& $this->_dso->chk_bsfilter($ref['iddevicefeatures'],
						     $context,
						     $bsfilter,
						     $ref['typevalextenumbersright']) === false)
				return(false);

			$id['iddevicefeatures'] = $ref['iddevicefeatures'];
			$id['fknum'] = $ref['fknum'];

			if($this->_phonefunckey->add($ref) === false)
				return(false);

			$this->_return['phonefunckey'][] = $id;
		}

		if(isset($this->_return['phonefunckey'][0]) === false)
			$this->_return['phonefunckey'] = false;

		return(true);
	}

	function add_phone($devicefeaturesid)
	{
		$rs = false;

		if(($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0
		|| ($rs = $this->get_result('autoprov')) === null
		|| $rs === false)
			return($rs);

		$rs['iddevicefeatures'] = $devicefeaturesid;

		if($this->_autoprov->authoritative($rs,$rs['modact']) === false)
			$this->_return['autoprov'] = false;
		else
			$this->_return['autoprov'] = $devicefeaturesid;

		$this->_service->discuss('dialplan reload');

		return($this->_return['autoprov']);
	}

	function add_queueskills($devicefeaturesid)
	{
		$rs = false;

		if(($devicefeaturesid = dwho_ulongint($devicefeaturesid)) === 0
		|| ($rs = $this->get_result('queueskills')) === null
		|| $rs === false)
			return($rs);

		foreach($rs as &$skill)
		{ $skill['userid'] = $devicefeaturesid; }

		$appqueue = &$this->_service->get_application('queue');
		$ret = $appqueue->userskills_add($rs);

		return $ret;
	}

	function add_schedule_path($devicefeaturesid)
	{
		return $this->_schedule_path->schedule_add(
			$this->get_result('schedule_id'),
			'user',
			$devicefeaturesid);
	}

	function _reverse_add()
	{
		if($this->get_errnb() > 0
		|| $this->_protocolname === false
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
				case 'protocol':
					$protocol = &$this->_service->get_protocol_module($this->_protocolname);
					$protocol->delete($val);
					break;
				case 'devicefeatures':
					$this->_devicefeatures->delete($val);
					break;
				case 'usermacro':
					$this->_extensions->delete_exten($val);
					break;
				case 'hints':
					$this->_extensions->delete_hints($val);
					break;
				case 'groupmember':
				case 'queuemember':
					if(is_array($val) === false)
						continue;

					foreach($val as $memberval)
						$this->_queuemember->delete($memberval);
					break;
				case 'rightcall':
					$this->_rightcall->reverse_add();
					break;
				case 'dialaction':
					$this->_dialaction->reverse_add();
					break;
				case 'contextnummember':
					$this->_contextnummember->reverse_add();
					break;
				case 'phonefunckey':
					if(is_array($val) === false)
						continue;

					foreach($val as $phonefkeyval)
					{
						if($phonefkeyval !== false)
							$this->_phonefunckey->delete($phonefkeyval);
					}
					break;
				case 'voicemail':
					$this->_voicemail->reverse_add();
					break;
				case 'autoprov':
					$this->_autoprov->userdeleted($val);
					break;
				case 'extenumbers':
					$this->_extenumbers->reverse_add();
					break;
			}
		}

		return(true);
	}

	function edit()
	{
		$this->_status = 'edit';
		$this->_return = array();

		if(is_array($this->_info) === false
		|| empty($this->_info) === true
		|| $this->get_errnb() > 0
		|| $this->_protocolname === false
		|| ($protocolret = $this->edit_protocol()) === false)
		{
			$this->_status = '';
			return(false);
		}
		else if($this->edit_devicefeatures($protocolret) === false)
		{
			$this->edit_origin_protocol($protocolret);
			$this->_status = '';
			return(false);
		}
		else if($this->_info['devicefeatures']['number'] !== '')
		{
			if($this->get_result('usermacro') === null
			|| $this->get_result('extenumbers') === null)
			{
				$this->delete_macro('usermacro');
				$this->delete_extenumbers();
				$this->delete_hints();
			}
			else if($this->edit_usermacro($this->_info['devicefeatures']['id']) === false
			|| $this->edit_extenumbers() === false)
			{
				$this->_reverse_edit($protocolret);
				$this->_status = '';
				return(false);
			}
			else if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
				$this->delete_hints();
			else
			{
				if($this->_info['devicefeatures']['protocol'] === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
					$hints = $this->add_hints();
				else
					$hints = $this->edit_hints();

				if($hints === false)
				{
					$this->_reverse_edit($protocolret);
					$this->_status = '';
					return(false);
				}
			}
		}
		else if($this->add_usermacro($this->_info['devicefeatures']['id']) === false
		|| $this->add_extenumbers($this->_info['devicefeatures']['id']) === false
		|| ($this->_protocolname !== XIVO_SRE_IPBX_AST_PROTO_CUSTOM
		   && $this->add_hints() === false) === true)
		{
			$this->_reverse_edit($protocolret);
			$this->_status = '';
			return(false);
		}

		if($this->edit_groupmember() === false
		|| $this->edit_queuemember() === false
		|| $this->edit_rightcall() === false
		|| $this->edit_dialaction() === false
		|| $this->edit_contextnummember() === false
		|| $this->edit_voicemail() === false
		|| $this->edit_phonefunckey() === false
		|| $this->edit_schedule_path() === false)
		{
			$this->_reverse_edit($protocolret);
			$this->_status = '';
			return(false);
		}

		$this->edit_phone();

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SCCP)
			$this->_service->discuss('sccp reload');

		$this->_status = '';
		return(true);
	}

	function edit_protocol()
	{
		if(dwho_issa('protocol',$this->_info) === false
		|| dwho_issa('devicefeatures',$this->_info) === false
		|| ($protocol = &$this->_service->get_protocol_module($this->_protocolname)) === false)
			return(false);
		else if($this->_info['devicefeatures']['protocol'] === $this->_protocolname)
		{
			if(($rs = $this->get_result('protocol')) === null)
				return(false);

			if(($ret = $protocol->edit($this->_info['protocol']['id'],$rs)) === false)
			{	$this->_return['protocol'] = $ret; return false; }

			return(($this->_return['protocol'] = $this->update_protocol_setvar($this->_info['protocol']['id'],  $this->_info['devicefeatures']['id'])));
		}
		else if(($protocolid = $this->add_protocol()) === false)
			return(false);
		else if($this->delete_protocol() === false
		|| $this->update_protocol_setvar($protocolid,
						 $this->_info['devicefeatures']['id']) === false)
		{
			$protocol->delete($protocolid);
			return(false);
		}

		return(($this->_return['protocol'] = $protocolid));
	}

	function edit_origin_protocol($protocolid=0)
	{
		if(dwho_issa('protocol',$this->_origin) === false
		|| dwho_issa('devicefeatures',$this->_info) === false
		|| ($protocol = &$this->_service->get_protocol_module($this->_info['devicefeatures']['protocol'])) === false)
			return(false);
		else if($this->_info['devicefeatures']['protocol'] === $this->_protocolname)
			return($protocol->edit_origin($this->_origin['protocol']));
		else if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($proto = &$this->_service->get_protocol_module($this->_protocolname)) === false
		|| $proto->delete($protocolid) === false)
			return(false);

		return($protocol->add_origin($this->_origin['protocol']));
	}

	function edit_devicefeatures($protocolid)
	{
		if(dwho_issa('devicefeatures',$this->_info) === false
		|| dwho_issa('protocol',$this->_info) === false
		|| ($rs = $this->get_result('devicefeatures')) === null
		|| $rs === false)
			return(false);
		else if($this->_info['devicefeatures']['protocol'] === $this->_protocolname)
		{
			$rs['protocolid'] = $this->_info['protocol']['id'];
			$provisioning = false;
		}
		else if(($protocolid = dwho_ulongint($protocolid)) !== 0)
		{
			$rs['protocolid'] = $protocolid;
			$provisioning = true;
		}
		else
			return(false);

		if (isset($rs['servicesgroup_id']) === true
		&& empty($rs['servicesgroup_id']) === false)
		{
			$arr = array();
			$arr['servicesgroup_id'] = (int) $rs['servicesgroup_id'];
			$arr['devicefeatures_id'] = (int) $this->_info['devicefeatures']['id'];
			if ($this->_servicesgroup_user->get_nb($arr) === 0)
				$this->_servicesgroup_user->add($arr);
			else
				$this->_servicesgroup_user->edit($arr['servicesgroup_id'],$arr);
		}

		return(($this->_return['devicefeatures'] = $this->_devicefeatures->edit($this->_info['devicefeatures']['id'],
										    $rs,
										    $provisioning)));
	}

	function edit_usermacro($devicefeaturesid)
	{
		if(($rs = $this->_set_usermacro('edit',$devicefeaturesid)) !== true)
			return($rs);

		$ret = parent::edit_macro('usermacro');
		return $ret;
	}

	function edit_hints()
	{
		$rs = false;

		if(dwho_issa('hints',$this->_info) === false
		|| ($rs = $this->get_result('hints')) === null
		|| $rs === false)
			return($rs);

		return(($this->_return['hints'] = $this->_extensions->edit($this->_info['hints']['id'],$rs)));
	}

	function edit_groupmember()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('groupmember',$this->_info) === false)
			return($this->add_groupmember($this->_info['devicefeatures']['id']));

		$this->_return['groupmember'] = $this->delete_groupmember();

		if($this->get_result('groupmember') === null)
			return($this->_return['groupmember']);

		return($this->_edit_member_type('group'));
	}

	function edit_queuemember()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('queuemember',$this->_info) === false)
			return($this->add_queuemember($this->_info['devicefeatures']['id']));

		$this->_return['queuemember'] = $this->delete_queuemember();

		if($this->get_result('queuemember') === null)
			return($this->_return['queuemember']);

		return($this->_edit_member_type('queue'));
	}

	function _edit_member_type($type)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $this->_info['devicefeatures']['id'];
			if($type == 'queue')
			{ $rs[$i]['skills'] = $this->_info['devicefeatures']['id']; }

			unset($rs[$i]['groupfeaturesid'],$rs[$i]['queuefeaturesid']);

			if($this->_queuemember->add($rs[$i]) === false)
				return(false);

			$ret['queue_name'] = $rs[$i]['queue_name'];
			$ret['interface'] = $rs[$i]['interface'];

			$this->_return[$key][] = $ret;
		}

		if(isset($this->_return[$key][0]) === false)
			$this->_return[$key] = false;

		return(true);
	}

	function edit_rightcall()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		return(parent::edit_rightcall($this->_info['devicefeatures']['id']));
	}

	function edit_dialaction()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		return(parent::edit_dialaction($this->_info['devicefeatures']['id']));
	}

	function edit_contextnummember()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		return(parent::edit_contextnummember($this->_info['devicefeatures']['id']));
	}

	function edit_voicemail()
	{
		$rs = false;

		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);
		else if(($voicemailid = dwho_ulongint($this->get_result_var('devicefeatures','voicemailid'))) === 0)
			return($this->_add_voicemail($this->_info['devicefeatures']['id']));
		else if(is_object($this->_voicemail) === false
		|| $this->_voicemail->get($voicemailid) === false
		|| ($rs = $this->get_result('voicemail')) === null
		|| $rs === false)
			return($rs);

		return(($this->_return['voicemail'] = $this->_voicemail->edit(false)));
	}

	function edit_phonefunckey()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('phonefunckey',$this->_info) === false)
			return($this->add_phonefunckey($this->_info['devicefeatures']['id']));

		$this->_return['phonefunckey'] = $this->delete_phonefunckey();

		if(($rs = $this->get_result('phonefunckey')) === null || $rs === false)
			return($rs);

		$context = $this->get_result_var('devicefeatures','context');
		$bsfilter = $this->get_result_var('devicefeatures','bsfilter');

		$id = $this->_return['phonefunckey'] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$ref['iddevicefeatures'] = $this->_info['devicefeatures']['id'];

			if(($ref['typeextenumbers'] !== null
			|| $ref['typeextenumbersright'] !== null) === true
			&& $this->_phonefunckey->is_valid($ref['typeextenumbers'],
							  $ref['typevalextenumbers'],
							  $ref['typeextenumbersright'],
							  $ref['typevalextenumbersright'],
							  $ref['iddevicefeatures'],
							  null,
							  $context) === false)
				return(false);
			else if($ref['typeextenumbers'] === 'extenfeatures'
			&& $ref['typevalextenumbers'] === 'bsfilter'
			&& $this->_dso->chk_bsfilter($ref['iddevicefeatures'],
						     $context,
						     $bsfilter,
						     $ref['typevalextenumbersright']) === false)
				return(false);

			$id['iddevicefeatures'] = $ref['iddevicefeatures'];
			$id['fknum'] = $ref['fknum'];

			if($this->_phonefunckey->add($ref) === false)
				return(false);

			$this->_return['phonefunckey'][] = $id;
		}

		if(isset($this->_return['phonefunckey'][0]) === false)
			$this->_return['phonefunckey'] = false;

		return(true);
	}

	function edit_phone()
	{
		if(($rs = dwho_issa('devicefeatures',$this->_info)) === false
		|| ($rs = $this->get_result('autoprov')) === null
		|| $rs === false)
			return($rs);

		$rs['iddevicefeatures'] = $this->_info['devicefeatures']['id'];

		if(dwho_issa('autoprov',$this->_info) !== false)
			$this->_return['autoprov'] = $this->_autoprov->notification($rs,$rs['modact']);
		else
			$this->_return['autoprov'] = $this->_autoprov->authoritative($rs,$rs['modact']);

		$this->_service->discuss('dialplan reload');

		return($this->_return['autoprov']);
	}

	function edit_schedule_path()
	{
		$this->_schedule_path->delete_where(array('path' => 'user', 'pathid' =>	intval($this->_info['devicefeatures']['id'])));

		return $this->_schedule_path->schedule_add(
			$this->get_result('schedule_id'),
			'user',
			$this->_info['devicefeatures']['id']);
	}

	function _reverse_edit($protocolid=0)
	{
		if($this->get_errnb() > 0
		|| $this->_protocolname === false
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
				case 'protocol':
					$this->edit_origin_protocol($protocolid);
					break;
				case 'devicefeatures':
					if(isset($this->_origin['devicefeatures']) === false
					|| $this->_origin['devicefeatures'] === false)
						$this->delete_devicefeatures();
					else
						$this->_devicefeatures->edit_origin($this->_origin['devicefeatures']);
					break;
				case 'voicemail':
					$this->_voicemail->reverse_edit();
					break;
				case 'usermacro':
					if(isset($this->_origin['usermacro']) === false
					|| $this->_origin['usermacro'] === false)
						$this->delete_macro('usermacro');
					else
						$this->_extensions->edit_origin($this->_origin['usermacro']);
					break;
				case 'hints':
					if(isset($this->_origin['hints']) === false
					|| $this->_origin['hints'] === false)
						$this->delete_hints();
					else
						$this->_extensions->edit_origin($this->_origin['hints']);
					break;
				case 'groupmember':
				case 'queuemember':
					if($key === 'groupmember')
						$this->delete_groupmember();
					else
						$this->delete_queuemember();

					if(isset($this->_origin[$key]) === true
					&& $this->_origin[$key] !== false)
						$this->_queuemember->add_origin_list($this->_origin[$key]);
					break;
				case 'rightcall':
					$this->_rightcall->reverse_edit($this->_status);
					break;
				case 'dialaction':
					$this->_dialaction->reverse_edit($this->_status);
					break;
				case 'contextnummember':
					$this->_contextnummember->reverse_edit($this->_status);
					break;
				case 'phonefunckey':
					$this->delete_phonefunckey();

					if(isset($this->_origin['phonefunckey']) === true
					&& $this->_origin['phonefunckey'] !== false)
						$this->_phonefunckey->add_origin_list($this->_origin['phonefunckey']);
					break;
				case 'autoprov':
					break;
				case 'extenumbers':
					$this->_extenumbers->reverse_edit($this->_status);
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

		if($this->delete_protocol() === false
		|| $this->delete_devicefeatures() === false
		|| $this->delete_macro('usermacro') === false
		|| $this->delete_hints() === false
		|| $this->delete_extenumbers() === false
		|| $this->delete_groupmember() === false
		|| $this->delete_queuemember() === false
		|| $this->delete_rightcall() === false
		|| $this->delete_dialaction() === false
		|| $this->delete_contextnummember() === false
		|| $this->delete_phonefunckey() === false
		|| $this->delete_phone() === false
		|| $this->delete_callfiltermember() === false
		|| $this->delete_queueskill() === false
		|| $this->delete_schedule_path() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}
		else
			$this->unlinks();

		$this->_status = '';

		return($r);
	}

	function delete_protocol()
	{
		if(dwho_issa('protocol',$this->_info) === false
		|| dwho_issa('devicefeatures',$this->_info) === false
		|| ($protocol = &$this->_service->get_protocol_module($this->_info['devicefeatures']['protocol'])) === false)
			return(false);

		$r = $protocol->delete($this->_info['protocol']['id']);

		if($this->_status === 'delete')
			$this->_return['protocol'] = $r;

		return($r);
	}

	function delete_devicefeatures()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$r = $this->_devicefeatures->delete($this->_info['devicefeatures']['id']);

		if($this->_status === 'delete')
			$this->_return['devicefeatures'] = $r;

		return($r);
	}

	function delete_hints()
	{
		return($this->delete_macro('hints'));
	}

	function delete_groupmember()
	{
		return($this->_delete_member_type('group'));
	}

	function delete_queuemember()
	{
		return($this->_delete_member_type('queue'));
	}

	function _delete_member_type($type)
	{
		if(($type !== 'group' && $type !== 'queue') === true)
			return(false);

		$key = $type.'member';

		if(dwho_issa($key,$this->_info) === false)
			return(null);
		else if(dwho_issa('devicefeatures',$this->_info) === false
		|| is_object($this->_queuemember) === false)
			return(false);

		$where = array();
		$where['usertype'] = 'user';
		$where['category'] = $type;
		$where['userid'] = $this->_info['devicefeatures']['id'];

		$r = $this->_queuemember->delete_where($where);

		if($this->_status === 'delete')
			$this->_return[$key] = $r;

		return($r);
	}

	function delete_phonefunckey()
	{
		if(dwho_issa('phonefunckey',$this->_info) === false)
			return(null);
		else if(dwho_issa('devicefeatures',$this->_info) === false
		|| is_object($this->_phonefunckey) === false)
			return(false);

		$where = array();
		$where['iddevicefeatures'] = $this->_info['devicefeatures']['id'];

		$r = $this->_phonefunckey->delete_where($where);

		if($this->_status === 'delete')
			$this->_return['phonefunckey'] = $r;

		return($r);
	}

	function delete_phone()
	{
		if(dwho_issa('autoprov',$this->_info) === false)
			return(null);
		else if(is_object($this->_autoprov) === false)
			return(false);

		$r = $this->_autoprov->userdeleted($this->_info['autoprov']['iddevicefeatures']);

		if($this->_status === 'delete')
			$this->_return['autoprov'] = $r;

		if($r !== false)
			$this->_service->discuss('dialplan reload');

		return($r);
	}

	function delete_callfiltermember()
	{
		if(($callfiltermember = &$this->_service->get_module('callfiltermember')) === false)
			return(true);

		$where = array();
		$where['type'] = 'user';
		$where['typeval'] = $this->_info['devicefeatures']['id'];

		$callfiltermember->delete_where($where);

		return(true);
	}

	function delete_queueskill()
	{
		$appqueue = &$this->_service->get_application('queue');
		return $appqueue->userskills_delete($this->_info['devicefeatures']['id']);
	}

	function delete_schedule_path()
	{
		return $this->_schedule_path->delete_where(array('path' => 'user', 'pathid' =>	$this->_info['user']['id']));
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
				case 'protocol':
					if(isset($this->_origin['protocol']) === false
					|| $this->_origin['protocol'] === false)
						continue;

					$protocol = &$this->_service->get_protocol_module($this->_info['devicefeatures']['protocol']);
					$protocol->add_origin($this->_origin['protocol']);
					break;
				case 'devicefeatures':
					if(isset($this->_origin['devicefeatures']) === true
					&& $this->_origin['devicefeatures'] !== false)
						$this->_devicefeatures->add_origin($this->_origin['devicefeatures']);
					break;
				case 'usermacro':
				case 'hints':
					if(isset($this->_origin[$key]) === true
					&& $this->_origin[$key] !== false)
						$this->_extensions->add_origin($this->_origin[$key]);
					break;
				case 'groupmember':
				case 'queuemember':
					if(isset($this->_origin[$key]) === true
					&& $this->_origin[$key] !== false)
						$this->_queuemember->add_origin_list($this->_origin[$key]);
					break;
				case 'rightcall':
					$this->_rightcall->add_origin_list();
					break;
				case 'dialaction':
					$this->_dialaction->add_origin_list();
					break;
				case 'contextnummember':
					$this->_contextnummember->add_origin();
					break;
				case 'phonefunckey':
					if(isset($this->_origin['phonefunckey']) === true
					&& $this->_origin['phonefunckey'] !== false)
						$this->_phonefunckey->add_origin_list($this->_origin['phonefunckey']);
					break;
				case 'autoprov':
					break;
				case 'extenumbers':
					if(isset($this->_origin['extenumbers']) === true
					&& $this->_origin['extenumbers'] !== false)
						$this->_extenumbers->add_origin($this->_origin['extenumbers']);
					break;
			}
		}

		return(true);
	}

	function unlinks()
	{
		if(dwho_issa('devicefeatures',$this->_info) === false)
			return(false);

		$this->_dialaction->unlinked('user',$this->_info['devicefeatures']['id']);

		return(true);
	}

	function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if(is_object($this->_protocol) === false)
			$r = false;
		else if($this->enable_protocol() === false
		|| $this->enable_devicefeatures() === false)
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

		if(is_object($this->_protocol) === false)
			$r = false;
		else if($this->disable_protocol() === false
		|| $this->disable_devicefeatures() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return(true);
	}

	function enable_protocol()
	{
		return($this->_enable_disable_protocol(false));
	}

	function disable_protocol()
	{
		return($this->_enable_disable_protocol(true));
	}

	function _enable_disable_protocol($disable=false)
	{
		if(dwho_issa('protocol',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_protocol->enable($this->_info['protocol']['id']);
		else
			$r = $this->_protocol->disable($this->_info['protocol']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['protocol'] = $r;

		return($r);
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
				case 'protocol':
					$this->_enable_disable_protocol($disable);
					break;
				case 'devicefeatures':
					$this->_enable_disable_devicefeatures($disable);
					break;
			}
		}

		return(true);
	}

	function _prepare_import($arr)
	{
		if(($issa_protocol = dwho_issa('protocol',$arr)) === false
		|| isset($arr['protocol']['protocol']) === false)
			return(false);

		$issa_devicefeatures = dwho_issa('devicefeatures',$arr);

		if(dwho_issa('voicemail',$arr) === true
		&& empty($arr['voicemail']) === false
		&& dwho_has_len($arr['voicemail'],'mailbox') === true)
		{
			if($issa_devicefeatures === true)
				$arr['devicefeatures']['enablevoicemail'] = true;

			if($issa_protocol === true && isset($arr['protocol']['subscribemwi']) === false)
				$arr['protocol']['subscribemwi'] = true;
		}
		else
			unset($arr['voicemail']);

		if($issa_protocol === true
		&& $issa_devicefeatures === true
		&& dwho_has_len($arr['protocol'],'callerid') === false)
		{
			$arr['protocol']['callerid'] = '';

			if(dwho_has_len($arr['devicefeatures'],'firstname') === true)
				$arr['protocol']['callerid'] = $arr['devicefeatures']['firstname'].' ';

			if(dwho_has_len($arr['devicefeatures'],'lastname') === true)
				$arr['protocol']['callerid'] .= $arr['devicefeatures']['lastname'];

			trim($arr['protocol']['callerid']);
		}

		if($issa_devicefeatures === true
		&& dwho_has_len($arr['devicefeatures'],'agentnumber') === true
		&& is_object($this->_agentfeatures) === true
		&& ($agentid = $this->_agentfeatures->get_primary(
						array('number' => $arr['devicefeatures']['agentnumber']))) !== false)
			$arr['devicefeatures']['agentid'] = $agentid;

		unset($arr['devicefeatures']['agentnumber']);

		return($arr);
	}

	function import_from_array($data,$save=true,$chkcontext=true)
	{
		$save = (bool) $save;

		if(is_array($data) === false
		|| ($nb = count($data)) === 0)
			return(false);

		$appincall = &$this->_service->get_application('incall');

		$incall = array();
		$incall['dialaction'] = array();

		$r = array();
		$r['lines'] = array();
		$r['total'] = array();
		$r['total']['success'] = 0;
		$r['total']['error'] = 0;
		$r['total']['count'] = $nb;

		$tpl = $GLOBALS['_TPL'];
		$tpl->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/pbx_settings/users/import.i18n', 'global');

		for($i = 0,$row = 1;$i < $nb;$i++,$row++)
		{
			if(($arr = $this->_prepare_import($data[$i])) === false
			|| $this->set_add($arr,$arr['protocol']['protocol'],$chkcontext) === false)
			{
				$r['lines'][$row] = 'error';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($data[$i], true), 'userimport', "line #$i");

				$err = array();
				foreach($this->get_error() as $k => $v)
					$err[] = $tpl->bbf("error(".$k."__".$v.")");
				$msg = sprintf('%s #%03d:&nbsp;&nbsp&nbsp&nbsp  %s', $tpl->bbf('line'), $i+1,
					implode(', ', $err));
				dwho_report::push('error', $msg, $tpl->bbf('import_fail'));
				continue;
			}
			else if(dwho_issa('incall',$arr) === false
			|| dwho_has_len($arr['incall'],'exten') === false)
			{
				if($save === true && $this->add() === false)
				{
					$r['lines'][$row] = 'error';
					$r['total']['error']++;

					dwho_logw(print_r($this->get_error(),true)."\n".print_r($data[$i], true), 'userimport', "line #$i");
					dwho_report::push('error', $this->get_error());
				}
				else
				{
					$r['lines'][$row] = 'success';
					$r['total']['success']++;
				}
				continue;
			}

			$incall['incall'] = $arr['incall'];

			$incall['dialaction']['answer'] = array();
			$incall['dialaction']['answer']['actiontype'] = 'user';
			$incall['dialaction']['answer']['actionarg1'] = 1;

			if(dwho_has_len($arr['incall'],'ringseconds') === true)
				$incall['dialaction']['answer']['actionarg2'] = $arr['incall']['ringseconds'];
			else
				$incall['dialaction']['answer']['actionarg2'] = '';

			unset($incall['incall']['ringseconds']);

			if($appincall->set_add($incall) === false)
			{
				$r['lines'][$row] = 'error';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($data[$i], true), 'userimport', "line #$i");
				continue;
			}
			else if($save === false)
			{
				$r['lines'][$row] = 'success';
				$r['total']['success']++;
				continue;
			}
			else if($this->add() === false)
			{
				$r['lines'][$row] = 'error';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($data[$i], true), 'userimport', "line #$i");
				dwho_report::push('error', $this->get_error());
				continue;
			}

			$incall['dialaction']['answer']['actionarg1'] = $this->get_return('devicefeatures');

			if($appincall->set_add($incall) === false
			|| $appincall->add() === false)
			{
				$r['lines'][$row] = 'error';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($data[$i], true), 'userimport', "line #$i");
				dwho_report::push('error', $this->get_error());
			}
			else
			{
				$r['lines'][$row] = 'success';
				$r['total']['success']++;
			}
		}


		return($r);
	}

	function import_csv($save=true)
	{
		$save = (bool) $save;

		if(dwho::load_class('dwho::file::csv') === false
		|| ($http_response = dwho_http::factory('response')) === false
		|| ($fileinfo = $http_response->upload_file('import',
							    $this->_conf['import']['file'])) === false)
			return(false);

		$filecsv = new dwho_file_csv();

		if(($data = $filecsv->parse($fileinfo['tmp_name'],
					    0,
					    '|',
					    null,
					    true,
					    $this->_conf['import']['field'])) === false
		|| empty($data) === true)
		{
			dwho_logw('cannot parse csv file (maybe fields are not separated by | ?)', 'users import', '');
			dwho_file::rm($fileinfo['tmp_name']);
			return(false);
		}

		$r = $this->import_from_array($data,$save);

		if($save === true)
			dwho_file::rm($fileinfo['tmp_name']);

		return($r);
	}

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data)) === false
		|| $this->set_add($arr,$arr['protocol']['protocol']) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}

	function edit_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data)) === false
		|| $this->set_edit($arr,$arr['protocol']['protocol']) === false
		|| $this->edit() === false)
			return(false);

		return(true);
	}

	function gen_password($len, $lower=false)
	{
		$pwd = '';
		for($i = 0; $i < $len; $i++)
		{
			$r = mt_rand(0, 35);
			$pwd .= $r < 10?$r:chr($r-10+65);
		}

		if($lower)
			$pwd = strtolower($pwd);

		return $pwd;
	}

	function mass_provisioning($userids, $reboot=false)
	{
		foreach($userids as $userid)
		{
			//$this->_info['devicefeatures'] = array('id' => $userid);
			$this->_info['devicefeatures'] = $this->_devicefeatures->get($userid);
			$this->_get_autoprov();
			if(is_null($this->_info['autoprov']['macaddr']))
				continue;

			$cmd = array(
				'from'           => 'webi',
				'iddevicefeatures' => $userid,
				'proto'          => $this->_info['devicefeatures']['protocol'],
				'macaddr'        => $this->_info['autoprov']['macaddr'],
				'actions'        => $reboot?'yes':'no'
			);

			$this->_autoprov->notification($cmd, 'prov');
		}
	}
}

?>
