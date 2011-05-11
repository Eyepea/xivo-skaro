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

	/**
	 * We need to merge certificates and keys to display all at once
	 **/
	function get_all()
	{	
		function certs_sort($a, $b)
		{
			return strcmp($a['name'], $b['name']);
		}
		
		$certs = $this->get_certs();
		if($certs === false)
			return false;

		$keys = $this->get_keys();
		if($keys === false)
		{
			usort($certs, "certs_sort");
			return $certs;
		}

		$certnames = array();
		function xtract_names(&$item)
		{
			global $certnames;

			$certnames[] = $item['name'];
			$item['type'] = 'certificate';
		}
		array_walk($certs, "xtract_names");

		function merge_keys($key)
		{
			global $certnames;
			return !in_array($key['name'], $certnames);
		}
		$certs = array_merge($certs, array_filter($keys, "merge_keys"));

		usort($certs, "certs_sort");
		var_dump($certs);

		return $certs;
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
		$this->_sysconfd->request_get('/openssl_deletecertificate', array(array('name',$name)));
	}

	function get_pubkey($name)
	{
		return $this->_sysconfd->request_get('/openssl_exportpubkey', array(array('name',$name)));
	}

	function import($arr)
	{
		return $this->_sysconfd->request_post('/openssl_import', $arr);
	}
}

?>
