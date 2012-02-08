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

class xivo_application_service_asterisk_ctiagentstatusgroup extends xivo_application_asterisk_abstract
{
	var $_ctiagentstatusgroup = false;
	var $_ctiagentstatus = false;
	var $_ctistatus = false;

	function xivo_application_service_asterisk_ctiagentstatusgroup(&$service,$param=null,$components=true)
	{
		$this->xivo_application_asterisk_abstract(&$service);
		if(($this->_ctiagentstatusgroup = &$this->_service->get_module('ctiagentstatusgroup')) === false
		|| ($this->_ctiagentstatus = &$this->_service->get_module('ctiagentstatus')) === false)
			return(false);
		else if((bool) $components === true)
			$this->load_components();

		return(true);
	}

	function get_agentstatusgroup_list($order=null,$limit=null,$assoc=false)
	{
		if(($rs = $this->_ctiagentstatusgroup->get_all(null,true,$order,$limit)) === false
		|| ($nb = count($rs)) === 0)
		{
			$this->_cnt = $this->_ctiagentstatusgroup->get_cnt();
			return(false);
		}

		$r = $info = array();
		for($i = 0;$i < $nb;$i++)
		{
			$info['ctiagentstatusgroup'] = $rs[$i];
			$r[$info['ctiagentstatusgroup']['id']] = $info;
		}

		if(empty($r) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($r));

		return($r);
	}

	function get_agentstatusgroup_edit()
	{
		return(false);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		$this->_info['agentstatusgroup'] = $this->_ctiagentstatusgroup->get($id);

		if($this->_components === false)
			return($this->_info);

		return($this->_info);
	}

	function get_nb($arr=null,$disable=null)
	{
		return($this->_ctiagentstatusgroup->get_nb($arr,$disable));
	}

	function get_elements()
	{
		$r = array();
		$r['agentstatusgroup'] = $this->_ctiagentstatusgroup->get_element();

		return($r);
	}

	function set_add($arr,$create_agentstatus_tpl=true)
	{
	return($this->_set('add',$arr,$create_agentstatus_tpl));
	}

	function set_edit($arr,$create_agentstatus_tpl=true)
	{
	if(empty($this->_info) === true)
	return(false);

	return($this->_set('edit',$arr,$create_agentstatus_tpl));
	}

	function _set($action,$arr,$create_agentstatus_tpl)
	{
		$this->_reset();

		if(($action !== 'add' && $action !== 'edit') === true
		|| dwho_issa('agentstatusgroup',$arr) === false)
			return(false);

		$this->set_agentstatusgroup($arr['agentstatusgroup']);

		if ($create_agentstatus_tpl)
		{
			$list = array();
			$list[] = array(0,'Logué','#0DFF25');
			$list[] = array(0,'Délogué','#030303');
			$list[] = array(0,'En communication','#FF032D');

			$res = array();
			$data = array();
			for($i=0;$i<count($list);$i++)
			{
				$line = &$list[$i];
				$data['idgroup'] = $line[0];
				$data['name'] = $line[1];
				$data['color'] = $line[2];

				if(($rs = $this->_ctiagentstatus->chk_values($data)) === false)
				{
					$this->_set_error('agentstatus',$this->_ctiagentstatus->get_filter_error());
					continue;
				}

				array_push($res,$rs);
			}

			$this->_set_result('agentstatus',$res);
		}

		return(($this->get_errnb() < 1));
	}

	function set_agentstatusgroup($arr)
	{
		if(is_array($arr) === false)
		{
			$this->_set_result('agentstatusgroup',null);
			$this->_set_error('agentstatusgroup','invalid data');
			return(false);
		}
		else if(($rs = $this->_ctiagentstatusgroup->chk_values($arr)) === false)
		{
			$this->_set_result('agentstatusgroup',$this->_ctiagentstatusgroup->get_filter_result());
			$this->_set_error('agentstatusgroup',$this->_ctiagentstatusgroup->get_filter_error());
			return(false);
		}

		$this->_set_result('agentstatusgroup',$rs);

		return(true);
	}

