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

$access_category = 'dundi';
$access_subcategory = 'mappings';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$apppeer = &$ipbx->get_application('dundimapping');

$act = $_QRY->get('act');
$serverid = $_QRY->get('serverid');

switch($act)
{
	case 'list':
	default:
		$act = 'list';
		
		$moddundi = &$ipbx->get_module('dundi');

		if($serverid === null)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		}

		if(($list = $moddundi->list_mappings($serverid)) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/struct/page/genericjson');

?>
