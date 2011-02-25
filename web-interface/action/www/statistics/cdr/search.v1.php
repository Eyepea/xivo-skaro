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

$act = isset($_QR['act']) === false ? 'search' : $_QR['act'];

$cdr = &$ipbx->get_module('cdr');
$element = $cdr->get_element();

$info = null;
$result = false;

if(isset($_QR['fm_send']) === true || isset($_QR['search']) === true)
{
	if(($info = $cdr->chk_values($_QR,false)) === false)
		$info = $cdr->get_filter_result();
	else
	{
		if(($result = $cdr->search($info,'calldate')) !== false && $result !== null)
			$total = $cdr->get_cnt();

		if($result === false)
			$info = null;
	}
}

$_TPL->set_var('element',$element);
$_TPL->set_var('info',$info);
$_TPL->set_var('result',$result);
$_TPL->set_var('act',$act);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');
$menu->set_toolbar('toolbar/statistics/cdr');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->set_js('js/statictics/cdr/cdr.js');
$dhtml->add_js('/struct/js/date.js.php');

$dhtml->set_css('js/jquery/jqGrid/css/ui.jqgrid.css');

$dhtml->set_js('js/jquery/jquery.jqGrid.min.js');
$dhtml->set_js('js/jquery/jqGrid/grid.loader.js');

$_TPL->set_bloc('main',"statistics/cdr/search");
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
