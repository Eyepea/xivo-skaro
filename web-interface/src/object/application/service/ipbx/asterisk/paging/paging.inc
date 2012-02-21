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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_paging extends xivo_application_asterisk_abstract
{
	var $_dso			= null;
	var $_paging		= false;
	var $_paginguser	= false;

	function xivo_application_service_asterisk_paging(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_paging = &$this->_service->get_module('paging')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function load_components()
	{
		$this->_components = true;

		if(($this->_paginguser = &$this->_service->get_module('paginguser')) === false)
			return(false);

		return(true);
	}

	function get($id,$disable=null,$nocomponents=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['paging'] = $this->_paging->get($id,$disable)) === false)
			return(false);

		$this->_origin['paging'] = $this->_paging->get_origin();
		
		if($this->_components === false)
			return($this->_info);

		if(dwho_ak('paginguser',$nocomponents,true) === false)
			$this->_get_paginguser();

		if(dwho_ak('pagingcaller',$nocomponents,true) === false)
			$this->_get_pagingcaller();

		return($this->_info);
	}
	
	function _get_paginguser()
	{
		$this->_info['paginguser'] = false;
		$this->_origin['paginguser'] = false;

		if(($this->_info['paginguser'] = $this->_paginguser->get_list_paginguser($this->_info['paging']['id'])) !== false)
			$this->_origin['paginguser'] = $this->_paginguser->get_origin_list();

		return($this->_info['paginguser']);
	}
	
	function _get_pagingcaller()
	{
		$this->_info['pagingcaller'] = false;
		$this->_origin['pagingcaller'] = false;

		if(($this->_info['pagingcaller'] = $this->_paginguser->get_list_paginguser($this->_info['paging']['id'],true)) !== false)
			$this->_origin['pagingcaller'] = $this->_paginguser->get_origin_list();

		return($this->_info['pagingcaller']);
	}

	function get_elements()
	{
		$r = array();
		$r['paging'] = $this->_paging->get_element();

		return($r);
	}

	function get_pagings_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_pagings('search',$search,$disable,$order,$limit,$assoc));
	}

	function get_pagings_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_pagings('list',null,$disable,$order,$limit,$assoc));
	}

	function _get_pagings($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_dso->get_all($disable,$order,$limit);
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = $identity = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$rs[$i]['id']] = $rs[$i];

			$ref = &$r[$rs[$i]['id']];

			$ref['commented'] = (bool) $ref['commented'];
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
		|| dwho_issa('paging',$arr) === false)
			return(false);

		$this->set_paging($arr['paging']);

		if(dwho_issa('paginguser',$arr) === true)
			$this->set_paginguser($arr['paginguser']);

		if(dwho_issa('pagingcaller',$arr) === true)
			$this->set_pagingcaller($arr['pagingcaller']);

		return(($this->get_errnb() < 1));
	}

	function set_paging($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('paging',null);
			$this->_set_error('paging','invalid data');
			return(false);
		}

		$arr['commented'] = false;

		if(($rs = $this->_paging->chk_values($arr)) === false)
		{
			$this->_set_result('paging',$this->_paging->get_filter_result());
			$this->_set_error('paging',$this->_paging->get_filter_error());
			return(false);
		}

		$this->_set_result('paging',$rs);

		return(true);
	}
	
	function set_paginguser($arr)
	{
		if(is_array($arr) === false || ($nb = count($arr)) === 0)
		{
			$this->_set_result('paginguser',null);
			$this->_set_error('paginguser','invalid data');
			return(false);
		}
		else if($this->_paginguser === false)
		{
			$this->_set_result('paginguser',false);
			return(false);
		}

		$arr = array_values($arr);

		$info = array();
		$info['pagingid'] = 0;
		$info['caller'] = 0;

		$reslist = $tmp = array();

		for($i = 0,$j = 0;$i < $nb;$i++)
		{
			$info['userfeaturesid'] = $arr[$j];
			if(($rs = $this->_paginguser->chk_values($info)) === false)
				continue;

			$reslist[$j++] = $rs;
		}

		if(isset($reslist[0]) === false)
		{
			$this->_set_result('paginguser',false);
			return(false);
		}

		$this->_set_result('paginguser',$reslist);
		return(true);
	}
	
	function set_pagingcaller($arr)
	{
		if(is_array($arr) === false || ($nb = count($arr)) === 0)
		{
			$this->_set_result('pagingcaller',null);
			$this->_set_error('pagingcaller','invalid data');
			return(false);
		}
		else if($this->_paginguser === false)
		{
			$this->_set_result('pagingcaller',false);
			return(false);
		}

		$arr = array_values($arr);

		$info = array();
		$info['pagingid'] = 0;
		$info['caller'] = 1;

		$reslist = $tmp = array();

		for($i = 0,$j = 0;$i < $nb;$i++)
		{
			$info['userfeaturesid'] = $arr[$j];
			if(($rs = $this->_paginguser->chk_values($info)) === false)
				continue;

			$reslist[$j++] = $rs;
		}

		if(isset($reslist[0]) === false)
		{
			$this->_set_result('pagingcaller',false);
			return(false);
		}

		$this->_set_result('pagingcaller',$reslist);
		return(true);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$pagingid = null;

		if($this->get_errnb() > 0
		|| ($pagingid = $this->add_paging()) === false
		|| $this->add_paginguser($pagingid) === false
		|| $this->add_pagingcaller($pagingid) === false)
		{
			$r = false;
			if($pagingid !== null)
				$this->_reverse_add($pagingid);
		}

		$this->_status = '';

		return($r);
	}

	function add_paging()
	{
		if(($rs = $this->get_result('paging')) === null
		|| $rs === false)
			return(false);

		return(($this->_return['paging'] = $this->_paging->add($rs)));
	}

	function add_paginguser($pagingid)
	{
		if(($rs = $this->get_result('paginguser')) === null)
			return($rs);
		
		if(($pagingid = dwho_ulongint($pagingid)) === 0
		|| $rs === false)
			return(false);

		$id = array();

		$nb = count($rs);

		$this->_return['paginguser'] = array();

		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['pagingid'] = $pagingid;

			$id['pagingid'] = $pagingid;

			if($this->_paginguser->add($rs[$i]) === false)
				return(false);

			$this->_return['paginguser'][] = $id;
		}

		if(isset($this->_return['paginguser'][0]) === false)
		{
			$this->_return['paginguser'] = false;
			return(false);
		}

		return(true);
	}

	function add_pagingcaller($pagingid)
	{
		if(($rs = $this->get_result('pagingcaller')) === null)
			return($rs);
			
		if(($pagingid = dwho_ulongint($pagingid)) === 0
		|| $rs === false)
			return(false);

		$id = array();

		$nb = count($rs);

		$this->_return['pagingcaller'] = array();

		for($i = 0;$i < $nb;$i++)
		{
			$rs[$i]['pagingid'] = $pagingid;

			$id['pagingid'] = $pagingid;

			if($this->_paginguser->add($rs[$i]) === false)
				return(false);

			$this->_return['pagingcaller'][] = $id;
		}

		if(isset($this->_return['pagingcaller'][0]) === false)
		{
			$this->_return['pagingcaller'] = false;
			return(false);
		}

		return(true);
	}

	function _reverse_add($pagingid)
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| ($pagingid = dwho_ulongint($pagingid)) === 0
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'paging':
					$this->_paging->delete($pagingid);
					break;
				case 'pagingcaller':
				case 'paginguser':
					$this->_paginguser->delete_where(array('pagingid' => $pagingid));
					break;
			}
		}

		return(true);
	}

	function edit()
	{
		$r = true;

		$this->_status = 'edit';
		$this->_return = array();
		
		if($this->get_errnb() > 0
		|| $this->edit_paging() === false
		|| $this->edit_paginguser() === false
		|| $this->edit_pagingcaller() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	function edit_paging()
	{
		if(dwho_issa('paging',$this->_info) === false
		|| ($rs = $this->get_result('paging')) === null
		|| $rs === false)
			return(false);

		$rs['commented'] = $this->_info['paging']['commented'];

		return(($this->_return['paging'] = $this->_paging->edit($this->_info['paging']['id'],$rs)));
	}

	function edit_paginguser()
	{
		if(dwho_issa('paging',$this->_info) === false)
			return(false);

		$this->_return['paginguser'] = $this->delete_paginguser();

		return($this->add_paginguser($this->_info['paging']['id']));
	}

	function edit_pagingcaller()
	{
		if(dwho_issa('paging',$this->_info) === false)
			return(false);

		$this->_return['pagingcaller'] = $this->delete_pagingcaller();

		return($this->add_pagingcaller($this->_info['paging']['id']));
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
				case 'paging':
					if(isset($this->_origin['paging']) === false
					|| $this->_origin['paging'] === false)
						$this->delete_paging();
					else
						$this->_paging->edit_origin($this->_origin['paging']);
					break;
				case 'paginguser':
					$this->delete_paginguser();
					if(isset($this->_origin['paginguser']) === true
					&& $this->_origin['paginguser'] !== false)
						$this->_paginguser->add_origin_list($this->_origin['paginguser']);
					break;
				case 'pagingcaller':
					$this->delete_pagingcaller();
					if(isset($this->_origin['pagingcaller']) === true
					&& $this->_origin['pagingcaller'] !== false)
						$this->_paginguser->add_origin_list($this->_origin['pagingcaller']);
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

		if($this->delete_paging() === false
		|| $this->delete_paginguser() === false
		|| $this->delete_pagingcaller() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	function delete_paging()
	{
		if(dwho_issa('paging',$this->_info) === false)
			return(false);

		$r = $this->_paging->delete($this->_info['paging']['id']);

		if($this->_status === 'delete')
			$this->_return['paging'] = $r;

		return($r);
	}

	function delete_paginguser()
	{
		if(dwho_issa('paginguser',$this->_info) === false)
			return(null);
		else if(dwho_issa('paging',$this->_info) === false)
			return(false);
			
		$w = array();
		$w['pagingid'] = $this->_info['paging']['id'];
		$w['caller'] = 0;

		$r = $this->_paginguser->delete_where($w);

		if($this->_status === 'delete')
			$this->_return['paginguser'] = $r;

		return($r);
	}
	
	function delete_pagingcaller()
	{
		if(dwho_issa('paginguser',$this->_info) === false)
			return(null);
		else if(dwho_issa('paging',$this->_info) === false)
			return(false);
			
		$w = array();
		$w['pagingid'] = $this->_info['paging']['id'];
		$w['caller'] = 1;

		$r = $this->_paginguser->delete_where($w);

		if($this->_status === 'delete')
			$this->_return['paginguser'] = $r;

		return($r);
	}

	function _reverse_delete()
	{
		if($this->_status !== 'delete'
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'paging':
					if(isset($this->_origin['paging']) === true
					&& $this->_origin['paging'] !== false)
						$this->_paging->add_origin($this->_origin['paging']);
					break;
				case 'paginguser':
					if(isset($this->_origin['paginguser']) === true
					&& $this->_origin['paginguser'] !== false)
						$this->_paginguser->add_origin_list($this->_origin['paginguser']);
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

		if($this->enable_paging() === false
		|| $this->enable_pagingmacro() === false)
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

		if($this->disable_paging() === false
		|| $this->disable_pagingmacro() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return($r);
	}

	function enable_paging()
	{
		return($this->_enable_disable_paging(false));
	}

	function disable_paging()
	{
		return($this->_enable_disable_paging(true));
	}

	function _enable_disable_paging($disable=false)
	{
		if(dwho_issa('paging',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_paging->enable($this->_info['paging']['id']);
		else
			$r = $this->_paging->disable($this->_info['paging']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['paging'] = $r;

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
				case 'paging':
					$this->_enable_disable_paging($disable);
					break;
			}
		}

		return(true);
	}

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_add($data) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}

	function edit_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_edit($data) === false
		|| $this->edit() === false)
			return(false);

		return(true);
	}
}

?>
