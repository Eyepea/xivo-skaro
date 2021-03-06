<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
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

dwho_file::required(array(XIVO_PATH_OBJECT,'application','service','ipbx','asterisk.inc'),true);

class xivo_application_service_asterisk_queue_log extends xivo_application_asterisk_abstract
{
	var $_dso			= null;
	var $_queue_log		= false;

	function xivo_application_service_asterisk_queue_log(&$service,&$dso,$param=null)
	{
		$this->xivo_application_asterisk_abstract(&$service);

		if(is_object($dso) === false)
			trigger_error('Invalid Datastorage object',E_USER_ERROR);

		$this->_dso = &$dso;

		if(($this->_queue_log = &$this->_service->get_module('queue_log')) === false)
			return(false);

		return(true);
	}

	function get($id,$disable=null)
	{
		$this->_info = $this->_origin = array();

		if(($this->_info = $this->_queue_log->get($id,$disable)) === false)
			return(false);

		return($this->_info);
	}

	function get_queue_logs_except($name=null,$order=null,$limit=null,$assoc=false)
	{
		return($this->_queue_log->get_all_except($name,$order,$limit,$assoc));
	}

	function get_queue_logs_search($search,$order=null,$limit=null,$assoc=false)
	{
		return($this->_get_queue_logs('search',$search,$order,$limit,$assoc));
	}

	function get_queue_logs_list($order=null,$limit=null,$assoc=false)
	{
		return($this->_get_queue_logs('list',null,$order,$limit,$assoc));
	}

	function _get_queue_logs($action,$search='',$order=null,$limit=null,$assoc=false)
	{
		$search = strval($search);

		switch($action)
		{
			case 'search':
				$rs = $this->_queue_log->search($search,$order,$limit);
				break;
			case 'list':
			default:
				$rs = $this->_queue_log->get_all(null,true,$order,$limit);
		}

		$this->_cnt = $this->_queue_log->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		if(empty($rs) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($rs));

		return($rs);
	}

	function get_min_and_max_time()
	{
		return($this->_queue_log->get_min_and_max_time());
	}

	function count_queue_logs_stats($type,$value,$event,$interval=null,$addwhere=null)
	{
		$this->_cnt = $this->_queue_log->get_cnt();
		return($this->_queue_log->count_stats($type,$value,$event,$interval,$addwhere));
	}

	function sum_queue_logs_stats($type,$value,$event,$field,$interval=null,$addwhere=null)
	{
		if(($rs = $this->_queue_log->get_sum_stats($type,$value,$event,$field,$interval,$addwhere)) === false)
			return(0);

		return($rs);
	}

	function get_queue_logs_stats($conf,$type,$data,$order=null,$limit=null,$assoc=false)
	{
		if (is_null($conf) === true)
			return(false);

		$rs = $this->_queue_log->stats($conf,$type,$data,$order,$limit);

		$this->_cnt = $this->_queue_log->get_cnt();

		if($rs === false || ($nb = count($rs)) === 0)
			return(false);

		if(empty($rs) === true)
			return(false);
		else if((bool) $assoc === false)
			return(array_values($rs));

		return($rs);
	}

}

?>
