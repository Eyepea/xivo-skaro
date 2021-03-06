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

xivo_service_asterisk::required(array('abstract','abstract.inc'),true);

class xivo_service_asterisk_contextmember extends xivo_service_asterisk_abstract
{
	var $_dso		= null;
	var $_name		= 'contextmember';
	var $_filter		= false;
	var $_origin		= false;
	var $_origin_list	= false;

	function xivo_service_asterisk_contextmember(&$sre,&$dso)
	{
		if(is_object($sre) === false)
			trigger_error('Invalid service in '.__CLASS__,E_USER_ERROR);

		if(is_object($dso) === false)
			trigger_error('Invalid datastorage in '.__CLASS__,E_USER_ERROR);

		$this->_sre = &$sre;
		$this->_dso = &$dso;

		$this->_load_config();
	}

	function add($arr,$id=0)
	{
		if(is_array($arr) === false)
			return(false);
		else if(isset($arr['context']) === true)
			$arr['context'] = strtolower($arr['context']);

		$arr['typeval'] = (string) $arr['typeval'];

		return(parent::add($arr,$id));
	}

	function edit($id,$arr)
	{
		if(is_array($arr) === false)
			return(false);
		else if(isset($arr['context']) === true)
			$arr['context'] = strtolower($arr['context']);

		$arr['typeval'] = (string) $arr['typeval'];

		return(parent::edit($id,$arr));
	}

	function get_all_by_type($arr=null,$disable=null,$prepare=true,$order=null,$limit=null)
	{
		$prepare = (bool) $prepare;

		if(isset($this->_origin_list) === true)
			$this->_origin_list = false;

		if(is_array($arr) === false || empty($arr) === true)
			$list = $this->_dso->get_all($disable,$order,$limit);
		else if(($where = $this->get_element_where($arr)) !== false)
			$list = $this->_dso->get_all_where($where,$disable,$order,$limit);
		else
			return(false);

		if($list === false || isset($list[0]) === false)
			return(false);
		else if(isset($this->_origin_list) === true)
			$this->_origin_list = $list;

		$r = array();

		if(is_array($list) === false || ($nb = count($list)) === 0)
			return(false);
		else if($prepare === true)
		{
			for($i = 0;$i < $nb;$i++)
			{
				$ref = &$list[$i];

				if(isset($r[$ref['type']]) === false)
					$r[$ref['type']] = array();

				switch($list[$i]['type'])
				{
					case 'generalsip':
					case 'generaliax':
					case 'generalvoicemail':
						$r[$ref['type']][$ref['varname']] = $this->_prepare($list[$i]);
						break;
					case 'voicemail':
						if(isset($r[$ref['type']][$ref['varname']]) === false)
							$r[$ref['type']][$ref['varname']] = array();

						$r[$ref['type']][$ref['varname']][] = $this->_prepare($list[$i]);
						break;
					default:
						$r[$ref['type']][] = $this->_prepare($list[$i]);
				}
			}
		}
		else
		{
			for($i = 0;$i < $nb;$i++)
			{
				if(isset($r[$list[$i]['type']]) === false)
					$r[$list[$i]['type']] = array();

				switch($list[$i]['type'])
				{
					case 'generalsip':
					case 'generaliax':
					case 'generalvoicemail':
						$r[$ref['type']][$list[$i]['varname']] = $list[$i];
						break;
					case 'voicemail':
						if(isset($r[$ref['type']][$ref['varname']]) === false)
							$r[$ref['type']][$ref['varname']] = array();

						$r[$ref['type']][$ref['varname']][] = $list[$i];
						break;
					default:
						$r[$ref['type']][] = $list[$i];
				}
			}
		}

		return($r);
	}
}

?>
