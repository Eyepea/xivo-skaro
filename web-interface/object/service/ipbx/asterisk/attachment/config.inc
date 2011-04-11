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

$array['element']['file'] = array();
$array['element']['file']['default'] = '';

$array['element']['object_type'] = array();
$array['element']['object_type']['default'] = '';

$array['element']['object_id'] = array();
$array['element']['object_id']['default'] = '';

$array['element']['size'] = array();
$array['element']['size']['default'] = 0;

$array['element']['mime'] = array();
$array['element']['mime']['default'] = '';

$array['filter'] = array();
$array['filter']['name'] = array('maxlen' => 64,'regexp' => '/^[a-z0-9\-._]+$/i');
$array['filter']['file'] = array('set' => true);
$array['filter']['object_type'] = array('maxlen' => 16,'regexp' => '/^[a-z]+$/');
$array['filter']['object_id'] = array('cast' => 'ulongint');
$array['filter']['mime'] = array('maxlen' => 16,'regexp' => '/^[a-z0-9\/]+$/');
$array['filter']['size'] = array('cast' => 'ulongint');

?>
