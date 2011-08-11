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

xivo_object::required(array('abstract','abstract.inc'),true);

class xivo_object_certificate extends xivo_object_abstract
{
	var $_name	= 'certificate';
	var $_filter	= false;
	var $_origin	= false;
	var $_identity	= false;

	var $_sysconfd  = false;

	function xivo_object_certificate(&$sre)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_sysconfd = $this->_sre->get_module('sysconfd');
		return $this->_sysconfd !== false;
	}

	#function get_all($none, $order, $limit, &$total)
	function get_all()
	{
		function certs_sort($a, $b)
		{
			if($a['name'] != $b['name'])
				return strcmp($a['name'], $b['name']);

			$aweight = $bweight = 0;
			if(in_array('privkey', $a['types']))
				$aweight += 1;
			if(in_array('certificate', $a['types'])) {
				$aweight += 2;

				if(count($a['types']) == 1)
					$aweight += 1;
			}

			if(in_array('privkey', $b['types']))
				$bweight += 1;
			if(in_array('certificate', $b['types'])) {
				$bweight += 2;

				if(count($b['types']) == 1)
					$bweight += 1;
			}

			return $bweight - $aweight;
		}

		$certs = $this->get_certs();
		if($certs === false)
			return false;

		usort($certs, "certs_sort");

		$total = count($certs);
		return $certs;
		#return array_slice($certs, $limit[0], $limit[1]);
	}

	function get($id)
	{
		return $this->_sysconfd->request_get('/openssl_certificateinfos', array(array('name',$id)));
	}


	function get_certs()
	{
		$res = $this->_sysconfd->request_get('/openssl_listcertificates');
		if($this->_sysconfd->_status_code != 200) {
			dwho_report::push('error', 'Cannot query <b>sysconfd</b> server. Please verify it is running !');
			return false;
		}

		return $res;
	}

	function get_keys()
	{
		return $this->_sysconfd->request_get('/openssl_listkeys');
	}

	function add($is_ca, $arr)
	{
		if ($is_ca)
			$ret = $this->_sysconfd->request_post('/openssl_createcacertificate', $arr);
		else
			$ret = $this->_sysconfd->request_post('/openssl_createcertificate', $arr);

		if($this->_sysconfd->_status_code != 200)
			dwho_report::push('error', 'Cannot create certificate: '.$ret['message'].' (errno='.$ret['code'].')');

		return $ret;
	}

	function delete($name)
	{
		$ret = $this->_sysconfd->request_get('/openssl_deletecertificate', array(array('name',$name)));
		if($this->_sysconfd->_status_code != 200) {
			dwho_report::push('error', $ret['message'].' (errno='.$ret['code'].')');
			return false;
		}

		return true;
	}

	function export($name)
	{
		$ret = $this->_sysconfd->request_get('/openssl_export',
			array(array('name',$name)));

		if($this->_sysconfd->_status_code != 200) {
			dwho_report::push('error', $ret['message'].' (errno='.$ret['code'].')');
			return false;
		}

		return $ret;
	}

	function import($arr)
	{
		$ret = $this->_sysconfd->request_post('/openssl_import', $arr);
		if($this->_sysconfd->_status_code != 200) {
			dwho_report::push('error', $ret['message'].' (errno='.$ret['code'].')');
			return false;
		}

		return true;
	}
}

?>
