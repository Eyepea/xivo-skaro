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

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$act = $_QRY->get('act');

switch($act)
{
	case 'dialaction':
	default:
		$act   = 'dialaction';
		$page  = 'dialaction';

		$_TPL->set_var('event', $_QRY->get('event'));
		// need to load dialaction elements & default values
		$appschedule = &$ipbx->get_application('schedule');
		$_TPL->set_var('element', $appschedule->get_elements());
		$_TPL->set_var('destination_list', $appschedule->get_dialaction_destination_list());

		// load translations
		$_TPL->load_i18n_file('tpl/www/struct/service/ipbx/dialaction.i18n', 'global');
		$_TPL->load_i18n_file('tpl/www/bloc/service/ipbx/asterisk/call_management/voicemenu/add.i18n', 'global');

		break;
}

$_TPL->set_var('act', $act);
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/call_management/schedule/'.$page);

?>
