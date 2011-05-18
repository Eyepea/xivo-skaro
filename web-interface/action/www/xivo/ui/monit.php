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

$access_category = 'monit';
$access_subcategory = '';

include(dwho_file::joinpath(dirname(__FILE__),'common.php'));

$act = $_QRY->get('act');

switch($act)
{
	case 'request':
		$monitoring = &$_SRE->get('monitoring');
		
		if(isset($_QR['service'],$_QR['action']) === true)
		{
			switch($_QR['action'])
			{
				case 'start':
					$monitoring->start_service($_QR['service']);
					break;
				case 'stop':
					$monitoring->stop_service($_QR['service']);
					break;
				case 'restart':
					$monitoring->restart_service($_QR['service']);
					break;
				case 'monitor':
					$monitoring->enable_monitor($_QR['service']);
					break;
				case 'unmonitor':
					$monitoring->disable_monitor($_QR['service']);
					break;
				default:
					$http_response->set_status_line(400);
					$http_response->send(true);
					break;
			}
			$http_response->set_status_line(200);
			$http_response->send(true);
		}
		break;
	default:
		$http_response->set_status_line(400);
		$http_response->send(true);
		break;
}

?>