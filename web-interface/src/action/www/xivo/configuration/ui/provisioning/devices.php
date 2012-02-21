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

$ipbx = &$_SRE->get('ipbx');
$act = $_QRY->get('act');

$code = 400;
$provddevice = &$_XOBJ->get_module('provddevice');

switch($act)
{
	case 'synchronize':
		$appdevice = &$ipbx->get_application('device',null,false);

		if(isset($_QR['id']) === false
		|| ($info = $appdevice->get($_QR['id'])) === false
		|| ($location = $provddevice->synchronize($info['devicefeatures']['deviceid'])) === false)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}
		die($location);
		break;
	case 'request_oip':
		if(dwho::load_class('dwho_json') === false)
		{
			$http_response->set_status_line(500);
			$http_response->send(true);
		}
		elseif (isset($_QR['path']) === false
		|| ($path = urldecode($_QR['path'])) === false
		|| ($data = $provddevice->request_oip($path)) === false
		|| isset($data['status']) === false)
		{
			$http_response->set_status_line(400);
			$http_response->send(true);
		}

		$status = $data['status'];
		$regex = '/(?:(\w+)\|)?(\w+)(?:;(\d+)(?:\/(\d+))?)?/';
		preg_match_all($regex,$status,$out);

		if (($nbout = count($out)) === 0
		|| ($nb = count($out[0])) === 0)
		{
			$http_response->set_status_line(204);
			$http_response->send(true);
		}

		$code = 400;
		$header = array_shift($out);
		$nbout--;

		$res = array();
		for ($i=0;$i<$nbout;$i++)
		{
			$ref = &$out[$i];
			for ($k=0;$k<$nb;$k++)
			{
				if (isset($res[$k]) === false)
					$res[$k] = array();
				if ($i > 1 && is_numeric($ref[$k]) === true)
					$ref[$k] = (int) $ref[$k];
				array_push($res[$k], $ref[$k]);
			}
		}

		$nbres = count($res);
		$rs = '';
		$rs .= "<ul>";
		for ($i=0;$i<$nbres;$i++)
		{
			$ref = &$res[$i];
			$nb = count($ref);
			$rs .= "<li>";
			for ($k=0;$k<$nb;$k++)
			{
				$str = &$ref[$k];
				switch($k)
				{
					case 0:
						if (empty($str) === false)
						$rs .= "<b>$str</b>:";
						break;
					case 1:
						$query = array();
						$q = $_QRY->build_query_str($query);
						if ($str === 'success')
						{
							dwho_report::push('info',dwho_i18n::babelfish('successfully_synchronize',array($_QR['id'])));
							$_SESSION['_report'] = dwho_report::encode();
							$uri = $_TPL->url('service/ipbx/pbx_settings/devices').'?'.$q;
							$msg = 'redirecturi::'.($uri);
							$provddevice->request_delete($path);
							die($msg);
						}
						elseif ($str === 'fail')
						{
							dwho_report::push('error',dwho_i18n::babelfish('error_during_synchronize',array($_QR['id'])));
							$_SESSION['_report'] = dwho_report::encode();
							$uri = $_TPL->url('service/ipbx/pbx_settings/devices').'?'.$q;
							$msg = 'redirecturi::'.($uri);
							$provddevice->request_delete($path);
							die($msg);
						}
						$rs .= " $str";
						break;
					case 2:
						if ($str === '') break;
						$rs .= " ->  $str /";
						break;
					case 3:
						if ($str === '') break;
						$rs .= " $str";
						break;
				}
			}
			$rs .= "</li>";
		}
		$rs .= "</ul>";

		die($rs);
		break;
}

$http_response->set_status_line($code);
$http_response->send(true);

?>