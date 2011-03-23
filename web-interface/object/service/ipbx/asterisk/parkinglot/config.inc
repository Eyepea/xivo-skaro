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

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['extension'] = array();
$array['element']['extension']['default'] = '';

$array['element']['pos_start'] = array();
$array['element']['pos_start']['value'] = range(0,500);
$array['element']['pos_start']['default'] = '';

$array['element']['pos_end'] = array();
$array['element']['pos_end']['value'] = range(0,500);
$array['element']['pos_end']['default'] = '';

$array['element']['next'] = array();
$array['element']['next']['value'] = array(0,1);
$array['element']['next']['default'] = 1;
$array['element']['next']['set'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['filter'] = array();
$array['filter']['name'] = array('set' => true, 'chk' => 1, 'maxlen' => 255);
$array['filter']['context'] = array('set' => true, 'chk' => 1, 'maxlen' => 39);
$array['filter']['extension'] = array('set' => true, 'chk' => 1, 'maxlen' => 40);
$array['filter']['pos_start'] = array('set' => true, 'chk' => 1, 'cast' => 'uint');
$array['filter']['pos_end'] = array('set' => true, 'chk' => 1, 'cast' => 'uint');
$array['filter']['next'] = array('bool' => true);
$array['filter']['description'] = array('set' => false, 'chk' => 2);
$array['filter']['commented'] = array('bool' => true);

?>
