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

class xivo_service_asterisk_cel_postgresql extends xivo_service_asterisk_abstract_sql
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
			else
				$format = '%Y-%m-%d';

			if(isset($arr['dend']) === true)
				$dend = $arr['dend'];
			else
				$dend = '';

			$this->_dso->wheredate('calldate',$dbeg,$dend,null,$format);
		}

		if(isset($arr['channel']) === true)
		{
			if(is_array($arr['channel']) === true)
				$this->_dso->andwherenotbegin('channel',$arr['channel']);
			else
				$this->_dso->andwherebegin('channel',$arr['channel']);
		}

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

		if(dwho_issa('src',$arr) === true)
			$this->_dso->andwherelike('src',$arr['src']['pattern'],$arr['src']['type']);

		if(dwho_issa('dst',$arr) === true)
			$this->_dso->andwherelike('dst',$arr['dst']['pattern'],$arr['dst']['type']);

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

		return(true);
	}

	public function stats_sum_by_type($type,$value,$event,$fieldsum,$interval=null,$addwhere=null)
	{
		$this->_cnt = 0;

		$s = microtime(true);

		$field = array((object) ('SUM(cast("'.$fieldsum.'" as int))'));

		$this->_dso->new_select($this->_table,$field);

		switch ($type)
		{
			case 'incall':
				if (is_array($value) === true)
				{
					if (count($value) === 1)
						$this->_dso->where(array('exten' => $value[0]));
					else
						$this->_dso->wherein('exten',$value);
				}
				else
					$this->_dso->where(array('exten' => $value));
				break;
			default:
				return(false);
		}

		$this->_dso->andwhere(array('eventtype' => $event));
		$this->_dso->andwhere('"'.$fieldsum.'" ~ \'^[0-9]+$\'');

		if (is_null($addwhere) === false)
			$this->search_add_where($addwhere);

		if (is_null($interval) === false)
		{
			if(isset($interval['beg']) === true
			&& isset($interval['end']) === true)
				$this->_dso->wherebetween('eventtime',$interval['beg'],$interval['end'],$this->_table);
			elseif (($nbinterval = count($interval)) > 2)
			{
				$this->_dso->aggregate_where(false,'AND');
				foreach ($interval as $itl)
					$this->_dso->orwherebetween('eventtime',$itl['beg'],$itl['end'],$this->_table);
				$this->_dso->aggregate_where(false,'AND');
			}
			else
				return(false);
		}

		$r = $this->_dso->select_singlecolumn();

		if(isset($r[0]) === false)
			$r = false;

		return((int) $r[0]);
	}

	public function stats_count_by_type($type,$value,$event,$interval=null,$addwhere=null)
	{
		$this->_cnt = 0;

		$s = microtime(true);

		$this->_dso->new_select($this->_table,array('eventtype'));

		switch ($type)
		{
			case 'incall':
				if (is_array($value) === true)
				{
					if (count($value) === 1)
						$this->_dso->where(array('exten' => $value[0]));
					else
						$this->_dso->wherein('exten',$value);
				}
				else
					$this->_dso->where(array('exten' => $value));
				break;
			default:
				return(false);
		}

		$this->_dso->andwhere(array('eventtype' => $event));

		if (is_null($addwhere) === false)
			$this->search_add_where($addwhere);

		if (is_null($interval) === false)
		{
			if(isset($interval['beg']) === true
			&& isset($interval['end']) === true)
				$this->_dso->wherebetween('eventtime',$interval['beg'],$interval['end'],$this->_table);
			elseif (($nbinterval = count($interval)) > 2)
			{
				$this->_dso->aggregate_where(false,'AND');

				foreach ($interval as $itl)
					$this->_dso->orwherebetween('eventtime',$itl['beg'],$itl['end'],$this->_table);

				$this->_dso->aggregate_where(false,'AND');
			}
			else
				return(0);
		}

		if(($this->_cnt = $this->_dso->select_count()) === false)
			$this->_cnt = 0;

		return($this->_cnt);
	}

	private function search_add_where($addwhere)
	{
		if(is_array($addwhere) === false)
			return(false);

		$type = $addwhere[0];
		$value = $addwhere[1];
		switch ($type)
		{
			case 'BETWEEN':
				$cast = '';
				if (is_numeric($value[1]) === true
				&& is_numeric($value[2]) === true)
				{
					$cast = '::int';
					$this->_dso->andwhere('"'.$value[0].'" ~ \'^[0-9]+$\'');
				}
				$this->_dso->andwhere('"'.$this->_table.'"."'.$value[0].'"'.$cast.' BETWEEN '.$value[1].' AND '.$value[2]);
				break;
			case 'ISNOT':
				$this->_dso->andwherenot(array($value[0] => $value[1]),$this->_table);
				break;
			case '<':
			case '>':
			case '=':
				$cast = '';
				if (is_numeric($value[1]) === true)
				{
					$cast = '::int';
					$this->_dso->andwhere('"'.$value[0].'" ~ \'^[0-9]+$\'');
				}
				$this->_dso->andwhere('"'.$this->_table.'"."'.$value[0].'"'.$cast.' '.$type.' '.$value[1]);
				break;
		}
	}
}

?>