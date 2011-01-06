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

$array['element']['timezone'] = array();
$array['element']['timezone']['default'] = '';

$array['element']['exchange_trunkid'] = array();
$array['element']['exchange_trunkid']['default'] = '';
$array['element']['exchange_trunkid']['null'] = true;

$array['element']['exchange_exten'] = array();
$array['element']['exchange_exten']['default'] = '';
$array['element']['exchange_exten']['null'] = true;

dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['timezone']         = array('set' => false, 'chk' => 2);
$array['filter']['exchange_trunkid'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['exchange_exten']   = array('set' => false, 'chk' => 2);

?>
