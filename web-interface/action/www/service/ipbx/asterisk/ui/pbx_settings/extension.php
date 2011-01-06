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

if(defined('XIVO_LOC_UI_ACL_CATEGORY') === true
&& defined('XIVO_LOC_UI_ACL_SUBCATEGORY') === true)
{
	$access_category = XIVO_LOC_UI_ACL_CATEGORY;
	$access_subcategory = XIVO_LOC_UI_ACL_SUBCATEGORY;
}
else
{
	$access_category = 'pbx_settings';
	$access_subcategory = 'extension';
}

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(defined('XIVO_LOC_UI_ACTION') === true)
	$act = XIVO_LOC_UI_ACTION;
else
	$act = $_QRY->get('act');

switch($act)
{
	case 'search':
	default:
		$act = 'search';
		$appcontext = &$ipbx->get_application('context');
		if(($context    = $appcontext->get($_QRY->get('context'))) === false)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		}		

		$obj = $_QRY->get('obj');
		if(is_null($obj) || !array_key_exists($obj, $context['contextnumbers']))
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		}		

		$filter  = $_QRY->get('startnum');
		if(strlen($filter) > 0 && !is_numeric($filter))
		{
			$_TPL->set_var('list', array());
			$_TPL->set_var('except',$_QRY->get('except'));
			break;
		}

		$filter  = intval($filter);
		$lfilter = floor(log10($filter)) + 1;

		//var_dump($context['contextnumbers']['user'],
		//	$context['contextnummember']['user']);
		$numbers = array();
		foreach($context['contextnumbers'][$obj]as $numb)
		{
			$start = intval($numb['numberbeg']);
			$end   = intval($numb['numberend']);
			$lstart = floor(log10($start)) + 1;
			$lend   = floor(log10($end)) + 1;

			if($lfilter > $lend)
				continue;

			$fstart = intval($start / pow(10, $lstart - $lfilter));
			$fend   = intval($end   / pow(10, $lend   - $lfilter));
			if($filter < $fstart || $fend < $filter)
				continue;

			$start = max($start, $filter * (pow(10, $lstart - $lfilter)));
			$end   = min($end  , ($filter+1) * (pow(10, $lend   - $lfilter)) - 1);

			$numbers = array_merge($numbers, range($start, $end));
		}

		foreach($context['contextnummember'][$obj] as $user)
		{
			if(strlen($user['number']) > 0 && 
				($idx = array_search($user['number'], $numbers)) !== false)
				unset($numbers[array_search($user['number'], $numbers)]);
		}

		// just to respect suggest.js data format
		$list = array();
		foreach(array_values($numbers) as $num)
			$list[] = array('id' => $num, 'identity' => strval($num), 'info' => '');

		$_TPL->set_var('list', $list);
		$_TPL->set_var('except',$_QRY->get('except'));
		break;
}

$_TPL->set_var('act',$act);
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/pbx_settings/extension');

?>
