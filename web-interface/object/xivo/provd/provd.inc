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

dwho::load_class('dwho_network');
dwho::load_class('dwho_uri');
dwho::load_class('dwho_curl');
dwho::load_class('dwho_json');
dwho::load_class('dwho_file');

xivo_object::required(array('abstract','abstract.inc'),true);

class xivo_object_provd extends xivo_object_abstract
{
	protected $_name		= 'provd';
	private $_module		= array('config' => false,
									'device' => false,
									'plugin' => false);

	public function __construct(&$xobj,$param=array())
	{
		$this->xivo_object_abstract(&$xobj);
		$this->_load_config();
		$this->_set_configuration();
	}

	public function get_module($module)
	{
		$class = 'module_provd_'.$module;
		
		if (isset($this->_module[$module]) === false
		|| dwho_file::load_file($module.'.inc',
			dwho_file::joinpath(dirname(__FILE__),'module')) === false
		|| class_exists($class) === false)
			return(false);
			
		$this->_module[$module] = new $class($this->_conf['provd']);
		
		return($this->_module[$module]);
	}

	private function _set_configuration()
	{
		$_CF = &dwho_gat::get('_CF');

		if(dwho_issa($this->_name,$_CF['xivo']['ini']) === false)
			return(null);

		$ref = &$_CF['xivo']['ini'][$this->_name];

		if(isset($ref['host']) === true)
		{
			if(dwho_network::valid_host($ref['host'],
						    (DWHO_NETWORK_HOST_IPV4_DOTDEC | DWHO_NETWORK_HOST_HOSTNAME)) === true)
				$this->_conf['provd']['host'] = $ref['host'];
			else
				dwho_report('warning','Invalid option host for section provd in XIVO init file');
		}

		if(isset($ref['port']) === true)
		{
			if(dwho_network::valid_port_number($ref['port']) === true)
				$this->_conf['provd']['port'] = (int) $ref['port'];
			else
				dwho_report('warning','Invalid option port for section provd in XIVO init file');
		}

		if(isset($ref['user']) === true)
		{
			if(empty($ref['user']) === false)
				$this->_conf['provd']['user'] = $ref['user'];
			else
				dwho_report('warning','Invalid option login for section provd in XIVO init file');
		}

		if(isset($ref['pass']) === true)
		{
			if(empty($ref['pass']) === false)
				$this->_conf['provd']['pass'] = $ref['pass'];
			else
				dwho_report('warning','Invalid option pass for section provd in XIVO init file');
		}

		if(isset($ref['connect_timeout']) === true)
		{
			if(dwho_is_uint($ref['connect_timeout']) === true)
				$this->_conf['connect_timeout'] = $ref['connect_timeout'];
			else
				dwho_report('warning','Invalid option connect_timeout for section provd in XIVO init file');
		}

		if(isset($ref['timeout']) === true)
		{
			if(dwho_is_uint($ref['timeout']) === true)
				$this->_conf['timeout'] = $ref['timeout'];
			else
				dwho_report('warning','Invalid option timeout for section provd in XIVO init file');
		}

		return(true);
	}
}

?>
