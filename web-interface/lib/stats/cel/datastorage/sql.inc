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
/*
	["id"] => string(1) "1"
    ["eventtype"] => string(10) "CHAN_START"
    ["eventtime"] => string(26) "2011-02-16 15:29:46.573929"
    ["userdeftype"] => string(0) ""
    ["cid_name"] => string(11) "celine dion"
    ["cid_num"] => string(4) "8001"
    ["cid_ani"] => string(0) ""
    ["cid_rdnis"] => string(0) ""
    ["cid_dnid"] => string(0) ""
    ["exten"] => string(4) "8000"
    ["context"] => string(7) "default"
    ["channame"] => string(17) "SIP/8001-00000000"
    ["appname"] => string(0) ""
    ["appdata"] => string(0) ""
    ["amaflags"] => string(1) "3"
    ["accountcode"] => string(0) ""
    ["peeraccount"] => string(0) ""
    ["uniqueid"] => string(12) "1297888186.0"
    ["linkedid"] => string(12) "1297888186.0"
    ["userfield"] => string(0) ""
    ["peer"] => string(0) ""
*/

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
				$dend = $arr['dend'];
			else
				$dend = '';

			$this->_dso->wheredate('eventtime',$dbeg,$dend,null,$format);
			#$this->_dso->wherebetween('eventtime',$arr['beg'],$arr['end']);
		}

		if(isset($arr['channel']) === true)
		{
			if(is_array($arr['channel']) === true)
				$this->_dso->andwherenotbegin('channame',$arr['channel']);
			else
				$this->_dso->andwherebegin('channame',$arr['channel']);
		}
/*
		if(isset($arr['eventtype']) === true)
			$this->_dso->andwhere(array('eventtype' => $arr['eventtype']));

		if(isset($arr['exten']) === true)
			$this->_dso->andwhere(array('exten' => $arr['exten']));

		if(isset($arr['context']) === true)
			$this->_dso->andwhere(array('context' => $arr['context']));

		if(isset($arr['uniqueid']) === true)
			$this->_dso->andwhere(array('uniqueid' => $arr['uniqueid']));

		if(isset($arr['linkedid']) === true)
			$this->_dso->andwhere(array('linkedid' => $arr['linkedid']));

		if(isset($arr['dcontext']) === true)
			$this->_dso->andwhereexact('dcontext',$arr['dcontext']);
*/
		if(dwho_issa('src',$arr) === true)
		{
			$this->_dso->aggregate_where();
			$this->_dso->andwherelike('exten',$arr['src']['pattern'],$arr['src']['type']);
			$this->_dso->orwherelike('cid_num',$arr['src']['pattern'],$arr['src']['type']);
			$this->_dso->aggregate_where();
		}

		if(dwho_issa('dst',$arr) === true)
		{
			$this->_dso->aggregate_where();
			$this->_dso->andwherelike('exten',$arr['dst']['pattern'],$arr['dst']['type']);
			$this->_dso->orwherelike('cid_num',$arr['src']['pattern'],$arr['src']['type']);
			$this->_dso->aggregate_where();
		}
/*
		if(dwho_issa('clid',$arr) === true)
			$this->_dso->andwherelike('clid',$arr['clid']['pattern'],$arr['clid']['type']);

		if(dwho_issa('accountcode',$arr) === true)
			$this->_dso->andwherelike('accountcode',$arr['accountcode']['pattern'],$arr['accountcode']['type']);

		if(dwho_issa('userfield',$arr) === true)
			$this->_dso->andwherelike('userfield',$arr['userfield']['pattern'],$arr['userfield']['type']);

		if(isset($arr['dubeg']) === true)
		{
			if(isset($arr['duend']) === true)
				$this->_dso->andwherebetween('duration',$arr['dubeg'],$arr['duend']);
			else
				$this->_dso->andwhereexact('duration',$arr['dubeg']);
		}
*/
		return(true);
	}
}

?>
