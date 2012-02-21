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

$access_category = 'system_management';
$access_subcategory = 'extensions';

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

		$context = $_QRY->get('context');

		if(($context = $appcontext->get($context)) === false)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		}

		$obj = $_QRY->get('obj');
		if(is_null($obj) || !array_key_exists($obj, $context['contextnumbers']))
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$number  = $_QRY->get('number');
		if(strlen($number) > 0 && !is_numeric($number))
		{   
			$http_response->set_status_line(500);
			$http_response->send(true);
		}   

		$numbers = array();
		foreach($context['contextnumbers'][$obj] as $numb)
		{   
			$start = intval($numb['numberbeg']);
			if(strlen($numb['numberend']) == 0)
			{
				array_push($numbers, $start);
				continue;
			}

			$end     = intval($numb['numberend']);
			$numbers = array_merge($numbers, range($start, $end));
		}

		if(strlen($number) > 0)
		{
			function match($val)
			{
				global $number;
				return (strpos(strval($val), $number) !== false);
			}
			$numbers = array_filter($numbers, "match");
		}


		foreach($context['contextnummember'][$obj] as $user)
		{
			if(strlen($user['number']) > 0 &&
			  ($idx = array_search(intval($user['number']), $numbers)) !== false)
					unset($numbers[$idx]);
		}


		$_TPL->set_var('list', array_values($numbers));
		break;
}

$_TPL->set_var('act',$act);
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/generic');

?>
