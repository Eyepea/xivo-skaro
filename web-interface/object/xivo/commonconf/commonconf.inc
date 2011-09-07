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

xivo_object::required(array('abstract','abstract.inc'),true);

class xivo_object_commonconf extends xivo_object_abstract
{
	var $_name	 = 'commonconf';
	var $_sysconfd	 = false;
	var $_dhcp       = false;
	var $_monitoring = false;
	var $_mail       = false;
	var $_netiface   = false;
	var $_resolvconf = false;
	var $_provisioning = false;
	var $_ha           = false;
	var $_ha_vips      = false;

	function xivo_object_commonconf(&$xobj)
	{
		$this->xivo_object_abstract(&$xobj);

		if(($this->_sysconfd    = &$this->_xobj->get_module('sysconfd'))     === false
		|| ($this->_dhcp        = &$this->_xobj->get_module('dhcp'))         === false
		|| ($this->_monitoring  = &$this->_xobj->get_module('monitoring'))   === false
		|| ($this->_mail        = &$this->_xobj->get_module('mail'))         === false
		|| ($this->_provisioning = &$this->_xobj->get_module('provisioning')) === false
		|| ($this->_ha_vips      = &$this->_xobj->get_module('ha_cluster_node')) === false
		|| ($this->_ha           = &$this->_xobj->get_module('ha')) === false)
			return(false);

		return(true);
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

	function _ip2bcast($ip, $netmask)
	{
		$dotted_ip = split('\.', $ip);
		$dotted_nm = split('\.', $netmask);

		/*NOTE:
		 * not bitwise operator (~) return a negative value (~255 = -256).
		* as we want a value between 0 and 255, we add 256 and take module of the
		* result
		*/
		$bcast = '';
		foreach(range(0,3) as $i)
			$bcast .= sprintf('%d.', ((int)$dotted_ip[$i]) | ((~ ((int)$dotted_nm[$i])+256)%256));
		$bcast = substr($bcast, 0, -1);

		return($bcast);
	}

	function generate($content, $onlystatic=true)
	{
		$conf = array();

		// dhcp
		$rawdata = $this->_dhcp->get(1);
		$pool_start = strlen($rawdata['pool_start'])==0?'':$rawdata['pool_start'];
		$conf = array_merge($conf, array(
			'xivo.dhcp.pool' 			=> $pool_start.' '.$rawdata['pool_end'],
			'xivo.dhcp.extra_ifaces'	=> $rawdata['extra_ifaces'],
			'xivo.dhcp.active'			=> $rawdata['active']==0?false:true,
		));

		// mail (postfix)
		$rawdata = $this->_mail->get(1);
		$mydomain = strlen($rawdata['mydomain'])==0?null:$rawdata['mydomain'];
		$conf = array_merge($conf, array(
			'xivo.smtp.mydomain' 			=> $mydomain,
			'xivo.smtp.origin'				=> $rawdata['origin'],
			'xivo.smtp.relayhost'			=> $rawdata['relayhost'],
			'xivo.smtp.fallback_relayhost'	=> $rawdata['fallback_relayhost'],
			'xivo.smtp.canonical'			=> $rawdata['canonical'],
		));

		// provisioning
		$rawdata = $this->_provisioning->get(1);
		$conf = array_merge($conf, array(
			'xivo.provd.net4_ip'		=> $rawdata['net4_ip'],
			'xivo.provd.http_port'		=> $rawdata['http_port'],
			'xivo.provd.username'		=> $rawdata['username'],
			'xivo.provd.password'		=> $rawdata['password'],
			'xivo.provd.rest_port'		=> $rawdata['rest_port'],
			'xivo.provd.rest_net4_ip'	=> $rawdata['net4_ip_rest'],
			'xivo.provd.rest_authentication'	=> (bool) $rawdata['private'],
			'xivo.provd.rest_ssl'		=> (bool) $rawdata['secure'],
			'xivo.provd.dhcp_integration' => (bool) $rawdata['dhcp_integration']
		));

		// monitoring
		$rawdata = $this->_monitoring->get(1);
		$maintenance = $rawdata['maintenance']==0?false:true;
		$alert_emails = strlen($rawdata['alert_emails']) == 0?null:str_replace("\r\n", " ", $rawdata['alert_emails']);
		$dahdi_monitor_ports = strlen($rawdata['dahdi_monitor_ports'])==0?null:$rawdata['dahdi_monitor_ports'];
		$max_call_duration = strlen($rawdata['max_call_duration'])==0?null:$rawdata['max_call_duration'];
		$conf = array_merge($conf, array(
			'xivo.maintenance'		=> $maintenance,
			'alert_emails'			=> $alert_emails,
			'dahdi_monitor_ports'	=> $dahdi_monitor_ports,
			'max_call_duration'		=> $max_call_duration,
		));

		//resolvconf
		// we can't load application at start, or we'll have an infinite loop
		if(($this->_resolvconf  = &$this->_xobj->get_application('resolvconf')) == false) {
			$content = 'cannot load *resolvconf* application';
			return false;
		}

		$rawdata = $this->_resolvconf->get(1);
		$ns = '';
		if(strlen($rawdata['resolvconf']['nameserver1']) > 0)
			$ns .= $rawdata['resolvconf']['nameserver1'] . " ";
		if(strlen($rawdata['resolvconf']['nameserver2']) > 0)
			$ns .= $rawdata['resolvconf']['nameserver2'] . " ";
		if(strlen($rawdata['resolvconf']['nameserver3']) > 0)
			$ns .= $rawdata['resolvconf']['nameserver3'];
		$ns = trim($ns);

		$hostname = is_null($rawdata['resolvconf']['hostname'])?'':$rawdata['resolvconf']['hostname'];
		$resolvconf = is_null($rawdata['resolvconf']['domain'])?'':$rawdata['resolvconf']['domain'];
		$conf = array_merge($conf, array(
			'xivo.hostname'			=> $hostname,
			'xivo.domain'			=> $resolvconf,
			'xivo.extra.dns.search'	=> '',
			'xivo.nameservers'		=> $ns,
		));

		// netiface
		// we can't load application at start, or we'll have an infinite loop
		if(($this->_netiface    = &$this->_xobj->get_application('netiface')) == false) {
			$content = 'cannot load *netiface* application';
			return false;
		}

		$list = $this->_netiface->get_netifaces_list();

		// we filter network devices list, keeping only 'voip' interfaces:
		//  1. 1st vlan
		//  2. 1st voip iface
		//  3. voip ifaces list
		$vlanid     = 0;        //0 means no vlan
		$ifaces     = "";
		$cidr_id    = -1;

		$_netifaces  = array();
		for($i = 0; $i < count($list); $i++)
		{
			$item = &$list[$i];
			if(array_key_exists('netiface', $item))
			$_netifaces[$item['netiface']['ifname']] = $item;

			if(!$item['actionable']
			|| $item['netiface']['disable']
			|| strcmp($item['netiface']['networktype'], 'voip') != 0)
			continue;

			$ifaces .= $item['netiface']['ifname'] . ' ';

			if($vlanid == 0 && $item['netinfo']['vlanif'])
			$vlanid = intval($item['netiface']['vlanid']);

			if($cidr_id < 0 && (!$onlystatic || strcmp($item['netiface']['method'], 'static') == 0))
			$cidr_id = $i;
		}

		// no VOIP netiface defined
		if($cidr_id < 0) {
			$content = 'no VOIP interface configured';
			return false;
		}

		$net = array(
			'ipaddr'    => $list[$cidr_id]['netiface']['address'],
			'netmask'   => $list[$cidr_id]['netiface']['netmask'],
			'broadcast' => $list[$cidr_id]['netiface']['broadcast']);

		$ifaces = trim($ifaces);
		$subnet = $this->_ip2subnet($list[$cidr_id]['netiface']['address'], $list[$cidr_id]['netiface']['netmask']);

		// HA
		$rawdata = $this->_ha->get(1);
		$conf['xivo.ha'] = intval($rawdata['active']);

		//
		$conf['ha.master.ip'] = '';
		$conf['ha.master.name'] = '';
		$conf['ha.slave.ip'] = '';
		$conf['ha.slave.name'] = '';
		//

		if($rawdata['active'] == 1)
		{
			$conf = array_merge($conf, array(
				'ha.master.ip'		=> strlen($rawdata['node1_ip']) == 0?null:$rawdata['node1_ip'],
				'ha.master.name'	=> strlen($rawdata['node1_name']) == 0?null:$rawdata['node1_name'],
				'ha.slave.ip'		=> strlen($rawdata['node2_ip']) == 0?null:$rawdata['node2_ip'],
				'ha.slave.name'		=> strlen($rawdata['node2_name']) == 0?null:$rawdata['node2_name'],
				'ha.data.iface'		=> strlen($rawdata['cluster_itf_data']) == 0?null:$rawdata['cluster_itf_data'],
				'ha.data.master.ip'	=> strlen($rawdata['cluster_itf_master_ip']) == 0?null:$rawdata['cluster_itf_master_ip'] ,
				'ha.data.slave.ip'	=> strlen($rawdata['cluster_itf_slave_ip']) == 0?null:$rawdata['cluster_itf_slave_ip']
			));

			$vips = $this->_ha_vips->get_all();
			if(count($vips) == 0) {
				$content = 'no VIP declared in HA configuration'; return false;
			}

			$ifaces = $vips[0]['device'];
			$subnet = $this->_ip2subnet($rawdata['netaddr'], $rawdata['netmask']);
			$net = array(
				'ipaddr'    => $vips[0]['address'],
				'netmask'   => $rawdata['netmask'],
				'broadcast'	=> $this->_ip2bcast($rawdata['netaddr'], $rawdata['netmask'])
			);

			// search vlan matching HA iface
			if(array_key_exists($ifaces, $_netifaces)) {
				$_iface = $_netifaces[$ifaces];
				if($_iface['netinfo']['vlanif']) {
					$vlanid = intval($_iface['netiface']['vlanid']);
				}
			}
		}

		$conf = array_merge($conf, array(
			'xivo.voip.ifaces'      => $ifaces,
			'xivo.voip.vlan.id'     => $vlanid,
			'xivo.net4.ip'          => $net['ipaddr'],
			'xivo.net4.netmask'     => $net['netmask'],
			'xivo.net4.broadcast'   => $net['broadcast'],
			'xivo.net4.subnet'      => $subnet
		));

		// load database uri
		// 1. xivo
		$config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'xivo.ini');
		$db_xivo = $config['general']['datastorage'];

		// 2. asterisk
		$config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');
		$db_ast  = $config['general']['datastorage'];

		$conf = array_merge($conf, array(
			'xivo.astdb'	=> $db_ast,
			'xivo.xivodb'	=> $db_xivo
		));

		return $this->_sysconfd->request_post('/commonconf_generate', $conf);
	}

	function apply()
	{
		$ret = $this->_sysconfd->request_get('/commonconf_apply');

		if (dwho_file::is_f('/var/lib/pf-xivo-web-interface/commonconf.reload'))
			unlink('/var/lib/pf-xivo-web-interface/commonconf.reload');

		return $ret;
	}

	function last_status_code()
	{
		return $this->_sysconfd->last_status_code();
	}

	function notify_changes()
	{
		touch('/var/lib/pf-xivo-web-interface/commonconf.reload');
	}
}

?>
