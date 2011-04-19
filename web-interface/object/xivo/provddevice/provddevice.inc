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

xivo_object::required(array('abstract','provd.inc'),true);

class xivo_object_provddevice extends xivo_object_provd_abstract
{
	protected $_name 		= 'provddevice';
	protected $_base_url 	= '/provd/pg_mgr';
	
	public function __construct(&$xobj,$param=array())
	{
		$this->_load_config(true);
		$this->_load_init();
	}
	
	public function get_device_list()
	{
		$uri = $this->_build_uri(array('devices'));
		
		if (($rs = $this->request_get($uri)) === false
		|| empty($rs['devices']) === true)
			return(false);
			
		return $rs['devices'];
	}
	
	public function get($str)
	{
		$uri = $this->_build_uri(array('devices',$str));
		
		if (($rs = $this->request_get($uri)) === false
		|| empty($rs['device']) === true)
			return(false);
			
		return $rs['device'];
	}
}

?>