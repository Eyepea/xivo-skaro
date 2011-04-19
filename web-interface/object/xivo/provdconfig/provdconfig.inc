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

class xivo_object_provdconfig extends xivo_object_provd_abstract
{
	protected $_name 		= 'provdconfig';
	protected $_base_url 	= '/provd/cfg_mgr';
	
	public function __construct(&$xobj,$param=array())
	{
		$this->_load_config(true);
		$this->_load_init();
	}
	
	public function get($str)
	{
		$res = array();
		
		$uri = $this->_build_uri(array('configs',$str,'raw'));
		
		if (($rs = $this->request_get($uri)) === false
		|| empty($rs['raw_config']) === true)
			return(false);
			
		$raw_config = $rs['raw_config'];
			
		return($res);
	}
	
	public function get_configs($type,$search='',$order=null,$limit=null,$assoc=false)
	{
		switch ($type)
		{
			default:
			case 'list':
				$uri = $this->_build_uri(array('configs'));
		}
		
		if (($rs = $this->request_get($uri)) === false
		|| ($rs = $rs['configs']) === false
		|| ($nb = count($rs)) === 0)
			return(false);
			
		$this->_cnt = $nb;
			
		$i = 0;
		foreach($rs as $k => &$r)
		{
			$r['name'] = $k;
			
			if ($search !== ''
			&& preg_match('/'.$search.'/', $r['name']) === 0)
				unset($rs[$k]);
			
			if (is_null($limit) === false
			&& ($i < $limit[0] || $i > ($limit[0]+$limit[1])))
				unset($rs[$k]);
			
			$i++;
		}

		if((bool) $assoc === false)
			return(array_values($rs));

		return($rs);
	}
}

?>