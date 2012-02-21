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

$step = $_QRY->get('step');

$_TPL->load_i18n_file('tpl/www/struct/page/redirect.i18n', 'global');

$appwizard = &$_XOBJ->get_application('wizard');
$code = 400;

switch($step)
{
	case 'commit_db_data':
		if($appwizard->commit_db_data() !== false)
			$code = 200;
		echo 'next::commit_syslanguage::', $_TPL->bbf('commit_syslanguage');
		break;
	case 'commit_syslanguage':
		if($appwizard->commit_syslanguage() !== false)
			$code = 200;
		echo 'next::commit_sysdbconfig::', $_TPL->bbf('commit_sysdbconfig');
		break;
	case 'commit_sysdbconfig':
		if($appwizard->commit_sysdbconfig() !== false)
			$code = 200;
		echo 'next::set_default_provisioning_values::', $_TPL->bbf('set_default_provisioning_values');
		break;
	case 'set_default_provisioning_values':
		if($appwizard->set_default_provisioning_values() !== false)
			$code = 200;
		echo 'next::commit_finished::',
			$_TPL->bbf('commit_netinfos'),
			'<br />',
			$_TPL->bbf('commit_commonconf'),
			'<br />',
			$_TPL->bbf('redirect_message');
		break;
	case 'commit_finished':
		$url = $appwizard->discover_finish_uri();
		if($appwizard->commit_netinfos() !== false
		&& $appwizard->commit_commonconf() !== false)
			$code = 200;
		echo 'redirecturi_on_success::'.$url;
		break;
	default:
		$code = 200;
		echo 'next::commit_db_data::', $_TPL->bbf('commit_db_data');
		break;
}

if ($code === 400)
	echo dwho_report::get_message('error');

$http_response->set_status_line($code);
$http_response->send(true);

?>