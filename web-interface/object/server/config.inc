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

$array = array();

$array['element'] = array();

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['host'] = array();
$array['element']['host']['default'] = '';

$array['element']['ws_login'] = array();
$array['element']['ws_login']['default'] = '';

$array['element']['ws_pass'] = array();
$array['element']['ws_pass']['default'] = '';

$array['element']['ws_port'] = array();
$array['element']['ws_port']['default'] = 443;

$array['element']['ws_ssl'] = array();
$array['element']['ws_ssl']['value'] = array(0,1);
$array['element']['ws_ssl']['default'] = 1;
$array['element']['ws_ssl']['set'] = true;

$array['element']['cti_login'] = array();
$array['element']['cti_login']['default'] = '';

$array['element']['cti_pass'] = array();
$array['element']['cti_pass']['default'] = '';

$array['element']['cti_port'] = array();
$array['element']['cti_port']['default'] = 5013;

$array['element']['cti_ssl'] = array();
$array['element']['cti_ssl']['value'] = array(0,1);
$array['element']['cti_ssl']['default'] = 1;
$array['element']['cti_ssl']['set'] = true;

$array['element']['disable'] = array();
$array['element']['disable']['value'] = array(0,1);
$array['element']['disable']['default'] = 0;
$array['element']['disable']['set'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';


dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['name'] = array('regexp' => '/^[a-z0-9_\.-]+$/','minlen' => 1,'maxlen' => 64);
$array['filter']['host'] = array('callback' => 'dwho_network::valid_host');
$array['filter']['ws_login'] = array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9_\.-]+$/','minlen' => 1,'maxlen' => 64);
$array['filter']['ws_pass'] = array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9_\.-]+$/','minlen' => 1,'maxlen' => 64);
$array['filter']['ws_port'] = array('cast' => 'uint','between' => array(1,65535));
$array['filter']['ws_ssl'] = array('bool' => true);
$array['filter']['cti_login'] = array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9_\.-]+$/','minlen' => 1,'maxlen' => 64);
$array['filter']['cti_pass'] = array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9_\.-]+$/','minlen' => 1,'maxlen' => 64);
$array['filter']['cti_port'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,65535));
$array['filter']['cti_ssl'] = array('bool' => true);
$array['filter']['disable'] = array('bool' => true);
$array['filter']['description'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);

?>
