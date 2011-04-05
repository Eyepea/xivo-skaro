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

$array['element'] = array();

$array['element']['macaddr'] = array();
$array['element']['macaddr']['default'] = '';

$array['element']['model'] = array();
$array['element']['model']['value']   = array('symmetric','inbound','outbound','none');
$array['element']['model']['default'] = '';

$array['element']['host'] = array();
$array['element']['host']['default'] = '';

$array['element']['inkey'] = array();
$array['element']['inkey']['default'] = '';

$array['element']['outkey'] = array();
$array['element']['outkey']['default'] = '';

$array['element']['include'] = array();
$array['element']['include']['default'] = '';

$array['element']['permit'] = array();
$array['element']['permit']['default'] = '';

$array['element']['qualify'] = array();
$array['element']['qualify']['value'] = array('no','yes',500,1000,1500,2000,2500,3000,3500,4000);
$array['element']['qualify']['default'] = 'yes';
$array['element']['qualify']['null'] = true;

$array['element']['order'] = array();
$array['element']['order']['value']   = array('primary','secondary','tertiary','quartiary');
$array['element']['order']['default'] = '';

$array['element']['precache'] = array();
$array['element']['precache']['value']   = array('symmetric','inbound','outbound','none');
$array['element']['precache']['default'] = '';

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['filter'] = array();
$array['filter']['macaddr'] = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['model'] = array('set' => true,'chk' => 1, 'key' => array('symmetric','inbound','outbound','none'));
$array['filter']['host'] = array('set' => true,'chk' => 1, 'maxlen'=>256);
$array['filter']['inkey'] = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['outkey'] = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['include'] = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['permit'] = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['qualify'] = array('set' => false, 'chk' => 2, 'key' => array('no','yes',500,1000,1500,2000,2500,3000,3500,4000));
$array['filter']['order'] = array('set' => true,'chk' => 1, 'key'=>array('primary','secondary','tertiary','quartiary'));
$array['filter']['precache'] = array('set' => true,'chk' => 1, 'key' => array('symmetric','inbound','outbound','none'));
$array['filter']['description'] = array('set' => false,'chk' => 2);
$array['filter']['commented'] = array('bool' => true);

?>
