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

$access_category = 'cdr';
$access_subcategory = 'search';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$page = isset($_QR['page']) === true ? dwho_uint($_QR['page'],1) : 1;
$rows = isset($_QR['rows']) === true ? dwho_uint($_QR['rows']) : 10;

$cdr = &$ipbx->get_module('cdr');

$result = null;

if(isset($_QR['dbeg']) === true 
&& isset($_QR['dend']) === true)
{
	$limit = array();
	$limit[0] = ($page - 1) * $rows;
	$limit[1] = $rows;  
	
	if(($result = $cdr->search_grid($_QR,'calldate',$limit)) !== false && $result !== null)
		$total = $cdr->get_cnt();

	if($result === false)
		$info = null;
}

$return = array();
$return['total'] = dwho_uint($total/$rows+1);
$return['records'] = $total;
$return['page'] = $page;
$return['rows'] = $result;

dwho::load_class('dwho_http');
$http_response = dwho_http::factory('response');

$data = dwho_json::encode($return);

if($data === false)
{
	$http_response->set_status_line(500);
	$http_response->send(true);
}

header(dwho_json::get_header());
die($data);

?>