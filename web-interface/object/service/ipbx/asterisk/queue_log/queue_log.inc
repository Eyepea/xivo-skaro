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

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'filter.inc'));
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
	
	function get_min_and_max_time()
	{
		if(($min = $this->_dso->get_min_time()) === false
		|| ($max = $this->_dso->get_max_time()) === false)
			$return(false);
			
		$rs = array();
		$rs['min'] = $min;
		$rs['max'] = $max;
		
		return($rs);
	}

	function get_sum_stats($type,$value,$event,$field,$interval=null,$addwhere=null)
	{
		return($this->_dso->stats_sum_by_type($type,$value,$event,$field,$interval,$addwhere));
	}

	function count_stats($type,$value,$event,$interval=null,$addwhere=null)
	{
		return($this->_dso->stats_count_by_type($type,$value,$event,$interval,$addwhere));
	}

	function search($arr,$order=null,$limit=null)
	{
		if(is_array($arr) === false)
			return(false);

		$search = array();

		if(dwho_has_len($arr,'dbeg') === true)
		{
			$date = array('dbeg' => null,'dend' => null);

			if(dwho_has_len($arr,'dend') === true
			&& ($date = dwho_filter::chk_between_date($arr['dbeg'],$arr['dend'])) === false)
				return(false);
			else if(($date['dbeg'] = dwho_filter::chk_date($arr['dbeg'])) === false)
				return(false);

			if($date['dbeg']['dateint'] > strftime($date['dbeg']['format']))
				return(false);
			else
				$search['dbeg'] = $date['dbeg']['date'];

			//if($date['dend'] !== null && $date['dend']['dateint'] > strftime($date['dend']['format']))
			//	return(false);
			//else
				$search['dend'] = $date['dend']['date'];
		}

		if(($result = $this->_dso->search($search,$order,$limit)) === false)
			return(null);

		return($result);
	}
}

?>
