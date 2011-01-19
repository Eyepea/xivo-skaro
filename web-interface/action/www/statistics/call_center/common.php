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

$_I18N->load_file('tpl/www/bloc/statistics/statistics');

$bench_start = microtime(true);

$gdir = XIVO_PATH_ROOT.DIRECTORY_SEPARATOR.'www/img/graphs/pchart/';
$basedir = '/img/graphs/pchart/';

$appstats_conf = &$_XOBJ->get_application('stats_conf');

if(xivo::load_class('xivo_statistics',XIVO_PATH_OBJECT,null,false) === false)
	die('Failed to load xivo_statistics object');
	
$_XS = new xivo_statistics(&$_XOBJ,&$ipbx);

$_XS->global_init($_QR);
$_XS->load_component();

$_TPL->set_var('basedir',$basedir);
$_TPL->set_var('listconf',$appstats_conf->get_stats_conf_list(null,'name'));
$_TPL->set_var('listaxetype',$_XS->get_list_axtype());
$_TPL->set_var('infocal',$_XS->get_infocal());
$_TPL->set_var('confid',$_XS->get_idconf());
$_TPL->set_var('conf',$_XS->get_conf());

$tpl_statistics = &$_TPL->get_module('statistics');
$tpl_statistics->set_basedir($basedir);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/statistics/call_center/conf.js');

?>