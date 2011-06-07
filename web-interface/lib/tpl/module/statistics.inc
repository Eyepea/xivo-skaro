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
require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'tpl','module.inc'));

class dwho_tpl_statistics extends dwho_tpl_module
{
	public	 $_tpl			= null;
	private	 $_xs			= null;
	private  $_basedir		= '';
	private  $_baseurl		= '';
	private  $_name			= '';
	private  $_col_struct	= '';
	private  $_row_key		= '';
	private  $_ignore_col	= array('rowdata');
	private  $_struct		= array();
	private  $_data			= array();
	private  $_data_custom	= array();
	private  $_data_table	= array();
	private  $_data_foot	= array();
	private  $_result		= array();
	private  $_prepare_rows	= array();
	private  $_full_rows	= array();
	private  $_prepare_cols	= array();
	private	 $_var_to_eval	= array();

	public function __construct(&$tpl)
	{
		$this->_tpl = &$tpl;
	}

	public function set_name($name)
	{
		$this->_name = $name;
	}

	public function get_name()
	{
		return($this->_name);
	}

	public function set_basedir($name)
	{
		$this->_basedir = $name;
	}

	public function set_baseurl($name)
	{
		$this->_baseurl = $name;
	}

	public function set_xs(&$obj)
	{
		$this->_xs = &$obj;
	}

	public function set_data_custom($key,$arr)
	{
		$this->_data_custom[$key] = $arr;
	}

	public function get_result()
	{
		return($this->_result);
	}

	public function get_data_table()
	{
		return($this->_data_table);
	}

	public function get_data_foot()
	{
		return($this->_data_foot);
	}

	public function get_data_custom($key)
	{
		if (isset($this->_data_custom[$key]) ===  true)
			return($this->_data_custom[$key]);

		return(null);
	}

	public function get_full_rows()
	{
		if (empty($this->_full_rows) === false
		&& is_array($this->_full_rows) === true)
			return($this->_full_rows);

		return(false);
	}

	public function get_data_rows()
	{
		if (empty($this->_prepare_rows) === false
		&& is_array($this->_prepare_rows) === true)
			return($this->_prepare_rows);

		return(false);
	}

	public function get_data_cols()
	{
		if (empty($this->_prepare_cols) === false
		&& is_array($this->_prepare_cols) === true)
			return($this->_prepare_cols);

		return(false);
	}

	public function set_rows($key,$arr,$field,$createkey=false)
	{
		if(is_array($arr) === false
		|| ($nb = count($arr)) === 0)
			return(false);

		$this->_row_key = $field;

		$this->_prepare_rows[$key] = array();
		$full_rows = $arr;
		foreach($arr as $k => &$ref)
		{
			if(isset($ref[$field]) === false)
				continue;
			if($createkey !== false)
				$ref['key'] = $ref[$field];
			$arr[$k] = $ref;
		}
		$this->_prepare_rows[$key] = $arr;
		$this->_full_rows = $arr;
		return(true);
	}

	public function has_data()
	{
		return(!empty($this->_data_table));
	}

	public function set_col_struct($str=null)
	{
		$arr = array();
		$arr['label'] = $str;
		$arr['content'] = array();

		array_push($this->_struct,$arr);
	}

	public function add_col($label,$type,$expression,$format='int',$ttotal='total')
	{
		$nbstruct = count($this->_struct);
		$refstruct = &$this->_struct[$nbstruct-1];

		array_push($refstruct['content'], $label);

		$ref = &$this->_prepare_cols;
		$arr = array();
		$arr['label'] = $label;
		$arr['type'] = $type;
		$arr['expression'] = trim($expression, "\x00..\x20");
		$arr['format'] = $format;
		$arr['ttotal'] = $ttotal;
		array_push($ref, $arr);
		return(true);
	}

