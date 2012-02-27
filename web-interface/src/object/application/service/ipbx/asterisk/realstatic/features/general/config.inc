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

$array['exten'] = array();
$array['exten']['parkext'] = true;
$array['exten']['pickupexten'] = true;

$array['sound'] = array();
$array['sound']['courtesytone'] = true;
$array['sound']['xfersound'] = true;
$array['sound']['xferfailsound'] = true;


$array['element'] = array();
$array['element']['parkext'] = array();
$array['element']['parkext']['default'] = 700;

$array['element']['parkpos'] = array();
$array['element']['parkpos']['default'] = '701-750';

$array['element']['context'] = array();
$array['element']['context']['default'] = 'parkedcalls';
$array['element']['context']['forcedef'] = true;

$array['element']['parkinghints'] = array();
$array['element']['parkinghints']['value'] = array('no','yes');
$array['element']['parkinghints']['default'] = 'no';
$array['element']['parkinghints']['set'] = true;

$array['element']['parkingtime'] = array();
$array['element']['parkingtime']['value'] = array(15,30,45,60,75,90,
						  105,120,135,150,165,180,
						  195,210,225,240,255,270,285,
						  300,600,900,1200,1500,1800);
$array['element']['parkingtime']['default'] = 45;

$array['element']['comebacktoorigin'] = array();
$array['element']['comebacktoorigin']['value'] = array('no','yes');
$array['element']['comebacktoorigin']['default'] = 'yes';
$array['element']['comebacktoorigin']['set'] = true;


$array['element']['courtesytone'] = array();
$array['element']['courtesytone']['default'] = '';
$array['element']['courtesytone']['null'] = true;


$array['element']['parkedplay'] = array();
$array['element']['parkedplay']['value'] = array('parked','caller','both');
$array['element']['parkedplay']['default'] = 'caller';
$array['element']['parkedplay']['null'] = true;

$array['element']['parkedcalltransfers'] = array();
$array['element']['parkedcalltransfers']['value'] = array('callee','caller','both','no');
$array['element']['parkedcalltransfers']['default'] = 'no';
$array['element']['parkedcalltransfers']['null'] = true;

$array['element']['parkedcallreparking'] = array();
$array['element']['parkedcallreparking']['value'] = array('callee','caller','both','no');
$array['element']['parkedcallreparking']['default'] = 'no';
$array['element']['parkedcallreparking']['null'] = true;

$array['element']['parkedcallhangup'] = array();
$array['element']['parkedcallhangup']['value'] = array('callee','caller','both','no');
$array['element']['parkedcallhangup']['default'] = 'no';
$array['element']['parkedcallhangup']['null'] = true;

$array['element']['parkedcallrecording'] = array();
$array['element']['parkedcallrecording']['value'] = array('callee','caller','both','no');
$array['element']['parkedcallrecording']['default'] = 'no';
$array['element']['parkedcallrecording']['null'] = true;

$array['element']['parkeddynamic'] = array();
$array['element']['parkeddynamic']['value'] = array('no','yes');
$array['element']['parkeddynamic']['default'] = 'no';
$array['element']['parkeddynamic']['set'] = true;

$array['element']['adsipark'] = array();
$array['element']['adsipark']['value'] = array('no','yes');
$array['element']['adsipark']['default'] = 'no';
$array['element']['adsipark']['set'] = true;

$array['element']['findslot'] = array();
$array['element']['findslot']['value'] = array('no','next');
$array['element']['findslot']['default'] = 'no';
$array['element']['findslot']['set'] = true;

$array['element']['parkedmusicclass'] = array();
$array['element']['parkedmusicclass']['default'] = 'default';
$array['element']['parkedmusicclass']['null'] = true;

$array['element']['transferdigittimeout'] = array();
$array['element']['transferdigittimeout']['value'] = range(1,30);
$array['element']['transferdigittimeout']['default'] = 3;

