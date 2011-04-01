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

class xivo_application_service_asterisk_user extends xivo_application_asterisk_abstract
{
	var $_dso			= null;
	var $_userfeatures 	= false;
	var $_rightcall		= false;
	var $_dialaction	= false;
	var $_queuemember	= null;
	var $_voicemail		= null;
	var $_agentfeatures	= null;
	var $_linefeatures	= false;
	var $_line			= false;
	var $_appentity		= false;
	var $_entity		= false;
	var $_phonefunckey	= null;
	var $_musiconhold	= array();
	var $_profileclientlist	= array();
	var $_conf			= array();
	var $_param			= array();
	var $_destination	= null;
	var $_queueskills   = null;
	var $_schedule_path = false;

	function xivo_application_service_asterisk_user(&$service,&$dso,$param=array(),$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_userfeatures = &$this->_service->get_module('userfeatures')) === false
		|| ($this->_queueskills = &$this->_service->get_module('userqueueskill')) === false
		|| ($this->_schedule_path = &$this->_service->get_module('schedule_path')) === false
		|| $this->load_init($param) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		$this->_load_config(dirname(__FILE__));

		if(($size = $this->_verify_can_upload_file()) === false)
			die();

		$this->_conf['import']['file']['size'] = $size;

		// init random generator
		mt_srand(time()+mt_rand());

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

		if(($this->_rightcall = $this->get_abstract('rightcall',array('type' => 'user'))) === false
		|| ($this->_dialaction = $this->get_abstract('dialaction',array('category' => 'user'))) === false
		|| ($this->_line = $this->_service->get_application('line')) === false
		|| ($_XOBJ = &dwho_gct::get('xivo_object')) === false
		|| ($this->_appentity = &$_XOBJ->get_application('entity')) === false
		|| ($this->_entity = &$_XOBJ->get_module('entity')) === false
		|| ($this->_linefeatures = $this->_service->get_module('linefeatures')) === false)
			return(false);

		$this->_queuemember = &$this->_service->get_module('queuemember');
		$this->_voicemail = &$this->_service->get_application('voicemail');
		$this->_agentfeatures = &$this->_service->get_module('agentfeatures');
		$this->_phonefunckey = &$this->_service->get_module('phonefunckey');

