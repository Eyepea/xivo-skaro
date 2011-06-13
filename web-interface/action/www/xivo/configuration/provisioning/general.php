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

$provdplugin = &$_XOBJ->get_module('provdplugin');
$provdconfig = &$_XOBJ->get_module('provdconfig');
$appprovisionning = &$_XOBJ->get_application('provisioning');

$info = array();
$info['configure'] = $provdplugin->get_infos_server();
$info['provd'] = $appprovisionning->get();

if(isset($_QR['act']) === true
&& $_QR['act'] === 'reset')
{
	if ($provdconfig->eval_required_config(null,true) === false)
		dwho_report::push('error','error_during_update');
	else
		dwho_report::push('info','successfully_updated');
}

if(isset($_QR['fm_send']) === true
&& isset($_QR['configure']) === true
&& isset($_QR['provd']) === true)
{
	if($appprovisionning->set($_QR['provd']) === false)
		dwho_report::push('error','error_during_update');
	else
	{
		dwho_report::push('info','successfully_updated');
		if($provdplugin->edit_infos_server($_QR['configure']) === false)
			dwho_report::push('error','can\'t update configure server');
				
		$_QRY->go($_TPL->url('xivo/configuration/provisioning/general'));
	}
	 			
	$info = array_merge($info,$_QR);
}


$_TPL->set_var('info', $info);

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/xivo/configuration');
$menu->set_toolbar('toolbar/xivo/configuration/provisioning/general');

$_TPL->set_bloc('main','xivo/configuration/provisioning/general');
$_TPL->set_struct('xivo/configuration');
$_TPL->display('index');

?>
