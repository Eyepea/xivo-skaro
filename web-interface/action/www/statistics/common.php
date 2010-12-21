<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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

require(DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'pchart.inc');

$glibpchart = DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'pchart';
dwho_load_lib_pchart($glibpchart);

$gdir = XIVO_PATH_ROOT.DIRECTORY_SEPARATOR.'www/img/graphs/pchart/';
$basedir = '/img/graphs/pchart/';

$statistics = &$_TPL->get_module('statistics');

$_TPL->set_var('basedir',$basedir);

?>