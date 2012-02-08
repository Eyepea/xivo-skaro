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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','xivo.inc'),true);

class xivo_application_xivo_object_ha extends xivo_application_xivo_object_abstract
{
	var $_sysconfd	    = false;
	var $_ha_svc        = false;
	var $_cnodes_svc    = false;
	var $_service_svc   = false;

	function xivo_application_xivo_object_ha(&$xobj)
	{
		$this->xivo_application_xivo_object_abstract(&$xobj);

		if(($this->_sysconfd    = &$this->_xobj->get_module('sysconfd'))   === false
		|| ($this->_ha_svc      = &$this->_xobj->get_module('ha'))         === false
		|| ($this->_service_svc = &$this->_xobj->get_module('ha_service')) === false
		|| ($this->_cnodes_svc    = &$this->_xobj->get_module('ha_cluster_node'))    === false)
			return(false);

		return(true);
	}

	function get()
	{
		$arr = array();
		$arr['ha'] = $this->_ha_svc->get(1);

		// services
		$arr['service'] = array();
		foreach($this->_service_svc->get_all() as $svc)
			$arr['service'][$svc['name']] = $svc;

		$arr['cnodes'] = $this->_cnodes_svc->get_all();

    return $arr;
	}


	function get_netifaces()
	{
	    $netifaces = $this->_sysconfd->request_get('/discover_netifaces');
	    if($netifaces === false)
	    { return false; }

	    $netifaces = array_keys($netifaces);
	    asort($netifaces);
	    return $netifaces;
	}

	function get_status()
    {
	    $status = $this->_sysconfd->request_get('/ha_status');
	    if($status === false)
	    { return false; }

	    return $status;
	}

	function _set_check($conf)
	{
		foreach($conf['service'] as $key => &$val) {
			if (strlen($val['monitor']) == 0)
				$val['monitor'] = null;
			if (strlen($val['timeout']) == 0)
				$val['timeout'] = null;
		}

		return true;
	}

	function _set_save($conf)
	{
        // IF ALL IT'S OK, SAVE DATA
        if($this->_ha_svc->edit(1, $conf['ha']) === false)
					return false;

				foreach($conf['service'] as $key => $val)
					if($this->_service_svc->edit($key, $val) === false)
						return false;


				// cluster nodes
        if($this->_cnodes_svc->delete_all(array()) === false)
            return false;

        foreach($conf['cnodes'] as $cnode)
					if($this->_cnodes_svc->add($cnode) === false)
						return false;

        if($this->get_errnb() > 0)
            return false;

				return true;
	}

	function set($arr)
	{
		$this->_reset();
		$this->_set_result('ha', $arr);

		if(!$this->_set_check(&$arr))
			return false;

		// IF ALL IT'S OK, SAVE DATA
		if($this->_set_save($arr) === false)
			return false;

		return $this->generate();
	}

	/** Send informations to sysconfd to update HA configuration file
	 **/
  function generate()
	{
		$arr  = $this->get();
		$conf = array('nodes' => array(), 'cluster' => array('services' => array()));

		# we need to reread database to get services rsc_class
		$rsc_classes = array();
		foreach($this->_service_svc->get_all() as $k => $v)
			$rsc_classes[$v['name']] = $v['rsc_class'];

		foreach($arr['service'] as $name => $attrs)
			if(intval($attrs['active']) === 1) {
				$conf['cluster']['services'][$name] = array();
				if(!is_null($attrs['monitor']))
					$conf['cluster']['services'][$name]['monitor'] = intval($attrs['monitor']);
				if(!is_null($attrs['timeout']))
					$conf['cluster']['services'][$name]['timeout'] = intval($attrs['timeout']);

				if(array_key_exists($name, $rsc_classes) && !is_null($rsc_classes[$name]))
					$conf['cluster']['services'][$name]['rsc_class'] = $rsc_classes[$name];
			}

		$conf['cluster']['cluster_addr'] = array();
		foreach($arr['cnodes'] as $node)
			$conf['cluster']['cluster_addr'][] = $node['device'].':'.$node['address'];

		foreach(array('name','itf_data','mailto','pingd') as $key)
			if(strlen($arr['ha']['cluster_'.$key]) > 2)
				$conf['cluster']['cluster_'.$key] = $arr['ha']['cluster_'.$key];
		$conf['cluster']['cluster_group'] = $arr['ha']['cluster_group'] == '1';
		$conf['cluster']['cluster_monitor']  = intval($arr['ha']['cluster_monitor']);
		$conf['cluster']['cluster_timeout']  = intval($arr['ha']['cluster_timeout']);

		$subnet = $this->_ip2subnet($arr['ha']['netaddr'], $arr['ha']['netmask']);
		$conf['nodes'] = array(
			'network_addr'     => $subnet,
			'multicast_addr'   => $arr['ha']['mcast'],

			'first_node'       => array(
				'name'           => $arr['ha']['node1_name'],
				'ip'             => $arr['ha']['node1_ip'],
			),
			'second_node'      => array(
				'name'           => $arr['ha']['node2_name'],
				'ip'             => $arr['ha']['node2_ip'],
			)
		);

		if($this->_sysconfd->request_post('/ha_generate', $conf) === false)
			return false;

		// update commonconf
        	if(($_commonconf = &$this->_xobj->get_module('commonconf')) === false)
			return $false;
		$_commonconf->notify_changes();

		return true;
	}

	function _ip2subnet($ip, $netmask)
	{
		$dotted_ip = split('\.', $ip);
		$dotted_nm = split('\.', $netmask);

		$subnet = sprintf("%d.%d.%d.%d",
			(((int)$dotted_ip[0]) & ((int)$dotted_nm[0])),
			(((int)$dotted_ip[1]) & ((int)$dotted_nm[1])),
			(((int)$dotted_ip[2]) & ((int)$dotted_nm[2])),
			(((int)$dotted_ip[3]) & ((int)$dotted_nm[3]))
		);

		return($subnet);
	}

}

?>