	public function init_data_table()
	{
		if (($data_rows = $this->get_data_rows()) === false
		|| ($data_cols = $this->get_data_cols()) === false
		|| ($full_rows = $this->get_full_rows()) === false)
			return(false);

		$data_table = &$this->_data_table;
		$data_foot = &$this->_data_foot;

		$nb_row_total = count($full_rows);
		$nb_row_with_value = 0;

		while($full_rows)
		{
			$rowdata = array_shift($full_rows);

			$rownum = $rowdata[$this->_row_key];

			if (isset($data_table[$rownum]) === false)
				$data_table[$rownum] = array();

			$row_data_table = &$data_table[$rownum];
			$row_data_table['rowdata'] = $rowdata;

			$nb_col_value = count($data_cols);
			for($u=0;$u<$nb_col_value;$u++)
			{
				$col = &$data_cols[$u];
				$label = $col['label'];
				$type = $col['type'];
				$expression = $col['expression'];
				$format = $col['format'];
				$ttotal = $col['ttotal'];

				if (isset($row_data_table[$label]) === false)
					$row_data_table[$label] = array();

				$row_data = &$row_data_table[$label];

				if (isset($row_data['result']) === false)
				{
					$row_data['expression'] = $expression;
					$row_data['format'] = $format;
					$row_data['result'] = 0;
					$row_data['operation'] = null;
				}

				$row_data_foot = &$data_foot[$label];

				if (isset($row_data_foot['total']) === false)
				{
					$row_data_foot['total'] = true;
					$row_data_foot['result'] = 0;
					$row_data_foot['format'] = $format;
					$row_data_foot['ttotal'] = $ttotal;
					$row_data_foot['counter'] = 0;
					$row_data_foot['operation'] = null;
				}

				$rs = 0;
				$op = null;
				switch($type)
				{
					case 'direct':
						$std = '#^([\w,:/\[\]]+)#i';
						# custom:queue,[name],deterred
						if(preg_match($std,$expression,$out) === 1)
						{
							$val = $this->eval_expression($expression,$rowdata);

							if (is_array($val) === false)
								break;

							$format = $val['type'];
							$rs = $val['result'];
							$op = $rs;
						}
						break;
					case 'expression':
						$regex_ope = '#^{([\w,:/\[\]]+)}([/+*\-]{1}){([\w,:/\[\]]+)}#i';
						$regex_stdif = '#^if\({([\w,:]+)}([><=]{1}){([\w,:\[\]:]+)}\)=([\w]+)([/+*\-]{0,1})([a-z]*)#i';
						$regex_multif = '#^if\(([\w,:><=\[\]\}\{&\|]+)\)=([\w]+)([/+*\-]{0,1})([a-z]*)#i';

						# {custom:agent,[number],calltime}/{custom:agent,[number],logintime}
						if(preg_match($regex_ope,$expression,$out) === 1)
						{
							$val1 = $this->eval_expression($out[1],$rowdata);
							if (is_array($val1) === true)
								$val1 = $val1['result'];

							$val2 = $this->eval_expression($out[3],$rowdata);
							if (is_array($val2) === true)
								$val2 = $val2['result'];

							$res = $this->eval_calculator($val1,$val2,$out[2]);
							$rs = $res['rs'];
							$op = $res['op'];
						}
						break;
					default:
				}

				$result = $this->get_result_formated($rs,$format);

				$row_data['result'] = $result;
				$row_data['operation'] = $op.' '.$row_data['operation'];

				if ($rs === 0)
					continue;

				switch ($ttotal)
				{
					case 'average':
						$nb_row_with_value++;
						$row_data_foot['counter'] += $rs;
						$row_data_foot['result'] = $row_data_foot['counter'] / $nb_row_with_value;
						$row_data_foot['operation'] = $row_data_foot['counter'].' / '.$nb_row_with_value;
						break;
					case 'total':
					default:
						$row_data_foot['result'] += $rs;
						$row_data_foot['operation'] = $rs .'+'. $row_data_foot['operation'];
				}
			}
		}
		return(true);
	}

