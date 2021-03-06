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
$access_subcategory = 'advanced';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$info = array();
$appagents = &$ipbx->get_apprealstatic('agents');
$appgeneralagents = &$appagents->get_module('general');
$info['generalagents'] = $appgeneralagents->get_all_by_category();

$appoptionsagents = &$appagents->get_module('agentoptions');
$info['agentoptions']  = $appoptionsagents->get_all_by_category();

$appqueues = &$ipbx->get_apprealstatic('queues');
$appgeneralqueues = &$appqueues->get_module('general');

$appmeetme = &$ipbx->get_apprealstatic('meetme');
$appgeneralmeetme = &$appmeetme->get_module('general');

$appuserguest = &$ipbx->get_application('user',array('internal' => 1),false);

$general   = &$ipbx->get_module('general');


$info['generalqueues'] = $appgeneralqueues->get_all_by_category();
$info['generalmeetme'] = $appgeneralmeetme->get_all_by_category();
$info['general']       = $general->get(1);

$guest = $appuserguest->get_where(array('name' => 'guest'),null,true);
$info['guest_active'] = !$guest['commented'];

$act = $_QRY->get('act');

switch($act)
{
	case 'view':
	default:
		//$info = $appgeneraliax->get_all_val_by_category();

		$_TPL->set_var('info',$info);
		break;

}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
