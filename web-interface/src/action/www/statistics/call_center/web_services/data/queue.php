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

$access_category = 'statistics';
$access_subcategory = 'call_center';

include(dwho_file::joinpath(dirname(__FILE__),'..','_common.php'));

$act = $_QRY->get('act');

switch($act)
{
	case 'listshowstatus':
		$act = 'listshowstatus';
		$appqueue = &$ipbx->get_application('queue',null,false);

		if(($queuelist = $appqueue->get_queues_list()) === false)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$cmd = &$ipbx->get_module('ami')->cmd('queue show',true);

		$list = array();
		foreach($cmd as $line)
		{
			if (preg_match('/^([a-z0-9_\.\-]{1,128}) /',$line,$qn) === 1
			&& preg_match('/([0-9]+)s holdtime,/',$line,$ht) === 1)
			{
				$tmp = array();
				$tmp['name'] = $qn[1];
				$tmp['holdtime'] = $ht[1];
				array_push($list,$tmp);
			}
		}

		$_TPL->set_var('list',$list);
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
}

$_TPL->set_var('act',$act);
$_TPL->display('/statistics/call_center/generic');

?>
