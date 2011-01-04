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

$bench_start = microtime(true);

$gdir = XIVO_PATH_ROOT.DIRECTORY_SEPARATOR.'www/img/graphs/pchart/';
$basedir = '/img/graphs/pchart/';

if(xivo::load_class('xivo_statistics',XIVO_PATH_OBJECT,null,false) === false)
	die('Can\'t load xivo_statistics object');

$xivo_statistics = new xivo_statistics();

$appstats_conf = &$_XOBJ->get_application('stats_conf');
$list = $appstats_conf->get_stats_conf_list();
$_TPL->set_var('listconf',$list);
$_TPL->set_var('basedir',$basedir);

?>