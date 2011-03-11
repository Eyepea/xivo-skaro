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

$array['element']['operator_id'] = array();

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['exten'] = array();
$array['element']['exten']['default'] = '';

$array['element']['price'] = array();
$array['element']['price']['default'] = '';

$array['element']['price_is'] = array();
$array['element']['price_is']['value'] = array('second','minute');
$array['element']['price_is']['default'] = 'minute';
$array['element']['price_is']['set'] = true;

$array['element']['disable'] = array();
$array['element']['disable']['value'] = array(0,1);
$array['element']['disable']['default'] = 0;
$array['element']['disable']['set'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';



$array['filter'] = array();
$array['filter']['operator_id'] = array('set' => false,'maxlen' => 10,'regexp' => '/^[0-9]+$/');
$array['filter']['name'] = array('maxlen' => 128,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['exten'] = array('maxlen' => 40,'regexp' => '/^_?\+?[0-9NXZ\*#\-\[\]]+[\.\!]?$/');
$array['filter']['price'] = array('maxlen' => 10,'regexp' => '/^[0-9\.\,]+$/');
$array['filter']['price_is'] = array('maxlen' => 16,'key' => array('second','minute'));
$array['filter']['disable'] = array('bool' => true);
$array['filter']['description'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);

?>
