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

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'date.inc'));

class stats_ressource_cel
{

	public		$_type		=    '';
	public		$_field		= array('duration_in'		=> array('type' => 'time'),
									'duration_out'		=> array('type' => 'time'),
									'duration_intern'	=> array('type' => 'time'),
									'duration_total'	=> array('type' => 'time'),
									'nb_in'				=> array('type' => 'int'),
									'nb_out'			=> array('type' => 'int'),
									'nb_intern'			=> array('type' => 'int'),
									'nb_total'			=> array('type' => 'int'),
									'max_concurrent_calls_in'		=> array('type' => 'int'),
									'max_concurrent_calls_out'		=> array('type' => 'int'),
									'max_concurrent_calls_intern'	=> array('type' => 'int'),
									'max_concurrent_calls_total'	=> array('type' => 'int'));
	public		$_fieldtop10	= array('call_duration_intern'	=> array('type' => 'time','mode' => 'max'),
										'call_duration_in'		=> array('type' => 'time','mode' => 'max'),
										'call_duration_out'		=> array('type' => 'time','mode' => 'max'),
										'call_nb_intern'		=> array('type' => 'int','mode' => 'sum'),
										'call_nb_in'			=> array('type' => 'int','mode' => 'sum'),
										'call_nb_out'			=> array('type' => 'int','mode' => 'sum'),
										'call_price'			=> array('type' => 'string','mode' => 'max'));
	private		$_result	= false;
	private		$_top10		= false;
	private		$_cel		= false;
	private		$_trunk		= false;
	private		$_trunklist	= false;
	private		$_operatorlist	= false;
	private		$_ipbx		= false;
	private		$_total		= 0;

	public function __construct()
	{
		$this->_type = 'cel';

		if(($_SRE = &dwho_gct::get('xivo_service')) === false
		|| ($this->_ipbx = &$_SRE->get('ipbx')) === false
		|| ($this->_cel = &$this->_ipbx->get_module('cel')) === false
		|| ($this->_trunk = &$this->_ipbx->get_application('trunk')) === false
		|| ($this->_operator = &$this->_ipbx->get_application('operator')) === false)
			die('Can\'t load object for xivo_statistics_cel');

		$this->get_operator_list();
	}

	private function _build_trunkname_from_identity($identity)
	{
		if (preg_match('/([\w]+) \(([\w]+)\)/i',$identity,$out) === 0
		|| empty($out) === true
		|| isset($out[1]) === false
		|| isset($out[2]) === false)
			return(false);

		return(($out[2].'/'.$out[1]));
	}

	public function get_operator_list()
	{
		if (($appoperator = $this->_operator) === false
		|| ($list = $appoperator->get_operator_list(false)) === false)
			return(false);

		$rs = array();

		$nb = count($list);
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$list[$i];
			$listdestination = $ref['destination'];
			$listtrunk = $ref['trunk'];

			$nbt = count($listdestination);
			for($d=0;$d<$nbt;$d++)
			{
				$refd = &$listdestination[$d];
				$refd['operator'] = $ref;
			}

			$nbt = count($listtrunk);
			for($u=0;$u<$nbt;$u++)
			{
				$reft = &$listtrunk[$u];
				if (isset($reft['protocol']) === false)
				    continue;
				$protocol = $reft['protocol'];
				if (($trunkname = $this->_build_trunkname_from_identity($protocol['identity'])) === false)
					continue;

				if (isset($rs[$trunkname]) === false)
					$rs[$trunkname] = array();

				$rs[$trunkname] = array_merge($rs[$trunkname], $listdestination);
			}
		}