	function add()
	{
		$r = true;

		$this->_status = 'add';
		$this->_return = array();

		if($this->get_errnb() > 0
		|| ($agentstatusgroupid = $this->add_agentstatusgroup()) === false
		|| $this->add_agentstatus($agentstatusgroupid) === false)
		{
			$r = false;
			if($agentstatusgroupid !== null)
				$this->_reverse_add($agentstatusgroupid);
		}

		$this->_status = '';

		return($r);
	}

	function add_agentstatusgroup()
	{
		if(($rs = $this->get_result('agentstatusgroup')) === null
		|| $rs === false)
			return(false);

		$rs['deletable'] = 1;
		$this->_return['agentstatusgroup'] = $this->_ctiagentstatusgroup->add($rs);
		return($this->_return['agentstatusgroup']);
	}

	function add_agentstatus($agentstatusgroupid)
	{
		if(($rs = $this->get_result('agentstatus')) === null
		|| $rs === false)
			return(false);

		for($i=0;$i<count($rs);$i++)
		{
			$line = &$rs[$i];
			$line['idgroup'] = (int) $agentstatusgroupid;
			if(($this->_return['agentstatus'][] = $this->_ctiagentstatus->add($line)) === false)
				return(false);
		}

		return($this->_return['agentstatus']);
	}

	function _reverse_add($agentstatusgroupid)
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
				case 'agentstatusgroup':
					$this->_ctiagentstatusgroup->delete($val);
					break;
				case 'agentstatus':
					$w = array('idgroup' => $agentstatusgroupid);
					$this->_ctiagentstatus->delete_where($w);
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
		|| $this->edit_agentstatusgroup() === false)
		{
			$r = false;
			$this->_reverse_edit();
		}

		$this->_status = '';

		return($r);
	}

    function edit_agentstatusgroup()
    {
        if(dwho_issa('agentstatusgroup',$this->_info) === false
        || ($rs = $this->get_result('agentstatusgroup')) === null
        || $rs === false)
            return(false);

        return(($this->_return['agentstatusgroup'] = $this->_ctiagentstatusgroup->edit($this->_info['agentstatusgroup']['id'],$rs)));
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
				case 'agentstatusgroup':
					if(isset($this->_origin['agentstatusgroup']) === false
					|| $this->_origin['agentstatusgroup'] === false)
						$this->delete_agentstatusgroup();
					else
						$this->_ctiagentstatusgroup->edit_origin($this->_origin['agentstatusgroup']);
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

		if($this->get_errnb() > 0
		|| $this->delete_agentstatusgroup() === false)
		{
			$r = false;
			$this->_reverse_delete();
		}

		$this->_status = '';

		return($r);
	}

	function delete_agentstatusgroup()
	{
		if(dwho_issa('agentstatusgroup',$this->_info) === false
		|| (string) $this->_info['agentstatusgroup']['id'] === '1')
			return(false);

		$r = $this->_ctiagentstatusgroup->delete($this->_info['agentstatusgroup']['id']);

		if($this->_status === 'delete')
			$this->_return['agentstatusgroup'] = $r;

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
				case 'agentstatusgroup':
                    if(isset($this->_origin['agentstatusgroup']) === true
                    && $this->_origin['agentstatusgroup'] !== false)
                        $this->_ctiagentstatusgroup->add_origin($this->_origin['agentstatusgroup']);
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

		if($this->enable_agentstatusgroup() === false)
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

		if($this->disable_agentstatusgroup() === false)
		{
			$r = false;
			$this->_reverse_enable_disable();
		}

		$this->_status = '';

		return(true);
	}

	function enable_agentstatusgroup()
	{
		return($this->_enable_disable_agentstatusgroup(false));
	}

	function disable_agentstatusgroup()
	{
		return($this->_enable_disable_agentstatusgroup(true));
	}

	function _enable_disable_agentstatusgroup($disable=false)
	{
		if(dwho_issa('agentstatusgroup',$this->_info) === false)
			return(false);
		else if((bool) $disable === false)
			$r = $this->_ctiagentstatusgroup->enable($this->_info['agentstatusgroup']['id']);
		else
			$r = $this->_ctiagentstatusgroup->disable($this->_info['agentstatusgroup']['id']);

		if($this->_status === 'enable' || $this->_status === 'disable')
			$this->_return['agentstatusgroup'] = $r;

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
				case 'agentstatusgroup':
					$this->_enable_disable_agentstatusgroup($disable);
					break;
			}
		}

		return(true);
	}
}

?>
