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
$array['element']['audiobuffers'] = array();
$array['element']['audiobuffers']['value'] = range(2,32);
$array['element']['audiobuffers']['default'] = 32;

$array['element']['schedule'] = array();
$array['element']['schedule']['value'] = array('no', 'yes');
$array['element']['schedule']['default'] = 'yes';
$array['element']['schedule']['set'] = true;

$array['element']['logmembercount'] = array();
$array['element']['logmembercount']['value'] = array('no', 'yes');
$array['element']['logmembercount']['default'] = 'yes';
$array['element']['logmembercount']['set'] = true;

$array['element']['fuzzystart'] = array();
$array['element']['fuzzystart']['value'] = array(0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500,520,540,560,580,600,620,640,660,680,700,720,740,760,780,800,820,840,860,880,900,920,940,960,980,1000,1020,1040,1060,1080,1100,1120,1140,1160,1180,1200);
$array['element']['fuzzystart']['default'] = 300;

$array['element']['earlyalert'] = array();
$array['element']['earlyalert']['value'] = array(0,60,120,300,600,900,1200,1500,1800,2100,2400,2700,3000,3300,3600);
$array['element']['earlyalert']['default'] = 3600;

$array['element']['endalert'] = array();
$array['element']['endalert']['value'] = array(0,10,20,30,60,90,120,150,180,210,240,270,300,330,360,390,420,450,480,510,540,570,600);
$array['element']['endalert']['default'] = 120;

// FILTER
$array['filter'] = array();
$array['filter']['audiobuffers'] = array('cast' => 'uint','between' => array(2,32));
$array['filter']['schedule'] = array('bool' => true);
$array['filter']['logmembercount'] = array('bool' => true);
$array['filter']['fuzzystart'] = array('cast' => 'uint','between' => array(0,1200,20));
$array['filter']['earlyalert'] = array('cast' => 'uint','between' => array(0,3600,350));
$array['filter']['endalert'] = array('cast' => 'uint','between' => array(0,600,30));


?>
