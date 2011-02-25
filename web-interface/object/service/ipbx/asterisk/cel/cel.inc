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

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_cel extends xivo_service_asterisk_abstract
{
	protected $_dso		= null;
	protected $_name	= 'cel';
	protected $_filter	= false;

	public function __construct(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}
	
	public function sum_stats($type,$value,$event,$field,$interval=null,$addwhere=null)
	{
		return($this->_dso->stats_sum_by_type($type,$value,$event,$field,$interval,$addwhere));
	}

	public function count_stats($type,$value,$event,$interval=null,$addwhere=null)
	{
		return($this->_dso->stats_count_by_type($type,$value,$event,$interval,$addwhere));
	}

	public function search($arr,$order=null,$limit=null)
	{
		if(is_array($arr) === false)
			return(false);

		$search = array();
		
		$search = $arr;
		
		if(($result = $this->_dso->search($search,$order,$limit)) === false)
			return(null);

		$nb = count($result);

		for($i = 0;$i < $nb;$i++)
			$ref = &$result[$i];

		return($result);
	}
}

?>
