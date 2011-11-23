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

$access_category = 'ressources';
$access_subcategory = 'agents';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$act = $_QRY->get('act');

switch($act)
{
	case 'view':
		if ($_QRY->get('id') === null
		&& $_QRY->get('number') === null)
		{
			$http_response->set_status_line(404);
			$http_response->send(true);
		}
		$appagent = &$_STS->get_application('agent',null,false);
		
		$type = $_QRY->get('id') === null ? 'number' : 'id';

		$status = -1;
		switch ($type)
		{
			case 'number':
				if(($info = $appagent->get_by_number($_QRY->get('number'))) === false)
					$status = 204;
				break;
			case 'id':
			default:
				if(($info = $appagent->get($_QRY->get('id'))) === false)
					$status = 204;
		}
		
		if ($status === 204)
		{
			$http_response->set_status_line($status);
			$http_response->send(true);
		}

		$_TPL->set_var('info',$info);
		break;
	case 'add':
		$appagent = &$_STS->get_application('agent');
		$status = $appagent->add_from_json() === true ? 200 : 400;
		$http_response->set_status_line($status);
		$http_response->send(true);
		break;
	case 'delete':
		$appagent = &$_STS->get_application('agent');

		if($appagent->get($_QRY->get('id')) === false)
			$status = 404;
		else if($appagent->delete() === true)
		{
			$status = 200;
		}
		else
			$status = 500;

		$http_response->set_status_line($status);
		$http_response->send(true);
		break;
	case 'search':
		$appagent = &$_STS->get_application('agent',null,false);

		if(($list = $appagent->get_agents_search($_QRY->get('search'))) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
		break;
	case 'list':
	default:
		$act = 'list';

		$appagent = &$_STS->get_application('agent',null,false);

		if(($list = $appagent->get_agents_list()) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/genericjson');

?>
