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

$array['element']['schedule_id'] = array();
$array['element']['schedule_id']['default'] = '';

$array['element']['mode'] = array();
$array['element']['mode']['value'] = array('opened','closed');
$array['element']['mode']['default'] = '';

$array['element']['hours'] = array();
$array['element']['hours']['default'] = '';
$array['element']['hours']['null'] = true;

$array['element']['weekdays'] = array();
$array['element']['weekdays']['default'] = '';
$array['element']['weekdays']['null'] = true;

$array['element']['monthdays'] = array();
$array['element']['monthdays']['default'] = '';
$array['element']['monthdays']['null'] = true;

$array['element']['months'] = array();
$array['element']['months']['default'] = '';
$array['element']['months']['null'] = true;

$array['element']['action'] = array();
$array['element']['action']['default'] = '';
$array['element']['action']['null'] = true;

$array['element']['actionid'] = array();
$array['element']['actionid']['default'] = '';
$array['element']['actionid']['null'] = true;

$array['element']['actionargs'] = array();
$array['element']['actionargs']['default'] = '';
$array['element']['actionargs']['null'] = true;

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['filter'] = array();
$array['filter']['schedule_id'] = array('set' => false, 'chk' => 2);
$array['filter']['mode'] = array('set' => false, 'chk' => 2, 'key' => array('opened','closed'));
$array['filter']['hours'] = array('set' => false, 'chk' => 2);
$array['filter']['weekdays'] = array('set' => false, 'chk' => 2);
$array['filter']['monthdays'] = array('set' => false, 'chk' => 2);
$array['filter']['months'] = array('set' => false, 'chk' => 2);
$array['filter']['action'] = array('set' => false, 'chk' => 2);
$array['filter']['actionid'] = array('set' => false, 'chk' => 2);
$array['filter']['actionargs'] = array('set' => false, 'chk' => 2);
$array['filter']['commented'] = array('bool' => true);

?>
