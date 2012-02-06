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
	var $_ctiprofiles	= false;
	var $_appentity		= false;
	var $_entity		= false;
	var $_phonefunckey	= null;
	var $_provdconfig	= false;
	var $_musiconhold	= array();
	var $_profileclientlist	= array();
	var $_conf			= array();
	var $_param			= array();
	var $_destination	= null;
	var $_queueskills   = null;
	var $_schedule_path = false;
	var $_attachment 	= false;

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
		$this->_conf['picture']['file']['size'] = $size;

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
		|| ($this->_ctiprofiles = $this->_service->get_application('ctiprofiles')) === false
		|| ($_XOBJ = &dwho_gct::get('xivo_object')) === false
		|| ($this->_appentity = &$_XOBJ->get_application('entity')) === false
		|| ($this->_entity = &$_XOBJ->get_module('entity')) === false
		|| ($this->_provdconfig = &$_XOBJ->get_module('provdconfig')) === false
		|| ($this->_linefeatures = $this->_service->get_module('linefeatures')) === false
		|| ($this->_attachment = $this->_service->get_module('attachment')) === false)
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

		if(dwho_ak('picture',$nocomponents,true) === false)
			$this->_get_picture();

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
		//$skills = $this->_queueskills->get_skills($this->_info['userfeatures']['id']);
		//$this->_info['queueskills'] = $skills === false?array():$skills;

		// schedule
		$this->_info['schedule_id'] = 0;
		$where = array('path' => 'user', 'pathid' => $this->_info['userfeatures']['id']);
		if(($schedule = $this->_schedule_path->get_where($where)) !== false)
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

		$order = array();
		$order['rules_group'] = SORT_ASC;
		$order['rules_order'] = SORT_ASC;

		$where = array();
		$where['iduserfeatures'] = $this->_info['userfeatures']['id'];

		$this->_info['linefeatures'] = $this->_linefeatures->get_all_where($where,
										   null,
										   $order);
		$this->_origin['linefeatures'] = $this->_linefeatures->get_origin_list();

		return($this->_info['linefeatures']);
	}

	function _get_picture()
	{
		$this->_info['picture'] = false;
		$this->_origin['picture'] = false;

		$pictureid = (int) $this->_info['userfeatures']['pictureid'];

		if(is_object($this->_attachment) === false
		|| $pictureid === 0)
			return(false);

		$this->_info['picture'] = $this->_attachment->get($this->_info['userfeatures']['pictureid']);
		$this->_origin['picture'] = $this->_attachment->get_origin();

		return($this->_info['picture']);
	}

	function _get_entity()
	{
		$this->_info['entity'] = false;
		$this->_origin['entity'] = false;

		if(is_object($this->_appentity) === false)
			return(false);

		$this->_info['entity']  = $this->_appentity->get($this->_info['userfeatures']['entityid'],null,'internal');

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

		$voicemailid = (int) $this->_info['userfeatures']['voicemailid'];

		if(is_object($this->_voicemail) === false
		|| $voicemailid === 0
		|| $this->_voicemail->get($voicemailid) === false)
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

	function get_config_picture_file()
	{
		return($this->_chk_exists_cfg('picture','file',true));
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
		elseif($this->_ctiprofiles === false
		|| ($list = $this->_ctiprofiles->get_profiles_list()) === false
		|| ($nb = count($list)) === 0)
			return(false);

		$this->_profileclientlist = array();

		for($i=0;$i<$nb;$i++)
		{
			$ref = &$list[$i]['ctiprofiles'];
			$this->_profileclientlist[$ref['name']] = $ref['appliname'];
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
		return($this->_get_users('search_number',$disable,$search,$order,$limit,$assoc));
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
				$rs = $this->_dso->search($search,$disable,true,$order,$limit);
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
/*
			// get userskills
			$skills = $this->_queueskills->get_skills($userfeatures['id']);
			if($skills === false)
				$skills = array();

			$r[$userfeatures['id']]['queueskills'] = $skills;
*/
			if($this->_components === false)
				continue;

			$where = array('iduserfeatures' => $userfeatures['id']);
			$r[$userfeatures['id']]['nb_line'] = $this->_linefeatures->get_nb($where);
			$r[$userfeatures['id']]['masterline'] = $this->_linefeatures->get_user_masterline($userfeatures['id']);
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
		$r['outcalls']  = $this->get_destination_outcall();
		//$r['trunk'] = $this->get_destination_trunk();

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

			$r[] = array('phonefunckey'	=> $phonefunckey, 'result' => $res);
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
		elseif(isset($this->_info['userfeatures']) === true
		&& isset($this->_info['userfeatures']['id']) === true)
			$iduserfeatures = (int) $this->_info['userfeatures']['id'];

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
		$this->set_picture($iduserfeatures);

		if(dwho_issa('linefeatures',$arr) === true)
		{
			$this->set_linefeatures($arr['linefeatures'],$iduserfeatures);

			if(dwho_issa('voicemail',$arr) === true
			&& dwho_empty($this->get_result('linefeatures')))
			{
				$this->_set_error('voicemail', dwho_i18n::babelfish('user_need_lines_to_have_voicemail'));
				dwho_report::push('error', dwho_i18n::babelfish('user_need_lines_to_have_voicemail'));
				return(false);
			}

			if(dwho_issa('queue',$arr) === true
			&& dwho_issa('queue-select',$arr) === true)
			{
				$this->_set_result('queue',$arr['queue']);
				$this->_set_result('queue-select',$arr['queue-select']);
			}
			if(dwho_issa('group',$arr) === true
			&& dwho_issa('group-select',$arr) === true)
			{
				$this->_set_result('group',$arr['group']);
				$this->_set_result('group-select',$arr['group-select']);
			}

			switch($this->get_result_var('userfeatures','voicemailtype'))
			{
				case 'asterisk':
				break;
				default:
					$vmaction = 'none';
					$this->_set_result_var('userfeatures','voicemailid',null);
				break;
			}

			if(dwho_issa('voicemail',$arr) === true
			&& dwho_has_len($arr['voicemail'],'mailbox') === true
			&& ($linefeatures = $this->get_result_var('linefeatures',0)) !== null)
			{
				$context = $linefeatures['context'];

				if($vmaction === 'add')
					$arr['voicemail']['context'] = $context;

				$arr['voicemail']['locale'] = $this->get_result_var('userfeatures','language');

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
			else
			{
				$this->_set_result_var('userfeatures','voicemailtype',null);
				$this->_set_result_var('userfeatures','enablevoicemail',false);
				$this->_set_result_var('userfeatures','voicemailid',null);
			}
		}


		if(dwho_issa('dialaction',$arr) === true)
			$this->set_dialaction($arr['dialaction']);

		if(dwho_issa('rightcall',$arr) === true)
			$this->set_rightcall($arr['rightcall']);

		if(dwho_issa('phonefunckey',$arr) === true)
			$this->set_phonefunckey($arr['phonefunckey']);
/*
		// QUEUESKILLS
		if(dwho_issa('queueskills',$arr) === true)
			$this->set_queueskills($action, $arr['queueskills']);
*/
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

		if (isset($arr['enableclient'])
		&& (bool) $arr['enableclient'] === true
		&& (dwho_has_len($arr['loginclient']) === false
			|| dwho_has_len($arr['passwdclient']) === false))
		{
			dwho_report::push('error', 'cant_activate_xivoclient_without_login_and_password');
			$err = array('loginclient' => 'empty', 'passwdclient' => 'empty');
			$this->_set_error('userfeatures', $err);
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
				$this->_set_error('userfeatures',array('loginclient' => 'client login exists'));
				return(false);
			}
		}

		if(dwho_has_len($rs['agentid']) === false
		|| is_object($this->_agentfeatures) === false
		|| $this->_agentfeatures->get_primary($rs['agentid']) === false)
			$rs['agentid'] = null;

		$this->_set_result('userfeatures',$rs);

		return(true);
	}

	function set_picture($iduserfeatures)
	{
		if($this->_attachment === false
		|| ($userfeatures = $this->get_result('userfeatures')) === null)
			return(false);

		if(($http_response = dwho_http::factory('response')) === false
		|| ($fileinfo = $http_response->upload_file('picture',$this->_conf['picture']['file'])) === false)
			return(false);

		$fileinfo['object_type'] = 'user';
		$fileinfo['object_id'] = (int) $iduserfeatures;
		$fileinfo['file'] = $fileinfo['tmp_name'];

		if($fileinfo['error'] > 0
		|| ($rs = $this->_attachment->chk_values($fileinfo)) === false)
		{
			$this->_set_result('picture',$this->_attachment->get_filter_result());
			$this->_set_error('picture',$this->_attachment->get_filter_error());
			return(false);
		}
		$this->_set_result('picture',$rs);

		return(true);
	}

	function set_linefeatures($arr,$iduserfeatures)
	{
		if(is_array($arr) === false
		|| $this->_linefeatures === false
		|| ($userfeatures = $this->get_result('userfeatures')) === null)
			return(false);

		$reslist = $error = array();
		$errnb = 0;

		foreach($arr as $key => $list)
		{
			for($i = 0;$i < count($list);$i++)
			{
				if (isset($arr[$key][$i]) === false
				|| $arr[$key][$i] === '')
					$reslist[$i][$key] = '';
				else
					$reslist[$i][$key] = $arr[$key][$i];
			}
		}

		if(empty($reslist) === true)
		{
			$this->_set_result('linefeatures',false);
			$this->_set_error('linefeatures','empty');
			return(false);
		}

		array_pop($reslist);

		for($i = 0;$i < count($reslist);$i++)
		{
			$ref = &$reslist[$i];

			if (isset($ref['id']) === true
			&& (int) $ref['id'] !== 0)
			{
				$this->_line->_reset_info();
				$this->_line->_reset();
				if (($line = $this->_line->get($ref['id'],null,null,false,$iduserfeatures)) === false
				|| ($linefeatures = $line['linefeatures']) === false)
				{
					$errnb++;
					$error[$i] = 'linefeatures_not_exist';
					continue;
				}

				$ref['id'] = (int) $ref['id'];
				$ref['protocol'] = $linefeatures['protocol'];
				$ref['protocolid'] = (int) $linefeatures['protocolid'];
				$ref['name'] = $linefeatures['name'];
				$ref['context'] = isset($ref['context']) ? $ref['context'] : $linefeatures['context'];
			}
			else
			{
				$ref['protocolid'] = 0;
				$ref['name'] = $this->gen_password(6,true);
				if (isset($ref['rules_order']) === false)
					$ref['rules_order'] = $i+1;
			}

			$protocolname = $ref['protocol'];
			$number = $ref['number'];

			if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
				$this->_set_result_var('userfeatures','voicemailtype',null);

			switch($userfeatures['voicemailtype'])
			{
				case 'asterisk':
				break;
				case 'exchange':
					if($number === '')
						$this->_set_result_var('userfeatures','voicemailtype',null);
				default:
					$vmaction = 'none';
					$this->_set_result_var('userfeatures','voicemailid',null);
			}

			$ref['iduserfeatures'] = (int) $iduserfeatures;
			$ref['rules_order'] = isset($ref['rules_order']) ? (int) $ref['rules_order'] : 0;
			$ref['rules_group'] = isset($ref['rules_group']) ? $ref['rules_group'] : '';
			$ref['rules_time'] = (int) $userfeatures['ringseconds'];
			$ref['num'] = isset($ref['num']) ? (int) $ref['num'] : 1;
			$ref['callerid'] = $this->_service->mk_callerid($userfeatures['callerid'],$number,$protocolname);

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
		else
			$this->_set_result('voicemail',$this->_voicemail->get_result('voicemail'));

		if(($voicemailfeatureserror = $this->_voicemail->get_error('voicemailfeatures')) !== null)
		{
			$this->_set_error('voicemailfeatures',$voicemailfeatureserror);
			$this->_set_result('voicemailfeatures',$this->_voicemail->get_result('voicemailfeatures'));
		}
		else
			$this->_set_result('voicemailfeatures',$this->_voicemail->get_result('voicemailfeatures'));

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

			if(($info['typeextenumbers'] !== null
			|| $info['typeextenumbersright'] !== null) === true
			&& $this->_phonefunckey->is_valid($info['typeextenumbers'],
							  $info['typevalextenumbers'],
							  $info['typeextenumbersright'],
							  $info['typevalextenumbersright'],
							  $info['iduserfeatures'],
							  null) === false)
				return(false);
			else if($info['typeextenumbers'] === 'extenfeatures'
			&& $info['typevalextenumbers'] === 'bsfilter'
			&& $this->_dso->chk_bsfilter($info['iduserfeatures'],
						     $this->get_result_var('userfeatures','bsfilter'),
						     $info['typevalextenumbersright']) === false)
				return(false);
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

	function update_pictureid($pictureid,$iduserfeatures)
	{
		if(($pictureid = dwho_ulongint($pictureid)) === 0
		|| ($iduserfeatures = dwho_ulongint($iduserfeatures)) === 0
		|| ($userfeatures = &$this->_service->get_module('userfeatures')) === false)
			return(false);

		$val = array();
		$val['pictureid'] = $pictureid;

		return($userfeatures->edit($iduserfeatures,$val));
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$userfeaturesid = null;

		if($this->get_errnb() > 0
		|| ($userfeaturesid = $this->add_userfeatures()) === false
		|| $this->add_picture($userfeaturesid) === false
		|| $this->edit_linefeatures($userfeaturesid) === false
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

		$this->_return['userfeatures'] = $this->_userfeatures->add($rs);

		return($this->_return['userfeatures']);
	}

	function add_picture()
	{
		if(($rs = $this->get_result('picture')) === null)
			return($rs);
		elseif($rs === false)
			return(false);

		$this->_return['picture'] = $this->_attachment->add($rs);

		return($this->_return['picture']);
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
		$id['iduserfeatures'] = $userfeaturesid;

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];
			$ref['iduserfeatures'] = $userfeaturesid;

			if($this->_phonefunckey->add($ref) === false)
				return(false);

			$id['fknum'] = $ref['fknum'];
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
		if($this->_status !== 'add'
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
		|| $this->edit_userfeatures() === false
		|| $this->edit_picture() === false
		|| $this->edit_linefeatures() === false
		|| $this->edit_rightcall() === false
		|| $this->edit_dialaction() === false
		|| $this->edit_voicemail() === false
		|| $this->edit_schedule_path() === false
		|| $this->edit_phonefunckey() === false)
		{
			$this->_reverse_edit();
			$this->_status = '';
			return(false);
		}

		if($this->_provdconfig->rebuild_master_line_user($this->_info['userfeatures']['id']) === false)
			return(false);

		$this->_status = '';
		return(true);
	}

	function edit_userfeatures()
	{
		if(dwho_issa('userfeatures',$this->_info) === false
		|| ($rs = $this->get_result('userfeatures')) === null
		|| $rs === false)
			return(false);

		$return = $this->_userfeatures->edit($this->_info['userfeatures']['id'],$rs);

		return(($this->_return['userfeatures'] = $return));
	}

	function edit_picture()
	{
		if(($rs = $this->get_result('picture')) === null)
			return($rs);
		elseif($this->_attachment === false
		|| $rs === false)
			return(false);

		if(dwho_issa('picture',$this->_info) === false)
		{
			$return = $this->_attachment->add($rs);
			$this->update_pictureid($return,$this->_info['userfeatures']['id']);
		}
		else
		{
			$return = $this->_attachment->edit($this->_info['picture']['id'],$rs);
			$this->update_pictureid($this->_info['picture']['id'],$this->_info['userfeatures']['id']);
		}

		return(($this->_return['picture'] = $return));
	}

	function edit_linefeatures($userfeaturesid=0)
	{
		if(($rs = $this->get_result('linefeatures')) === null
		|| (($nbrs = count($rs)) === 0
			&& $this->_info['linefeatures'] === false))
			return(null);

		if(is_null($rs) === true)
			$rs = array();

		$res = array();
		if (isset($this->_info['linefeatures']) === true
		&& ($info = $this->_info['linefeatures']) !== false
		&& ($nbinfo = count($info)) !== 0)
		{
			for($i = 0;$i < $nbinfo;$i++)
			{
				$ref = &$info[$i];
				$res[$ref['id']] = $ref;
			}
		}

		$return = $error = array();
		$errnb = 0;

		$arr = array();
		$arr['userfeatures'] = $this->get_result('userfeatures');

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
				if (isset($ref['id']) === false)
					continue;
				if($this->_line->get($ref['id']) === false
				||$this->_line->delete() === false)
					dwho_report::push('error','Can\'t disassociate line: '.$ref['id'],'linefeatures');
			}
		}

		for($i = 0;$i < $nbrs;$i++)
		{
			$line = &$rs[$i];

			if($userfeaturesid !== 0)
				$line['iduserfeatures'] = (int) $userfeaturesid;

			$this->_line->_reset();

			if (isset($line['id']) === true
			&& (int) $line['id'] !== 0)
			{
				$methodset = 'set_edit';
				$method = 'edit';

				if ($this->_line->get($line['id'],null,null,false,$line['iduserfeatures']) === false)
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
			$arr['protocol']['language'] = $arr['userfeatures']['language'];
			$arr['protocol']['mailbox'] = $this->get_result_var('protocol','mailbox');

			if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
				$arr['protocol']['interface'] = $line['name'];

			$arr['callgroup'] = $this->get_result('callgroup');

			if(($queue = $this->get_result('queue')) !== null
			&& ($queue_select = $this->get_result('queue-select')) !== null)
			{
				$arr['queue'] = $queue;
				$arr['queue-select'] = $queue_select;
			}
			if(($group = $this->get_result('group')) !== null
			&& ($group_select = $this->get_result('group-select')) !== null)
			{
				$arr['group'] = $group;
				$arr['group-select'] = $group_select;
			}

			if($this->_line->$methodset($arr,$protocolname) === false
			|| $this->_line->$method() === false)
			{
				$errnb++;
				$error[$i] = $this->_line->get_error();
				$msgkey = array_shift(array_keys($this->_line->get_error()));
				$msg = array_shift($this->_line->get_error());
				if (empty($msgkey) === false)
					dwho_report::push('error','Line '.($i+1).': '.$msgkey.' '.$msg,'linefeatures');
				else
					dwho_report::push('error','Line '.($i+1).': unknow error during '.$method,'linefeatures');
			}
			$return[$i] = $line;
		}

		if ($errnb >> 0)
		{
			$this->_set_error('linefeatures',$error);
			return(false);
		}

		return(($this->_return['linefeatures'] = $return));
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

		return($this->add_phonefunckey($this->_info['userfeatures']['id']));
	}

	function edit_schedule_path()
	{
		$this->_schedule_path->delete_where(array('path' => 'user', 'pathid' => intval($this->_info['userfeatures']['id'])));

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
			return(null);

		$r = array();
		foreach($this->_info['linefeatures'] as $line)
		{
			if($this->_line->get($line['id']) === false
			|| $this->_line->delete() === false)
				dwho_report::push('error','Can\'t remove line: '.$line['id'],'linefeatures');
		}

		if($this->_status === 'delete')
			$this->_return['linefeatures'] = $r;

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
		$where['typeval'] = strval($this->_info['userfeatures']['id']);

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
				case 'rightcall':
					$this->_rightcall->add_origin_list();
					break;
				case 'dialaction':
					$this->_dialaction->add_origin_list();
					break;
				case 'groupmember':
				case 'queuemember':
					if(isset($this->_origin[$key]) === true
					&& $this->_origin[$key] !== false)
						$this->_queuemember->add_origin_list($this->_origin[$key]);
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

	function _prepare_import($arr, $partial=false)
	{
		$issa_userfeatures = dwho_issa('userfeatures',$arr);

		if(dwho_issa('voicemail',$arr) === true
		&& empty($arr['voicemail']) === false
		&& dwho_has_len($arr['voicemail'],'mailbox') === true) {
			if($issa_userfeatures === true) {
				$arr['userfeatures']['enablevoicemail'] = true;
			}
		} else {
			unset($arr['voicemail']);
		}

		if($issa_userfeatures === true)
		{
			if (dwho_issa('entityid',$arr['userfeatures']) === false)
				$arr['userfeatures']['entityid'] = 1;

			if(dwho_has_len($arr['userfeatures'],'firstname') === true)
				$arr['userfeatures']['callerid'] = $arr['userfeatures']['firstname'].' ';

			if(dwho_has_len($arr['userfeatures'],'lastname') === true)
				$arr['userfeatures']['callerid'] .= $arr['userfeatures']['lastname'];
		}

		if($issa_userfeatures === true
		&& dwho_has_len($arr['userfeatures'],'agentnumber') === true
		&& is_object($this->_agentfeatures) === true
		&& ($agentid = $this->_agentfeatures->get_primary(
					array('number' => $arr['userfeatures']['agentnumber']))) !== false) {
			$arr['userfeatures']['agentid'] = $agentid;
		}

		unset($arr['userfeatures']['agentnumber']);

		if(dwho_issa('linefeatures',$arr) === true) {
			if (!dwho_issa('id', $arr['linefeatures'])) {
				$arr['linefeatures']['id'] = array();
				array_push($arr['linefeatures']['id'], 0);
			}
			array_push($arr['linefeatures']['id'], 0);
		}

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
			$ref = &$data[$i];

			if(($arr = $this->_prepare_import($ref)) === false
			|| $this->set_add($arr) === false)
			{
				$r['lines'][$row] = 'error_import';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($ref, true), 'userimport', "line #$i");

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
					$r['lines'][$row] = 'error_user';
					$r['total']['error']++;

					$this->_reverse_add();

					dwho_logw(print_r($this->get_error(),true)."\n".print_r($ref, true), 'userimport', "line #$i");
					dwho_report::push('error', $this->get_error());
				}
				else
				{
					$r['lines'][$row] = 'success_incall';
					$r['total']['success']++;
				}
				continue;
			}

			$incall['incall'] = $arr['incall'];
			$incall['incall']['context'] = 'incall';

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
				$r['lines'][$row] = 'error_incall';
				$r['total']['error']++;

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($ref, true), 'userimport', "line #$i");
				dwho_report::push('error', $appincall->get_error());
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

				$this->_reverse_add();

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($ref, true), 'userimport', "line #$i");
				dwho_report::push('error', $this->get_error());
				continue;
			}

			$incall['dialaction']['answer']['actionarg1'] = $this->get_return('userfeatures');

			if($appincall->set_add($incall) === false
			|| $appincall->add() === false)
			{
				$r['lines'][$row] = 'error';
				$r['total']['error']++;

				$appincall->_reverse_add();

				dwho_logw(print_r($this->get_error(),true)."\n".print_r($ref, true), 'userimport', "line #$i");
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

	function array_merge_recursive($arr1, $arr2)
	{
		foreach($arr2 as $k => $v)
		{
			if(array_key_exists($k, $arr1) && is_array($arr1[$k]) && is_array($v))
				$arr1[$k] = $this->array_merge_recursive($arr1[$k], $arr2[$k]);
			else
				$arr1[$k] = $v;
		}

		return $arr1;
	}

	function edit_from_json($mergewith=null)
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data, !is_null($mergewith))) === false)
		{
			return(false);
		}

		if(!is_null($mergewith))
			$arr = $this->array_merge_recursive($mergewith,$arr);

		if($this->set_edit($arr) === false
		|| $this->edit() === false)
		{
			return(false);
		}

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
