<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2012  Avencall
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

$array['element']['category'] = array();
$array['element']['category']['default'] = '';

$array['element']['option_name'] = array();
$array['element']['option_name']['default'] = '';

$array['element']['option_value'] = array();
$array['element']['option_value']['default'] = '';

$array['filter'] = array();

$array['filter']['category'] = array('set' => false,'chk' => 2,'cast' => 'sgraph','maxlen' => 128);
$array['filter']['option_name'] = array('set' => false,'chk' => 2,'cast' => 'sgraph','maxlen' => 128);
$array['filter']['option_value'] = array('set' => false,'chk' => 2);

?>
