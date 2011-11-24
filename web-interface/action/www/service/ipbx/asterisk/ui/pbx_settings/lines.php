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

if(defined('XIVO_LOC_UI_ACL_CATEGORY') === true
&& defined('XIVO_LOC_UI_ACL_SUBCATEGORY') === true)
{
	$access_category = XIVO_LOC_UI_ACL_CATEGORY;
	$access_subcategory = XIVO_LOC_UI_ACL_SUBCATEGORY;
}
else
{
	$access_category = 'pbx_settings';
	$access_subcategory = 'lines';
}

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

if(defined('XIVO_LOC_UI_ACTION') === true)
	$act = XIVO_LOC_UI_ACTION;
else
	$act = $_QRY->get('act');
	
$order = array('name' => SORT_ASC);		

switch($act)
{
	case 'search':
		$act = 'search';
		$appline = &$ipbx->get_application('line',null,false);
		
		$context = $_QRY->get('context');

		if(($list = $appline->get_lines_search($_QRY->get('search'),$context)) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
		break;
	case 'contexts':
		$act = 'contexts';
		$appline = &$ipbx->get_application('line',null,false);
		$appcontext = &$ipbx->get_application('context',null,false);
		
		$contexttype = $_QRY->get('contexttype');
		$entityid = $_QRY->get('entityid');
		$free = $_QRY->get('free');
		
		if(($listcontext = $appcontext->get_contexts_list(null,null,$order,false,$contexttype)) === false
		|| ($nb_contexts = count($listcontext)) === 0)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}
		
		$rscontexts = array();
		for($i=0;$i<$nb_contexts;$i++)
		{
			$ref = $listcontext[$i];
			if (isset($ref['context']) === false
			|| $ref['entity']['id'] !== $entityid)
				continue;
			$rscontexts[] = $ref['context']['name'];
		}
		
		if(($list = $appline->get_lines_contexts($rscontexts,null,null,$order,null,false,null,$free)) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$_TPL->set_var('list',$list);
		break;
	case 'list':
	default:
		$appline = &$ipbx->get_application('line');
		
		if(($list = $appline->get_lines_contexts(null,null,$order,null,false,null,true)) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}
		
		$_TPL->set_var('list',$list);
		break;
}

$_TPL->set_var('act',$act);
$_TPL->display('/service/ipbx/'.$ipbx->get_name().'/pbx_settings/generic');

?>
