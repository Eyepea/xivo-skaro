<?php

#
# XiVO Web-Interface
# Copyright (C) 2020  Proformatique <technique@proformatique.com>
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

$array['element']['net4_ip'] = array();
$array['element']['net4_ip']['default'] = '';

$array['element']['http_port'] = array();
$array['element']['http_port']['default'] = 8667;

$array['element']['username'] = array();
$array['element']['username']['default'] = 'admin';

$array['element']['password'] = array();
$array['element']['password']['default'] = 'admin';

$array['element']['rest_port'] = array();
$array['element']['rest_port']['default'] = 8666;

$array['element']['dhcp_integration'] = array();
$array['element']['dhcp_integration']['value'] = array(0,1);
$array['element']['dhcp_integration']['default'] = 0;
$array['element']['dhcp_integration']['set'] = true;

### filters ###
$array['filter'] = array();

$array['filter']['net4_ip'] = array('set' 		=> false,
						    'chk'			=> 2,
						    'callback'		=> 'dwho_network::valid_host',
						    'callbackarg'	=> array(DWHO_NETWORK_HOST_IPV4_DOTDEC));
$array['filter']['http_port'] = array('cast' => 'uint','between' => array(1,65535));
$array['filter']['rest_port'] = array('cast' => 'uint','between' => array(1,65535));
$array['filter']['username'] = array('maxlen' => 128,'regexp' => '/^[a-z0-9\-_]+$/');
$array['filter']['password'] = array('maxlen' => 128,'regexp' => '/^[a-z0-9\-_]+$/');
$array['filter']['dhcp_integration'] = array('bool' => true);

?>
