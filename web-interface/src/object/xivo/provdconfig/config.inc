<?php

#
# XiVO Web-Interface
# Copyright (C) 2020  Avencall
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

$array = array();

// Config base
$array['base'] = array();
$array['base']['id'] = 'base';
$array['base']['parent_ids'] = array();

$array['base']['raw_config'] = array();
$array['base']['raw_config']['sip_dtmf_mode'] = 'SIP-INFO';
$array['base']['raw_config']['sip_lines'] = array();
$array['base']['raw_config']['sip_lines'][1] = array();
$array['base']['raw_config']['sccp_call_managers'] = array();

// Config autoprov
$array['autoprov'] = array();
$array['autoprov']['id'] = 'autoprov';
$array['autoprov']['role'] = 'autocreate';
$array['autoprov']['parent_ids'] = array('base','defaultconfigdevice');

$array['autoprov']['raw_config'] = array();
$array['autoprov']['raw_config']['sip_lines'] = array();
$array['autoprov']['raw_config']['sip_lines'][1] = array();
$array['autoprov']['raw_config']['sip_lines'][1]['display_name'] = 'Autoprov';
$array['autoprov']['raw_config']['sip_lines'][1]['username'] ='autoprov';
$array['autoprov']['raw_config']['sip_lines'][1]['password'] ='autoprov';
$array['autoprov']['raw_config']['sip_lines'][1]['number'] ='autoprov';
$array['autoprov']['raw_config']['sccp_call_managers'] = array();



$array['element'] = array();

$array['element']['_comment'] = array();
$array['element']['_comment']['default'] = '';

$array['element']['label'] = array();
$array['element']['label']['default'] = '';

$array['element']['ip'] = array();
$array['element']['ip']['default'] = '';

$array['element']['http_port'] = array();
$array['element']['http_port']['default'] = '';

$array['element']['tftp_port'] = array();
$array['element']['tftp_port']['default'] = '';

$array['element']['ntp_enabled'] = array();
$array['element']['ntp_enabled']['value'] = array('',0,1);
$array['element']['ntp_enabled']['default'] = '';

$array['element']['ntp_ip'] = array();
$array['element']['ntp_ip']['default'] = '';

$array['element']['vlan_enabled'] = array();
$array['element']['vlan_enabled']['value'] = array('',0,1);
$array['element']['vlan_enabled']['default'] = '';
$array['element']['vlan_enabled']['null'] = true;

$array['element']['vlan_id'] = array();
$array['element']['vlan_id']['default'] = '';

$array['element']['vlan_priority'] = array();
$array['element']['vlan_priority']['value'] = array(0,1,2,3,4,5,6,7);
$array['element']['vlan_priority']['default'] = '';

$array['element']['vlan_pc_port_id'] = array();
$array['element']['vlan_pc_port_id']['default'] = '';

$array['element']['ntp_server_ip'] = array();
$array['element']['ntp_server_ip']['default'] = '';

$array['element']['syslog_enabled'] = array();
$array['element']['syslog_enabled']['value'] = array('',0,1);
$array['element']['syslog_enabled']['default'] = '';
$array['element']['syslog_enabled']['null'] = true;

$array['element']['syslog_ip'] = array();
$array['element']['syslog_ip']['default'] = '';

$array['element']['syslog_port'] = array();
$array['element']['syslog_port']['default'] = '';

$array['element']['syslog_level']['value'] = array('','critical','error','warning','info','debug');
$array['element']['syslog_level']['default'] = '';
$array['element']['syslog_level']['null'] = true;

$array['element']['admin_username'] = array();
$array['element']['admin_username']['default'] = '';

$array['element']['admin_password'] = array();
$array['element']['admin_password']['default'] = '';

$array['element']['user_username'] = array();
$array['element']['user_username']['default'] = '';

$array['element']['user_password'] = array();
$array['element']['user_password']['default'] = '';

$array['element']['timezone'] = array();
$array['element']['timezone']['default'] = '';

$array['element']['locale'] = array();
$array['element']['locale']['value'] = array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA');
$array['element']['locale']['default'] = '';
$array['element']['locale']['null'] = true;

$array['element']['config_encryption_enabled'] = array();
$array['element']['config_encryption_enabled']['value'] = array('',0,1);
$array['element']['config_encryption_enabled']['default'] = '';
$array['element']['config_encryption_enabled']['null'] = true;

$array['element']['protocol'] = array();
$array['element']['protocol']['value'] = array('SIP','SCCP');
$array['element']['protocol']['default'] = 'SIP';

$array['element']['sip_proxy_ip'] = array();
$array['element']['sip_proxy_ip']['default'] = '';

$array['element']['sip_proxy_port'] = array();
$array['element']['sip_proxy_port']['default'] = '';

$array['element']['sip_backup_proxy_port'] = array();
$array['element']['sip_backup_proxy_port']['default'] = '';

$array['element']['sip_registrar_ip'] = array();
$array['element']['sip_registrar_ip']['default'] = '';

$array['element']['sip_registrar_port'] = array();
$array['element']['sip_registrar_port']['default'] = '';

$array['element']['sip_backup_registrar_ip'] = array();
$array['element']['sip_backup_registrar_ip']['default'] = '';

$array['element']['sip_backup_registrar_port'] = array();
$array['element']['sip_backup_registrar_port']['default'] = '';

$array['element']['sip_outbound_proxy_ip'] = array();
$array['element']['sip_outbound_proxy_ip']['default'] = '';

