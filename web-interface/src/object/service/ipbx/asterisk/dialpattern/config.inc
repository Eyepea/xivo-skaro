<?php

#
# XiVO Web-Interface
# Copyright (C) 2020  Avencall
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

$array['element']['type'] = array();
$array['element']['type']['default'] = '';

$array['element']['typeid'] = array();
$array['element']['typeid']['default'] = '';

$array['element']['prefix'] = array();
$array['element']['prefix']['default'] = '';

$array['element']['externprefix'] = array();
$array['element']['externprefix']['default'] = '';

$array['element']['callerid'] = array();
$array['element']['callerid']['default'] = '';

$array['element']['exten'] = array();
$array['element']['exten']['default'] = '';

$array['element']['stripnum'] = array();
$array['element']['stripnum']['value'] = range(0,20);
$array['element']['stripnum']['default'] = 0;
$array['element']['stripnum']['setdef'] = true;

$array['filter'] = array();
$array['filter']['typeid'] =  array('cast' => 'ulongint');
$array['filter']['prefix'] =  array('set' => false,'chk' => 2,'maxlen' => 10,'regexp' => '/^(?:\+|\+?[0-9#\*]+)$/');
$array['filter']['externprefix'] = array('set' => false,'chk' => 2,'maxlen' => 20,'regexp' => '/^(?:\+|\+?[0-9#\*]+)$/');
$array['filter']['callerid'] = array('set'	=> false,
				     'chk'	=> 2,
				     'maxlen'	=> 80,
				     'regexp'	=> '/^'.XIVO_SRE_IPBX_AST_REGEXP_CALLERID.'$/u',
				     'notag'	=> false);
$array['filter']['type'] =  array('maxlen' => 32,'regexp' => '/^[a-z\-_]+$/');
$array['filter']['exten'] = array('maxlen' => 40,'regexp' => '/^_?\+?[0-9NXZ\*#\-\[\]]+[\.\!]?$/');
$array['filter']['stripnum'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(0,20));

?>
