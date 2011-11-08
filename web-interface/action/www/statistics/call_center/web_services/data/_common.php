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

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'date.inc'));

$act = isset($_QR['act']) === true ? $_QR['act'] : '';

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'stats','stats.inc'));

$_XS = new xivo_stats_lib();
$_XS->global_init($_QR);

$axetype = $_XS->get_axetype();

$_TPL->set_var('listaxetype',$_XS->get_list_axetype());
$_TPL->set_var('axetype',$axetype);
$_TPL->set_var('infocal',$_XS->get_datecal());
$_TPL->set_var('confid',$_XS->get_idconf());
$_TPL->set_var('conf',$_XS->get_conf());

$tpl_statistics = &$_TPL->get_module('statistics');
$tpl_statistics->set_xs(&$_XS);

?>
