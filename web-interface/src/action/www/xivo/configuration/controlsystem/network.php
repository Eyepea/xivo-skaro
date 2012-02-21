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
/*
*/

$appnetiface = &$_XOBJ->get_application('netiface');

if($appnetiface->commit_sysconfnet() !== false
|| $appnetiface->update_server() !== false) {
	$currentiface = $appnetiface->discover_current_interface();

	dwho_report::push('info',dwho_i18n::babelfish('successfully_apply',
					array(dwho_i18n::babelfish('network_config'))));
	$appnetiface->changes_executed();

	if(is_array($currentiface) === true
	&& isset($currentiface['name']) === true
	&& ($uri = $appnetiface->get_redirect_uri(
			$appnetiface->get_result_var('netiface', 'ifname'),
			$currentiface['name'])) !== false)
	{
		$_TPL->set_var('redirect_url',$uri.$_TPL->url('xivo/configuration/network/interface'));
		$_TPL->set_var('redirect_url_query',array());
		$_TPL->set_var('redirect_seconds',5);
		$_TPL->display('redirect');
		die;
	}

	$_QRY->go($_TPL->url('xivo/configuration/network/interface'));
}

?>
