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

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['autosigned'] = array();
$array['element']['autosigned']['value'] = array(0,1);
$array['element']['autosigned']['default'] = 0;
$array['element']['autosigned']['set'] = true;

$array['element']['is_ca'] = array();
$array['element']['is_ca']['value'] = array(0,1);
$array['element']['is_ca']['default'] = 0;
$array['element']['is_ca']['set'] = true;

$array['element']['password'] = array();
$array['element']['password']['default'] = '';

$array['element']['length'] = array();
$array['element']['length']['value'] = array(1024,2048);
$array['element']['length']['default'] = '';

$array['element']['validity'] = array();
$array['element']['validity']['value'] = range(0,3650);
$array['element']['validity']['default'] = '';

$array['element']['CN'] = array();
$array['element']['CN']['default'] = '';

$array['element']['C'] = array();
$array['element']['C']['default'] = '';

$array['element']['ST'] = array();
$array['element']['ST']['default'] = '';

$array['element']['L'] = array();
$array['element']['L']['default'] = '';

$array['element']['O'] = array();
$array['element']['O']['default'] = '';

$array['element']['OU'] = array();
$array['element']['OU']['default'] = '';

$array['element']['emailAddress'] = array();
$array['element']['emailAddress']['default'] = '';

$array['element']['ca'] = array();
$array['element']['ca']['default'] = '';

$array['element']['ca_password'] = array();
$array['element']['ca_password']['default'] = '';

$array['element']['cipher'] = array();
$array['element']['cipher']['value'] = array('aes');
$array['element']['cipher']['default'] = 'aes';
$array['element']['cipher']['null'] = true;

$array['filter'] = array();
$array['filter']['name'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['password'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['CN'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['C'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['ST'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['L'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['O'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['OU'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['emailAddress'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['ca'] = array('set' => false, 'chk' => 1, 'maxlen' => 255);
$array['filter']['ca_password'] = array('set' => false, 'chk' => 1, 'maxlen' => 255);
$array['filter']['length'] = array('set' => true, 'chk' => 1, 'cast' => 'uint');
$array['filter']['validity'] = array('set' => true, 'chk' => 1, 'cast' => 'uint');
$array['filter']['is_ca'] = array('bool' => true);
$array['filter']['autosigned'] = array('bool' => true);
$array['filter']['cipher'] = array('set' => false, 'chk' => 2, 'key' => array('aes','des','des3','idea'));

?>