		return(($this->_operatorlist = $rs));
	}

	public function get_trunk_list($withintern=false)
	{
		if (($apptrunk = $this->_trunk) === false)
			return(false);

		$rs = array();

		switch($withintern)
		{
			case false:
				break;
			default:
			case true:
				$tmp = array();
				$tmp['identity'] = dwho_i18n::babelfish('trunk_intern');
				$tmp['key'] = 'intern';
				$tmp['name'] = 'intern';
				$rs['intern'] = $tmp;
				$this->_init_result('intern');
				if ($withintern === 'only')
					return($this->_trunklist = $rs);
		}

		if (($list = $apptrunk->get_trunks_list(false)) === false)
			return(false);

		$nb = count($list);
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$list[$i];
			if (($trunkname = $this->_build_trunkname_from_identity($ref['identity'])) === false)
				continue;
			$tmp = array();
			$tmp['identity'] = $ref['identity'];
			$tmp['key'] = $trunkname;
			$tmp['name'] = $trunkname;
			$rs[$tmp['key']] = $tmp;
			$this->_init_result($trunkname);
		}

		return(($this->_trunklist = $rs));
	}

	public function get_cnt()
	{
		return($this->_total);
	}

	public function get_list_call($arr=null, $order=null, $limit=null)
	{
		if (is_null($arr) === true)
		{
			$arr = array();
			$arr['dbeg'] = date('Y-m-d').'';
			#$arr['dend'] = date('Y-m-d').'';
		}

		if ($this->_trunk === false
		|| ($list = $this->_cel->search($arr, $order, $limit)) === false)
			return(false);

		$rs = array();
		while($list)
		{
			$ref = array_shift($list);
			$uid = $ref['linkedid'];
			if (isset($rs[$uid]) === false)
				$rs[$uid] = array();
			array_push($rs[$uid], $ref);
		}
		return($rs);
	}

	public function init_result_by_list($arr)
	{
		while($arr)
		{
			$data = array_shift($arr);
			$this->_init_result($data['key']);
		}
	}

	public function get_top10($name)
	{
		if (isset($this->_top10[$name]) === false
		|| ($ipbx = &$this->_ipbx) === false)
			return(null);

		$appuser = &$ipbx->get_application('user');

		$data = $this->_top10[$name];
		$result = $data['result'];

		dwho::load_class('dwho_sort');

		$ret = array();
		switch($data['mode'])
		{
			case 'max':
				$sort = new dwho_sort(array('key' => 'val'));
				uasort($result,array(&$sort,'num_usort'));
				$result = array_values($result);
				krsort($result);
				$ret = array_values($result);
				break;
			case 'sum':
				$tmp = array();
				foreach($result as $k => $listval)
				{
					$arr = array();
					$arr['key'] = $k;
					$arr['val'] = count($listval);
					$arr['datacall'] = $listval;
					array_push($tmp,$arr);
				}
				$sort = new dwho_sort(array('key' => 'val'));
				uasort($tmp,array(&$sort,'num_usort'));
				$tmp = array_values($tmp);
				krsort($tmp);
				$ret = array_values($tmp);
				break;
			default:
		}

		if (empty($ret) === false)
		{
			$ret = array_chunk($ret, 10, true);
			$ret = array_shift($ret);
		}

		$rs = array();
		$rs['type'] = $data['type'];
		$rs['result'] = $ret;

		return($rs);
	}

	private function _init_top10()
	{
		$res = &$this->_top10;

		foreach ($this->_fieldtop10 as $k => $field)
		{
			$res[$k] = array();
			$res[$k]['mode'] = $field['mode'];
			$res[$k]['type'] = $field['type'];
			$res[$k]['result'] = array();
		}
	}

	private function _init_result($key)
	{
		$res = &$this->_result;

		if (isset($res[$key]) === false)
		{
			$data_process = &$res[$key];
			$data_process = array();

			foreach ($this->_field as $k => $field)
			{
				$data_process[$k] = array();
				$data_process[$k]['type'] = $field['type'];
				$data_process[$k]['result'] = 0;
			}
		}
	}

	private function _call_is($callfrom,$callto)
	{
		$trunklist = $this->get_trunk_list(true);

		if (isset($trunklist[$callfrom['trunk']]) === false
		&& isset($trunklist[$callto['trunk']]) === false)
			return('intern');
		elseif (isset($trunklist[$callfrom['trunk']]) === false
		&& isset($trunklist[$callto['trunk']]) === true)
			return('out');
		elseif (isset($trunklist[$callfrom['trunk']]) === true
		&& isset($trunklist[$callto['trunk']]) === false)
			return('in');

		return(false);
	}

	private function _get_key($axetype,$type_call,$callfrom,$callto)
	{
		$key = 'none';
		switch ($axetype)
		{
			case 'period':
				$key = (int) date('Ymd',$callfrom['start']);
				break;
			case 'day':
				$hour = (string) strftime('%H',$callfrom['start']);
				$key = (int) date('H',$callfrom['start']);
				break;
			case 'week':
				$key = strtolower(date('l',$callfrom['start']));
				break;
			case 'month':
				$key = date('d',$callfrom['start']);
				break;
			case 'trunk':
			default:
				if ($type_call === 'intern')
					$key = 'intern';
				elseif ($type_call === 'in')
					$key = $callfrom['trunk'];
				elseif ($type_call === 'out')
					$key = $callto['trunk'];
		}
		return($key);
	}

	private function _eval_price($datacall,$destination)
	{
		$call_price = 0;
		$nb = count($destination);
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$destination[$i];
			$operator = $ref['operator'];
			$exten = $ref['exten'];
			$pattern = preg_replace_callback(
		        '|[X]+|',
		        create_function(
		            '$matches',
		            'return "[0-9]{".strlen($matches[0])."}";'
		        ),
		        $exten
		    );
			if (preg_match('/'.$pattern.'/',$datacall['to'],$out) === 1)
			{
				switch($ref['price_is'])
				{
					case 'second':
						$duration = $datacall['duration'];
						break;
					case 'minute':
					default:
						$duration = ($datacall['duration'] / 60);
				}
				$call_price = round($duration * $ref['price'],2);
			}
			else
			{
				switch($operator['default_price_is'])
				{
					case 'second':
						$duration = $datacall['duration'];
						break;
					case 'minute':
					default:
						$duration = ($datacall['duration'] / 60);
				}
				$call_price = (float) round($duration * $operator['default_price'],2);
			}
			$call_price .= ' '.$operator['currency'];
		}
		return($call_price);
	}

	private function _analyse_call_bridged($axetype,$callfrom,$callto)
	{
		$type_call = $this->_call_is($callfrom,$callto);
		$key = $this->_get_key($axetype,$type_call,$callfrom,$callto);

		$this->update_result(array($key,'nb_total'),1);

		$duration = (isset($callfrom['duration'])) ? $callfrom['duration'] : 0;
		$this->update_result(array($key,'duration_total'),$duration);

		$data = array();
		$data['key'] = $callfrom['from'];

		$datacall = array();
		$datacall['start'] = $callfrom['start'];
		$datacall['end'] = $callfrom['end'];
		$datacall['from'] = $callfrom['from'];
		$datacall['identityfrom'] = $callfrom['cid_name'].' ('.$callfrom['cid_num'].')';
		$datacall['to'] = $callfrom['to'];
		$datacall['identityto'] = $callto['cid_name'].' ('.$callto['cid_num'].')';
		$datacall['trunk'] = $key;
		$datacall['duration'] = $callfrom['duration'];
		$datacall['answer'] = $callfrom['answer'];
		$datacall['identity'] = $callfrom['cid_name'].' ('.$callfrom['cid_num'].')';

		$data['datacall'] = $datacall;

		if ($type_call === 'out'
		&& isset($this->_operatorlist[$key]) === true)
		{
			$data['val'] = $this->_eval_price($datacall,$this->_operatorlist[$key]);
			$data['datacall']['price'] = $data['val'];
			$this->update_top10('call_price',$data);
		}

		$this->update_result(array($key,'nb_'.$type_call),1);
		$this->update_result(array($key,'duration_'.$type_call),$duration);

		$data['val'] = $duration;
		$this->update_top10('call_duration_'.$type_call,$data);
		$data['val'] = 1;
		$this->update_top10('call_nb_'.$type_call,$data);

		return(array($type_call,$key));
	}

	public function parse_data($axetype,$search=null)
	{
		$data = $this->_build_data($search);
		$this->_init_top10();
		$data1 = $data;
		while($data1)
		{
			$call = array_shift($data1);
			$uniqueid = array_shift(array_keys($call));
			$callfrom = array_shift($call);
			$callto = array_shift($call);

			if (isset($callfrom['end']) === false)
				continue;

			$infos = $this->_analyse_call_bridged($axetype,$callfrom,$callto);
			$type_call = array_shift($infos);
			$key = array_shift($infos);

			// calculate concurrent calls
			$data2 = $data;
			while($data2)
			{
				$call2 = array_shift($data2);
				$callfrom2 = array_shift($call2);
				$callto2 = array_shift($call2);

				if (isset($callfrom2['end']) === false)
					continue;

				if ($callfrom2['start'] === $callfrom['start']
				&& $callfrom2['end'] === $callfrom['end'])
					continue;

				if ($callfrom2['start'] > $callfrom['start']
				&& $callfrom2['start'] < $callfrom['end'])
				{
					$this->update_result(array($key,'max_concurrent_calls_'.$type_call),1);
					$this->update_result(array($key,'max_concurrent_calls_total'),1);
				}
			}
		}
		return($this->_result);
	}

	public function get_calls_records($search=null, $order=null, $limit=null)
	{
		return($this->_build_data($search, $order, $limit));
	}

	private function _build_search($pattern, $type)
	{
		switch($type)
		{
			case 'begin':
				$like_format = '/^%s/i';
				break;
			case 'contain':
				$like_format = '/%s/i';
				break;
			case 'end':
				$like_format = '/%s$/i';
				break;
			default:
				$like_format = '/^%s$/i';
		}

		return(sprintf($like_format,$pattern));
	}

	private function _build_data($search=null, $order=null, $limit=null)
	{
		$rs = array();
		if (($listcall = $this->get_list_call($search, $order)) === false)
			return(false);

		$total = count($listcall);

		if ($total === 0)
			return(null);

		if(dwho_has_len($search,'src') === true && isset($search['srcformat']) === true)
			$search_src = $this->_build_search($search['src'], $search['srcformat']);

		if(dwho_has_len($search,'dst') === true && isset($search['dstformat']) === true)
			$search_dst = $this->_build_search($search['dst'], $search['dstformat']);

		$listcall = array_values($listcall);
		$token = $itl = $tmp = array();
		for ($i=0; $i < $total; $i++)
		{
			$ticketcall = &$listcall[$i];
			$token = $itl = $tmp = array();
			while ($ticketcall)
			{
				$call = array_shift($ticketcall);

				$eventtime = dwho_date::all_to_unixtime($call['eventtime']);
				$uniqueid = $call['uniqueid'];
				$linkedid = $call['linkedid'];
				$eventtype = $call['eventtype'];
				$channame = $call['channame'];
				$trunkname = substr($channame,0,-strlen(strrchr($channame,'-')));

				if (isset($token[$uniqueid]) === false)
					$token[$uniqueid] = array();

				$ref = &$token[$uniqueid];

				if (isset($ref['event']) === false)
					$ref['event'] = array();

				$event = &$ref['event'];

				if (isset($event[$eventtype]) === false)
					$event[$eventtype] = 0;

				$event_cnt = &$event[$eventtype];
				$event_cnt++;

				if (isset($tmp[$uniqueid]) === false)
					$tmp[$uniqueid] = array();

				$cc = &$tmp[$uniqueid];

				if (!isset($ref['duration']))
					$ref['duration'] = 0;

				switch ($eventtype)
				{
					case 'CHAN_START':
						switch ($event_cnt)
						{
							case 1:
								$ref['uniqueid'] = $uniqueid;
								$ref['channame'] = $channame;
								$ref['dstart'] = date('Y-m-d H:i:s',$eventtime);
								$ref['start'] = $eventtime;
								$ref['trunk'] = $trunkname;
								if (dwho_has_len($call['cid_name']) && dwho_has_len($call['cid_num']))
									$ref['from'] = $call['cid_name'].' ('.$call['cid_num'].')';
								if (preg_match('/^'.XIVO_SRE_IPBX_AST_REGEXP_DIALPLAN_EXTEN.'$/', $call['exten']))
									$ref['to'] = $call['exten'];
								$ref['context'] = $call['context'];
								$ref['userdeftype'] = $call['userdeftype'];
								$ref['answer'] = false;
								$ref['userfield'] = $call['userfield'];
								$ref['accountcode'] = $call['accountcode'];
								$ref['amaflags'] = $call['amaflags'];
								$ref['amaflagsmeta'] = $call['amaflagsmeta'];

								$cc['ringing'] = $eventtime;
								break;
							case 2:
								if (dwho_has_len($call['cid_name']) && dwho_has_len($call['cid_num']))
									$ref['to'] = $call['cid_name'].' ('.$call['cid_num'].')';
								break;
							default:
								$ref['dstart'] = date('Y-m-d H:i:s',$eventtime);
								$ref['start'] = $eventtime;
								$ref['context'] = $call['context'];
								break;
						}
						break;
					case 'APP_START':
						switch ($event_cnt)
						{
							case 1:
								if (!isset($ref['from']) || !dwho_has_len($ref['from']))
									$ref['from'] = $call['cid_name'].' ('.$call['cid_num'].')';
								break;
							case 2:
								if (!dwho_has_len($ref['to']))
									$ref['to'] = $call['cid_name'].' ('.$call['cid_num'].')';
								break;
						}
						break;
					case 'ANSWER':
						if (!isset($ref['to']) || !dwho_has_len($ref['to']))
							$ref['to'] = $call['cid_name'];
						$cc['danswer'] = $eventtime;
						$ref['answer'] = true;
						break;
					case 'BRIDGE_START':
						if (isset($cc['ringing']))
							$ref['ringing'] = (int) ($eventtime - $cc['ringing']);
						break;
					case 'BRIDGE_END':
						break;
					case 'HANGUP':
						if (isset($cc['danswer']))
							$ref['duration'] = (int) ($eventtime - $cc['danswer']);
						break;
					case 'CHAN_END':
						$ref['end'] = $eventtime;
						$ref['dend'] = date('Y-m-d H:i:s',$eventtime);
						break;
					default:
				}
			}
			if (isset($search_dst))
			{
				$tt = current($token);
				if (!isset($tt['to'])
				|| !preg_match($search_dst, $tt['to']))
					continue;
			}
			if (isset($search_src))
			{
				$tt = current($token);
				if (!isset($tt['from'])
				|| !preg_match($search_src, $tt['from']))
					continue;
			}
			array_push($rs,$token);
		}

		$this->_total = count($rs);

		if ($this->_total === 0)
			return(null);

		if ($limit === null)
			$limit = array(0, $this->_total);
		elseif(is_numeric($limit))
			$limit = array(0, $limit);

		if (($delta = (int) ($limit[0] + $limit[1])) > $this->_total)
			$delta = $this->_total;

		$result = array();
		for ($i=$limit[0]; $i < $delta; $i++)
		{
			$ref = &$rs[$i];
			array_push($result, $ref);
		}
		return($result);
	}

	protected function update_result($var,$str,$operator='+')
	{
		if (($res = call_user_func_array(array($this,'eval_result_var'), $var)) === null
		|| isset($res['result']) === false)
			return(false);

		$result = $res['result'];

		switch($operator)
		{
			case '+':
				$result += $str;
				break;
			case '-':
				$result -= $str;
				break;
			default:
		}

		$this->set_result_var($result,$var);

		return(true);
	}

	protected function update_top10($var,$arr)
	{
		if (isset($this->_top10[$var]) === false
		|| isset($arr['key']) === false
		|| isset($arr['val']) === false
		|| isset($arr['datacall']) === false)
			return(false);

		$result = &$this->_top10[$var]['result'];
		$mode = &$this->_top10[$var]['mode'];

		$key = $arr['key'];
		$val = $arr['val'];
		$datacall = $arr['datacall'];

		switch($mode)
		{
			case 'max':
				array_push($result, $arr);
				break;
			case 'sum':
				if (isset($result[$key]) === false)
					$result[$key] = array();

				array_push($result[$key], $arr);
				break;
		}
		return(true);
	}

	private function set_result_var($result,$arr)
	{
		$var = &$this->_result;

		for($i = 0;$i < count($arr);$i++)
		{
			$key = $arr[$i];
			if (isset($var[$key]) === true)
				$var = &$var[$key];
		}

		$var['result'] = $result;
	}

	private function eval_result_var()
	{
		if(($argc = func_num_args()) === 0)
			return(null);

		$name = (string) func_get_arg(0);

		if (isset($this->_result[$name]) === true)
			$var = $this->_result;
		else
			return(null);

		$ref = $var[$name];

		if($argc === 1)
			return($ref);
		else if(is_array($var[$name]) === false)
			return(null);

		for($i = 1;$i < $argc;$i++)
		{
			$key = func_get_arg($i);

			if(dwho_ak($key,$ref) === false)
			        return(null);

			$ref = $ref[$key];
		}

		return($ref);
	}

}

?>