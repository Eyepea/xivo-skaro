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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_queuepenalty extends xivo_application_asterisk_abstract
{
	var $_queuepenaltys		   = false;
	var $_queuepenaltychange = false;

	function xivo_application_service_asterisk_queuepenalty(&$service,&$dso,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_queuepenalty = &$this->_service->get_module('queuepenalty')) === false)
			return(false);
		else if(($this->_queuepenaltychange = &$this->_service->get_module('queuepenaltychange')) === false)
			return(false);

		return(true);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info['queuepenalty'] = $this->_queuepenalty->get($id,$disable)) === false)
			return(false);
		
		$this->_info['changes'] = $this->_queuepenaltychange->get_all_where(array('queuepenalty_id' => $id));

		$this->_origin['queuepenalty'] = $this->_queuepenalty->get_origin();

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_elements()
	{
		$r = array();
		$r['queuepenalty'] = $this->_queuepenalty->get_element();

		return($r);
	}

	function get_queuepenalty_search($search,$disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_queuepenalty('search',$search,$disable,$order,$limit,$assoc));
	}

	function get_queuepenalty_list($disable=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_queuepenalty('list',null,$disable,$order,$limit,$assoc));
	}

	function _get_queuepenalty($action,$search='',$disable=null,$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_dso->search($search,$disable,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_queuepenalty->get_all();
		}

		$this->_cnt = $this->_dso->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		$r = array();

		for($i = 0;$i < $nb;$i++)
		{
			$r[$rs[$i]['id']] = $rs[$i];

			$ref = &$r[$rs[$i]['id']];

			$queuepenalty = array();
			$queuepenalty['name'] = $ref['name'];
			$ref = array_merge($ref,$this->_queuepenalty->_prepare($queuepenalty));

			$ref['description'] = $ref['description'];
			$ref['commented']   = (bool) $ref['commented'];

			$arr = array();
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	function get_result_for_display()
	{
		$r = $this->get_result();

		if(is_array($r) === false)
			$r = array();

		if(dwho_issa('queuepenalty',$r) === false)
			$r['queuepenalty'] = array();

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
		|| dwho_issa('queuepenalty',$arr) === false)
			return(false);

		$this->set_queuepenalty($arr['queuepenalty']);
		$this->set_queuepenalty_changes($arr['changes']);

		return(($this->get_errnb() < 1));
	}

	function set_queuepenalty($arr)
	{
		$r = true;
		$arr['commented'] = false;

		if(($rs = $this->_queuepenalty->chk_values($arr)) === false)
		{
			$r = false;
			$rs = $this->_queuepenalty->get_filter_result();
			$this->_set_error('queuepenalty', $this->_queuepenalty->get_filter_error());
		}

		$this->_set_result('queuepenalty',$rs);

		return($r);
	}

	function set_queuepenalty_changes($arr)
	{
		$errs    = array();
		$changes = array();
		foreach($arr as $rs)
		{
			if(($rs = $this->_queuepenaltychange->chk_values($rs)) === false)
				$errs[] = $this->_queuepenaltychange->get_filter_error();

			$changes[] = $rs;
		}

		$this->_set_result('changes',$changes);
		return true;
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();
		$queuepenaltyid = null;

		if($this->get_errnb() > 0
		|| ($queuepenaltyid = $this->add_queuepenalty()) === false
		|| $this->add_queuepenalty_changes($queuepenaltyid) === false)
		{
			$r = false;

			if($queuepenaltyid !== null)
				$this->_reverse_add($queuepenaltyid);
		}

		$this->_status = '';

		return($r);
	}

	function add_queuepenalty()
	{
		if(($rs = $this->get_result('queuepenalty')) === null
		|| $rs === false)
			return(false);

		return(($this->_return['queuepenalty'] = $this->_queuepenalty->add($rs)));
	}

	function add_queuepenalty_changes($queuepenaltyid)
	{
		foreach($this->get_result('changes') as $rs)
		{
			$rs['queuepenalty_id'] = $queuepenaltyid;
			$ret = $this->_queuepenaltychange->add($rs);
		}

		return true;
	}

	//TODO
	function _reverse_add($queuepenaltyid)
	{
		if($this->get_errnb() > 0
		|| $this->_status !== 'add'
		|| ($queuepenaltyid = dwho_ulongint($queuepenaltyid)) === 0
		|| is_array($this->_return) === false
		|| empty($this->_return) === true)
			return(false);

		foreach($this->_return as $key => $val)
		{
			if($val === false)
				continue;

			switch($key)
			{
				case 'queuepenalty':
					$this->_queuepenalty->delete($queuepenaltyid);
					break;
				case 'dialaction':
					$this->_dialaction->reverse_add();
					break;
				case 'contextmember':
					$this->_contextmember->reverse_add();
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
		|| ($queuepenaltyid = $this->edit_queuepenalty()) === false
		|| $this->edit_queuepenalty_changes($queuepenaltyid) === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

	function edit_queuepenalty()
	{
		if(dwho_issa('queuepenalty',$this->_info) === false
		|| ($rs = $this->get_result('queuepenalty')) === null
		|| $rs === false)
			return(false);

		$rs['commented'] = $this->_info['queuepenalty']['commented'];
		$this->_return['queuepenalty'] = $this->_queuepenalty->edit($this->_info['queuepenalty']['id'], $rs);

		return($this->_return['queuepenalty']);
	}


	function edit_queuepenalty_changes($queuepenaltyid)
	{
		$this->_queuepenaltychange->delete_where(array('queuepenalty_id' => $queuepenaltyid));
		foreach($this->get_result('changes') as $rs)
		{
			$rs['queuepenalty_id'] = $queuepenaltyid;
			$ret = $this->_queuepenaltychange->add($rs);
		}

		return true;
	}

	// TODO
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
				case 'queuepenalty':
					if(isset($this->_origin['queuepenalty']) === false
					|| $this->_origin['queuepenalty'] === false)
						$this->delete_queuepenalty();
					else
						$this->_queuepenalty->edit_origin($this->_origin['queuepenalty']);
					break;
				case 'dialaction':
					$this->_dialaction->reverse_edit($this->_status);
					break;
				case 'contextmember':
					$this->_contextmember->reverse_edit($this->_status);
					break;
			}
		}

		return(true);
	}

	function delete($id)
	{
		$r = true;

		$this->_status = 'delete';
		$this->_return = array();
		$this->_info['queuepenalty'] = array('id' => $id);

		if($this->delete_queuepenalty() === false
		|| $this->delete_queuepenalty_changes() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';
		return($r);
	}

	function delete_queuepenalty()
	{
		if(dwho_issa('queuepenalty',$this->_info) === false)
			return(false);

		$r = $this->_queuepenalty->delete($this->_info['queuepenalty']['id']);

		if($this->_status === 'delete')
			$this->_return['queuepenalty'] = $r;

		return($r);
	}

	function delete_queuepenalty_changes()
	{
		$r = $this->_queuepenaltychange->delete_where(array('queuepenalty_id' => $this->_info['queuepenalty']['id']));
		return $r;
	}

	function enable($id)
	{
		$r = true;
		$this->_status = 'enable';
		$this->_return = array();
		$this->_info['queuepenalty'] = array('id' => $id);

		if($this->enable_queuepenalty() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function disable($id)
	{
		$r = true;
		$this->_status = 'disable';
		$this->_return = array();
		$this->_info['queuepenalty'] = array('id' => $id);

		if($this->disable_queuepenalty() === false)
			$r = false;

		$this->_status = '';

		return($r);
	}

	function enable_queuepenalty()
	{
		return($this->_enable_disable_queuepenalty(false));
	}

	function disable_queuepenalty()
	{
		return($this->_enable_disable_queuepenalty(true));
	}

	function _enable_disable_queuepenalty($disable=false)
	{
		if(dwho_issa('queuepenalty',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_queuepenalty->enable($this->_info['queuepenalty']['id']);
		else
			$r = $this->_queuepenalty->disable($this->_info['queuepenalty']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['queuepenalty'] = $r;

		return($r);
	}

	function add_from_json()
	{
		if(($data = $this->_get_data_from_json()) === false
		|| $this->set_add($data) === false
		|| $this->add() === false)
			return(false);

		return(true);
	}
}
?>
