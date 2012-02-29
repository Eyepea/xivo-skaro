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

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_linefeatures extends xivo_service_asterisk_abstract
{
	var $_dso		= null;
	var $_name		= 'linefeatures';
	var $_filter	= false;
	var $_origin	= false;
	var $_identity	= false;

	function xivo_service_asterisk_linefeatures(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}

	function _prepare($data)
	{
		$data['id'] = (int) $data['id'];
		$data['protocolid'] = (int) $data['protocolid'];
		$data['provisioningid'] = (int) $data['provisioningid'];
		$data['iduserfeatures'] = (int) $data['iduserfeatures'];
		$data['rules_order'] = (int) $data['rules_order'];
		$data['num'] = (int) $data['num'];
		$data['line_num'] = (int) $data['line_num'];
		$data['internal'] = (bool) $data['internal'];
		$data['commented'] = (bool) $data['commented'];
		$data['encryption'] = isset($data['encryption']) ? (bool) $data['encryption'] : false;

		return($data);
	}

	function get_user_masterline($userid=null,$deviceid=null)
	{
		if ($userid === null
		&& $deviceid === null)
			return(false);

		if(($rs = $this->_dso->user_masterline($userid,$deviceid)) === false)
			return(false);

		return($this->_prepare($rs));
	}

	function get_line_provisioniable($provisioningid)
	{
		if(($rs = $this->_dso->get(array('provisioningid' => $provisioningid))) === false)
			return(false);

		if (dwho_has_len($rs['device']))
			return(false);

		return($this->_prepare($rs));
	}

	function get($id,$orig=true,$disable=null)
	{
		$orig = (bool) $orig;
		$origin = $this->_origin;

		if($orig === false)
			$this->_origin = null;

		if(($r = parent::get($id,$disable)) === false
		|| $this->_sre->chk_protocol($r['protocol']) === false)
		{
			$this->_origin = $origin;
			return(false);
		}
		else if($orig === false)
			$this->_origin = $origin;

		return($this->_prepare($r));
	}

	function get_where($arr,$orig=true,$disable=null,$id=null)
	{
		$orig = (bool) $orig;
		$origin = $this->_origin;

		if($orig === false)
			$this->_origin = null;

		if(($r = parent::get_where($arr,$disable,$id)) === false)
		{
			$this->_origin = $origin;
			return(false);
		}
		else if($orig === false)
			$this->_origin = $origin;

		return($r);
	}

	function _mk_provisioning_id($protocol)
	{
		if($this->_chk_exists_cfg('provisioning_id',$protocol) === false)
			return(null);

		$ref = &$this->_conf['provisioning_id'][$protocol];

		$min = $ref['prefix'] * $ref['range'];
		$max = $min + $ref['range'];
		$len = strlen($max)-strlen($ref['prefix']);

		$r = $ref['prefix'].substr(crc32(uniqid(rand(),true)),1,$len);

		if($r > $min && $r < $max && $this->get_primary(array('provisioningid' => $r)) === false)
			return($r);

		return($this->_mk_provisioning_id($protocol));
	}

	function add($arr,$id=0)
	{
		if(is_array($arr) === false
		|| isset($arr['protocol']) === false
		|| ($arr['provisioningid'] = (int) $this->_mk_provisioning_id($arr['protocol'])) === false
		|| $this->_sre->chk_protocol($arr['protocol']) === false)
			return(false);
		else if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);

		if (is_int($arr['num']) === false)
			$arr['num'] = (int) $arr['num'];

		if (is_int($arr['line_num']) === false)
			$arr['line_num'] = (int) $arr['line_num'];

		$arr['ipfrom'] = $_SERVER['SERVER_ADDR'];

		return(parent::add($arr,$id));
	}

	function edit($id,$arr,$provisioning=false,$disable=null)
	{
		if(is_array($arr) === false)
			return(false);
		else if(isset($arr['name']) === true)
			$arr['name'] = strtolower($arr['name']);

		if(isset($arr['protocol']) === true)
		{
			if((bool) $provisioning === true
			&& ($arr['provisioningid'] = $this->_mk_provisioning_id($arr['protocol'])) === false)
				return(false);

			if($this->_sre->chk_protocol($arr['protocol']) === false)
				return(false);
		}

		if (isset($arr['num']) === true)
			$arr['num'] = (int) $arr['num'];
		else
			$arr['num'] = 0;

		if (isset($arr['line_num']) === true)
			$arr['line_num'] = (int) $arr['line_num'];
		else
			$arr['line_num'] = 0;

		$arr['ipfrom'] = $_SERVER['SERVER_ADDR'];

		return(parent::edit($id,$arr,$disable));
	}

	function search($value,$disable=null,$order=null,$limit=null,$number=false)
	{
		if(($list = $this->_dso->search($value,$disable,$order,$limit,$number)) === false)
			return(false);

		$nb = count($list);

		$r = array();

		for($i = 0;$i < $nb;$i++)
			$r[] = $this->_prepare($list[$i]);

		if(isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function get_all_wherein($id,$where)
	{
		if(($list = $this->_dso->get_all_wherein($id,$where)) === false)
			return(false);

		$nb = count($list);
		$list = array_values($list);

		for($i = 0;$i < $nb;$i++)
		{
			$data = &$list[$i];
			$data = $this->_prepare($data);
		}

		return($list);
	}

	function get_all_where($arr,$disable=null,$order=null,$limit=null)
	{
		if(($list = $this->_dso->get_all_where($arr,$disable,$order,$limit)) === false)
			return(false);

		$nb = count($list);
		$list = array_values($list);

		for($i = 0;$i < $nb;$i++)
		{
			$data = &$list[$i];
			$data = $this->_prepare($data);
		}

		return($list);
	}

	function search_number($value,$disable=null,$order=null,$limit=null)
	{
		return($this->search($value,$disable,$order,$limit,true));
	}

	function get_all_except($id=0,$number=false,$order=null,$limit=null)
	{
		if(($id = dwho_ulongint($id)) === 0 && (bool) $number === false)
			return($this->get_all(null,true,$order,$limit));

		if(isset($this->_origin_list) === true)
			$this->_origin_list = false;

		if(($list = $this->_dso->get_all_except($id,$number,$order,$limit)) === false
		|| isset($list[0]) === false)
			return(false);
		else if(isset($this->_origin_list) === true)
			$this->_origin_list = $list;

		return($this->_mk_list_assoc_prepare($list,false,true));
	}

	function get_all_context($disable=null)
	{
		if(($list = $this->_dso->get_all_context($disable)) === false)
			return(false);

		$nb = count($list);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$info = $list[$i];

			$r[$info['context']] = $info['context'];
		}

		if(empty($r) === true)
			$r = false;

		return($r);
	}

	public function disassociate_line($id)
	{
		if($this->get($id) === false)
			return(false);

		$arr = array();
		$arr['iduserfeatures'] = 0;
		$arr['config'] = '';
		$arr['device'] = 0;
		$arr['configregistrar'] = '';
		$arr['number'] = '';

		if($this->edit($id,$arr) === false)
			return(false);

		return(true);
	}

	public function reset_device($iddevice)
	{
		$arr = array();
		$arr['device'] = 0;
		$where = array('device' => (string) $iddevice);

		return(parent::edit_where($where,$arr));
	}
}

?>
