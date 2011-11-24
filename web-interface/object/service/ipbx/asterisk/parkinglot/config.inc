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

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['extension'] = array();
$array['element']['extension']['default'] = '';

$array['element']['positions'] = array();
$array['element']['positions']['default'] = 50;

$array['element']['next'] = array();
$array['element']['next']['value'] = array(0,1);
$array['element']['next']['default'] = 1;
$array['element']['next']['set'] = true;

$array['element']['duration'] = array();
$array['element']['duration']['default'] = '';
$array['element']['duration']['null'] = true;

$array['element']['calltransfers'] = array();
$array['element']['calltransfers']['value'] = array('callee','caller','both');
$array['element']['calltransfers']['default'] = '';
$array['element']['calltransfers']['null'] = true;

$array['element']['callreparking'] = array();
$array['element']['callreparking']['value'] = array('callee','caller','both');
$array['element']['callreparking']['default'] = '';
$array['element']['callreparking']['null'] = true;

$array['element']['callhangup'] = array();
$array['element']['callhangup']['value'] = array('callee','caller','both');
$array['element']['callhangup']['default'] = '';
$array['element']['callhangup']['null'] = true;

$array['element']['callrecording'] = array();
$array['element']['callrecording']['value'] = array('callee','caller','both');
$array['element']['callrecording']['default'] = '';
$array['element']['callrecording']['null'] = true;

$array['element']['musicclass'] = array();
$array['element']['musicclass']['default'] = '';

$array['element']['hints'] = array();
$array['element']['hints']['value'] = array(0,1);
$array['element']['hints']['default'] = 0;
$array['element']['hints']['set'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['filter'] = array();
$array['filter']['name'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['context'] = array('set' => true, 'chk' => 1, 'maxlen' => 39);
$array['filter']['extension'] = array('set' => true, 'chk' => 1, 'maxlen' => 40, 'cast' => 'uint');
$array['filter']['positions'] = array('set' => true, 'chk' => 1, 'cast' => 'uint');
$array['filter']['next'] = array('bool' => true);
$array['filter']['duration'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['calltransfers'] = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both'));
$array['filter']['callreparking'] = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both'));
$array['filter']['callhangup']    = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both'));
$array['filter']['callrecording'] = array('set' => false,'chk' => 2, 'key' => array('callee','caller','both'));
$array['filter']['musicclass'] = array('set' => false, 'chk' => 2, 'maxlen' => 255);
$array['filter']['hints'] = array('bool' => true);
$array['filter']['description'] = array('set' => false, 'chk' => 2);
$array['filter']['commented'] = array('bool' => true);

?>
