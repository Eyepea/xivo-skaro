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

$access_category = 'general_settings';
$access_subcategory = 'sip';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));


$appsip = &$ipbx->get_apprealstatic('sip');
$appgeneralsip = &$appsip->get_module('general');
$modauth = &$ipbx->get_module('sipauthentication');

$act = $_QRY->get('act');

switch($act)
{
	case 'view':
	default:
		$info = $appgeneralsip->get_all_val_by_category();

		// mwi and register MUST be list of values
		if(array_key_exists('mwi', $info) && !is_array($info['mwi'][0]))
			$info['mwi'] = array($info['mwi']);
		if(array_key_exists('register', $info) && !is_array($info['register'][0]))
			$info['register'] = array($info['register']);

		$info['authentication'] = $modauth->get_all_where(array('usersip_id' => null));

		$_TPL->set_var('info',$info);
		break;

}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
