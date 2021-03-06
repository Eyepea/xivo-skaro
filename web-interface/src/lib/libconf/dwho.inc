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

$array['ini'] = array();

$array['ini']['error'] = array(
                'level'        => 2047,
                'report_type'    => 7,
                'report_mode'    => 1,
                'report_func'    => 1,
                'email'        => null,
                'file'        => null);

$array['ini']['locale'] = array(
                'language'    => 'en',
                'territory'    => 'US',
                'charset'    => 'UTF-8');

$array['ini']['session'] = array(
                'name'        => '_eid',
                'time'        => 7200,
                'path'        => '/',
                'save_path'    => null);

?>
