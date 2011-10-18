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

/*
 *

$_QRY->get('context')
eg. default, intern ......

$_QRY->get('obj')
eg. user, group ...

$_QRY->get('startnum')
eg. 80, 422 ...

$_QRY->get('except')
eg.

 *
 */

switch($act)
{
	case 'search':
	default:
		$act = 'search';
		$appcontext = &$ipbx->get_application('context');
		$context = $_QRY->get('context');
		if(($context = $appcontext->get($context)) === false)
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

		if (is_null($_QRY->get('startnum')) === false)
			$filter  = $_QRY->get('startnum');
		elseif(is_null($_QRY->get('q')) === false)
			$filter  = $_QRY->get('q');

		if(strlen($filter) > 0 && !is_numeric($filter))
		{
			$_TPL->set_var('list', array());
			$_TPL->set_var('except',$_QRY->get('except'));
			break;
		}

		$filter  = intval($filter);
		$lfilter = floor(log10($filter)) + 1;

		$numbers = array();
		$list_pool_free = array();
		foreach($context['contextnumbers'][$obj] as $numb)
		{
			$start = intval($numb['numberbeg']);
			$end   = intval($numb['numberend']);
			$lstart = floor(log10($start)) + 1;
			$lend   = floor(log10($end)) + 1;

			array_push($list_pool_free,array('numberbeg' => $start, 'numberend' => $end));

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

		if ($_QRY->get('getnumpool') !== null)
		{
			$_TPL->set_var('list', $list_pool_free);
			$_TPL->set_var('act',$act);
			$_TPL->display('genericjson');
			return;
		}

		foreach($context['contextnummember'][$obj] as $user)
		{
			if(strlen($user['number']) > 0 &&
				($idx = array_search($user['number'], $numbers)) !== false)
				unset($numbers[array_search($user['number'], $numbers)]);
		}

		switch ($_QRY->get('format'))
		{
			case 'jquery':
				$list = '';
				foreach(array_values($numbers) as $num)
					$list .=  $num."\n";
				break;
			case null:
			default:
				$list = array();
				// just to respect suggest.js data format
				foreach(array_values($numbers) as $num)
					$list[] = array('id' => $num, 'identity' => strval($num), 'info' => '');
		}

		$_TPL->set_var('list', $list);
		$_TPL->set_var('except',$_QRY->get('except'));
		break;
}

$_TPL->set_var('act',$act);
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/pbx_settings/extension');

?>
