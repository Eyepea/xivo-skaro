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

$total = 0;
$cats = false;

if($cat === '')
	$cat = false;

if(($infos = $musiconhold->get_category($cat)) === false)
	$_QRY->go($_TPL->url('service/ipbx/pbx_services/musiconhold'),'act=list');

if(($files = $infos['dir']['files']) !== false)
{
	$total = count($files);
	dwho::load_class('dwho_sort');
	$sort = new dwho_sort(array('key' => 'name'));
	usort($files,array(&$sort,'strnat_usort'));
}

$_TPL->set_var('pager',dwho_calc_page($page,20,$total));
$_TPL->set_var('list',$files);

?>
