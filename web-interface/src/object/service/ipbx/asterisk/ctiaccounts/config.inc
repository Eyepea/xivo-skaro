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

$array['element']['label'] = array();
$array['element']['label']['default'] = '';

$array['element']['login'] = array();
$array['element']['login']['default'] = '';

$array['element']['password'] = array();
$array['element']['password']['default'] = '';

$array['filter'] = array();
$array['filter']['label'] = array('cast' => 'sgraph','minlen' => 3,'maxlen' => 64);
$array['filter']['login'] = array('cast' => 'sgraph','minlen' => 3,'maxlen' => 64);
$array['filter']['password'] = array('cast' => 'sgraph','minlen' => 3,'maxlen' => 64);

?>