		return(true);
	}

	function get($id,$disable=null,$where=false,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if((bool) $where === false)
			$this->_info['userfeatures'] = $this->_userfeatures->get($id);
		else
			$this->_info['userfeatures'] = $this->_userfeatures->get_where($id);

		if ($this->_info['userfeatures'] === false)
			return(false);

		$this->_origin['userfeatures'] = $this->_userfeatures->get_origin();

		if($this->_components === false)
			return($this->_info);

		if(dwho_ak('entity',$nocomponents,true) === false)
			$this->_get_entity();

		if(dwho_ak('linefeatures',$nocomponents,true) === false)
			$this->_get_linefeatures();

		if(dwho_ak('groupmember',$nocomponents,true) === false)
			$this->_get_groupmember();

		if(dwho_ak('queuemember',$nocomponents,true) === false)
			$this->_get_queuemember();

		if(dwho_ak('rightcall',$nocomponents,true) === false)
			$this->_get_rightcall($this->_info['userfeatures']['id']);

		if(dwho_ak('dialaction',$nocomponents,true) === false)
			$this->_get_dialaction($this->_info['userfeatures']['id']);

		if(dwho_ak('voicemail',$nocomponents,true) === false)
			$this->_get_voicemail();

		if(dwho_ak('phonefunckey',$nocomponents,true) === false)
			$this->_get_phonefunckey();

		// queueskills
		$skills = $this->_queueskills->get_skills($this->_info['userfeatures']['id']);
		$this->_info['queueskills'] = $skills === false?array():$skills;

		// schedule
		$schedule = $this->_schedule_path->get_where(array('path' => 'user', 'pathid' => $this->_info['userfeatures']['id']));

		if($schedule !== false)
			$this->_info['schedule_id'] = intval($schedule['schedule_id']);

		return($this->_info);
	}

	function get_where($arr,$disable=null)
	{
		return($this->get($arr,$disable));
	}

	function get_nb($arr=null,$disable=null,$initialized=null)
	{
		return($this->_dso->get_nb($arr,$disable,$initialized));
	}

	function _get_linefeatures()
	{
		$this->_info['linefeatures'] = false;
		$this->_origin['linefeatures'] = false;

		if(is_object($this->_linefeatures) === false)
			return(false);

		$where = array();
		$where['iduserfeatures'] = $this->_info['userfeatures']['id'];

		$this->_info['linefeatures'] = $this->_linefeatures->get_all_where($where,
										   null,
										   array('rules_order' => SORT_ASC));
		$this->_origin['linefeatures'] = $this->_linefeatures->get_origin_list();

		return($this->_info['linefeatures']);
	}

	function _get_entity()
	{
		$this->_info['entity'] = false;
		$this->_origin['entity'] = false;

		if(is_object($this->_appentity) === false)
			return(false);

		$this->_info['entity']  = $this->_appentity->get($this->_info['userfeatures']['entityid'],null,'intern');

		return($this->_info['entity']);
	}

	function _get_groupmember()
	{
		return($this->_get_member_type('group'));
	}

	function _get_queuemember()
	{
		return($this->_get_member_type('queue'));
	}

	function _get_member_type($type)
	{
		if($type !== 'group' && $type !== 'queue')
			return(false);

		$membertype = $type.'member';

		$this->_info[$membertype] = false;
		$this->_origin[$membertype] = false;

		$where = array();
		$where['category'] = $type;
		$where['usertype'] = 'user';
		$where['userid'] = $this->_info['userfeatures']['id'];

		if(is_object($this->_queuemember) === false
		|| ($module = &$this->_service->get_module($type.'features')) === false
		|| ($this->_info[$membertype] = $this->_queuemember->get_all_where($where)) === false
		|| ($nb = count($this->_info[$membertype])) === 0)
		{
			$this->_info[$membertype] = false;
			return(false);
		}

		$ref = &$this->_info[$membertype];

		for($i = 0;$i < $nb;$i++)
		{
			if(($id = $module->get_primary(array('name' => $ref[$i]['queue_name']))) === false)
				continue;
			else if($type === 'queue')
				$ref[$i]['queuefeaturesid'] = $id;
			else
				$ref[$i]['groupfeaturesid'] = $id;
		}

		$this->_origin[$membertype] = $this->_queuemember->get_origin_list();

		return($this->_info[$membertype]);
	}

	function _get_voicemail()
	{
		$this->_info['voicemail'] = $this->_info['voicemailfeatures'] = false;
		$this->_origin['voicemail'] = $this->_origin['voicemailfeatures'] = false;

		if(is_object($this->_voicemail) === false
		|| $this->_voicemail->get($this->_info['userfeatures']['voicemailid']) === false)
			return(false);

		$this->_info['voicemail'] = $this->_voicemail->get_info('voicemail');
		$this->_info['voicemailfeatures'] = $this->_voicemail->get_info('voicemailfeatures');

		$this->_origin['voicemail'] = $this->_voicemail->get_origin('voicemail');
		$this->_origin['voicemailfeatures'] = $this->_voicemail->get_origin('voicemailfeatures');

		return($this->_info['voicemail']);
	}

	function _get_agentfeatures()
	{
		$this->_info['agentfeatures'] = false;
		$this->_origin['agentfeatures'] = false;

		if(is_object($this->_agentfeatures) === false
		|| $this->_agentfeatures->get($this->_info['userfeatures']['agentid']) === false)
			return(false);

		$this->_origin['agentfeatures'] = $this->_agentfeatures->get_origin();

		return($this->_info['agentfeatures']);
	}

	function _get_phonefunckey()
	{
		$this->_info['phonefunckey'] = false;
		$this->_origin['phonefunckey'] = false;

		if(is_object($this->_phonefunckey) === false)
			return(false);

		$where = array();
		$where['iduserfeatures'] = $this->_info['userfeatures']['id'];

		$this->_info['phonefunckey'] = $this->_phonefunckey->get_all_where($where,
										   null,
										   true,
										   array('fknum' => SORT_ASC));
		$this->_origin['phonefunckey'] = $this->_phonefunckey->get_origin_list();

		return($this->_info['phonefunckey']);
	}

	function get_timezones()
	{
		if(is_object($this->_voicemail) === false)
			return(false);

		return($this->_voicemail->get_timezones());
	}

	function get_phonefunckey_type()
	{
		return($this->_phonefunckey->get_type_list());
	}

	function get_bsfilter_list()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);

		$rs = $this->_dso->get_bsfilter($this->_info['userfeatures']['id'],
						$this->_info['userfeatures']['bsfilter']);

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$ref = $this->_userfeatures->_prepare($ref);
			$ref['callfilteridentity'] = $ref['callfiltername'].' / '.$ref['identity'];
		}

		if(empty($rs) === true)
			$rs = false;

		return($rs);
	}

	function get_config_import_file()
	{
		return($this->_chk_exists_cfg('import','file',true));
	}

	function _get_config_file_maxsize()
	{
		if(($import_file = $this->_chk_exists_cfg('import','file',true)) !== false
		&& isset($import_file['size']) === true)
			return(dwho_get_memory($import_file['size'],false));

		return(false);
	}

	function get_voicemail_list()
	{
		if(is_object($this->_voicemail) === false)
			return(false);

		$order = array();
		$order['fullname'] = SORT_ASC;
		$order['mailbox'] = SORT_ASC;

		return($this->_voicemail->get_voicemail_list(null,$order));
	}

	function get_agent_list()
	{
		if(is_object($this->_agentfeatures) === false)
			return(false);

		$order = array();
		$order['firstname'] = SORT_ASC;
		$order['lastname'] = SORT_ASC;
		$order['number'] = SORT_ASC;

		return($this->_agentfeatures->get_all(null,true,$order));
	}

	function get_profileclient_list()
	{
		if(empty($this->_profileclientlist) === false)
			return($this->_profileclientlist);
		else if(($list = $this->_service->discuss('xivo[ctiprofilelist,get]',true)) === false
		|| is_array($list) === false
		|| isset($list[0]) === false
		|| dwho::load_class('dwho_json') === false
		|| ($list = dwho_json::decode($list[0],true)) === false
		|| is_array($list) === false
		|| empty($list) === true)
			return(false);

		$this->_profileclientlist = array();

		foreach($list as $key => $val)
		{
			if(preg_match('/^[a-z0-9_-]+$/',$key) === 1)
				$this->_profileclientlist[$key] = $val;
		}

		return($this->_profileclientlist);
	}

	function get_elements()
	{
		$r = array();

		$r['userfeatures'] = $this->_userfeatures->get_element();
		$r['linefeatures'] = $this->_linefeatures->get_element();
		$r['dialaction'] = $this->_dialaction->get_element();

		if(is_object($this->_queuemember) === true)
			$r['qmember'] = $this->_queuemember->get_element();
		else
			$r['qmember'] = false;

		if(is_object($this->_voicemail) === true
		&& ($vmelement = $this->_voicemail->get_elements()) !== false)
			$r = array_merge($vmelement,$r);
		else
			$r['voicemail'] = $r['voicemailfeatures'] = false;

		if(is_object($this->_phonefunckey) === true)
			$r['phonefunckey'] = $this->_phonefunckey->get_element();
		else
			$r['phonefunckey'] = false;

		return($r);
	}

	function get_users_search($search,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_users('search',$disable,$search,$order,$limit,$assoc,$initialized));
	}

	function get_users_search_number($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_users('search_number',$disable,$search,$order,$limit,$assoc,$initialized));
	}

	function get_users_list($disable=null,$order=null,$limit=null,$assoc=false,$initialized=null)
	{
		return($this->_get_users('list',$disable,null,$order,$limit,$assoc,$initialized));
	}

	function _get_users($action,$disable=null,$search='',$order=null,$limit=null,$assoc=false,$initialized=null)
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
				$rs = $this->_dso->get_all($disable,$initialized,$order,$limit);
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];

			$userfeatures = dwho_array_startswith_key($ref,'userfeatures.',true);
			$r[$userfeatures['id']] = $this->_userfeatures->_prepare($userfeatures);

			// get userskills
			$skills = $this->_queueskills->get_skills($userfeatures['id']);
			if($skills === false)
				$skills = array();

			$r[$userfeatures['id']]['queueskills'] = $skills;

			if($this->_components === false)
				continue;

			$where = array('iduserfeatures' => $userfeatures['id']);
			$r[$userfeatures['id']]['nb_line'] = $this->_linefeatures->get_nb($where);
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	function get_dialaction_result()
	{
		return($this->_dialaction->get_result_for_display());
	}

	function get_phonefunckey_result()
	{
		$result = $this->get_result('phonefunckey');

		if(is_array($result) === false
		|| ($nb = count($result)) === 0)
			return(null);

		$r = array();

		for($i = 0;$i < $nb;$i++)
			$r[$i] = $this->_phonefunckey->_prepare($result[$i]);

		return($r);
	}

	function get_destination_list()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			$id = 0;
		else
			$id = $this->_info['userfeatures']['id'];

		$this->_get_destination();

		$r = $this->_destination;
		$r['users'] = $this->get_destination_users($id);
		$r['groups'] = $this->get_destination_groups();
		$r['queues'] = $this->get_destination_queues();
		$r['meetme'] = $this->get_destination_meetme();
		$r['voicemail'] = $this->get_destination_voicemail();
		$r['schedule'] = $this->get_destination_schedule();
		$r['sounds'] = $this->_dialaction->get_sound();
		$r['voicemenu'] = $this->get_destination_voicemenu();

		return($r);
	}

	function get_phonefunckey_identity()
	{
		if(dwho_issa('userfeatures',$this->_info) === false
		|| ($rs = $this->_dso->get_phonefunckey($this->_info['userfeatures']['id'])) === false
		|| ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];

			$phonefunckey = $this->_phonefunckey->_prepare(
						dwho_array_startswith_key($ref,'phonefunckey.',true));

			$res = null;

			switch($phonefunckey['type'])
			{
				case 'user':
					$res = dwho_array_startswith_key($ref,'userfeatures.',true);
					$res['identity'] = $this->_service->identity('userfeatures',$res,false);
					break;
				case 'extenfeatures-groupaddmember':
				case 'extenfeatures-groupremovemember':
				case 'extenfeatures-grouptogglemember':
				case 'group':
					$res = dwho_array_startswith_key($ref,'groupfeatures.',true);
					$res['identity'] = $this->_service->identity('groupfeatures',$res,false);
					break;
				case 'extenfeatures-queueaddmember':
				case 'extenfeatures-queueremovemember':
				case 'extenfeatures-queuetogglemember':
				case 'queue':
					$res = dwho_array_startswith_key($ref,'queuefeatures.',true);
					$res['identity'] = $this->_service->identity('queuefeatures',$res,false);
					break;
				case 'meetme':
					$res = dwho_array_startswith_key($ref,'meetmefeatures.',true);
					$res['identity'] = $this->_service->identity('meetmefeatures',$res,false);
					break;
				case 'extenfeatures-agentdynamiclogin':
				case 'extenfeatures-agentstaticlogin':
				case 'extenfeatures-agentstaticlogoff':
				case 'extenfeatures-agentstaticlogtoggle':
					$res = dwho_array_startswith_key($ref,'agentfeatures.',true);
					$res['identity'] = $this->_service->identity('agentfeatures',$res,false);
					break;
			}

			$r[] = array('phonefunckey'	=> $phonefunckey,
				     'result'		=> $res);
		}

		if(empty($r) === true)
			return(false);

		return($r);
	}

	function _get_destination()
	{
		if(is_array($this->_destination) === true)
			return(true);

		$this->_destination = array();

		return(true);
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
		|| dwho_issa('userfeatures',$arr) === false)
			return(false);

		$iduserfeatures = 0;
		if(isset($arr['id']) === true)
			$iduserfeatures = (int) $arr['id'];

		if(isset($arr['userfeatures']['callerid']) === true)
			$arr['userfeatures']['callerid'] = $this->_service->mk_callerid($arr['userfeatures']['callerid']);

		$vmaction = $action;

		if(isset($arr['voicemail-option']) === true)
		{
			switch($arr['voicemail-option'])
			{
				case 'add':
				case 'none':
					$vmaction = $arr['voicemail-option'];
					$arr['userfeatures']['voicemailid'] = null;
					break;
				case 'search':
					$vmaction = 'edit';
					break;
			}
		}

		$this->set_userfeatures($action,$arr['userfeatures']);

		if(dwho_issa('linefeatures',$arr) === true
		&& isset($iduserfeatures) === true)
			$this->set_linefeatures($arr,$iduserfeatures);

		$simultcalls = (int) $this->get_result_var('userfeatures','simultcalls');
		$musiconhold = (string) $this->get_result_var('userfeatures','musiconhold');

		switch($this->get_result_var('userfeatures','voicemailtype'))
		{
		  case 'asterisk':
		    break;
		  case 'exchange':
		      $this->_set_result_var('userfeatures','voicemailtype',null);
		  default:
		    $vmaction = 'none';
		    $this->_set_result_var('userfeatures','voicemailid',null);
		    break;
		}

		if(dwho_issa('group',$arr) === true
		&& dwho_issa('group-select',$arr) === true
		&& $this->set_groupmember($arr['group'],
					  $arr['group-select'],
					  $name) === true)
		{
			$callgroup = $this->get_result('callgroup');

			if(is_array($callgroup) === true && isset($callgroup[0]) === true)
				$callgroup = implode(',',$callgroup);
			else
				$callgroup = '';
		}

		if(dwho_issa('dialaction',$arr) === true)
			$this->set_dialaction($arr['dialaction']);

		if(dwho_issa('rightcall',$arr) === true)
			$this->set_rightcall($arr['rightcall']);

		if(dwho_issa('voicemail',$arr) === true
		&& dwho_has_len($arr['voicemail'],'mailbox') === true)
		{
			if(isset($arr['voicemail']['deletevoicemail']) === false)
				$arr['voicemail']['deletevoicemail'] = 0;

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

		// QUEUESKILLS
		if(dwho_issa('queueskills',$arr) === true)
			$this->set_queueskills($action, $arr['queueskills']);

		if($this->get_errnb() > 0)
			$r = false;
		else
			$r = true;

		// schedule
		if(array_key_exists('schedule_id', $arr))
			$this->_set_result('schedule_id', intval($arr['schedule_id']));

		return($r);
	}

	function set_userfeatures($action,$arr)
	{
		if(($action !== 'add' && $action !== 'edit') === true
		|| ($action === 'edit' && dwho_issa('userfeatures',$this->_origin) === false) === true)
			return(false);
		else if(is_array($arr) === false)
		{
			$this->_set_result('userfeatures',null);
			$this->_set_error('userfeatures','invalid data');
			return(false);
		}

		$this->get_musiconhold();

		if(isset($arr['musiconhold']) === true
		&& isset($this->_musiconhold[$arr['musiconhold']]) === false)
			$arr['musiconhold'] = '';

		if($action === 'edit'
		&& isset($arr['profileclient']) === false
		&& isset($arr['enableclient']) === false)
			$arr['profileclient'] = $this->_origin['userfeatures']['profileclient'];

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

		if(($rs = $this->_userfeatures->chk_values($arr)) === false)
		{
			$this->_set_result('userfeatures',$this->_userfeatures->get_filter_result());
			$this->_set_error('userfeatures',$this->_userfeatures->get_filter_error());
			return(false);
		}
		else
		{
			if($action === 'edit')
				$id = $this->_origin['userfeatures']['id'];
			else
				$id = null;

			if($this->_userfeatures->loginclient_exists($rs['loginclient'],$id) === true)
			{
				$this->_set_result('userfeatures',$rs);
				$this->_set_error('userfeatures','client login exists');
				return(false);
			}
		}

		if(isset($rs['loginclient']) === false
		|| dwho_has_len($rs['loginclient']) === false)
		{
			$rs['enableclient'] = false;
			$rs['passwdclient'] = '';
		}

		if(dwho_has_len($rs['agentid']) === false
		|| is_object($this->_agentfeatures) === false
		|| $this->_agentfeatures->get_primary($rs['agentid']) === false)
			$rs['agentid'] = null;

		$this->_set_result('userfeatures',$rs);

		return(true);
	}

	function set_linefeatures($arr,$iduserfeatures)
	{
		if(is_array($arr) === false
		|| $this->_linefeatures === false
		|| ($userfeatures = $this->get_result('userfeatures')) === null)
			return(false);

		$linefeatures = $arr['linefeatures'];

		$reslist = $error = array();
		$errnb = 0;

		foreach($linefeatures as $key => $list)
		{
			for($i = 0;$i < count($list);$i++)
			{
				if (isset($linefeatures[$key][$i]) === false
				|| $linefeatures[$key][$i] === '')
					$reslist[$i][$key] = '';
				else
					$reslist[$i][$key] = $linefeatures[$key][$i];
			}
		}

		if(empty($reslist) === true)
		{
			$this->_set_result('linefeatures',false);
			$this->_set_error('linefeatures','empty');
			return(false);
		}

		array_pop($reslist);

		/*
		 * je prend quelle line ?????????????????????

		if(dwho_issa('queue',$arr) === true
		&& dwho_issa('queue-select',$arr) === true)
			$this->set_queuemember($arr['queue'],
					       $arr['queue-select'],
					       $name,
					       $context,
					       $number,
					       $protocolname);

		*/

		$simultcalls = (int) $this->get_result_var('userfeatures','simultcalls');
		$musiconhold = (string) $this->get_result_var('userfeatures','musiconhold');

		for($i = 0;$i < count($reslist);$i++)
		{
			$ref = &$reslist[$i];

			$protocolname = $ref['protocol'];
			$number = $ref['number'];

			if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			  $this->_set_result_var('userfeatures','voicemailtype',null);

			switch($this->get_result_var('userfeatures','voicemailtype'))
			{
			  case 'asterisk':
			    break;
			  case 'exchange':
			    if($number === '')
			      $this->_set_result_var('userfeatures','voicemailtype',null);
			  default:
			    $vmaction = 'none';
			    $this->_set_result_var('userfeatures','voicemailid',null);
			    break;
			}

			$ref['iduserfeatures'] = (int) $iduserfeatures;
			$ref['rules_order'] = (int) $ref['rules_order'];
			$ref['rules_group'] = (int) $ref['rules_group'];
			$callerid = $this->get_result_var('userfeatures','callerid');
			$ref['callerid'] = $this->_service->mk_callerid($callerid,$number,$protocolname);

			if (isset($ref['id']) === true)
			{
			/*
				if (($line = $this->_line->get($ref['id'])) === false
				|| ($linefeatures = $line['linefeatures']) === false)
				{
					$errnb++;
					$error[$i] = 'line_not_exist';
					continue;
				}
				$ref['id'] = (int) $ref['id'];
				$ref['protocolid'] = $linefeatures['protocolid'];
				$ref['name'] = $linefeatures['name'];
			*/
				$ref['id'] = (int) $ref['id'];
				$ref['protocolid'] = 0;
			}
			else
			{
				$ref['protocolid'] = 0;
				$ref['iduserfeatures'] = 0;
				$ref['name'] = $this->gen_password(6,true);
				$ref['secret'] = $this->gen_password(6);
			}

			if($this->_linefeatures->chk_values($ref) === false)
			{
				$errnb++;
				$error[$i] = $this->_linefeatures->get_filter_error();
			}
		}
		$this->_set_result('linefeatures',$reslist);

		if ($errnb >> 0)
		{
			$this->_set_errors('linefeatures',$error);
			return(false);
		}

		return(true);
	}

	function set_groupmember($group,$select,$name)
	{
		return($this->_set_member_type('group',$group,$select,$name));
	}

	function set_queuemember($queue,$select,$name)
	{
		return($this->_set_member_type('queue',$queue,$select,$name));
	}

	function _set_member_type($type,$list,$select,$name)
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
			|| ($interface = $this->mk_interface($name,$chantype)) === false
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
			$ref['iduserfeatures'] = 0;

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
		$userfeaturesid = null;

		if($this->get_errnb() > 0
		|| ($userfeaturesid = $this->add_userfeatures()) === false
		|| $this->add_linefeatures($userfeaturesid) === false
		|| $this->add_groupmember($userfeaturesid) === false
		|| $this->add_queuemember($userfeaturesid) === false
		|| $this->add_rightcall($userfeaturesid) === false
		|| $this->add_dialaction($userfeaturesid) === false
		|| $this->add_voicemail($userfeaturesid) === false
		|| $this->add_phonefunckey($userfeaturesid) === false
		|| $this->add_queueskills($userfeaturesid) === false
		|| $this->add_schedule_path($userfeaturesid) === false)
		{
			$r = false;

			if($userfeaturesid !== null)
				$this->_reverse_add();
		}

		$this->_status = '';

		return($r);
	}

	function add_userfeatures()
	{
		if(($rs = $this->get_result('userfeatures')) === null
		|| $rs === false)
			return(false);

		if(empty($rs['alarmclock_hour']) === false)
		{
			$alarmclock = $rs['alarmclock_hour'];
			$alarmclock .= ':';
			if(empty($rs['alarmclock_minute']) === true)
				$alarmclock .= '00';
			else
				$alarmclock .= $rs['alarmclock_minute'];
			$rs['alarmclock'] = $alarmclock;
		}

		unset($rs['alarmclock_hour']);
		unset($rs['alarmclock_minute']);

		$this->_return['userfeatures'] = $this->_userfeatures->add($rs);

		return($this->_return['userfeatures']);
	}

	function add_linefeatures($userfeaturesid)
	{
		if(($rs = $this->get_result('linefeatures')) === null
		|| $rs === false)
			return(true);

		if($this->_line === false)
			return(false);

		$userfeatures = $this->_info['userfeatures'];
		$userfeatures['id'] = $userfeaturesid;

		$return = $error = array();
		$errnb = 0;

		$arr = array();
		$arr['userfeatures'] = $userfeatures;

		for($i = 0;$i < count($rs);$i++)
		{
			$line = &$rs[$i];

			$methodset = 'set_add';
			$method = 'add';

			$protocolname = $line['protocol'];

			$arr['linefeatures'] = $line;
			$arr['protocol'] = $line;

			if($this->_line->set_add($arr,$protocolname) === false
			|| $this->_line->add() === false)
			{
				$errnb++;
				$return[$i] = $line;
				$error[$i] = $this->_line->get_error();
				$msgkey = array_shift(array_keys($this->_line->get_error()));
				$msg = array_shift($this->_line->get_error());
				if (empty($msgkey) === false)
					dwho_report::push('error','Line '.($i+1).': '.$msgkey.' '.$msg,'linefeatures');
			}
			else
				$return[$i] = $line;
		}

		if ($errnb >> 0)
		{
			$this->_set_error('linefeatures',$error);
			return(false);
		}

		return(($this->_return['linefeatures'] = $return));
	}

	function add_groupmember($userfeaturesid)
	{
		return($this->_add_member_type('group',$userfeaturesid));
	}

	function add_queuemember($userfeaturesid)
	{
		return($this->_add_member_type('queue',$userfeaturesid));
	}

	function _add_member_type($type,$userfeaturesid)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| ($userfeaturesid = dwho_ulongint($userfeaturesid)) === 0)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $userfeaturesid;
			if($type == 'queue')
			{ $rs[$i]['skills'] = $userfeaturesid; }

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

	function add_voicemail($userfeaturesid)
	{
		if(($voicemailid = dwho_ulongint($this->get_result_var('userfeatures','voicemailid'))) === 0)
			return($this->_add_voicemail($userfeaturesid));
		else if(is_object($this->_voicemail) === false
		|| $this->_voicemail->get($voicemailid) === false
		|| ($rs = $this->get_result('voicemail')) === null
		|| $rs === false)
			return($rs);

		return(($this->_return['voicemail'] = $this->_voicemail->edit(false)));
	}

	function _add_voicemail($userfeaturesid)
	{
		if(($userfeaturesid = dwho_ulongint($userfeaturesid)) === 0
		|| ($rs = $this->get_result('voicemail')) === null
		|| $rs === false)
			return($rs);
		else if(($this->_return['voicemail'] = $this->_voicemail->add()) === true
		&& (($voicemailid = dwho_ulongint($voicemailid = $this->_voicemail->get_return('voicemail'))) === 0
		   || $this->_userfeatures->edit($userfeaturesid,array('voicemailid' => $voicemailid)) === false) === true)
			return(false);

		return($this->_return['voicemail']);
	}

	function add_phonefunckey($userfeaturesid)
	{
		$rs = false;

		if(($userfeaturesid = dwho_ulongint($userfeaturesid)) === 0
		|| ($rs = $this->get_result('phonefunckey')) === null
		|| $rs === false)
			return($rs);

		$bsfilter = $this->get_result_var('userfeatures','bsfilter');

		$id = $this->_return['phonefunckey'] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$ref['iduserfeatures'] = $userfeaturesid;

			if(($ref['typeextenumbers'] !== null
			   || $ref['typeextenumbersright'] !== null) === true
			&& $this->_phonefunckey->is_valid($ref['typeextenumbers'],
							  $ref['typevalextenumbers'],
							  $ref['typeextenumbersright'],
							  $ref['typevalextenumbersright'],
							  $ref['iduserfeatures'],
							  null) === false)
				return(false);
			else if($ref['typeextenumbers'] === 'extenfeatures'
			&& $ref['typevalextenumbers'] === 'bsfilter'
			&& $this->_dso->chk_bsfilter($ref['iduserfeatures'],
						     $bsfilter,
						     $ref['typevalextenumbersright']) === false)
				return(false);

			$id['iduserfeatures'] = $ref['iduserfeatures'];
			$id['fknum'] = $ref['fknum'];

			if($this->_phonefunckey->add($ref) === false)
				return(false);

			$this->_return['phonefunckey'][] = $id;
		}

		if(isset($this->_return['phonefunckey'][0]) === false)
			$this->_return['phonefunckey'] = false;

		return(true);
	}

	function add_queueskills($userfeaturesid)
	{
		$rs = false;

		if(($userfeaturesid = dwho_ulongint($userfeaturesid)) === 0
		|| ($rs = $this->get_result('queueskills')) === null
		|| $rs === false)
			return($rs);

		foreach($rs as &$skill)
		{ $skill['userid'] = $userfeaturesid; }

		$appqueue = &$this->_service->get_application('queue');
		$ret = $appqueue->userskills_add($rs);

		return $ret;
	}

	function add_schedule_path($userfeaturesid)
	{
		return $this->_schedule_path->schedule_add(
			$this->get_result('schedule_id'),
			'user',
			$userfeaturesid);
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
				case 'userfeatures':
					$this->_userfeatures->delete($val);
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
		|| $this->edit_userfeatures() === false)
		{
			$this->_status = '';
			return(false);
		}

		if($this->edit_linefeatures() === false
		|| $this->edit_groupmember() === false
		|| $this->edit_queuemember() === false
		|| $this->edit_rightcall() === false
		|| $this->edit_dialaction() === false
		|| $this->edit_voicemail() === false
		|| $this->edit_phonefunckey() === false
		|| $this->edit_schedule_path() === false)
		{
			$this->_reverse_edit();
			$this->_status = '';
			return(false);
		}

		$this->_status = '';
		return(true);
	}

	function edit_userfeatures()
	{
		if(dwho_issa('userfeatures',$this->_info) === false
		|| ($rs = $this->get_result('userfeatures')) === null
		|| $rs === false)
			return(false);

		if(empty($rs['alarmclock_hour']) === false)
		{
			$alarmclock = $rs['alarmclock_hour'];
			$alarmclock .= ':';
			if(empty($rs['alarmclock_minute']) === true)
				$alarmclock .= '00';
			else
				$alarmclock .= $rs['alarmclock_minute'];
			$rs['alarmclock'] = $alarmclock;
		}

		unset($rs['alarmclock_hour']);
		unset($rs['alarmclock_minute']);

		$return = $this->_userfeatures->edit($this->_info['userfeatures']['id'],$rs);

		return(($this->_return['userfeatures'] = $return));
	}

	function edit_linefeatures()
	{
		if(($rs = $this->get_result('linefeatures')) === null
		|| $rs === false
		|| $this->_line === false)
			return(false);

		$info = $this->_info['linefeatures'];

		$userfeatures = $this->_info['userfeatures'];

		$return = $error = array();
		$errnb = 0;

		$arr = array();
		$arr['userfeatures'] = $userfeatures;

		$res = array();
		for($i = 0;$i < count($info);$i++)
		{
			$ref = &$info[$i];
			$res[$ref['id']] = $ref;
		}

		$linefeatures = array();
		$linefeatures['list'] = $res;
		$linefeatures['slt'] = dwho_array_intersect_key($rs,$linefeatures['list'],'id');
		$linefeatures['info'] = false;

		if($linefeatures['slt'] !== false)
		{
			$linefeatures['info'] = dwho_array_copy_intersect_key($rs,$linefeatures['slt'],'id');
			$linefeatures['list'] = dwho_array_diff_key($linefeatures['list'],$linefeatures['slt']);
		}

		if(empty($linefeatures['list']) === false)
		{
			$nb = count($linefeatures['list']);
			$linefeatures_list = array_values($linefeatures['list']);
			for($i = 0;$i < $nb;$i++)
			{
				$ref = &$linefeatures_list[$i];
				if (isset($ref['id']) === true)
				if ($this->_line->get($ref['id']) !== false
				&& $this->_line->delete() !== false)
					continue;
			}
		}

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$line = &$rs[$i];

			$this->_line->_reset_info();

			if (isset($line['id']) === true
			&& (int) $line['id'] !== 0)
			{
				$methodset = 'set_edit';
				$method = 'edit';

				if (($this->_line->get($line['id'])) === false)
				{
					$errnb++;
					$error[$i] = 'line_not_exist';
					dwho_report::push('error',dwho_i18n::babelfish('Row '.($i+1).': line_not_exist'),'linefeatures');
					continue;
				}
			}
			else
			{
				$methodset = 'set_add';
				$method = 'add';
			}

			$protocolname = $line['protocol'];

			$arr['linefeatures'] = $line;
			$arr['protocol'] = $line;

			if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
				$arr['protocol']['interface'] = $line['name'];

			if($this->_line->$methodset($arr,$protocolname) === false
			|| $this->_line->$method() === false)
			{
				$errnb++;
				$return[$i] = $line;
				$error[$i] = $this->_line->get_error();
				$msgkey = array_shift(array_keys($this->_line->get_error()));
				$msg = array_shift($this->_line->get_error());
				if (empty($msgkey) === false)
					dwho_report::push('error','Line '.($i+1).': '.$msgkey.' '.$msg,'linefeatures');
			}
			else
				$return[$i] = $line;
		}

		if ($errnb >> 0)
		{
			$this->_set_error('linefeatures',$error);
			return(false);
		}

		return(($this->_return['linefeatures'] = $return));
	}

	function edit_groupmember()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('groupmember',$this->_info) === false)
			return($this->add_groupmember($this->_info['userfeatures']['id']));

		$this->_return['groupmember'] = $this->delete_groupmember();

		if($this->get_result('groupmember') === null)
			return($this->_return['groupmember']);

		return($this->_edit_member_type('group'));
	}

	function edit_queuemember()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('queuemember',$this->_info) === false)
			return($this->add_queuemember($this->_info['userfeatures']['id']));

		$this->_return['queuemember'] = $this->delete_queuemember();

		if($this->get_result('queuemember') === null)
			return($this->_return['queuemember']);

		return($this->_edit_member_type('queue'));
	}

	function _edit_member_type($type)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| dwho_issa('userfeatures',$this->_info) === false)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $this->_info['userfeatures']['id'];
			if($type == 'queue')
			{ $rs[$i]['skills'] = $this->_info['userfeatures']['id']; }

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
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);

		return(parent::edit_rightcall($this->_info['userfeatures']['id']));
	}

	function edit_dialaction()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);

		return(parent::edit_dialaction($this->_info['userfeatures']['id']));
	}

	function edit_voicemail()
	{
		$rs = false;

		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);
		else if(($voicemailid = dwho_ulongint($this->get_result_var('userfeatures','voicemailid'))) === 0)
			return($this->_add_voicemail($this->_info['userfeatures']['id']));
		else if(is_object($this->_voicemail) === false
		|| $this->_voicemail->get($voicemailid) === false
		|| ($rs = $this->get_result('voicemail')) === null
		|| $rs === false)
			return($rs);

		return(($this->_return['voicemail'] = $this->_voicemail->edit(false)));
	}

	function edit_phonefunckey()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('phonefunckey',$this->_info) === false)
			return($this->add_phonefunckey($this->_info['userfeatures']['id']));

		$this->_return['phonefunckey'] = $this->delete_phonefunckey();

		if(($rs = $this->get_result('phonefunckey')) === null || $rs === false)
			return($rs);

		$bsfilter = $this->get_result_var('userfeatures','bsfilter');

		$id = $this->_return['phonefunckey'] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$ref['iduserfeatures'] = $this->_info['userfeatures']['id'];

			if(($ref['typeextenumbers'] !== null
			|| $ref['typeextenumbersright'] !== null) === true
			&& $this->_phonefunckey->is_valid($ref['typeextenumbers'],
							  $ref['typevalextenumbers'],
							  $ref['typeextenumbersright'],
							  $ref['typevalextenumbersright'],
							  $ref['iduserfeatures'],
							  null) === false)
				return(false);
			else if($ref['typeextenumbers'] === 'extenfeatures'
			&& $ref['typevalextenumbers'] === 'bsfilter'
			&& $this->_dso->chk_bsfilter($ref['iduserfeatures'],
						     $bsfilter,
						     $ref['typevalextenumbersright']) === false)
				return(false);

			$id['iduserfeatures'] = $ref['iduserfeatures'];
			$id['fknum'] = $ref['fknum'];

			if($this->_phonefunckey->add($ref) === false)
				return(false);

			$this->_return['phonefunckey'][] = $id;
		}

		if(isset($this->_return['phonefunckey'][0]) === false)
			$this->_return['phonefunckey'] = false;

		return(true);
	}

	function edit_schedule_path()
	{
		$this->_schedule_path->delete_where(array('path' => 'user', 'pathid' =>	intval($this->_info['userfeatures']['id'])));

		return $this->_schedule_path->schedule_add(
			$this->get_result('schedule_id'),
			'user',
			$this->_info['userfeatures']['id']);
	}

	function _reverse_edit()
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
				case 'userfeatures':
					if(isset($this->_origin['userfeatures']) === false
					|| $this->_origin['userfeatures'] === false)
						$this->delete_userfeatures();
					else
						$this->_userfeatures->edit_origin($this->_origin['userfeatures']);
					break;
				case 'voicemail':
					$this->_voicemail->reverse_edit();
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
				case 'phonefunckey':
					$this->delete_phonefunckey();

					if(isset($this->_origin['phonefunckey']) === true
					&& $this->_origin['phonefunckey'] !== false)
						$this->_phonefunckey->add_origin_list($this->_origin['phonefunckey']);
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

		if($this->delete_userfeatures() === false
		|| $this->delete_linefeatures() === false
		|| $this->delete_groupmember() === false
		|| $this->delete_queuemember() === false
		|| $this->delete_rightcall() === false
		|| $this->delete_dialaction() === false
		|| $this->delete_phonefunckey() === false
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

	function delete_userfeatures()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);

		$r = $this->_userfeatures->delete($this->_info['userfeatures']['id']);

		if($this->_status === 'delete')
			$this->_return['userfeatures'] = $r;

		return($r);
	}

	function delete_linefeatures()
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);

		$where = array('iduserfeatures' => (int) $this->_info['userfeatures']['id']);

		if (($listline = $this->_linefeatures->get_all_where($where)) === false)
			return(true);

		$r = array();

		foreach($listline as $line)
		{
			if (($rs = $this->_line->get($line['id'])) === false)
				continue;

			$r[] = $this->_line->delete();

		}

		if($this->_status === 'delete')
			$this->_return['linefeatures'] = $r;

		return($r);
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
		else if(dwho_issa('userfeatures',$this->_info) === false
		|| is_object($this->_queuemember) === false)
			return(false);

		$where = array();
		$where['usertype'] = 'user';
		$where['category'] = $type;
		$where['userid'] = $this->_info['userfeatures']['id'];

		$r = $this->_queuemember->delete_where($where);

		if($this->_status === 'delete')
			$this->_return[$key] = $r;

		return($r);
	}

	function delete_phonefunckey()
	{
		if(dwho_issa('phonefunckey',$this->_info) === false)
			return(null);
		else if(dwho_issa('userfeatures',$this->_info) === false
		|| is_object($this->_phonefunckey) === false)
			return(false);

		$where = array();
		$where['iduserfeatures'] = $this->_info['userfeatures']['id'];

		$r = $this->_phonefunckey->delete_where($where);

		if($this->_status === 'delete')
			$this->_return['phonefunckey'] = $r;

		return($r);
	}

	function delete_callfiltermember()
	{
		if(($callfiltermember = &$this->_service->get_module('callfiltermember')) === false)
			return(true);

		$where = array();
		$where['type'] = 'user';
		$where['typeval'] = $this->_info['userfeatures']['id'];

		$callfiltermember->delete_where($where);

		return(true);
	}

	function delete_queueskill()
	{
		$appqueue = &$this->_service->get_application('queue');
		return $appqueue->userskills_delete($this->_info['userfeatures']['id']);
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
				case 'userfeatures':
					if(isset($this->_origin['userfeatures']) === true
					&& $this->_origin['userfeatures'] !== false)
						$this->_userfeatures->add_origin($this->_origin['userfeatures']);
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
				case 'phonefunckey':
					if(isset($this->_origin['phonefunckey']) === true
					&& $this->_origin['phonefunckey'] !== false)
						$this->_phonefunckey->add_origin_list($this->_origin['phonefunckey']);
					break;
			}
		}

		return(true);
	}

	function unlinks()
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);

		$this->_dialaction->unlinked('user',$this->_info['userfeatures']['id']);

		return(true);
	}

	function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if($this->enable_userfeatures() === false)
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

		if($this->disable_userfeatures() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return(true);
	}

	function enable_userfeatures()
	{
		return($this->_enable_disable_userfeatures(false));
	}

	function disable_userfeatures()
	{
		return($this->_enable_disable_userfeatures(true));
	}

	function _enable_disable_userfeatures($disable=false)
	{
		if(dwho_issa('userfeatures',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_userfeatures->enable($this->_info['userfeatures']['id']);
		else
			$r = $this->_userfeatures->disable($this->_info['userfeatures']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['userfeatures'] = $r;

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
				case 'userfeatures':
					$this->_enable_disable_userfeatures($disable);
					break;
			}
		}

		return(true);
	}

	function _prepare_import($arr)
	{
		$issa_userfeatures = dwho_issa('userfeatures',$arr);

		if(dwho_issa('voicemail',$arr) === true
		&& empty($arr['voicemail']) === false
		&& dwho_has_len($arr['voicemail'],'mailbox') === true)
		{
			if($issa_userfeatures === true)
				$arr['userfeatures']['enablevoicemail'] = true;
		}
		else
			unset($arr['voicemail']);

		if($issa_userfeatures === true)
		{
			$arr['userfeatures']['callerid'] = '';

			if(dwho_has_len($arr['userfeatures'],'firstname') === true)
				$arr['userfeatures']['callerid'] = $arr['userfeatures']['firstname'].' ';

			if(dwho_has_len($arr['userfeatures'],'lastname') === true)
				$arr['userfeatures']['callerid'] .= $arr['userfeatures']['lastname'];

			trim($arr['userfeatures']['callerid']);
		}

		if($issa_userfeatures === true
		&& dwho_has_len($arr['userfeatures'],'agentnumber') === true
		&& is_object($this->_agentfeatures) === true
		&& ($agentid = $this->_agentfeatures->get_primary(
						array('number' => $arr['userfeatures']['agentnumber']))) !== false)
			$arr['userfeatures']['agentid'] = $agentid;

		unset($arr['userfeatures']['agentnumber']);

		return($arr);
	}

	function import_from_array($data,$save=true)
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
			|| $this->set_add($arr) === false)
			{
				$r['lines'][$row] = 'error';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($data[$i], true), 'userimport', "line #$i");

				$err = array();
				foreach($this->get_error() as $k => $v)
					$err[] = $tpl->bbf("error(".$k."__".$v.")");
				$msg = sprintf('%s #%03d:&nbsp;&nbsp;&nbsp;&nbsp; %s', $tpl->bbf('line'), $i+1,
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

			$incall['dialaction']['answer']['actionarg1'] = $this->get_return('userfeatures');

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
}

?>
