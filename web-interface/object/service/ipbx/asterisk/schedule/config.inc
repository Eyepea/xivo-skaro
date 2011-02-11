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

$array['element']['timezone'] = array();
$array['element']['timezone']['default'] = '';

$array['element']['fallback_action'] = array();
$array['element']['fallback_action']['default'] = '';

$array['element']['fallback_actionid'] = array();
$array['element']['fallback_actionid']['default'] = '';
$array['element']['fallback_actionid']['null'] = true;

$array['element']['fallback_actionargs'] = array();
$array['element']['fallback_actionargs']['default'] = '';

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['filter'] = array();
$array['filter']['name'] = array('maxlen' => 256);
$array['filter']['timezone'] = array('set' => false, 'chk' => 2);
$array['filter']['fallback_action'] = array('set' => false, 'chk' => 2);
$array['filter']['fallback_actionid'] = array('set' => false, 'chk' => 2);
$array['filter']['fallback_actionargs'] = array('set' => false, 'chk' => 2);
$array['filter']['description'] = array('set' => false, 'chk' => 2);
$array['filter']['commented'] = array('bool' => true);

?>
