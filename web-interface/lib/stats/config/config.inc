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

$array['module'] = array();

$array['module']['agentfeatures'] = array();
$array['module']['agentfeatures']['datastorage'] = true;

$array['module']['queuefeatures'] = array();
$array['module']['queuefeatures']['datastorage'] = true;

$array['module']['cdr'] = array();
$array['module']['cdr']['datastorage'] = array();
$array['module']['cdr']['datastorage']['custom'] = true;

$array['module']['cel'] = array();
$array['module']['cel']['datastorage'] = true;

$array['module']['queue_log'] = array();
$array['module']['queue_log']['datastorage'] = true;


?>
