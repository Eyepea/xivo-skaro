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

include(dirname(__FILE__).'/common.php');

if(xivo::load_class('xivo_statistics_queue',XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics','queue',false) === false)
	die('Can\'t load xivo_statistics_queue object');

$stats_queue = new xivo_statistics_queue(&$_XOBJ,&$ipbx);

if (isset($_QR['confid']) === true)
	$stats_queue->set_idconf($_QR['confid']);

$_TPL->set_var('confid',$stats_queue->get_idconf());

$bench_end = microtime(true);
$_TPL->set_var('bench',($bench_end - $bench_start));

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics');

$_TPL->set_bloc('main',"statistics/index");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
