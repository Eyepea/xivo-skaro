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

class xivo_service_asterisk_ctiaccounts extends xivo_service_asterisk_abstract
{
	var $_dso		    = null;
	var $_name		    = 'ctiaccounts';
	var $_filter		= false;
	var $_origin		= false;
	var $_origin_list	= false;

	function xivo_service_asterisk_ctiaccounts(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}
	
	function set($arr)
	{
		if(is_array($arr) === false)
			return(false);
		
	    $reslist = $error = array();
		$errnb = 0;

		foreach($arr as $key => $list)
		{
			for($i = 0;$i < count($list);$i++)
			{
				if (isset($arr[$key][$i]) === false
				|| $arr[$key][$i] === '')
					$reslist[$i][$key] = '';
				else
					$reslist[$i][$key] = $arr[$key][$i];
			}
		}

		if(empty($reslist) === true)
			return(true);
		
		array_pop($reslist);
		
		$nbrs = count($reslist);
		$rs = array();
		for($i = 0;$i < $nbrs;$i++)
		{
			$ref = &$reslist[$i];

			if(($rs[] = $this->chk_values($ref)) === false)
			{
				$errnb++;
				$error[$i] = $this->get_filter_error();
			}
		}

		if ($errnb >> 0)
			return(false);
		
		$this->delete_all();

		for($i = 0;$i < $nbrs;$i++)
		{
			$account = &$rs[$i];

			if($this->add($account) === false)
			{
				$errnb++;
				$error[$i] = $this->get_error();
				$msgkey = array_shift(array_keys($this->get_error()));
				$msg = array_shift($this->get_error());
				if (empty($msgkey) === false)
					dwho_report::push('error','Account '.($i+1).': '.$msgkey.' '.$msg,'ctiaccount');
				else
					dwho_report::push('error','Account '.($i+1).': unknow error during '.$method,'ctiaccount');
			}
			$return[$i] = $account;
		}

		return(true);
	}
	
}

?>
