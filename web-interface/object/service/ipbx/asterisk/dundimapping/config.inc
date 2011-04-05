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


$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['weight'] = array();
$array['element']['weight']['default'] = '';

$array['element']['trunk'] = array();
$array['element']['trunk']['default'] = '';

$array['element']['number'] = array();
$array['element']['number']['default'] = '';

$array['element']['nounsolicited'] = array();
$array['element']['nounsolicited']['value'] = array(0,1);
$array['element']['nounsolicited']['default'] = 0;
$array['element']['nounsolicited']['set'] = true;

$array['element']['nocomunsolicit'] = array();
$array['element']['nocomunsolicit']['value'] = array(0,1);
$array['element']['nocomunsolicit']['default'] = 0;
$array['element']['nocomunsolicit']['set'] = true;

$array['element']['residential'] = array();
$array['element']['residential']['value'] = array(0,1);
$array['element']['residential']['default'] = 0;
$array['element']['residential']['set'] = true;

$array['element']['commercial'] = array();
$array['element']['commercial']['value'] = array(0,1);
$array['element']['commercial']['default'] = 0;
$array['element']['commercial']['set'] = true;

$array['element']['mobile'] = array();
$array['element']['mobile']['value'] = array(0,1);
$array['element']['mobile']['default'] = 0;
$array['element']['mobile']['set'] = true;

$array['element']['nopartial'] = array();
$array['element']['nopartial']['value'] = array(0,1);
$array['element']['nopartial']['default'] = 0;
$array['element']['nopartial']['set'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;


$array['filter'] = array();
$array['filter']['name']        = array('set' => true,'chk' => 1, 'maxlen'=>255);
$array['filter']['context']     = array('set' => true,'chk' => 1, 'maxlen'=>39);
$array['filter']['weight']      = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['trunk']       = array('set' => true,'chk' => 1, 'cast'  => 'uint');
$array['filter']['number'] = array('set' => true,'chk' => 1, 'maxlen'=>64);
$array['filter']['nounsolicited'] = array('bool' => true);
$array['filter']['nocomunsolicit'] = array('bool' => true);
$array['filter']['residential'] = array('bool' => true);
$array['filter']['commercial'] = array('bool' => true);
$array['filter']['mobile'] = array('bool' => true);
$array['filter']['nopartial'] = array('bool' => true);
$array['filter']['description'] = array('set' => false,'chk' => 2);
$array['filter']['commented'] = array('bool' => true);

?>
