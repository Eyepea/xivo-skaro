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
        if($this->_ha_svc->chk_values($conf['global']) === false)
            $this->_set_errors($this->_ha_svc->get_filter_error());
            
        // uname_node array
        for($i = 0; $i < count($conf['uname_node']); $i++)
        {
            if($this->_uname_svc->chk_values(array('uname_node' => $conf['uname_node'][$i])) === false)
               $this->_set_errors('pf_ha_uname_node', $i, $this->_uname_svc->get_filter_error());
        }

         // ping_ipaddr
        for($i = 0; $i < count($conf['ping_ipaddr']); $i++)
        {
            if($this->_ping_svc->chk_values(array('ping_ipaddr' => $conf['ping_ipaddr'][$i])) === false)
               $this->_set_errors('pf_ha_ping_ipaddr', $i, $this->_ping_svc->get_filter_error());
        }            

        // virtnet
        for($i = 0; $i < count($conf['virtnet']); $i++)
        {
            if($this->_virtnet_svc->chk_values($conf['virtnet'][$i]) === false)
                $this->_set_errors("virtnet", $i, $this->_virtnet_svc->get_filter_error());
        }

        // peer
        for($i = 0; $i < count($conf['peer']); $i++)
        {
            if($this->_peer_svc->chk_values($conf['peer'][$i]) === false)
                $this->_set_errors("peer", $i, $this->_peer_svc->get_filter_error());
        }

        return ($this->get_errnb() == 0);
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
        if($this->_cnodes_svc->delete_all() === false)
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
        
		// 1. TEST DATA
		/*
		if(!$this->_set_check($conf))
			return false;
		*/
            
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
		$conf = array('nodes' => array(), 'cluster' => array(), 'services' => array());

		foreach($arr['service'] as $name => $attrs)
			if(intval($attrs['active']) === 1)
				$conf['services'][$name] = array(
					'monitor' => intval($attrs['monitor']),
					'timeout' => intval($attrs['timeout'])
			);

		$conf['cluster']['cluster_addr'] = array();
		foreach($arr['cnodes'] as $node)
			$conf['cluster']['cluster_addr'][] = $node['device'].':'.$node['address'];

		$conf['cluster']['cluster_name']  = $arr['ha']['cluster_name'];
		$conf['cluster']['cluster_group'] = $arr['ha']['cluster_group'] == '1';

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
		//var_dump($conf); return(true);	

		if($this->_sysconfd->request_post('/ha_generate', $conf) === false)
			return false;
        
		// update commonconf
		/*
        if(($_commonconf = &$this->_xobj->get_module('commonconf')) === false
        || $_commonconf->generate()                                 === false)
            return false;
		*/
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