$array['element']['sip_outbound_proxy_port'] = array();
$array['element']['sip_outbound_proxy_port']['default'] = '';

$array['element']['sip_dtmf_mode'] = array();
$array['element']['sip_dtmf_mode']['value'] = array('RTP-in-band','RTP-out-of-band','SIP-INFO');
$array['element']['sip_dtmf_mode']['default'] = '';

$array['element']['sip_srtp_mode'] = array();
#'disabled','preferred','required'
$array['element']['sip_srtp_mode']['value'] = array('preferred','required');
$array['element']['sip_srtp_mode']['default'] = '';

$array['element']['sip_transport'] = array();
$array['element']['sip_transport']['value'] = array('udp','tcp','tls');
$array['element']['sip_transport']['default'] = '';

$array['element']['sip_servers_root_and_intermediate_certificates'] = array();
$array['element']['sip_servers_root_and_intermediate_certificates']['default'] = '';

$array['element']['sip_local_root_and_intermediate_certificates'] = array();
$array['element']['sip_local_root_and_intermediate_certificates']['default'] = '';

$array['element']['sip_local_certificate'] = array();
$array['element']['sip_local_certificate']['default'] = '';

$array['element']['sip_local_key'] = array();
$array['element']['sip_local_key']['default'] = '';

$array['element']['sip_subscribe_mwi'] = array();
$array['element']['sip_subscribe_mwi']['value'] = array('',0,1);
$array['element']['sip_subscribe_mwi']['default'] = '';
$array['element']['sip_subscribe_mwi']['null'] = true;

// exten
$array['element']['exten_dnd'] = array();
$array['element']['exten_dnd']['default'] = '';

$array['element']['exten_fwd_unconditional'] = array();
$array['element']['exten_fwd_unconditional']['default'] = '';

$array['element']['exten_fwd_no_answer'] = array();
$array['element']['exten_fwd_no_answer']['default'] = '';

$array['element']['exten_fwd_busy'] = array();
$array['element']['exten_fwd_busy']['default'] = '';

$array['element']['exten_fwd_disable_all'] = array();
$array['element']['exten_fwd_disable_all']['default'] = '';

$array['element']['exten_park'] = array();
$array['element']['exten_park']['default'] = '';

$array['element']['exten_pickup_group'] = array();
$array['element']['exten_pickup_group']['default'] = '';

$array['element']['exten_pickup_call'] = array();
$array['element']['exten_pickup_call']['default'] = '';

$array['element']['exten_voicemail'] = array();
$array['element']['exten_voicemail']['default'] = '';



dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['label'] = array('set' => false,'chk' => 2,'maxlen' => 64,'cast' => 'sgraph_crlf_tab','eol' => true);
$array['filter']['_comment'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);
$array['filter']['ip'] = array('set' => false,
				    'chk'			=> 2,
				    'callback'		=> 'dwho_network::valid_host',
				    'callbackarg'	=> array(DWHO_NETWORK_HOST_IPV4_DOTDEC));
$array['filter']['http_port'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,65535));
$array['filter']['tftp_port'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,65535));
$array['filter']['ntp_enabled'] = array('set' => false,'key' => $array['element']['ntp_enabled']['value']);
$array['filter']['ntp_ip'] = array('set' => false,
				    'chk'			=> 2,
				    'callback'		=> 'dwho_network::valid_host',
				    'callbackarg'	=> array(DWHO_NETWORK_HOST_IPV4_DOTDEC));
$array['filter']['vlan_enabled'] = array('set' => false,'key' => $array['element']['vlan_enabled']['value']);
$array['filter']['vlan_id'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,4094));
$array['filter']['vlan_priority'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(0,7));
$array['filter']['vlan_pc_port_id'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,4094));
$array['filter']['syslog_ip'] = array('set' => false,
				    'chk'			=> 2,
				    'callback'		=> 'dwho_network::valid_host',
				    'callbackarg'	=> array(DWHO_NETWORK_HOST_IPV4_DOTDEC));
$array['filter']['syslog_enabled'] = array('set' => false,'key' => $array['element']['syslog_enabled']['value']);
$array['filter']['syslog_port'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,65535));
$array['filter']['syslog_level'] = array('key' => $array['element']['syslog_level']['value']);
$array['filter']['admin_username'] = array('set' => false,'chk' => 2);
$array['filter']['admin_password'] = array('set' => false,'chk' => 2);
$array['filter']['user_username'] = array('set' => false,'chk' => 2);
$array['filter']['user_password'] = array('set' => false,'chk' => 2);
$array['filter']['timezone'] = array('set' => false,'chk' => 2);
$array['filter']['sip_subscribe_mwi'] = array('set' => false, 'key' => $array['element']['sip_subscribe_mwi']['value']);
$array['filter']['locale'] = array('set' => false,'chk' => 2,'minlen' =>5,'maxlen' => 5,'key' => $array['element']['locale']['value']);
$array['filter']['config_encryption_enabled'] = array('set' => false,'key' => $array['element']['config_encryption_enabled']['value']);
$array['filter']['protocol'] = array('set' => false,'chk' => 2,'key' => $array['element']['protocol']['value']);
$array['filter']['sip_dtmf_mode'] = array('set' => false,'chk' => 2,'key' => $array['element']['sip_dtmf_mode']['value']);
$array['filter']['sip_srtp_mode'] = array('set' => false,'chk' => 2,'key' => $array['element']['sip_srtp_mode']['value']);
$array['filter']['sip_transport'] = array('set' => false,'chk' => 2,'key' => $array['element']['sip_transport']['value']);


?>
