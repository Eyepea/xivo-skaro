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

$array = array();
$array['element'] = array();

$array['element']['host'] = array();
$array['element']['host']['default'] = '';

$array['element']['commandset'] = array();
$array['element']['commandset']['value'] = array('xivocti');
$array['element']['commandset']['default'] = 'xivocti';

$array['element']['ami_login'] = array();
$array['element']['ami_login']['default'] = 'xivo_cti_user';
$array['element']['ami_password'] = array();
$array['element']['ami_password']['default'] = 'phaickbebs9';
$array['element']['ami_ip'] = array();
$array['element']['ami_ip']['default'] = '127.0.0.1';
$array['element']['ami_port'] = array();
$array['element']['ami_port']['default'] = 5038;

$array['element']['fagi_ip'] = array();
$array['element']['fagi_ip']['default'] = '127.0.0.1';
$array['element']['fagi_port'] = array();
$array['element']['fagi_port']['default'] = 5002;
$array['element']['fagi_active'] = array();
$array['element']['fagi_active']['value'] = array(0,1);
$array['element']['fagi_active']['default'] = 1;
$array['element']['fagi_active']['set'] = true;

$array['element']['cti_ip'] = array();
$array['element']['cti_ip']['default'] = '0.0.0.0';
$array['element']['cti_port'] = array();
$array['element']['cti_port']['default'] = 5003;
$array['element']['cti_active'] = array();
$array['element']['cti_active']['value'] = array(0,1);
$array['element']['cti_active']['default'] = 1;
$array['element']['cti_active']['set'] = true;

$array['element']['ctis_ip'] = array();
$array['element']['ctis_ip']['default'] = '0.0.0.0';
$array['element']['ctis_port'] = array();
$array['element']['ctis_port']['default'] = 5013;
$array['element']['ctis_active'] = array();
$array['element']['ctis_active']['value'] = array(0,1);
$array['element']['ctis_active']['default'] = 1;
$array['element']['ctis_active']['set'] = true;

$array['element']['webi_ip'] = array();
$array['element']['webi_ip']['default'] = '127.0.0.1';
$array['element']['webi_port'] = array();
$array['element']['webi_port']['default'] = 5004;
$array['element']['webi_active'] = array();
$array['element']['webi_active']['value'] = array(0,1);
$array['element']['webi_active']['default'] = 1;
$array['element']['webi_active']['set'] = true;

$array['element']['info_ip'] = array();
$array['element']['info_ip']['default'] = '127.0.0.1';
$array['element']['info_port'] = array();
$array['element']['info_port']['default'] = 5005;
$array['element']['info_active'] = array();
$array['element']['info_active']['value'] = array(0,1);
$array['element']['info_active']['default'] = 1;
$array['element']['info_active']['set'] = true;

$array['element']['announce_ip'] = array();
$array['element']['announce_ip']['default'] = '127.0.0.1';
$array['element']['announce_port'] = array();
$array['element']['announce_port']['default'] = 5006;
$array['element']['announce_active'] = array();
$array['element']['announce_active']['value'] = array(0,1);
$array['element']['announce_active']['default'] = 1;
$array['element']['announce_active']['set'] = true;

$array['element']['tlscertfile'] = array();
$array['element']['tlscertfile']['default'] = '';
$array['element']['tlsprivkeyfile'] = array();
$array['element']['tlsprivkeyfile']['default'] = '';

$array['element']['asterisklist'] = array();
$array['element']['asterisklist']['default'] = 'xivo';
$array['element']['asterisklist']['value'] = array('xivo');

$array['element']['updates_period'] = array();
$array['element']['updates_period']['default'] = 3600;

$array['element']['socket_timeout'] = array();
$array['element']['socket_timeout']['default'] = 10;

$array['element']['login_timeout'] = array();
$array['element']['login_timeout']['default'] = 5;

dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['commandset'] 		= array('key' => array('xivocti'));
$array['filter']['ami_ip']          = array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['ami_port']        = array('cast' => 'uint', 'between' => array(1,65535));
$array['filter']['ami_login']       = array('cast' => 'sgraph','minlen' => 3,'maxlen' => 64);
$array['filter']['ami_password']    = array('cast' => 'sgraph','minlen' => 3,'maxlen' => 64);
$array['filter']['fagi_ip'] 		= array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['fagi_port'] 		= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,65535));
$array['filter']['cti_ip'] 			= array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['cti_port'] 		= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,65535));
$array['filter']['ctis_ip'] 		= array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['ctis_port'] 		= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,65535));
$array['filter']['webi_ip'] 		= array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['webi_port'] 		= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,65535));
$array['filter']['info_ip'] 		= array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['info_port'] 		= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,65535));
$array['filter']['announce_ip'] 	= array('callback' => 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['announce_port'] 	= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,65535));
$array['filter']['tlscertfile'] 	= array('set' => false, 'chk' => 2, 'cast' => 'sgraph', 'maxlen' => 128);
$array['filter']['tlsprivkeyfile'] 		= array('set' => false, 'chk' => 2, 'cast' => 'sgraph', 'maxlen' => 128);
$array['filter']['asterisklist'] 	= array('set' => false, 'chk' => 2, 'regexp' => '/^[a-z0-9_\-\,]+$/i');
$array['filter']['updates_period'] 	= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(60,86400));
$array['filter']['socket_timeout'] 	= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,20));
$array['filter']['login_timeout'] 	= array('set' => false, 'chk' => 2, 'cast' => 'uint', 'between' => array(1,20));
$array['filter']['parting_astid_context'] = array('set' => false, 'chk' => 2, 'key' => array('astid', 'context', 'context,astid'));

$array['filter']['fagi_active'] = array('set' => true, 'chk' => 2, 'cast' => 'bool');
$array['filter']['cti_active'] = array('set' => true, 'chk' => 2, 'cast' => 'bool');
$array['filter']['ctis_active'] = array('set' => true, 'chk' => 2, 'cast' => 'bool');
$array['filter']['webi_active'] = array('set' => true, 'chk' => 2, 'cast' => 'bool');
$array['filter']['info_active'] = array('set' => true, 'chk' => 2, 'cast' => 'bool');
$array['filter']['announce_active'] = array('set' => true, 'chk' => 2, 'cast' => 'bool');
?>
