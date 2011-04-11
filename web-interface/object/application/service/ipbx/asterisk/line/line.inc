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

class xivo_application_service_asterisk_line extends xivo_application_asterisk_abstract
{
	var $_dso				= null;
	var	$_contextlist		= false;
	var $_linefeatures 		= false;
	var $_protocolname		= false;
	var $_extenumbers		= false;
	var $_extensions		= false;
	var $_contextnummember	= false;
	var $_protocol			= false;
	var $_conf				= array();
	var $_param				= array('internal'	=> false);

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

		if(($this->_servicesgroup = &$this->_service->get_application('servicesgroup')) === false
		|| ($this->_servicesgroup_user = &$this->_service->get_module('servicesgroup_user')) === false
		|| ($this->_extensions = &$this->_service->get_module('extensions')) === false
		|| ($this->_extenumbers = $this->get_abstract('extenumbers',array('type' => 'user'))) === false
		|| ($this->_contextnummember = $this->get_abstract('contextnummember',array('type' => 'user'))) === false)
			return(false);

		return(true);
	}

	public  function _reset()
	{
		$this->_protocolname = false;

		return(parent::_reset());
	}

	/**
	 * NOTE: internal can take 3 values:
	 *	- false : don't search in internal users
	 *	- true  : search ONLY in internal users
	 *	- null  : search in BOTH internal and non-internal users
	 */
	public function get($id,$disable=null,$internal=false,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['linefeatures'] = $this->_linefeatures->get($id)) === false)
			return(false);

		if($this->_info['linefeatures'] === false
		|| ($this->_protocol = &$this->_service->get_protocol_module($this->_info['linefeatures']['protocol'])) === false
		|| ($this->_info['protocol'] = $this->_protocol->get($this->_info['linefeatures']['protocolid'],$disable)) === false)
		{
			$this->_linefeatures->set_dso_param('internal',$this->_param['internal']);
			return(false);
		}

		$this->_linefeatures->set_dso_param('internal',$this->_param['internal']);

		$this->_origin['protocol'] = $this->_protocol->get_origin();
		$this->_origin['linefeatures'] = $this->_linefeatures->get_origin();

		if($this->_components === false)
			return($this->_info);

		if(dwho_ak('usermacro',$nocomponents,true) === false)
			$this->_get_usermacro();

		if(dwho_ak('hints',$nocomponents,true) === false)
			$this->_get_hints();

		if(dwho_ak('extenumbers',$nocomponents,true) === false)
			$this->_get_extenumbers($this->_info['linefeatures']['id']);

		if(dwho_ak('contextnummember',$nocomponents,true) === false)
			$this->_get_contextnummember($this->_info['linefeatures']['id']);

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

	function _get_hints()
	{
		$this->_info['hints'] = false;
		$this->_origin['hints'] = false;

		if(isset($this->_info['linefeatures']['context']) === true
		&& ($this->_info['hints'] = $this->_extensions->get_hints($this->_info['linefeatures']['name'],
									  $this->_info['linefeatures']['protocol'],
									  $this->_info['linefeatures']['number'])) !== false)
			$this->_origin['hints'] = $this->_extensions->get_origin();

		return($this->_info['hints']);
	}

	function _get_ipbx_infos()
	{
		$protocols = array(
			'sip'  => 'sip show peer',
			'iax'  => 'iax2 show peer',
			'sccp' => 'sccp show line'
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
					$item = explode(':',$line);
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
		$r['servicesgroup'] = $this->_servicesgroup->get_element();

		return($r);
	}

	public function get_all_context()
	{
		if(($r = $this->_linefeatures->get_all_context()) !== false)
			ksort($r);

		return($r);
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
	private function _get_lines($action,$protocols=null,$disable=null,$search='',$context='',$order=null,$limit=null,$assoc=false,$initialized=null,$free=null,$internal=null)
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
					#$sccp = dwho_array_startswith_key($ref,'sccpline.',true);
					$sccp = dwho_array_startswith_key($ref,'usersccp.',true);
					$sccp['initialized'] = true;
					$sccp['identity'] = strtoupper($sccp['protocol']).'/'.$sccp['name'];
					$r[$linefeatures['id']] = array_merge($sccp,$linefeatures);
					break;
				case XIVO_SRE_IPBX_AST_PROTO_CUSTOM:
					$custom = dwho_array_startswith_key($ref,'usercustom.',true);
					$custom['initialized'] = true;
					$custom['identity'] = strtoupper(XIVO_SRE_IPBX_AST_PROTO_CUSTOM).'/'.$custom['interface'];
					$r[$linefeatures['id']] = array_merge($custom,$linefeatures);
					break;
				default:
					$this->_cnt = 0;
					return(false);
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

		if(isset($arr['protocol']['callerid']) === true)
			$arr['protocol']['callerid'] = $this->_service->mk_callerid($arr['protocol']['callerid']);
		elseif(isset($arr['linefeatures']['callerid']) === true)
			$arr['protocol']['callerid'] = $this->_service->mk_callerid($arr['linefeatures']['callerid']);

		$this->set_protocol($arr['protocol'],$protocolname);

		if($protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			$name = $this->get_result_var('protocol','interface');
		else
			$name = $this->get_result_var('protocol','name');

		$context = $this->get_result_var('protocol','context');

		$arr['linefeatures']['protocol'] = $protocolname;
		$arr['linefeatures']['protocolid'] = 0;
		$arr['linefeatures']['name'] = $name;
		$arr['linefeatures']['context'] = $context;
		$arr['linefeatures']['iduserfeatures'] = 0;

		if (dwho_issa('linefeatures',$arr) === false
		&& $this->get_errnb() === 0)
		{
			$this->set_linefeatures($action,$arr['linefeatures']);
			return(true);
		}

		if (dwho_issa('userfeatures',$arr) === true)
		{
			if (isset($arr['userfeatures']['id']) === true)
				$arr['linefeatures']['iduserfeatures'] = (int) $arr['userfeatures']['id'];

			$simultcalls = (int) $arr['userfeatures']['simultcalls'];
			$musiconhold = (string) $arr['userfeatures']['musiconhold'];

			if($protocolname === XIVO_SRE_IPBX_AST_PROTO_SIP)
				$protocol['call-limit'] = (2 * $simultcalls);

			if($protocolname == 'sccp')
			{
				if(array_key_exists('musiconhold',$userfeatures))
					$protocol['musicclass'] = $userfeatures['musiconhold'];
			}

			if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SIP)
				$this->_set_result_var('protocol','call-limit',(2 * $simultcalls));

			if($this->_protocolname !== XIVO_SRE_IPBX_AST_PROTO_CUSTOM
			&& dwho_has_len($musiconhold) === true)
				$this->_set_result_var('protocol','mohsuggest',$musiconhold);
		}

		$this->set_linefeatures($action,$arr['linefeatures']);

		$this->_extenumbers->_reset();
		$this->_contextnummember->_reset();

		$number = (string) $this->get_result_var('linefeatures','number');

		$numhaslen = dwho_has_len($number);

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
/*
			if(dwho_issa('group',$arr) === true
			&& dwho_issa('group-select',$arr) === true
			&& $this->set_groupmember($arr['group'],
						  $arr['group-select'],
						  $name,
						  $context,
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
*/
			if((bool) $chkcontext === true)
				$this->set_contextnummember($context,$number);

			if(($rsusermacro = $this->chk_macro('usermacro',
							    $number,
							    $this->_mk_usermacro_appdata(0),
							    $context)) !== false)
				$this->_set_result('usermacro',$rsusermacro);

			$this->set_extenumbers($action,$number,$context);

			$callerid = (string) $this->get_result_var('protocol','callerid');
			$callerid = $this->_service->mk_callerid($callerid, '', $protocolname);
			$this->_set_result_var('protocol','callerid',$callerid);

			$enablehint = (bool) $this->get_result_var('userfeatures','enablehint') === false;

			if(($hints = $this->set_hints($action,$name,$protocolname,$number,$enablehint)) === false)
				$this->_set_error('hints');

			$this->_set_result('hints',$hints);
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

		$this->_set_result('linefeatures',$rs);

		return(true);
	}

	function _set_usermacro($action,$iduserfeatures)
	{
		$rs = false;

		if(($iduserfeatures = dwho_ulongint($iduserfeatures)) === 0
		|| ($rs = $this->get_result('usermacro')) === null
		|| $rs === false)
			return($rs);
		else if(($rsmacro = $this->set_macro($action,
						     'usermacro',
						     $rs['exten'],
						     $this->_mk_usermacro_appdata($iduserfeatures),
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

	function _mk_usermacro_appdata($iduserfeatures,$timeout='')
	{
		$arr = array();
		$arr['appdata'][0] = XIVO_SRE_IPBX_AST_USER_MACRO;
		$arr['appdata'][1] = dwho_ulongint($iduserfeatures);
		$arr['appdata'][2] = dwho_has_len($timeout) === true ? dwho_ufloat($timeout) : '';
		$arr['appdata'][3] = $this->_result['protocol']['language'];

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
		|| ($linefeaturesid = $this->add_linefeatures($protocolid)) === false)
		{
			$r = false;
			if($linefeaturesid !== null)
				$this->_reverse_add();
		}

		if (((int) $iduserfeatures = $this->get_result_var('linefeatures','iduserfeatures')) !== 0
		&& is_null($iduserfeatures) === false
		&& dwho_has_len($this->get_result_var('linefeatures','number')) === true)
		{
			if($this->update_protocol_setvar($protocolid,$iduserfeatures) === false
			|| $this->add_usermacro($iduserfeatures) === false
			|| $this->add_hints() === false
			|| $this->add_extenumbers($linefeaturesid) === false
			|| $this->add_contextnummember($linefeaturesid) === false)
			{
				$r = false;
				if($linefeaturesid !== null)
					$this->_reverse_add();
			}
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

	function add_linefeatures($protocolid)
	{
		if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($rs = $this->get_result('linefeatures')) === null
		|| $rs === false)
			return(false);

		$rs['protocolid'] = (int) $protocolid;

		$this->_return['linefeatures'] = $this->_linefeatures->add($rs);

		if (isset($rs['servicesgroup_id']) === true
		&& empty($rs['servicesgroup_id']) === false)
		{
			$arr = array();
			$arr['servicesgroup_id'] = (int) $rs['servicesgroup_id'];
			$arr['linefeatures_id'] = (int) $this->_return['linefeatures'];
			$this->_servicesgroup_user->add($arr);
		}
		return($this->_return['linefeatures']);
	}

	function update_protocol_setvar($protocolid,$iduserfeatures)
	{
		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
			return(null);
		else if(($protocolid = dwho_ulongint($protocolid)) === 0
		|| ($iduserfeatures = dwho_ulongint($iduserfeatures)) === 0
		|| ($protocol = &$this->_service->get_protocol_module($this->_protocolname)) === false)
			return(false);

		$val = array();
		$val['setvar'] = 'XIVO_USERID='.$iduserfeatures;

		return($protocol->edit($protocolid,$val));
	}

	function add_usermacro($iduserfeatures)
	{
		if(($rs = $this->_set_usermacro('add',$iduserfeatures)) !== true)
			return($rs);

		return(parent::add_macro('usermacro'));
	}

	function add_hints()
	{
		if(($rs = $this->get_result('hints')) === null || $rs === false)
			return($rs);

		return(($this->_return['hints'] = $this->_extensions->add_hints($rs)));
	}

	function add_groupmember($linefeaturesid)
	{
		return($this->_add_member_type('group',$linefeaturesid));
	}

	function add_queuemember($linefeaturesid)
	{
		return($this->_add_member_type('queue',$linefeaturesid));
	}

	function _add_member_type($type,$linefeaturesid)
	{
		if(($type !== 'group' && $type !== 'queue') === true
		|| ($linefeaturesid = dwho_ulongint($linefeaturesid)) === 0)
			return(false);

		$key = $type.'member';

		if(($rs = $this->get_result($key)) === null || $rs === false)
			return($rs);

		$ret = $this->_return[$key] = array();

		$nb = count($rs);
		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['userid'] = $linefeaturesid;
			if($type == 'queue')
			{ $rs[$i]['skills'] = $linefeaturesid; }

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
				case 'hints':
					$this->_extensions->delete_hints($val);
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

		if ($this->get_result('linefeatures') !== null)
		{				
			if($this->edit_linefeatures($protocolret) === false)
			{
				$this->edit_origin_protocol($protocolret);
				$this->_status = '';
				return(false);
			}
			else if($this->_info['linefeatures']['iduserfeatures'] !== 0)
			{
				$iduserfeatures = $this->_info['linefeatures']['iduserfeatures'];

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
						$this->delete_hints();
					}
					else if ($this->edit_usermacro($iduserfeatures) === false
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
						if($this->_info['linefeatures']['protocol'] === XIVO_SRE_IPBX_AST_PROTO_CUSTOM)
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
				else if($this->add_usermacro($iduserfeatures) === false
				|| $this->add_extenumbers($this->_info['linefeatures']['id']) === false
				|| ($this->_protocolname !== XIVO_SRE_IPBX_AST_PROTO_CUSTOM
				   && $this->add_hints() === false) === true)
				{
					$this->_reverse_edit($protocolret);
					$this->_status = '';
					return(false);
				}
			}

			if($this->edit_contextnummember() === false)
			#|| $this->edit_groupmember() === false
			#|| $this->edit_queuemember() === false)
			{
				$this->_reverse_edit($protocolret);
				$this->_status = '';
				return(false);
			}

		}

		if($this->_protocolname === XIVO_SRE_IPBX_AST_PROTO_SCCP)
			$this->_service->discuss('sccp reload');

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
			{	$this->_return['protocol'] = $ret; return false; }

			return(($this->_return['protocol'] = $ret));
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

		if (isset($rs['servicesgroup_id']) === true
		&& empty($rs['servicesgroup_id']) === false)
		{
			$arr = array();
			$arr['servicesgroup_id'] = (int) $rs['servicesgroup_id'];
			$arr['linefeatures_id'] = (int) $this->_info['linefeatures']['id'];
			if ($this->_servicesgroup_user->get_nb($arr) === 0)
				$this->_servicesgroup_user->add($arr);
			else
				$this->_servicesgroup_user->edit($arr['servicesgroup_id'],$arr);
		}

		return(($this->_return['linefeatures'] = $this->_linefeatures->edit($this->_info['linefeatures']['id'],
										    $rs,
										    $provisioning)));
	}

	function edit_usermacro($iduserfeatures)
	{
		if(($rs = $this->_set_usermacro('edit',$iduserfeatures)) !== true)
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
		if(dwho_issa('linefeatures',$this->_info) === false)
			return(false);
		else if(dwho_issa('groupmember',$this->_info) === false)
			return($this->add_groupmember($this->_info['linefeatures']['id']));

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
			return($this->add_queuemember($this->_info['linefeatures']['id']));

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
			$rs[$i]['userid'] = $this->_info['linefeatures']['id'];
			if($type == 'queue')
			{ $rs[$i]['skills'] = $this->_info['linefeatures']['id']; }

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
				case 'contextnummember':
					$this->_contextnummember->reverse_edit($this->_status);
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
		|| $this->delete_linefeatures() === false
		|| $this->delete_macro('usermacro') === false
		|| $this->delete_hints() === false
		|| $this->delete_extenumbers() === false
		#|| $this->delete_groupmember() === false
		#|| $this->delete_queuemember() === false
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
		else if(dwho_issa('linefeatures',$this->_info) === false
		|| is_object($this->_queuemember) === false)
			return(false);

		$where = array();
		$where['usertype'] = 'user';
		$where['category'] = $type;
		$where['userid'] = $this->_info['linefeatures']['id'];

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
			//$this->_info['linefeatures'] = array('id' => $userid);
			$this->_info['linefeatures'] = $this->_linefeatures->get($userid);
			$this->_get_autoprov();
			if(is_null($this->_info['autoprov']['macaddr']))
				continue;

			$cmd = array(
				'from'           => 'webi',
				'idlinefeatures' => $userid,
				'proto'          => $this->_info['linefeatures']['protocol'],
				'macaddr'        => $this->_info['autoprov']['macaddr'],
				'actions'        => $reboot?'yes':'no'
			);

			$this->_autoprov->notification($cmd, 'prov');
		}
	}
}

?>
