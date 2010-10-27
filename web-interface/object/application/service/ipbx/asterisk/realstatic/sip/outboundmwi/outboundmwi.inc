<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk','realstatic','abstract.inc'),true);

class xivo_application_service_asterisk_realstatic_sip_outboundmwi extends xivo_application_service_asterisk_realstatic_abstract
{
	var $_name		    = 'outboundmwi';
	var $_modulename	= 'staticsip';
	var $_category		= 'general';
	var $_cat_metric	= 0;
	var $_filename		= 'sip.conf';
	var $_var_name		= 'mwi';

	function xivo_application_service_asterisk_realstatic_sip_outboundmwi(&$service)
	{
		return($this->_init(&$service));
	}

	function _load_config()
	{
		return(parent::_load_config(dirname(__FILE__)));
	}

	function get_all($order=null, $limit=null)
	{
		$raw = $this->_realstatic->get_all();
		if (!is_array($raw))
			return false;

		$res = array();
		foreach($raw as $item)
		{
			$res[] = $this->_realstatic->parse_outboundmwi_uri($item['var_val']);
			$res[count($res)-1]['id']  = $item['id'];
			$res[count($res)-1]['uri'] = $item['var_val'];
			$res[count($res)-1]['commented'] = $item['commented'];
		}

		return $res;
	}

	function get_nb()
	{
		return $this->_realstatic->get_nb();
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = false;

		if(($_info = $this->_realstatic->get($id,$disable)) === false)
			return(false);

		$info = $this->_realstatic->parse_outboundmwi_uri($_info['var_val']);
		$info['id']        = $_info['id'];
		$info['uri']       = $_info['var_val'];
		$info['commented'] = $_info['commented'];

		$this->_info = $this->_origin = array();
		$this->_info[$this->_name] = $info;
		$this->_origin[$this->_name] = $this->_realstatic->get_origin();

		return($this->_info[$this->_name]);
	}

	function set_outboundmwi($arr)
	{
		$this->_reset();

		if(is_array($arr) === false)
		{
			$this->_set_result($this->_name,null);
			$this->_set_error($this->_name,'invalid data');
			return(false);
		}
		else if(($rs = $this->chk_values($arr)) === false)
		{
			$rs = $this->get_filter_result();
			$rs['commented'] = false;

			$this->_set_result($this->_name,$rs);
			$this->_set_error($this->_name,'invalid data');
			return(false);
		}
		else if(($res = $this->_realstatic->build_outboundmwi_uri($rs)) === false)
		{
			$rs['commented'] = false;
			$this->_set_result($this->_name,$rs);
			$this->_set_error($this->_name,'invalid data');
			return(false);
		}
		$res['arr']['commented'] = false;

		$this->_set_result($this->_name,$res);

		return(true);
	}

	function add_outboundmwi()
	{
		if(($rs = $this->get_result($this->_name)) === null || $rs === false)
			return($rs);
		else if(isset($rs['str'],$rs['arr']) === false)
			return(false);

		$info = array();
		$info['category'] = $this->_category;
		$info['cat_metric'] = $this->_cat_metric;
		$info['var_name'] = $this->_var_name;
		$info['var_val'] = $rs['str'];

		if(isset($rs['arr']['commented']) === true)
			$info['commented'] = intval((bool) $rs['arr']['commented']);

		return(($this->_return[$this->_name] = $this->_realstatic->add($info)) > 0);
	}

	function edit_outboundmwi($id)
	{
		if(dwho_issa($this->_name,$this->_info) === true)
			$id = $this->_info[$this->_name]['id'];
		else if(($id = dwho_ulongint($id)) === 0)
			return(false);

		if(($rs = $this->get_result($this->_name)) === null)
			return(null);
		elseif(is_array($rs) === false || isset($rs['str'],$rs['arr']) === false)
			return(false);

		$where = array();
		$where['category'] = $this->_category;
		$where['cat_metric'] = $this->_cat_metric;
		$where['var_name'] = $this->_var_name;

		$info = $where;
		$info['var_val'] = $rs['str'];

		if(isset($rs['arr']['commented']) === true)
			$info['commented'] = intval((bool) $rs['arr']['commented']);

		$this->_return[$this->_name] = $this->_realstatic->edit_where($where,$info,null,$id);
		return($this->_return[$this->_name] > 0);
	}

	function delete_outboundmwi($status,$id=0)
	{
		if(dwho_issa($this->_name,$this->_info) === true)
			$id = $this->_info[$this->_name]['id'];
		else if(($id = dwho_ulongint($id)) === 0)
			return(null);

		$r = $this->_realstatic->delete($id);

		if($status === 'delete')
			$this->_return[$this->_name] = $r;

		return($r);
	}

	function _enable_disable_outboundmwi($status,$disable=false,$id=0)
	{
		if(dwho_issa($this->_name,$this->_info) === true)
			$id = $this->_info[$this->_name]['id'];
		else if(($id = dwho_ulongint($id)) === 0)
			return(null);

		if((bool) $disable === false)
			$r = $this->_realstatic->enable($id);
		else
			$r = $this->_realstatic->disable($id);

		if($status === 'enable' || $status === 'disable')
			$this->_return[$this->_name] = $r;

		return($r);
	}

	function enable_outboundmwi($status,$id=0)
	{
		return($this->_enable_disable_outboundmwi($status,false,$id));
	}

	function disable_outboundmwi($status,$id=0)
	{
		return($this->_enable_disable_outboundmwi($status,true,$id));
	}
}

?>
