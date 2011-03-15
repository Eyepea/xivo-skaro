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

$array['element']['queuepenalty_id'] = array();
$array['element']['queuepenalty_id']['default'] = '';

$array['element']['seconds'] = array();
$array['element']['seconds']['default'] = '';

$array['element']['maxp_value'] = array();
$array['element']['maxp_value']['default'] = '';
$array['element']['maxp_value']['null'] = true;

$array['element']['minp_value'] = array();
$array['element']['minp_value']['default'] = '';
$array['element']['minp_value']['null'] = true;

$array['element']['maxp_sign'] = array();
$array['element']['maxp_sign']['value'] = array('+','-','=');
$array['element']['maxp_sign']['null'] = true;

$array['element']['minp_sign'] = array();
$array['element']['minp_sign']['value'] = array('+','-','=');
$array['element']['minp_sign']['null'] = true;

$array['filter'] = array();
$array['filter']['queuepenalty_id'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['seconds'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['maxp_value'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['minp_value'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['maxp_sign'] = array('set' => false, 'chk' => 2, 'key' => array('+','-','='));
$array['filter']['minp_sign'] = array('set' => false, 'chk' => 2, 'key' => array('+','-','='));

?>
