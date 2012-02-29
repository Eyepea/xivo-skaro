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

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'filter.inc'));
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

		if(dwho_has_len($arr,'channel') === true)
			$search['channel'] = $this->_search_channel($arr['channel']);

		if(dwho_has_len($arr,'amaflags') === true)
			$search['amaflags'] = $arr['amaflags'];

		if(dwho_has_len($arr,'dcontext') === true)
			$search['dcontext'] = $arr['dcontext'];

		if(dwho_has_len($arr,'accountcode') === true && isset($arr['accountcodeformat']) === true)
			$search['accountcode'] = array('pattern' => $arr['accountcode'],'type' => $arr['accountcodeformat']);

		if(dwho_has_len($arr,'userfield') === true && isset($arr['userfieldformat']) === true)
			$search['userfield'] = array('pattern' => $arr['userfield'],'type' => $arr['userfieldformat']);

		if(($result = $this->_dso->search($search,$order,$limit)) === false)
			return(null);

		$nb = count($result);

		for($i = 0;$i < $nb;$i++)
		{
			$ref = &$result[$i];

			if(isset($ref['amaflags']) === false)
				$ref['amaflags'] = 0;

			$ref['amaflagsmeta'] = $this->amaflags_meta($ref['amaflags']);
		}

		return($result);
	}

	public function _search_channel($channel)
	{
		if($channel !== 'others')
			return($channel);

		$channel = $this->get_element_value('channel');
		unset($channel['others']);
		$channel = array_keys($channel);

		return($channel);
	}

	public function amaflags_meta($int)
	{
		$int = dwho_uint($int);

		$amaflags = $this->get_element_value('amaflags');

		if(isset($amaflags[$int]) === true)
			return($amaflags[$int]);

		return(XIVO_SRE_IPBX_AST_CDR_AMAFLAGS_META_DEFAULT);
	}

	public function channel_meta($str)
	{
		$str = (string) $str;

		$channels = $this->get_element_value('channel');

		if(isset($channels[$str]) === true)
			return($channels[$str]);

		return(false);
	}
}

?>
