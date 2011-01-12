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

class xivo_service_asterisk_queue_log extends xivo_service_asterisk_abstract
{
	var $_dso		= null;
	var $_name		= 'queue_log';
	var $_filter	= false;

	function xivo_service_asterisk_queue_log(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}
	
	function stats($conf,$type,$data,$order=null,$limit=null)
	{
		if(($result = $this->_dso->stats($conf,$type,$data,$order,$limit)) === false)
			return(false);

		return($result);
	}

	function get_sum_stats($conf,$type,$value,$event,$field,$addwhere=null)
	{
		return($this->_dso->stats_sum_by_type($conf,$type,$value,$event,$field,$addwhere));
	}

	function count_stats($conf,$type,$value,$event,$addwhere=null)
	{
		return($this->_dso->stats_count_by_type($conf,$type,$value,$event,$addwhere));
	}

	function search($arr,$order=null,$limit=null)
	{
		if(is_array($arr) === false)
			return(false);

		$search = array();

		if(($result = $this->_dso->search($search,$order,$limit)) === false)
			return(null);

		return($result);
	}
}

?>