$array['element']['xfersound'] = array();
$array['element']['xfersound']['default'] = '';
$array['element']['xfersound']['null'] = true;

$array['element']['xferfailsound'] = array();
$array['element']['xferfailsound']['default'] = '';
$array['element']['xferfailsound']['null'] = true;

$array['element']['pickupexten'] = array();
$array['element']['pickupexten']['default'] = '*8';

$array['element']['featuredigittimeout'] = array();
$array['element']['featuredigittimeout']['value'] = array(1,500,1000,1500,2000,2500,3000,3500,4000);
$array['element']['featuredigittimeout']['default'] = 500;

$array['element']['atxfernoanswertimeout'] = array();
$array['element']['atxfernoanswertimeout']['value'] = range(1,60);
$array['element']['atxfernoanswertimeout']['default'] = 15;

$array['element']['atxferdropcall'] = array();
$array['element']['atxferdropcall']['value'] = array('no','yes');
$array['element']['atxferdropcall']['default'] = 'no';
$array['element']['atxferdropcall']['set'] = true;

$array['element']['atxferloopdelay'] = array();
$array['element']['atxferloopdelay']['value'] = range(1,60);
$array['element']['atxferloopdelay']['default'] = 10;

$array['element']['atxfercallbackretries'] = array();
$array['element']['atxfercallbackretries']['value'] = range(1,20);
$array['element']['atxfercallbackretries']['default'] = 2;



$array['filter'] = array();

$array['filter']['parkext'] = array('regexp' => '/^[0-9\*#]+$/','minlen' => 1,'maxlen' => 40);
$array['filter']['parkpos'] = array('regexp' => '/^[0-9]{1,5}-[0-9]{1,5}$/','minlen' => 3,'maxlen' => 11);
$array['filter']['context'] = array('set' => false);
$array['filter']['parkinghints'] = array('bool' => true);
$array['filter']['parkingtime'] = array('key' => array(15,30,45,60,75,90,
						       105,120,135,150,165,180,
						       195,210,225,240,255,270,285,
									 300,600,900,1200,1500,1800));
$array['filter']['comebacktoorigin'] = array('bool' => true);

$array['filter']['courtesytone'] = array('set' => false,'chk' => 2,'maxlen' => 255,'cast' => 'sgraph');

$array['filter']['parkedplay']          = array('set' => false,'chk' => 2, 'key' => array('parked','caller','both'));
$array['filter']['parkedcalltransfers'] = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both','no'));
$array['filter']['parkedcallreparking'] = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both','no'));
$array['filter']['parkedcallhangup']    = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both','no'));
$array['filter']['parkedcallrecording'] = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both','no'));
$array['filter']['parkeddynamic'] = array('bool' => true);
$array['filter']['adsipark'] = array('bool' => true);
$array['filter']['findslot'] = array('bool' => true);
$array['filter']['parkedmusicclass'] = array('set' => false);

$array['filter']['transferdigittimeout'] = array('cast' => 'uint','between' => array(1,30));
$array['filter']['xfersound'] = array('set' => false,'chk' => 2,'maxlen' => 255,'cast' => 'sgraph');
$array['filter']['xferfailsound'] = array('set' => false,'chk' => 2,'maxlen' => 255,'cast' => 'sgraph');
$array['filter']['pickupexten'] = array('regexp' => '/^[0-9\*#]+$/','minlen' => 1,'maxlen' => 40);
$array['filter']['featuredigittimeout'] = array('cast' => 'uint','between' => array(1,4000,500));
$array['filter']['atxfernoanswertimeout'] = array('cast' => 'uint','between' => array(1,600));
$array['filter']['atxferdropcall'] = array('bool' => true);
$array['filter']['atxferloopdelay'] = array('cast' => 'uint','between' => array(1,600));
$array['filter']['atxfercallbackretries'] = array('cast' => 'uint','between' => array(1,600));


?>
