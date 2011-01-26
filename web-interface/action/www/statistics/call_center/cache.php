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

dwho::load_class('dwho_prefs');
$prefs = new dwho_prefs('cache');

$act     = isset($_QR['act']) === true ? $_QR['act'] : '';
$page    = dwho_uint($prefs->get('page', 1));
$search  = strval($prefs->get('search', ''));
$sort    = $prefs->flipflop('sort', 'name');

$param = array();
$param['act'] = 'list';
	
if(xivo::load_class('xivo_statistics',XIVO_PATH_OBJECT,null,false) === false)
	die('Failed to load xivo_statistics object');
	
$_XS = new xivo_statistics(&$_XOBJ,&$ipbx);

if(isset($_QR['idconf']) === false
|| ((int) $idconf = $_QR['idconf']) === 0
|| $_XS->set_idconf($_QR['idconf']) === false
|| $_XS->load_component() === false)
	return;

switch($act)
{
	/*
	case 'enables':
	case 'disables':
		$param['page'] = $page;

		if(($values = dwho_issa_val('stats_conf',$_QR)) === false)
			$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);

		$nb = count($values);

		for($i = 0;$i < $nb;$i++)
		{
			if($appstats_conf->get($values[$i]) === false)
				continue;
			else if($act === 'disables')
				$appstats_conf->disable();
			else
				$appstats_conf->enable();
		}

		$_QRY->go($_TPL->url('statistics/call_center/configuration'),$param);
		break;
	*/
	case 'test':
		$act = 'test';
		if(xivo::load_class('xivo_statistics_period',
			XIVO_PATH_OBJECT.DWHO_SEP_DIR.'statistics',
			'period',false) === false)
			die('Can\'t load xivo_statistics_period object');
		
		$stats_period = new xivo_statistics_period(&$_XS);
		
		$dend = strtotime($interval['max']);
		$dbeg = mktime(0,0,0,date('m',$dend)-1,1,date('Y',$dend));
		$_XS->generate_cache($idconf,$dbeg,$dend,'period');
		$full_interval = array();
		$full_interval['beg'] = $dbeg;
		$full_interval['end'] = $dend;
		$_XS->_interval_process = $full_interval;
		$stats_period->parse_log('queue8001',4);		
		var_dump($stats_period->_result[4]);
		break;
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
			
			if (($appqueue_log = &$ipbx->get_application('queue_log')) === false
			|| ($interval = $appqueue_log->get_min_and_max_time()) === false)
				break;		
			
			$dbeg = strtotime($interval['min']);
			$dend = strtotime($interval['max']);
		
			$listmonth = $_XS->get_listmonth_for_interval($dbeg,$dend);
			
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
#$menu->set_toolbar('toolbar/statistics/call_center/configuration');

$dhtml = &$_TPL->get_module('dhtml');
$dhtml->set_js('js/dwho/submenu.js');
$dhtml->set_js('js/dwho/uri.js');
$dhtml->set_js('js/dwho/http.js');
$dhtml->set_js('js/statistics/call_center/genercache.js');

$_TPL->set_bloc('main','statistics/call_center/cache/'.$act);
$_TPL->set_struct('statistics/index');
$_TPL->display('index');

?>