	private function eval_calculator($val1,$val2,$operator)
	{
		if (is_array($val1) === true
		&& isset($val1['result']) === true)
			$val1 = $val1['result'];
		if (is_array($val2) === true
		&& isset($val2['result']) === true)
			$val2 = $val2['result'];

		switch($operator)
		{
			case '/':
				if ($val2 === 0
				|| empty($val1) === true
				|| empty($val2) === true)
					$rs = 0;
				else
					$rs = ($val1 / $val2);
				$op = "($val1 / $val2)";
				break;
			case '+':
				$rs = ($val1 + $val2);
				$op = "($val1 + $val2)";
				break;
			case '*':
				$rs = ($val1 * $val2);
				$op = "($val1 * $val2)";
				break;
			case '-':
				if ($val1 === 0
				|| empty($val1) === true
				|| empty($val2) === true)
					$rs = 0;
				else
					$rs = ($val1 - $val2);
				$op = "($val1 - $val2)";
				break;
			default:
				$rs = 0;
				$op = null;
		}

		$res = array();
		$res['rs'] = $rs;
		$res['op'] = $op;

		return($res);
	}

	public function get_val_expression($expression,$customevalvar=null,$format=null)
	{
		$rs = $this->eval_expression($expression,$customevalvar);

		if (is_null($format) === true)
			return($rs);

		return($this->get_result_formated($format,$rs));
	}

	private function eval_expression($expr,$customevalvar=null)
	{
		$arr = explode(':',$expr);

		if(empty($arr) === true)
			return(false);

		if (count($arr) === 1)
			return(array_shift($arr));

		switch ($arr[0])
		{
			case 'custom':
				$this->_var_to_eval = $this->_data_custom;
				break;
			default:
				return(false);
		}

		$dcs = explode(',',$arr[1]);

		if(empty($dcs) === true)
			return(false);

		$tmp = array();
		$nb = count($dcs);
		for	($i=0;$i<$nb;$i++)
		{
			$key = $dcs[$i];
			if (preg_match('#^\[([a-z]+)\]#i',$key,$dcsout) === 1
			&& is_null($customevalvar) === true
			&& isset($this->_var_to_eval[$dcsout[1]]) === true)
				array_push($tmp,$this->_var_to_eval[$dcsout[1]]);
			elseif (preg_match('#^\[([a-z]+)\]#i',$key,$dcsout) === 1
			&& is_null($customevalvar) === false
			&& isset($customevalvar[$dcsout[1]]) === true)
				array_push($tmp,$customevalvar[$dcsout[1]]);
			else
				array_push($tmp,$key);
		}

		return(call_user_func_array(array($this,'eval_var'), $tmp));
	}

