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

require_once('xivo.php');

$ipbx = &$_SRE->get('ipbx');

dwho::load_class('dwho_http');
$http_response = dwho_http::factory('response');

$modattachment = &$ipbx->get_module('attachment');

$act = isset($_QR['act']) === false ? null : $_QR['act'];
$obj = isset($_QR['obj']) === false ? null : $_QR['obj'];
$id = isset($_QR['id']) === false ? null : (int) $_QR['id'];

switch ($obj)
{
    case null:
        if(($rs = $modattachment->get($id)) === false)
        {
            $http_response->set_status_line(400);
            $http_response->send(true);
        }
        break;
    default:
        $arr = array();
        $arr['object_type'] = $obj;
        $arr['object_id'] = $id;
        if(($rs = $modattachment->get_where($arr)) === false)
        {
            $http_response->set_status_line(400);
            $http_response->send(true);
        }
}

switch ($act)
{
    case 'download':
        header("Pragma: public"); // required 
        header("Expires: 0"); 
        header("Cache-Control: must-revalidate, post-check=0, pre-check=0"); 
        header("Cache-Control: private",false); // required for certain browsers 
        header("Content-Type: ".$rs['mime']); 
        header("Content-Disposition: attachment; filename=\"".$rs['name']."\";" ); 
        header("Content-Transfer-Encoding: binary"); 
        header("Content-Length: ".$rs['size']);
        break;
    case null:
    default: 
        header("Content-Type: ".$rs['mime']); 
}

ob_clean(); 
flush();
echo $rs['file'];
die();

?>