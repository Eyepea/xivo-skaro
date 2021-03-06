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

$bench_start = microtime(true);
$base_memory = memory_get_usage();

$_I18N->load_file('tpl/www/bloc/statistics/statistics');

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'date.inc'));
require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'stats','stats.inc'));
include(dwho_file::joinpath(DWHO_PATH_ROOT,'jqplot.inc'));

$xivo_jqplot = new xivo_jqplot;

$act = isset($_QR['act']) === true ? $_QR['act'] : '';

$appstats_conf = &$_XOBJ->get_application('stats_conf');

$_XS = new xivo_stats_lib();
$_XS->global_init($_QR);

$conf = $_XS->get_conf();

if ($conf !== false
&& $_SESSION['_USR']->meta === 'admin'
&& $conf['client'] !== STATS_CLIENT)
{
	$_SESSION['statsdb'] = $conf['statsdb'];
	$_QRY->go($_TPL->url('statistics/call_center'.$_SERVER['PATH_INFO']));
}

$axetype = $_XS->get_axetype();

$userid = false;
if ($_USR->_info['meta'] === 'admin')
	$userid = $_USR->_info['id'];

$order_conf = array('name' => SORT_ASC);
$_TPL->set_var('listconf',$appstats_conf->get_stats_conf_list(null,$order_conf,null,false,$userid));
$_TPL->set_var('listaxetype',$_XS->get_list_axetype());
$_TPL->set_var('axetype',$axetype);
$_TPL->set_var('infocal',$_XS->get_datecal());
$_TPL->set_var('confid',$_XS->get_idconf());
$_TPL->set_var('conf',$conf);

$tpl_statistics = &$_TPL->get_module('statistics');
$tpl_statistics->set_xs(&$_XS);

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/statistics/common.js');

?>
