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

class xivo_object_provdconfigure extends xivo_object_provd_abstract
{
	protected $_name 		= 'provdconfigure';
	protected $_base_url 	= '/provd/configure';
	
	public function __construct(&$xobj,$param=array())
	{
		$this->_load_config(true);
		$this->_load_init();
	}
	
	public function get($param)
	{
		$uri = $this->_build_uri(array('configure',$param));
		if (($rs = $this->get_params($uri)) === false)
		    return(false);
		
		return($rs);
	}
	
	public function get_configures($search='',$assoc=false)
	{
		$uri = $this->_build_uri(array());
		$rs = $this->request_get($uri);
		
		if (is_array($rs) === false
		|| $this->_status_code !== 200
		|| ($rs = $rs['params']) === false
		|| ($nb = count($rs)) === 0)
			return(false);
			
		for($i=0;$i<$nb;$i++)
		{
		    $r = &$rs[$i];
			$r['name'] = $r['id'];
			if ($search !== ''
			&& preg_match('/'.$search.'/', $r['name']) === 0
			&& preg_match('/'.$search.'/', $r['value']) === 0
			&& preg_match('/'.$search.'/', $r['description']) === 0)
				unset($rs[$k]);
		}

		if((bool) $assoc === false)
			return(array_values($rs));

		return($rs);
	}
	
	public function edit($arr)
	{
	    $err = 0;
		foreach($arr as $k => &$value)
		{
    		$uri = $this->_build_uri(array($k));
    		if ($value === '')
    		    $value = null;
    		if ($this->edit_params($uri,$value) === false)
    		    $err++;
		}
		
		if ($err > 0)
		    return(false);
		    
		return(true);
	}
}

?>