	private function eval_var()
	{
		if(($argc = func_num_args()) === 0)
			return(null);

		$name = (string) func_get_arg(0);

		if (isset($this->_var_to_eval) === true
		&& is_array($this->_var_to_eval) === true
		&& isset($this->_var_to_eval[$name]) === true)
			$var = $this->_var_to_eval;
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

	private function get_result_formated($str,$type=null)
	{
		if (is_array($str) === true
		&& isset($str['result']) === true)
			$str = $str['result'];

		if (is_array($str) === true
		&& isset($str['fype']) === true
		&& empty($str['type']) === false)
			$type = $str['type'];

		switch ($type)
		{
			case 'int':
				return((int) $str);
				break;
			case 'float':
				return((float) round($str,2));
				break;
			case 'percent':
				return((float) round($str*100,2));
				break;
			case 'time':
				return($str);
				break;
			case 'string':
			default:
				return($str);
		}
	}

	private function eval_result_data($arr)
	{
		if (isset($arr['result']) === false
		|| isset($arr['format']) === false)
			return(false);

		$result	= $arr['result'];

		$str = '-';
		switch ($arr['format'])
		{
			case 'int':
				$str = (int) $result;
				break;
			case 'float':
				$str = (float) $result;
				break;
			case 'percent':
				if (isset($arr['total']) === false)
					$str = (intval($result)).' %';
				break;
			case 'time':
				$str = dwho_sec_to_time($result);
				break;
			case 'string':
			default:
				$str = $result;
		}
		return($str);
	}

	public function gener_table()
	{
		$this->init_data_table();
	}

	public function infos_html()
	{
		$return = '';
		if (isset($this->_data_custom['axetype']) === true)
		{
			$axetype = $this->_data_custom['axetype'];
			$return .= '<p>';
			/*
			switch ($axetype)
			{
				case 'day':
					$day_process = $this->_data_custom['day_process'];
					$return .= dwho_change_date_format($day_process['dday'],'Y-m-d','D, d M Y');
					break;
				case 'week':
					$week_range = $this->_data_custom['week_range'];
					$from = $week_range['from'];
					$to = $week_range['to'];
					$return .= $this->bbf('week_number-opt',array(date('W',$from),date('Y',$from)));
					$return .= ' => ';
					$return .= date('Y-m-d',$from).' - '.date('Y-m-d',$to);
					break;
				case 'month':
					$month_process = $this->_data_custom['month_process'];
					break;
				case 'year':
					break;
				case 'type':
						// for period
						if (is_array($conf) === true
						&& isset($conf['periods']) === true):
							$return = '';
							foreach($conf['periods'] as $period => $value):
								$return .= $this->bbf('col_t'.$period);
								$return .= ': '.$value['beg'].'-'.$value['end'].'s';
								$return .= ' / ';
							endforeach;
							echo $return;
						endif;
				default:
					$return .= '';
			}
			*/
			$return .= '</p>';
		}

		return( $return );
	}

	public function get_error()
	{
		if (isset($this->_data_custom['listtype']) === false)
			return($this->bbf('no_conf_selected'));

		$listtype = $this->_data_custom['listtype'];

		if ($this->has_data() === false
		&& $listtype !== false)
			return($this->bbf('no_conf_selected'));
		elseif($listtype === false)
			return($this->bbf('no_type_in_conf'));
		elseif (is_object($this->_xs) === true
		&& $this->_xs->has_cache_type() === false)
			return($this->bbf('no_cache_generate'));
		else
			return(false);

		return(false);
	}

	public function render_top10($data)
	{
		if (isset($data['type']) === false
		|| isset($data['result']) === false
		|| is_array($data['result']) === false)
			return(null);

		$result = $data['result'];
		$format = $data['type'];

		$return = '';
		$return .= '<table>';

		$return .= '<thead>';
		$return .= '<tr class="sb-top">';
		$return .= '<th class="th-single" colspan="3">'.$this->bbf($this->_name).'</th>';
		$return .= '</tr>';
		$return .= '</thead>';

		$divtoken = '';
		$total = 0;
		for($i=0;$i<count($result);$i++)
		{
			$ref = &$result[$i];
			$key = $ref['key'];
			$val = $ref['val'];

			$datacall = $ref['datacall'];
			if(isset($datacall['identity']) === true)
				$identity = $datacall['identity'];
			elseif (isset($datacall[0]['datacall']['identity']) === true)
				$identity = $datacall[0]['datacall']['identity'];
			else
				$identity = $ref;

			$uid = uniqid();

			$divinfos = '';
			$divinfos .= '<div id="infos-'.$uid.'" title="'.$uid.'" class="b-nodisplay">';
			if (isset($datacall['from']) === true)
			{
				$divinfos .= 'date: '.strftime('%D %T',$datacall['start']).'<br>';
				$divinfos .= 'duration: '.dwho_sec_to_time($datacall['duration']).'<br>';
				$divinfos .= $datacall['identityfrom'].' call '.$datacall['to'].' via '.$datacall['trunk']."<br>";
				if (isset($datacall['price']) === true)
					$divinfos .= ' callprice: '.$datacall['price']."<br>";
				$link = '<a href="#" onclick="show_infos_'.$uid.'()">'.$identity.'</a>';
			}
			else
				$link = $identity;
			$divinfos .= '</div>';

			$divinfos .= '
			<script type="text/javascript">
				function show_infos_'.$uid.'() {$("#infos-'.$uid.'").dialog();}
			</script>';

			$return .= '<tbody id="disp">';
			$return .= '<tr class="fm-paragraph l-infos-'.(($i % 2) + 1).'on2" title="'.dwho_alttitle($identity).'">';
			$return .= '<td class="td-left">'.($i+1).'</td>';
			$return .= '<td class="td-center">'.$link.'</td>';
			$return .= '<td class="td-right">';
			$eval = array('format' => $format,'result' => $val);
			$return .= $this->eval_result_data($eval);
			$return .= '</td>';
			$return .= '</tr>';
			$return .= '</tbody>';
			$total += $val;
			$divtoken .= $divinfos;
		}

		$return .= '<tfoot>';
		$return .= '<tr> ';
		$return .= '<td class="td-left" colspan="2">&nbsp;'.$this->bbf('total').'</td>';
		$eval = array('format' => $format,'result' => $total);
		$return .= '<td class="td-right">'.$this->eval_result_data($eval).'</td>';
		$return .= '</tr>';
		$return .= '</tfoot>';

		$return .= '</table>';

		$return .= $divtoken;

		return($return);
	}

	public function render_html($chkbox=true,$rowname=true,$total=true,$colstruct=true)
	{
		$url = &$this->_tpl->get_module('url');
		if (isset($this->_data_custom['axetype']) === false)
		    return(false);
		
		$axetype = $this->_data_custom['axetype'];

		if (is_object($this->_xs) === true)
		{
			$idconf = $this->_xs->get_idconf();
			$infocal = $this->_xs->get_datecal();
			$objectkey = $this->_xs->get_objectkey();
			$qry = array();
		}
		else
		{
			$idconf = null;
			$objectkey = null;
			$infocal = dwho_date::get_infocal();
			$_QRY = &dwho_gct::get('dwho_query');
			$qry = $_QRY->request_meth_raw();
		}

		$return = '';
		$return .= '<table>';

		if ($colstruct === true)
		{
			$return .= '<thead>';
			$return .= '<tr class="sb-top">';

			if ($chkbox === true)
				$return .= '<th class="th-left">&nbsp;</th>';
			if ($rowname === true)
				$return .= '<th class="th-center">&nbsp;</th>';

			$nbstruct = count($this->_struct);
			for($i=0;$i<$nbstruct;$i++)
			{
				$refstruct = &$this->_struct[$i];

				$label = '&nbsp;';
				if (is_null($refstruct['label']) === false)
					$label = $this->bbf('colstruct_'.$refstruct['label']);

				if ($i < count($this->_struct)-1)
					$return .= '<th class="th-center" colspan="'.(count($refstruct['content'])).'">'.$label.'</th>';
				else
					$return .= '<th class="th-right" colspan="'.(count($refstruct['content'])).'">'.$label.'</th>';
			}

			$return .= '</tr>';
			$return .= '</thead>';
		}

		$y=0;
		foreach ($this->_data_table as $row => $cols)
		{
			if ($y>0)
				continue;

			$return .= '<thead>';
			$return .= '<tr class="sb-top">';
			$nbcolsup = 0;
			if ($chkbox === true)
			{
				$return .= '<th class="th-left">&nbsp;</th>';
				$nbcolsup++;
			}
			if ($rowname === true)
			{
				$return .= '<th class="th-center">&nbsp;</th>';
				$nbcolsup++;
			}
			$nb_cols = (int) (count($cols) + $nbcolsup);
			$c=0;
			foreach ($cols as $colname => $colvalue)
			{
				$c++;
				if (in_array($colname,$this->_ignore_col) === true)
					continue;
				if ($c < ($nb_cols - $nbcolsup))
					$return .= '<th class="th-center">'.$this->bbf('col_'.$colname).'</th>';
				else
					$return .= '<th class="th-right">'.$this->bbf('col_'.$colname).'</th>';
			}
			$return .= '</tr>';
			$return .= '</thead>';
			$y++;
		}

		$c=0;
		$week_process = '';
		foreach ($this->_data_table as $row => $cols)
		{
			$coldata = $cols['rowdata'];
			$identity = $type = 'unknown';

			if (isset($coldata['identity']) === true)
				$identity = $coldata['identity'];
			elseif(isset($coldata[$this->_row_key]) === true)
				$identity = $coldata[$this->_row_key];
			if (isset($coldata['type']) === true)
				$type = $coldata['type'];

			if ($axetype === 'month')
			{
				$day_num = $coldata['day'];
				$day_time = strtotime($infocal['dmonth'].'-'.$day_num);
				$week_num = date('W',$day_time);
				if ($week_num !== $week_process)
				{
					$week_process = $week_num;
					$return .= '<tr class="sb-top">';
					$return .= '<th class="th-right" colspan="'.$nb_cols.'">';
					$return .= $url->href_html($this->bbf('week',array($week_num)),
											$this->_baseurl,array_merge($qry,
											array(	'axetype' => 'week',
													'confid' => $idconf,
													'key' => $objectkey,
													'dweek' => date('Y-m-d',$day_time))));
					$return .= '</th>';
					$return .= '</tr>';
				}
			}

			$return .= '<tbody id="disp">';
			$return .= '<tr class="fm-paragraph l-infos-'.(($c % 2) + 1).'on2" title="'.dwho_alttitle($identity).'">';
			$nbcolsup = 0;
			if ($chkbox === true)
			{
				$return .= '<td class="td-left"><input type="checkbox" name="stats[]" id="it-stats-0" class="it-checkbox" value="1" /></td>';
				$nbcolsup++;
			}
			if ($rowname === true)
			{
				$bbf = array();
				$return .= '<td class="txt-left">';
				switch ($type)
				{
					case 'user':
						$return .= '<img src="/img/site/personal-trans.png" alt="" width="16" height="16" />';
						break;
					case 'agent':
						$return .= '<img src="/img/site/agent-trans.png" alt="" width="16" height="16" />';
						break;
					case 'queue':
						break;
					case 'group':
						break;
					default:
				}
				$return .= '&nbsp;';

				switch ($axetype)
				{
					case 'week':
						$time = strtotime($infocal['dweek']);
						$date = dwho_date::get_day_from_week_by_name_day(date('Y',$time),date('W',$time),$coldata['key']);
						$return .= $url->href_html($this->bbf($coldata['name'].'-opt',array(date('d',strtotime($date)))),
												$this->_baseurl,array_merge($qry,
												array(	'axetype' => 'day',
														'confid' => $idconf,
														'key' => $objectkey,
														'dday' => $date)));
						break;
					case 'month':
						$day_num = $coldata['day'];
						$day_time = strtotime($infocal['dmonth'].'-'.$day_num);
						$week_num = date('W',$day_time);
						$return .= $url->href_html($this->bbf($identity,$bbf),
												$this->_baseurl,array_merge($qry,
												array(	'axetype' => 'day',
														'confid' => $idconf,
														'key' => $objectkey,
														'dday' => date('Y-m-d',$day_time))));
						break;
					case 'year':
						$month_num = $coldata['key'];
						$month_time = strtotime($infocal['dyear'].'-'.$month_num);
						$return .= $url->href_html($this->bbf($identity,$bbf),
												$this->_baseurl,array_merge($qry,
												array(	'axetype' => 'month',
														'confid' => $idconf,
														'key' => $objectkey,
														'dmonth' => date('Y-m',$month_time))));
						break;
					case 'type':
						$return .= $url->href_html($this->bbf($identity,$bbf),
												$this->_baseurl,array_merge($qry,
												array(	'axetype' => 'day',
														'confid' => $idconf,
														'key' => $objectkey,
														'dday' => $infocal['dbeg'])));
						break;
					case 'day':
					default:
						$return .= $this->bbf($identity,$bbf);
				}

				$return .= '</td>';
				$nbcolsup++;
			}

			$nb_cols = count($cols) + $nbcolsup;
			$i=0;
			foreach ($cols as $colname => $colvalue)
			{
				$i++;
				if (in_array($colname,$this->_ignore_col) === true)
					continue;
				/*
				 * if($this->_xs->get_axetype() !== 'day'
				&& $this->_xs->has_cache_type($row) === false)
					$return .= '<td>'.$this->bbf('no_cache').'</td>';
				*/
				if ($i < ($nb_cols - $nbcolsup))
					$return .= '<td class="td-center">'.$this->eval_result_data($colvalue).'</td>';
				else
					$return .= '<td class="td-right">'.$this->eval_result_data($colvalue).'</td>';
			}
			$return .= '</tr>';
			$return .= '</tbody>';
			$c++;
		}

		if ($total === true)
		{
			$return .= '<tfoot>';
			$return .= '<tr> ';
			$return .= '<td class="txt-left">'.$this->bbf('total').'</td>';

			$i = 0;
			foreach ($this->_data_foot as $colname => $colvalue)
			{
				if (in_array($colname,$this->_ignore_col) === true)
					continue;
				$i++;
				if ($i < ($nb_cols - 3))
					$return .= '<td class="td-center">'.$this->eval_result_data($colvalue).'</td>';
				else
					$return .= '<td class="td-right">'.$this->eval_result_data($colvalue).'</td>';
			}

			$return .= '</tr>';
			$return .= '</tfoot>';
		}

		$return .= '</table>';

		$get = $url->_query->raw;
		$get = array_merge($get,array('act' => 'exportcsv'));

		$href = $url->href($this->_baseurl,$get);
/*
		$return .= '<p class="it-exportcsv">';
		$return .= '<input type="button" name="exportcsv" value="'.$this->bbf('tbl-lnk-expotcsv').'" onclick="window.location.href=\''.$href.'\'" />';
		#$return .= $url->href_html($this->bbf('tbl-lnk-expotcsv'),$this->_baseurl,$get);
		$return .= '</p>';
*/
		return( $return );
	}

	public function render_csv($rowname=true)
	{
		$url = &$this->_tpl->get_module('url');

		$return = '';
		$data_table = $this->_data_table;

		$coltitle = array_shift($data_table);
		$coltitle = array_keys($coltitle);

		if ($rowname === true)
			$return .= '"'.str_replace('"','""','').'";';

		while ($coltitle)
		{
			$fieldname = array_shift($coltitle);
			if (in_array($fieldname,$this->_ignore_col) === true)
				continue;
			# <acronym title="Période 3">P3</acronym>
			$fieldname = preg_replace('/<+\s*\/*\s*([A-Z][A-Z0-9]*)\b[^>]*\/*\s*>+/i','',$this->bbf('col_'.$fieldname));
			$return .= '"'.str_replace('"','""',$fieldname).'";';
		}

		$return .= "\n";

		$data_table = $this->_data_table;
		$coltitle = $data_table;
		$coltitlekey = array_keys($coltitle);

		while ($coltitle)
		{
			$listcols = array_shift($coltitle);
			$titlecolskey = array_shift($coltitlekey);
			$listcolskey = array_keys($listcols);

			if ($rowname === true)
				$return .= '"'.str_replace('"','""',$listcols['rowdata']['identity']).'";';

			while ($listcols)
			{
				$cols = array_shift($listcols);
				$colskey = array_shift($listcolskey);

				if (in_array($colskey,$this->_ignore_col) === true)
					continue;

				$return .= '"'.str_replace('"','""',$this->eval_result_data($cols)).'";';
			}
			$return .= "\n";
		}
		/*
		 * total
		 *

		if ($rowname === true)
			$return .= '"'.str_replace('"','""','total: ').'";';

		foreach ($this->_data_foot as $colname => $colvalue)
		{
			if (in_array($colname,$this->_ignore_col) === true)
				continue;
			$return .= '"'.str_replace('"','""',$this->eval_result_data($colvalue)).'";';
		}
		$return .= "\n";
		*/
		return( $return );
	}

	public function reset_all()
	{
		$this->_name			= '';
		$this->_col_struct		= '';
		$this->_struct			= array();
		$this->_data			= array();
		$this->_data_custom		= array();
		$this->_data_table		= array();
		$this->_data_foot		= array();
		$this->_result			= array();
		$this->_prepare_rows	= array();
		$this->_prepare_cols	= array();
		$this->_var_to_eval		= array();
	}

	public function reset_col()
	{
		$this->_col_struct		= '';
		$this->_struct			= array();
		$this->_data_table		= array();
		$this->_result			= array();
		$this->_prepare_cols	= array();
		$this->_var_to_eval		= array();
	}

}

?>