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

class xivo_application_service_asterisk_line extends xivo_application_asterisk_abstract
{
	protected $_dso				= null;
	protected $_contextlist		= false;
	protected $_linefeatures 	= false;
	protected $_protocolname	= false;
	protected $_extenumbers		= false;
	protected $_extensions		= false;
	protected $_contextnummember= false;
	protected $_protocol		= false;
	protected $_queuemember		= null;
	protected $_provdconfig		= false;
	protected $_provddevice		= false;
	protected $_devicefeatures 	= false;
	protected $_device		 	= false;
	protected $_sccpdevice		= false;
	protected $_conf			= array();
	protected $_param			= array('internal'	=> false);

	public function __construct(&$service,&$dso,$param=array(),$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_linefeatures = &$this->_service->get_module('linefeatures')) === false
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

		if(is_array($param) === true
		&& isset($param['internal']) === true)
			$this->_param['internal'] = (bool) $param['internal'];

		return(true);
	}

	public function load_components()
	{
		$this->_components = true;

		if(($this->_extensions = &$this->_service->get_module('extensions')) === false
		|| ($this->_extenumbers = $this->get_abstract('extenumbers',array('type' => 'user'))) === false
		|| ($this->_contextnummember = $this->get_abstract('contextnummember',array('type' => 'user'))) === false
		|| ($this->_devicefeatures = &$this->_service->get_module('devicefeatures')) === false
		|| ($this->_device = &$this->_service->get_application('device')) === false
		|| ($this->_sccpdevice = &$this->_service->get_module('sccpdevice')) === false
		|| ($_XOBJ = &dwho_gct::get('xivo_object')) === false
		|| ($this->_provdconfig = &$_XOBJ->get_module('provdconfig')) === false
		|| ($this->_provddevice = &$_XOBJ->get_module('provddevice')) === false)
			return(false);

		$this->_queuemember = &$this->_service->get_module('queuemember');

		return(true);
	}

	public  function _reset()
	{
		$this->_protocolname = false;

		return(parent::_reset());
	}

	public function get($id,$disable=null,$nocomponents=null,$ipbxinfos=false,$userid=0)
	{
		$this->_info = $this->_origin = array();

		$this->_linefeatures->set_dso_param('internal',$this->_param['internal']);

		if(($this->_info['linefeatures'] = $this->_linefeatures->get($id)) === false)
			return(false);

		if($this->_info['linefeatures'] === false
		|| ($this->_protocol = &$this->_service->get_protocol_module($this->_info['linefeatures']['protocol'])) === false
		|| ($this->_info['protocol'] = $this->_protocol->get($this->_info['linefeatures']['protocolid'],$disable)) === false)
			return(false);

		$this->_origin['protocol'] = $this->_protocol->get_origin();
		$this->_origin['linefeatures'] = $this->_linefeatures->get_origin();

		if($this->_components === false)
			return($this->_info);

		if(dwho_ak('groupmember',$nocomponents,true) === false)
			$this->_get_groupmember($userid);

		if(dwho_ak('queuemember',$nocomponents,true) === false)
			$this->_get_queuemember($userid);

		if(dwho_ak('usermacro',$nocomponents,true) === false)
			$this->_get_usermacro();

		if(dwho_ak('extenumbers',$nocomponents,true) === false)
			$this->_get_extenumbers($this->_info['linefeatures']['id']);

		if(dwho_ak('contextnummember',$nocomponents,true) === false)
			$this->_get_contextnummember($this->_info['linefeatures']['id']);

		if ($ipbxinfos === true)
			$this->_get_ipbx_infos();

		return($this->_info);
	}

	public function get_nb($arr=null,$disable=null,$initialized=null)
	{
		return($this->_dso->get_nb($arr,$disable,$initialized));
	}

	function _get_usermacro()
	{
		$this->_info['usermacro'] = false;
		$this->_origin['usermacro'] = false;

		if(isset($this->_info['protocol']['context']) === true
		&& ($this->_info['usermacro'] = $this->_extensions->get_exten($this->_info['linefeatures']['number'],
									      $this->_info['protocol']['context'],
									      'macro')) !== false)
			$this->_origin['usermacro'] = $this->_extensions->get_origin();

		return($this->_info['usermacro']);
	}

	function _get_groupmember($userid)
	{
		return($this->_get_member_type('group', $userid));
	}

	function _get_queuemember($userid)
	{
		return($this->_get_member_type('queue', $userid));
	}

	function _get_member_type($type, $userid)
	{
		if($type !== 'group' && $type !== 'queue')
			return(false);
		elseif ((int) $userid === 0)
			return(false);

		$membertype = $type.'member';

		$this->_info[$membertype] = false;
		$this->_origin[$membertype] = false;

		$where = array();
		$where['category'] = $type;
		$where['usertype'] = 'user';
		$where['userid'] = $userid;

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

	function _get_ipbx_infos()
	{
		$protocols = array(
			'sip'  => 'sip show peer',
			'iax'  => 'iax2 show peer',
		);

		$this->_info['ipbx'] = false;

		if (!array_key_exists($this->_info['linefeatures']['protocol'], $protocols))
			return false;

		$q = sprintf("%s %s load",
			$protocols[$this->_info['linefeatures']['protocol']],
			$this->_info['protocol']['name']
		);

		$infos = $this->_service->discuss($q, true);

		if(!is_array($infos))
			return false;

		$res = array();
		foreach($infos as $line)
		{
			if (strstr($line, 'XIVO_USERID = '))
			{
				$item = explode('=',$line);
				$res['xivo_userid'] = trim($item[1]);
			} else {
				if (strpos($line,':'))
				{
					$item = explode(':',$line,2);
					// Remove bad characters and normalize the key values
					$item[0] = str_replace(array('.'),'',$item[0]);
					$item[0] = trim(str_replace(array('*','=','->'),' ',$item[0]));
					$item[0] = strtolower(str_replace(array(' ','-'),'_',$item[0]));
					$res[$item[0]] = trim($item[1]);
				}
			}
		}

		$this->_info['ipbx'] = $res;
		return true;
	}

	public function get_elements()
	{
		$r = array();

		$r['protocol'] = $this->_service->get_protocol_element();

		return($r);
	}

	public function get_all_context()
	{
		if(($r = $this->_linefeatures->get_all_context()) !== false)
			ksort($r);

		return($r);
	}

	public function get_lines_user($userfeaturesid,$order=null,$limit=null,$assoc=false,$free=null)
	{
		return($this->_get_lines('user',null,null,'','',$order,$limit,$assoc,null,$free,null,null,$userfeaturesid));
	}

	public function get_lines_device($deviceid,$context='',$disable=null,$order=null,$limit=null,$assoc=false,$free=null)
	{
		return($this->_get_lines('device',null,$disable,'',$context,$order,$limit,$assoc,null,$free,null,$deviceid));
	}

	public function get_lines_search($search,$context='',$protocols=null,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null)
	{
		return($this->_get_lines('search',$protocols,$disable,$search,$context,$order,$limit,$assoc,$initialized,$free,$internal));
	}

	public function get_lines_search_number($search,$context='',$protocols=null,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null)
	{
		return($this->_get_lines('search_number',$protocols,$disable,$search,$context,$order,$limit,$assoc,$initialized,$free,$internal));
	}

	public function get_lines_context($context,$protocols=null,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null)
	{
		return($this->_get_lines('context',$protocols,$disable,null,$context,$order,$limit,$assoc,$initialized,$free,$internal));
	}

	public function get_lines_contexts($contexts,$protocols=null,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null)
	{
		return($this->_get_lines('contexts',$protocols,$disable,null,$contexts,$order,$limit,$assoc,$initialized,$free,$internal));
	}

	public function get_lines_list($protocols=null,$disable=null,$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null)
	{
		return($this->_get_lines('list',$protocols,$disable,null,null,$order,$limit,$assoc,$initialized,$free,$internal));
	}

	/*
	 * options:
	 *		- internal: if true, also return internal accounts (*guest* account indeed)
	 *		- free: if true, also return iduserfeatures=0, null = both, false return iduserfeatures != 0	 *
	*/
	private function _get_lines($action,$protocols=null,$disable=null,$search='',$context='',
	$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null,
	$deviceid=null,$userfeaturesid=null)
	{
		$search = strval($search);

		if(is_array($protocols) === true && empty($protocols) === false)
			$protocols = array_values($protocols);
		else
			$protocols = null;

		if (is_null($free) === false)
			$free = (bool) intval($free);

		switch($action)
		{
			case 'user':
				$rs = $this->_dso->get_all(null,null,null,$order,$limit,null,null,null,null,$free,$userfeaturesid);
				break;
			case 'device':
				$rs = $this->_dso->device($deviceid,$context,$disable,$order,$limit,$free);
				break;
			case 'search':
				$rs = $this->_dso->search($search,$context,$protocols,$disable,$initialized,$order,$limit);
				break;
			case 'search_number':
				$rs = $this->_dso->search($search,$context,$protocols,$disable,$initialized,$order,$limit,'number');
				break;
			case 'context':
				$rs = $this->_dso->get_all($protocols,$disable,$initialized,$order,$limit,null,$context,null,$internal,$free);
				break;
			case 'contexts':
				$rs = $this->_dso->get_all_in_contexts($context,$protocols,$disable,$initialized,$order,$limit,$internal,$free);
				break;
			case 'list':
			default:
				$rs = $this->_dso->get_all($protocols,$disable,$initialized,$order,$limit,null,null,null,$internal,$free);
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$rs[$i];

			$linefeatures = dwho_array_startswith_key($ref,'linefeatures.',true);
			$linefeatures = $this->_linefeatures->_prepare($linefeatures);

			$r[$linefeatures['id']] = array();

			$userfeatures = dwho_array_startswith_key($ref,'userfeatures.',true);

			if (is_array($userfeatures) === true
			&& isset($userfeatures['firstname'], $userfeatures['lastname']))
				$linefeatures['useridentity'] = $userfeatures['firstname'].' '.$userfeatures['lastname'];
			else
				$linefeatures['useridentity'] = '-';

			switch($linefeatures['protocol'])
			{
				case XIVO_SRE_IPBX_AST_PROTO_SIP:
					$sip = dwho_array_startswith_key($ref,'usersip.',true);
					$sip['initialized'] = dwho_has_len($sip['fullcontact']);
					unset($sip['fullcontact']);
					$sip['identity'] = strtoupper($sip['protocol']).'/'.$sip['name'];
					$r[$linefeatures['id']] = array_merge($sip,$linefeatures);
					break;
				case XIVO_SRE_IPBX_AST_PROTO_IAX:
					$iax = dwho_array_startswith_key($ref,'useriax.',true);
					$iax['initialized'] = true;
					$iax['identity'] = strtoupper($iax['protocol']).'/'.$iax['name'];
					$r[$linefeatures['id']] = array_merge($iax,$linefeatures);
					break;
				case XIVO_SRE_IPBX_AST_PROTO_SCCP:
					$sccp = dwho_array_startswith_key($ref,'sccpline.',true);
					$sccp['protocol'] = 'SCCP';
					$sccp['initialized'] = true;
					$sccp['identity'] = strtoupper($sccp['protocol']).'/'.$sccp['name'];
					$r[$linefeatures['id']] = array_merge($sccp,$linefeatures);
					break;
				case XIVO_SRE_IPBX_AST_PROTO_CUSTOM:
					$custom = dwho_array_startswith_key($ref,'usercustom.',true);
					$custom['initialized'] = true;
					#$custom['identity'] = strtoupper(XIVO_SRE_IPBX_AST_PROTO_CUSTOM).'/'.$custom['interface'];
					$custom['identity'] = $custom['interface'];
					$r[$linefeatures['id']] = array_merge($custom,$linefeatures);
					break;
				default:
					continue;
			}
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	public function set_add($arr,$protocolname)
	{
		return($this->_set('add',$arr,$protocolname));
	}

	public function set_edit($arr,$protocolname)
	{
		if(empty($this->_info) === true)
			return(false);

		return($this->_set('edit',$arr,$protocolname));
	}

	private function _set($action,$arr,$protocolname,$chkcontext=true)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('protocol',$arr) === false)
			return(false);

		$this->_protocolname = $protocolname;

		if ($action === 'add')
			$arr['protocol']['secret'] = $this->gen_password(6);

		$callerid = '';
		if(isset($arr['protocol']['callerid']) === true)
			$callerid =$arr['protocol']['callerid'];
		elseif(isset($arr['linefeatures']['callerid']) === true)
			$callerid = $arr['linefeatures']['callerid'];

		if(isset($arr['linefeatures']['mailbox']) === true)
			$arr['protocol']['mailbox'] = $arr['linefeatures']['mailbox'];

		$arr['protocol']['callerid'] = $this->_service->mk_callerid($callerid, '', $protocolname);

		if ($this->_protocol !== false
		&& ($protocol = $this->_protocol->get($arr['linefeatures']['protocolid'])) !== false) {
			$arr['protocol'] = array_merge($protocol, $arr['protocol']);
			if (dwho_issa('callgroup', $arr['protocol']) === true)
				$arr['protocol']['callgroup'] = implode(',', $arr['protocol']['callgroup']);
			if (dwho_issa('pickupgroup', $arr['protocol']) === true)
				$arr['protocol']['pickupgroup'] = implode(',', $arr['protocol']['pickupgroup']);
		}
		if (dwho_issa('userfeatures',$arr) === true
		&& $this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SIP)
			$arr['protocol']['call-limit'] = (2 * (int) $arr['userfeatures']['simultcalls']);

		$this->set_protocol($arr['protocol'],$protocolname);

		if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			$name = $arr['protocol']['interface'];
		else
			$name = $arr['protocol']['name'];

		$context = (string) $arr['protocol']['context'];

		if (dwho_issa('linefeatures',$arr) === false)
		{
			$arr['linefeatures']['protocolid'] = 0;
			$arr['linefeatures']['rules_order'] = 0;
			$arr['linefeatures']['rules_group'] = '';
			$arr['linefeatures']['iduserfeatures'] = 0;
		}

		$arr['linefeatures']['protocol'] = $protocolname;
		$arr['linefeatures']['name'] = $name;
		$arr['linefeatures']['context'] = $context;

		if (dwho_issa('userfeatures',$arr) === false)
		{
			$this->set_linefeatures($action,$arr['linefeatures']);
			if($this->get_errnb() > 0)
				$this->_protocolname = $r = false;
			else
				$r = true;

			return($r);
		}

		$userfeatures = $arr['userfeatures'];

		if (isset($userfeatures['id']) === true)
			$arr['linefeatures']['iduserfeatures'] = (int) $userfeatures['id'];

		$this->set_linefeatures($action,$arr['linefeatures']);

		$number = (string) $arr['linefeatures']['number'];
		$numhaslen = dwho_has_len($number);
		$musiconhold = (string) $userfeatures['musiconhold'];

		switch ($protocolname)
		{
			case XIVO_SRE_IPBX_AST_PROTO_SIP:
				if(dwho_issa('group',$arr) === true
				&& dwho_issa('group-select',$arr) === true
				&& $this->set_groupmember($arr['group'],
										$arr['group-select'],
										$name,
										$context,
										$number,
										$protocolname) === true)
				{
					$callgroup = $this->get_result('callgroup');

					if(is_array($callgroup) === true && isset($callgroup[0]) === true)
						$callgroup = implode(',',$callgroup);
					else
						$callgroup = '';
					$this->_set_result_var('protocol','callgroup',$callgroup);
				}
				break;
		}

		if(dwho_issa('queue',$arr) === true && dwho_issa('queue-select',$arr) === true) {
			$this->set_queuemember($arr['queue'],
						$arr['queue-select'],
						$name,
						$context,
						$number,
						$protocolname);
		}

		$this->_set_result('userfeatures',$userfeatures);

		$this->_extenumbers->_reset();
		$this->_contextnummember->_reset();

		if ($this->_errnb === 0 && $numhaslen === true)
		{
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
						$arr['userfeatures']['voicemailid'] = null;
						break;
					case 'search':
						$vmaction = 'edit';
						break;
				}
			}

			if((bool) $chkcontext === true)
				$this->set_contextnummember($context,$number);

			if(($rsusermacro = $this->chk_macro('usermacro',
							    $number,
							    $this->_mk_usermacro_appdata(0,'',0),
							    $context)) !== false) {
				$this->_set_result('usermacro',$rsusermacro);
			}

			$this->set_extenumbers($action,$number,$context);
		}

		if($this->get_errnb() > 0)
			$this->_protocolname = $r = false;
		else
			$r = true;

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

		if(dwho_issa('allow',$arr) === false)
			$arr['allow'] = null;

		$this->_set_result('mailbox',$arr['mailbox']);

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

	function set_linefeatures($action,$arr)
	{
		if(($action !== 'add' && $action !== 'edit') === true
		|| ($action === 'edit' && dwho_issa('linefeatures',$this->_origin) === false) === true)
			return(false);
		else if(is_array($arr) === false)
		{
			$this->_set_result('linefeatures',null);
			$this->_set_error('linefeatures','invalid data');
			return(false);
		}
		elseif(($rs = $this->_linefeatures->chk_values($arr)) === false)
		{
			$this->_set_result('linefeatures',$this->_linefeatures->get_filter_result());
			$this->_set_error('linefeatures',$this->_linefeatures->get_filter_error());
			return(false);
		}

		if (isset($this->_info['linefeatures']) === true
		&& ($iduserfeatures = $this->_info['linefeatures']['iduserfeatures']) !== 0)
			$rs['iduserfeatures'] = (int) $iduserfeatures;

		$this->_set_result('linefeatures',$rs);

		return(true);
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
			|| ($typeid = $module->get_primary(array('name' => $qname))) === false) {
				continue;
			}

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

	function _set_usermacro($action,$iduserfeatures,$idlinefeatures)
	{
		$rs = false;

		if(($iduserfeatures = dwho_ulongint($iduserfeatures)) === 0
		|| ($rs = $this->get_result('usermacro')) === null
		|| $rs === false)
			return($rs);
		else if(($rsmacro = $this->set_macro($action,
						     'usermacro',
						     $rs['exten'],
						     $this->_mk_usermacro_appdata($iduserfeatures,'',$idlinefeatures),
						     $rs['context'])) === false)
			return(false);

		$this->_set_result('usermacro',$rsmacro);

		return(true);
	}

	function _mk_usermacro_appdata($iduserfeatures,$timeout='',$idlinefeatures)
	{
		$arr = array();
		$arr['appdata'][0] = XIVO_SRE_IPBX_AST_USER_MACRO;
		$arr['appdata'][1] = (int) ($iduserfeatures);
		$arr['appdata'][2] = (int) ($idlinefeatures);
		$arr['appdata'][3] = dwho_has_len($timeout) === true ? dwho_ufloat($timeout) : '';
		$arr['appdata'][4] = $this->get_result_var('protocol','language');

		return($arr);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$linefeaturesid = null;
		$iduserfeatures = null;

		if($this->get_errnb() > 0
		|| $this->_protocolname === false
		|| ($protocolid = $this->add_protocol()) === false
		|| ($linefeaturesid = $this->add_linefeatures($protocolid)) === false
		|| $this->add_config($linefeaturesid,$protocolid) === false)
		{
			$r = false;
			if($protocolid !== null) {
				$this->_reverse_add();
			}
		}

		if(dwho_has_len($this->get_result_var('linefeatures','number')) === true)
		{
			if($this->add_extenumbers($linefeaturesid) === false
			|| $this->add_contextnummember($linefeaturesid) === false)
			{
				$r = false;
				if($protocolid !== null) {
					$this->_reverse_add();
				}
			}
		}

		if(((int) $iduserfeatures = $this->get_result_var('linefeatures','iduserfeatures')) !== 0)
		{
			if($this->add_groupmember($iduserfeatures) === false
			|| $this->add_queuemember($iduserfeatures) === false) {
				$r = false;
			}
			elseif(dwho_has_len($this->get_result_var('linefeatures','number')) === true
			&& ($this->update_protocol_setvar($protocolid,$iduserfeatures) === false
			|| $this->add_usermacro($iduserfeatures,$linefeaturesid) === false)) {
				$r = false;
			}
		}

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

	function add_linefeatures($protocolid)
	{
		if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($rs = $this->get_result('linefeatures')) === null
		|| $rs === false)
			return(false);

		$rs['protocolid'] = (int) $protocolid;

		$this->_return['linefeatures'] = $this->_linefeatures->add($rs);

		return($this->_return['linefeatures']);
	}

	function add_config($linefeaturesid,$protocolid)
	{
		if(($linefeaturesid = dwho_ulongint($linefeaturesid)) === 0
		|| $this->_provddevice === false
		|| ($rs = $this->get_result('linefeatures')) === null
		|| $rs === false)
			return(false);

		if (empty($rs['device']) === false)
		{
			$this->_set_result_var('linefeatures', 'id',$linefeaturesid);

			$vm_number = '';
			if (dwho_has_len(($mailbox = $this->get_result('mailbox'))))
				$vm_number = strstr($mailbox, '@', true);

			$arr = array();
			$arr['linefeatures'] = $this->get_result('linefeatures');
			$arr['userfeatures'] = $this->get_result('userfeatures');
			$arr['protocol'] = $this->get_result('protocol');

			// new device associated
			if (empty($rs['device']) === false)
			{
				if (($device = $this->_devicefeatures->get($rs['device'])) === false)
				{
					dwho_report::push('error', 'device doesn\'t exist');
					return(false);
				}
				elseif($this->_provddevice->update_config_from_line($arr,$device['deviceid']) === false)
				{
					dwho_report::push('error', 'Can\'t edit device');
					return(false);
				}
				elseif ($rs['protocol'] === XIVO_SRE_IPBX_AST_PROTO_SCCP
				&& $this->_sccpdevice->init_device($device['mac'],$rs['name'],$vm_number) === false)
					return(false);
			}
		}
		return(true);
	}

	function update_protocol_setvar($protocolid,$iduserfeatures)
	{
		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM
		|| $this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SCCP)
			return(null);
		else if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($iduserfeatures = dwho_ulongint($iduserfeatures)) === 0
		|| ($protocol = &$this->_service->get_protocol_module($this->_protocolname)) === false)
			return(false);

		$val = array();
		$val['setvar'] = 'XIVO_USERID='.$iduserfeatures;

		return($protocol->edit($protocolid,$val));
	}

	function add_usermacro($iduserfeatures,$linefeaturesid)
	{
		if(($rs = $this->_set_usermacro('add',$iduserfeatures,$linefeaturesid)) !== true)
			return($rs);

		return(parent::add_macro('usermacro'));
	}

	function add_groupmember($iduserfeatures)
	{
		return($this->_add_member_type('group',$iduserfeatures));
	}

	function add_queuemember($iduserfeatures)
	{
		return($this->_add_member_type('queue',$iduserfeatures));
	}

	function _add_member_type($type,$iduserfeatures)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| ($iduserfeatures = dwho_ulongint($iduserfeatures)) === 0)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $iduserfeatures;
			if($type == 'queue')
				$rs[$i]['skills'] = $iduserfeatures;

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
				case 'linefeatures':
					$this->_linefeatures->delete($val);
					break;
				case 'usermacro':
					$this->_extensions->delete_exten($val);
					break;
				case 'groupmember':
				case 'queuemember':
					if(is_array($val) === false)
						continue;

					foreach($val as $memberval)
						$this->_queuemember->delete($memberval);
					break;
				case 'contextnummember':
					$this->_contextnummember->reverse_add();
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

		$linefeaturesid = (int) $this->_info['linefeatures']['id'];

		if($this->edit_linefeatures($protocolret) === false
		|| $this->edit_config() === false)
		{
			$this->edit_origin_protocol($protocolret);
			$this->_status = '';
			return(false);
		}
		elseif($this->get_result('userfeatures') !== null
		&& (((int) $iduserfeatures = $this->get_result_var('linefeatures','iduserfeatures'))) !== 0)
		{
			if($this->_info['linefeatures']['iduserfeatures'] === 0)
			{
				if($this->add_usermacro($iduserfeatures,$linefeaturesid) === false
				|| $this->add_extenumbers($linefeaturesid) === false)
				{
					$this->_reverse_edit($protocolret);
					$this->_status = '';
					return(false);
				}
			}
			else
			{
				if ($this->update_protocol_setvar($this->_info['protocol']['id'], $iduserfeatures) === false)
				{
					$this->_reverse_edit($protocolret);
					$this->_status = '';
					return(false);
				}
				else if($this->_info['linefeatures']['number'] !== '')
				{
					if($this->get_result('usermacro') === null
					|| $this->get_result('extenumbers') === null)
					{
						$this->delete_macro('usermacro');
						$this->delete_extenumbers();
					}
					else if ($this->edit_usermacro($iduserfeatures,$linefeaturesid) === false
					|| $this->edit_extenumbers() === false)
					{
						$this->_reverse_edit($protocolret);
						$this->_status = '';
						return(false);
					}
				}
				else if($this->add_usermacro($iduserfeatures,$linefeaturesid) === false
				|| $this->add_extenumbers($linefeaturesid) === false)
				{
					$this->_reverse_edit($protocolret);
					$this->_status = '';
					return(false);
				}
			}

			if($this->edit_contextnummember() === false
			|| $this->edit_groupmember() === false
			|| $this->edit_queuemember() === false)
			{
				$this->_reverse_edit($protocolret);
				$this->_status = '';
				return(false);
			}
		}

		$this->_status = '';
		return(true);
	}

	function edit_protocol()
	{
		if(dwho_issa('protocol',$this->_info) === false
		|| dwho_issa('linefeatures',$this->_info) === false
		|| ($protocol = &$this->_service->get_protocol_module($this->_protocolname)) === false)
			return(false);
		else if($this->_info['linefeatures']['protocol'] === $this->_protocolname)
		{
			if(($rs = $this->get_result('protocol')) === null)
				return(false);

			if(($ret = $protocol->edit($this->_info['protocol']['id'],$rs)) === false)
			{
				$this->_return['protocol'] = $ret;
				return(false);
			}

			return(($this->_return['protocol'] = $this->_info['protocol']['id']));
		}
		else if(($protocolid = $this->add_protocol()) === false)
			return(false);
		else if($this->delete_protocol() === false
		|| $this->update_protocol_setvar($protocolid, $this->_info['linefeatures']['id']) === false)
		{
			$protocol->delete($protocolid);
			return(false);
		}
		return(($this->_return['protocol'] = $protocolid));
	}

	function edit_origin_protocol($protocolid=0)
	{
		if(dwho_issa('protocol',$this->_origin) === false
		|| dwho_issa('linefeatures',$this->_info) === false
		|| ($protocol = &$this->_service->get_protocol_module($this->_info['linefeatures']['protocol'])) === false)
			return(false);
		else if($this->_info['linefeatures']['protocol'] === $this->_protocolname)
			return($protocol->edit_origin($this->_origin['protocol']));
		else if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($proto = &$this->_service->get_protocol_module($this->_protocolname)) === false
		|| $proto->delete($protocolid) === false)
			return(false);

		return($protocol->add_origin($this->_origin['protocol']));
	}

	function edit_linefeatures($protocolid)
	{
		if(dwho_issa('linefeatures',$this->_info) === false
		|| dwho_issa('protocol',$this->_info) === false
		|| ($rs = $this->get_result('linefeatures')) === null
		|| $rs === false)
			return(false);
		else if($this->_info['linefeatures']['protocol'] === $this->_protocolname)
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

		return(($this->_return['linefeatures'] = $this->_linefeatures->edit(
											$this->_info['linefeatures']['id'],
											$rs,
											$provisioning)));
	}

	function edit_config()
	{
		if(dwho_issa('linefeatures',$this->_info) === false
		|| dwho_issa('protocol',$this->_info) === false
		|| ($rs = $this->get_result('linefeatures')) === null
		|| $rs === false)
			return(false);

		$vm_number = '';
		if (dwho_has_len(($mailbox = $this->get_result('mailbox'))))
			$vm_number = strstr($mailbox, '@', true);

		// Device change, update it.
		if ($this->_info['linefeatures']['device'] !== $rs['device'])
		{
			// Delete the old device associated.
			if (empty($this->_info['linefeatures']['device']) === false)
			{
				$old_deviceid = $this->_info['linefeatures']['device'];
				if (($device = $this->_device->get($old_deviceid,null,true)) === false)
				{
					dwho_report::push('error', 'device doesn\'t exist: '.$old_deviceid);
					return(false);
				}
				elseif ($this->_device->remove_line($this->_info['linefeatures']['num']) === false)
					return(false);
				elseif ($this->_info['linefeatures']['protocol'] === XIVO_SRE_IPBX_AST_PROTO_SCCP
				&& $this->_sccpdevice->init_device($device['devicefeatures']['mac'],'') === false)
					return(false);
			}
			// Add the new device associated.
			if (empty($rs['device']) === false)
			{
				$linefeaturesid = $this->_info['linefeatures']['id'];
				$this->_set_result_var('linefeatures', 'id',$linefeaturesid);

				$arr = array();
				$arr['linefeatures'] = $this->get_result('linefeatures');
				$arr['userfeatures'] = $this->get_result('userfeatures');

				if(($this->_protocol = &$this->_service->get_protocol_module($arr['linefeatures']['protocol'])) === false
				|| ($protocol = $this->_protocol->get($arr['linefeatures']['protocolid'])) === false)
					return(false);

				$arr['protocol'] = $protocol;

				if (($device = $this->_devicefeatures->get($rs['device'])) === false)
				{
					dwho_report::push('error', 'device doesn\'t exist: '.$rs['device']);
					return(false);
				}
				elseif($this->_provddevice->update_config_from_line($arr,$device['deviceid']) === false)
					return(false);
				elseif ($rs['protocol'] === XIVO_SRE_IPBX_AST_PROTO_SCCP
				&& $this->_sccpdevice->init_device($device['mac'],$rs['number'],$vm_number) === false)
					return(false);
			}
		}
		// Device has not changed, just update.
		elseif (empty($rs['device']) === false
		&& empty($this->_info['linefeatures']['device']) === false)
		{
			if (($device = $this->_devicefeatures->get($this->_info['linefeatures']['device'])) === false)
			{
				dwho_report::push('error', 'device doesn\'t exist: '.$this->_info['linefeatures']['device']);
				return(false);
			}

			$this->_provdconfig->rebuild_device_config($device['id']);

			if ($rs['protocol'] === XIVO_SRE_IPBX_AST_PROTO_SCCP
			&& $this->_sccpdevice->init_device($device['mac'],$rs['number'],$vm_number) === false)
				return(false);
		}

		return(true);
	}

	function edit_usermacro($iduserfeatures,$linefeaturesid)
	{
		if(($rs = $this->_set_usermacro('edit',$iduserfeatures,$linefeaturesid)) !== true)
			return($rs);

		$ret = parent::edit_macro('usermacro');
		return $ret;
	}

	function edit_groupmember()
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('groupmember',$this->_info) === false)
			return($this->add_groupmember($this->get_result_var('linefeatures','iduserfeatures')));

		$this->_return['groupmember'] = $this->delete_groupmember();

		if($this->get_result('groupmember') === null)
			return($this->_return['groupmember']);

		return($this->_edit_member_type('group'));
	}

	function edit_queuemember()
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('queuemember',$this->_info) === false)
			return($this->add_queuemember($this->get_result_var('linefeatures','iduserfeatures')));

		$this->_return['queuemember'] = $this->delete_queuemember();

		if($this->get_result('queuemember') === null)
			return($this->_return['queuemember']);

		return($this->_edit_member_type('queue'));
	}

	function _edit_member_type($type)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| dwho_issa('linefeatures',$this->_info) === false)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);

		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $this->_info['linefeatures']['iduserfeatures'];
			if($type == 'queue') {
				$rs[$i]['skills'] = $rs[$i]['userid'];
			}

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

	function edit_contextnummember()
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);

		return(parent::edit_contextnummember($this->_info['linefeatures']['id']));
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
				case 'linefeatures':
					if(isset($this->_origin['linefeatures']) === false
					|| $this->_origin['linefeatures'] === false)
						$this->delete_linefeatures();
					else
						$this->_linefeatures->edit_origin($this->_origin['linefeatures']);
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
				case 'contextnummember':
					$this->_contextnummember->reverse_edit($this->_status);
					break;
				case 'extenumbers':
					$this->_extenumbers->reverse_edit($this->_status);
					break;
			}
		}

		$this->_extensions->delete_exten($this->_return['usermacro']);
		$this->_extenumbers->reverse_add();
		$this->_contextnummember->reverse_add();
		return(true);
	}

	function delete()
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();

		if($this->delete_protocol() === false
		|| $this->delete_linefeatures() === false
		|| $this->delete_config() === false
		|| $this->delete_macro('usermacro') === false
		|| $this->delete_extenumbers() === false
		|| $this->delete_groupmember() === false
		|| $this->delete_queuemember() === false
		|| $this->delete_contextnummember() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	function delete_protocol()
	{
		if(dwho_issa('protocol',$this->_info) === false
		|| dwho_issa('linefeatures',$this->_info) === false
		|| ($protocol = &$this->_service->get_protocol_module($this->_info['linefeatures']['protocol'])) === false)
			return(false);

		if(isset($this->_info['protocol']['voicemailmailbox']))
		{
			$this->_set_error('voicemail', dwho_i18n::babelfish('user_need_lines_to_have_voicemail'));
			dwho_report::push('error', dwho_i18n::babelfish('user_need_lines_to_have_voicemail'));
			return(false);
		}

		$r = $protocol->delete($this->_info['protocol']['id']);

		if($this->_status === 'delete')
			$this->_return['protocol'] = $r;

		return($r);
	}

	function delete_linefeatures()
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);

		$r = $this->_linefeatures->delete($this->_info['linefeatures']['id']);

		if($this->_status === 'delete')
			$this->_return['linefeatures'] = $r;

		return($r);
	}

	function delete_config()
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);

		// remove device if associated
		if(($device = $this->_device->get($this->_info['linefeatures']['device'],null,true)) === false)
			return(true);
		elseif($this->_device->remove_line($device,$this->_info['linefeatures']['num']) === false)
			return(false);
		elseif ($this->_info['linefeatures']['protocol'] === XIVO_SRE_IPBX_AST_PROTO_SCCP
		&& $this->_sccpdevice->init_device($device['mac'],'') === false)
			return(false);

		return(true);
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
		else if(dwho_issa('linefeatures',$this->_info) === false
		|| is_object($this->_queuemember) === false)
			return(false);

		$where = array();
		$where['usertype'] = 'user';
		$where['category'] = $type;
		$where['userid'] = $this->_info['linefeatures']['iduserfeatures'];

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
				case 'protocol':
					if(isset($this->_origin['protocol']) === false
					|| $this->_origin['protocol'] === false)
						continue;

					$protocol = &$this->_service->get_protocol_module($this->_info['linefeatures']['protocol']);
					$protocol->add_origin($this->_origin['protocol']);
					break;
				case 'linefeatures':
					if(isset($this->_origin['linefeatures']) === true
					&& $this->_origin['linefeatures'] !== false)
						$this->_linefeatures->add_origin($this->_origin['linefeatures']);
					break;
				case 'usermacro':
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
				case 'contextnummember':
					$this->_contextnummember->add_origin();
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

	function enable()
	{
		$r = true;

		$this->_status = 'enable';
		$this->_return = array();

		if(is_object($this->_protocol) === false)
			$r = false;
		else if($this->enable_protocol() === false
		|| $this->enable_linefeatures() === false)
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
		|| $this->disable_linefeatures() === false)
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

	function enable_linefeatures()
	{
		return($this->_enable_disable_linefeatures(false));
	}

	function disable_linefeatures()
	{
		return($this->_enable_disable_linefeatures(true));
	}

	function _enable_disable_linefeatures($disable=false)
	{
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_linefeatures->enable($this->_info['linefeatures']['id']);
		else
			$r = $this->_linefeatures->disable($this->_info['linefeatures']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['linefeatures'] = $r;

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
				case 'linefeatures':
					$this->_enable_disable_linefeatures($disable);
					break;
			}
		}

		return(true);
	}

	function _prepare_import($arr)
	{
		if(dwho_issa('protocol',$arr) === false)
			return(false);

		return($arr);
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

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data)) === false
		|| $this->set_add($arr,$arr['protocol']['protocol']) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}

	function edit_from_json($mergewith=null)
	{
		if(($data = $this->_get_data_from_json()) === false
		|| ($arr = $this->_prepare_import($data)) === false)
			return false;

		if(!is_null($mergewith))
			$arr = $this->array_merge_recursive($mergewith,$arr);

		if($this->set_edit($arr,$arr['protocol']['protocol']) === false
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
