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

$array['element']['department'] = array();
$array['element']['department']['default'] = '';
$array['element']['department']['null'] = true;

$array['element']['organization'] = array();
$array['element']['organization']['default'] = '';
$array['element']['organization']['null'] = true;

$array['element']['locality'] = array();
$array['element']['locality']['default'] = '';
$array['element']['locality']['null'] = true;

$array['element']['stateprov'] = array();
$array['element']['stateprov']['default'] = '';
$array['element']['stateprov']['null'] = true;

$array['element']['country'] = array();
$array['element']['country']['default'] = '';
$array['element']['country']['null'] = true;

$array['element']['email'] = array();
$array['element']['email']['default'] = '';
$array['element']['email']['null'] = true;

$array['element']['phone'] = array();
$array['element']['phone']['default'] = '';
$array['element']['phone']['null'] = true;

$array['element']['bindaddr'] = array();
$array['element']['bindaddr']['default'] = '0.0.0.0';
$array['element']['bindaddr']['null'] = true;

$array['element']['port'] = array();
$array['element']['port']['default'] = '4520';
$array['element']['port']['null'] = true;

$array['element']['tos'] = array();
$array['element']['tos']['value'] = array('CS0','CS1','CS2','CS3','CS4','CS5','CS6','CS7',
					      'AF11','AF12','AF13','AF21','AF22','AF23',
					      'AF31', 'AF32','AF33','AF41','AF42','AF43','EF');
$array['element']['tos']['default'] = '';
$array['element']['tos']['null'] = true;

$array['element']['entityid'] = array();
$array['element']['entityid']['default'] = '';
$array['element']['entityid']['null'] = true;

$array['element']['cachetime'] = array();
$array['element']['cachetime']['default'] = '5';
$array['element']['cachetime']['null'] = true;

$array['element']['ttl'] = array();
$array['element']['ttl']['default'] = '';
$array['element']['ttl']['null'] = true;

$array['element']['autokill'] = array();
$array['element']['autokill']['value'] = array('no','yes',500,1000,1500,2000,2500,3000,3500,4000);
$array['element']['autokill']['default'] = 'yes';

$array['element']['secretpath'] = array();
$array['element']['secretpath']['default'] = '';
$array['element']['secretpath']['null'] = true;

$array['element']['storehistory'] = array();
$array['element']['storehistory']['value'] = array(0,1);
$array['element']['storehistory']['default'] = 1;
$array['element']['storehistory']['set'] = true;

$array['filter'] = array();
$array['filter']['department'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['organization'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['locality'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['stateprov'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['country'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['email'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['phone'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['bindaddr'] = array('set'		=> false,
				     'chk'		=> 2,
				     'callback'		=> 'dwho_network::valid_host',
				     'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
								  DWHO_NETWORK_HOST_HOSTNAME)),
				     'maxlen'		=> 64);
$array['filter']['port'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['tos'] = array('set' => false,'chk' => 2,'regexp' => '/^(CS[0-7]|AF[1-4][1-3]|EF)$/');
$array['filter']['entityid'] = array('set' => false, 'chk' => 2, 'maxlen' => 20);
$array['filter']['cachetime'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['ttl'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['autokill'] = array('key' => array('no','yes',500,1000,1500,2000,2500,3000,3500,4000));
$array['filter']['secretpath'] = array('set' => false, 'chk' => 2, 'maxlen' => 64);
$array['filter']['storehistory'] = array('set' => false, 'chk' => 2, 'bool' => 'true');
?>
