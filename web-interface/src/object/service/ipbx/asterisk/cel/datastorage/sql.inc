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

xivo_service_asterisk::required(array('abstract','datastorage','abstract','sql.inc'),true);

class xivo_service_asterisk_cel_sql extends xivo_service_asterisk_abstract_sql
{
	var $_disable	= null;

	function search($arr,$order=null,$limit=null)
	{
		$this->_cnt = 0;

		$this->_dso->new_select($this->_table);

		if($this->_search_where($arr) === false)
			return(false);

		$this->_dso->new_order($order);
		$this->_dso->limit($limit);

		$r = $this->_dso->select_all();

		$this->_dso->reset_order();
		$this->_dso->reset_limit();

		if(($this->_cnt = $this->_dso->select_count()) === false
		|| isset($r[0]) === false)
			$r = false;

		return($r);
	}

	function _search_where($arr)
	{
		if(is_array($arr) === false)
			return(false);

		if(isset($arr['idbeg']) === true)
		{
			$this->_dso->where('id > '.$arr['idbeg']);
		}

		if(isset($arr['dbeg']) === true)
		{
			$dbeg = $arr['dbeg'];
			$len = strlen($dbeg);

			if($len === 4)
				$format = '%Y';
			else if($len === 7)
				$format = '%Y-%m';
			else if($len === 10)
				$format = '%Y-%m-%d';
			else
				$format = '%Y-%m-%d %H:%i:%s';

			if(isset($arr['dend']) === true)
			{
				$dend = $arr['dend'];
				if ($dbeg === $dend)
					$dend = '';
			}
			else
				$dend = date('Y-m-d');

			$this->_dso->wheredate('eventtime',$dbeg,$dend,null,$format);
		}

		if(isset($arr['channel']) === true)
		{
			if(is_array($arr['channel']) === true)
				$this->_dso->andwherenotbegin('channame',$arr['channel']);
			else
				$this->_dso->andwherebegin('channame',$arr['channel']);
		}

		if(isset($arr['context']) === true)
			$this->_dso->andwhere(array('context' => $arr['context']));

		if(isset($arr['uniqueid']) === true)
			$this->_dso->andwhere(array('uniqueid' => $arr['uniqueid']));

		if(isset($arr['linkedid']) === true)
			$this->_dso->andwhere(array('linkedid' => $arr['linkedid']));

		if(isset($arr['dcontext']) === true)
			$this->_dso->andwhereexact('context',$arr['dcontext']);

		if(dwho_issa('accountcode',$arr) === true)
			$this->_dso->andwherelike('accountcode',$arr['accountcode']['pattern'],$arr['accountcode']['type']);

		if(dwho_issa('userfield',$arr) === true)
			$this->_dso->andwherelike('userfield',$arr['userfield']['pattern'],$arr['userfield']['type']);

		return(true);
	}
}

?>
