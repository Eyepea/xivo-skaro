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

$access_category = 'cti';
$access_subcategory = 'accounts';

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

$act = $_QRY->get('act');

switch($act)
{
    case 'view':
    default:
        $act = 'view';

        $ctiaccounts = &$ipbx->get_module('ctiaccounts');
        if(($rs = $ctiaccounts->get_all()) === false
        || ($nb = count($rs)) === 0)
        {
        	$http_response->set_status_line(204);
        	$http_response->send(false);
        }

        $out = array();
        for ($i=0;$i<$nb;$i++)
        {
            $ref = &$rs[$i];
            $out[$i] = array();
            $out[$i]['id'] = "cs:".uniqid();
            $out[$i]['loginclient'] = $ref['login'];
            $out[$i]['passwdclient'] = $ref['password'];
            $out[$i]['profileclient'] = "ctiserver";
            $out[$i]['enableclient'] = true;
        }

        $_TPL->set_var('info',$out);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/genericjson');

?>
