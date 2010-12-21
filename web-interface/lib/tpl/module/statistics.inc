<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
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

dwho::load_class('dwho_uri');

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'tpl','module.inc'));

class dwho_tpl_statistics extends dwho_tpl_module
{
	public  $_tpl			= null;
	public  $_queue			= array();
	public  $_table_rows	= array();
	public  $_table_cols	= array();
	public	$_conf_events	= array(
						/*
						* The caller abandoned their position in the queue. The position is the 
						* caller's position in the queue when they hungup, the origposition is 
						* the original position the caller was when they first entered the 
						* queue, and the waittime is how long the call had been waiting in the 
						* queue at the time of disconnect.
						*/
						'ABANDON'	=> array('position','origposition','waittime'),
						/*
						* The agent dumped the caller while listening to the queue announcement.
						*/
						'AGENTDUMP'	=> array(),
						/*
						* The agent logged in. The channel is recorded.
						*/
						'AGENTLOGIN'	=> array('channel'),
						/*
						* The callback agent logged in. The login extension and context is recorded. 
						*/
						'AGENTCALLBACKLOGIN'	=> array('exten@context'),
						);
	
	public function __construct(&$tpl)
	{
		$this->_tpl = &$tpl;
	}
	
	public function set_rows($rows) 
	{
		if(is_array($rows) === false 
		|| ($nb = count($rows)) === 0)
			return(false);
		
		$this->_table_rows = $rows;
		
	}
	
	public function init_queue($arr) 
	{		
		if(is_array($arr) === false 
		|| ($nb = count($arr)) === 0)
			return(false);
		else
		{
			for($i = 0;$i < $nb;$i++)
			{
				$ref  = &$arr[$i];
				array_push($this->_queue,$ref);
			}
		}		
	}

}

?>