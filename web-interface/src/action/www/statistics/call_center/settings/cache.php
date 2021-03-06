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

if(xivo_user::chk_acl('settings','cache') === false)
	$_QRY->go($_TPL->url('statistics/call_center'));

$_I18N->load_file('tpl/www/bloc/statistics/call_center/settings/cache');

dwho::load_class('dwho_date');
dwho::load_class('dwho_prefs');
$prefs = new dwho_prefs('cache');

$act     = isset($_QR['act']) === true ? $_QR['act'] : 'list';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';

require_once(dwho_file::joinpath(XIVO_PATH_OBJECT,'stats','stats.inc'));
$_XS = new xivo_stats_lib();

if(isset($_QR['idconf']) === false
|| ((int) $idconf = $_QR['idconf']) === 0
|| $_XS->set_idconf($_QR['idconf']) === false
|| $_XS->load_component() === false)
	$_QRY->go($_TPL->url('statistics/call_center/settings/configuration'),$param);

$stats_conf = $_XS->get_conf();

switch($act)
{
	case 'list':
	default:
		$act = 'list';
		if (isset($_QR['type']) === true)
		{
			$typeprocess = $_QR['type'];
			$listype = $_XS->get_listtype();
			while ($listype)
			{
				$type = array_shift($listype);
				if (($list = $_XS->get_list_by_type($type)) === false
				&& $type !== $typeprocess)
					continue;
				$_TPL->set_var('list'.$type,$list);
			}
			$_TPL->set_var('type',$typeprocess);

			$dbeg = $stats_conf['dbegcache'];
			$dend = $stats_conf['dendcache'];

			if (($listmonth = dwho_date::get_listmonth_for_interval($dbeg,$dend)) === false)
				break;

			$_TPL->set_var('listmonth',$listmonth);
			$_TPL->set_var('dbeg',$dbeg);
			$_TPL->set_var('dend',$dend);
		}
}

$_TPL->set_var('act',$act);
$_TPL->set_var('ifconf',$idconf);
$_TPL->set_var('conf',$_XS->get_conf());
$_TPL->set_var('listtype',$_XS->get_listtype());

$menu = &$_TPL->get_module('menu');
$menu->set_top('top/user/'.$_USR->get_info('meta'));
$menu->set_left('left/statistics/statistics');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/statistics/call_center/settings/genercache.js');

$_TPL->set_bloc('main','statistics/call_center/settings/cache/'.$act);
$_TPL->set_struct('statistics/index');
$_TPL->display('index');


?>
