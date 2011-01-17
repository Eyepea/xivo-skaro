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
	private  $_basedir		= '';
	private  $_baseurl		= '';
	private  $_name			= '';
	private  $_col_struct	= '';
	private  $_row_key		= '';
	private  $_ignore_col	= array('identity','key');
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
	
	public function set_data_custom($key,$arr)
	{			
		$this->_data_custom[$key] = $arr;
	}
	
	public function set_rows($key,$arr,$field) 
	{
		if(is_array($arr) === false 
		|| ($nb = count($arr)) === 0)
			return(false);
			
		$this->_row_key = $field;
		
		$this->_prepare_rows[$key] = array();
		$tmp = array();
		for($i=0;$i<$nb;$i++)
		{
			$ref = &$arr[$i];
			if(isset($ref[$field]) === false)
				continue;
			array_push($tmp, $ref[$field]);
		}
		$this->_prepare_rows[$key] = $tmp;
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
	
	public function add_col($label,$type,$expression,$format='int',$order=null) 
	{			
		$nbstruct = count($this->_struct);		
		$refstruct = &$this->_struct[$nbstruct-1];
		
		array_push($refstruct['content'], $label);
		
		$ref = &$this->_prepare_cols;
		$arr = array();
		$arr['label'] = $label;
		$arr['type'] = $type;
		$arr['expression'] = $expression;
		$arr['format'] = $format;
		$arr['order'] = $order;
		array_push($ref, $arr);
		return(true);
	}
	
	private function get_full_rows()
	{
		if (empty($this->_full_rows) === false
		&& is_array($this->_full_rows) === true)
			return($this->_full_rows);
		
		return(false);
	}
	
	private function get_data_rows()
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
	
	public function init_data_table()
	{
		if (($data_rows = $this->get_data_rows()) === false
		|| ($data_cols = $this->get_data_cols()) === false
		|| ($full_rows = $this->get_full_rows()) === false)
			return(false);
			
		$row_value = $full_rows;
		$nb_row_value = count($full_rows);
		
		$data_table = &$this->_data_table;
		$data_foot = &$this->_data_foot;
			
		for ($t=0;$t<$nb_row_value;$t++)
		{
			$rowdata = $row_value[$t];
		
			if (isset($rowdata['identity']) === true)
				$rowidentity = $rowdata['identity'];
			elseif (isset($rowdata['fullname']) === true)
				$rowidentity = $rowdata['fullname'];
			elseif(isset($rowdata['name']) === true)
				$rowidentity = $rowdata['name'];
			else 
				$rowidentity = 'null_data';
				
			if (isset($rowdata['id']) === true)
				$rowkey = $rowdata['id'];
			elseif(isset($rowdata['name']) === true)
				$rowkey = $rowdata['name'];
			else 
				$rowkey = $t;
				
			$rownum = $rowdata[$this->_row_key];
			
			if (isset($data_table[$rownum]) === false)
				$data_table[$rownum] = array();
					
			$row_data_table = &$data_table[$rownum];
					
			$row_data_table['identity'] = $rowidentity;
			$row_data_table['key'] = $rowkey;
					
			$nb_col_value = count($data_cols);
			for($u=0;$u<$nb_col_value;$u++)
			{
				$col = &$data_cols[$u];
				$label = $col['label'];
				$type = $col['type'];
				$expression = $col['expression'];
				$format = $col['format'];
				
				if (isset($row_data_table[$label]) === false)
					$row_data_table[$label] = array();
					
				$row_data_foot = &$data_foot[$label];
					
				$rs = 0;
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
						}						
						break;
					case 'expression':
						$ope = '#^{([\w,:/\[\]]+)}([/+*\-]{1}){([\w,:/\[\]]+)}#i';
						$stdif = '#^if\({([\w,:]+)}([><=]{1}){([\w,:\[\]:]+)}\)=([\w]+)([/+*\-]{0,1})([a-z]*)#i';						
						$multif = '#^if\(([\w,:><=\[\]\}\{&\|]+)\)=([\w]+)([/+*\-]{0,1})([a-z]*)#i';
							
						# {custom:agent,[number],calltime}/{custom:agent,[number],logintime}
						if(preg_match($ope,$expression,$out) === 1)
						{
							$val1 = $this->eval_expression($out[1],$rowdata);
							if (is_array($val1) === true)
								$val1 = $val1['result'];
							
							$val2 = $this->eval_expression($out[3],$rowdata);
							if (is_array($val2) === true)
								$val2 = $val2['result'];
								
							$rs = $this->eval_calculator($val1,$val2,$out[2]);
						}
						break;
					default:
				}				
				$result = $this->get_result_formated($rs,$format);
				$row_data_table[$label]['expression'] = $expression;
				$row_data_table[$label]['format'] = $format;
				$row_data_table[$label]['result'] = $result;
				
				if (isset($row_data_foot['result']) === false)
				{
					$row_data_foot['total'] = true;
					$row_data_foot['result'] = 0;
					$row_data_foot['format'] = $format;
				}
				$row_data_foot['result'] += $rs;				
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
				if ($val2 === 0)
					$rs = 0;
				else
					$rs = ($val1 / $val2);
				break;
			case '+':
				$rs = ($val1 + $val2);
				break;
			case '*':
				$rs = ($val1 * $val2);
				break;
			case '-':
				$rs = ($val1 - $val2);
				break;
			default:
				$rs = 0;
		}
		return($rs);
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
		$var = call_user_func_array(array($this,'eval_var'), $tmp);
		
		return($var);
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
		
		switch ($arr['format'])
		{
			case 'int':
				$str = (int) $result;
				break;
			case 'float':
				$str = (float) $result;
				break;
			case 'percent':			
				if (isset($arr['total']) === true)
					return('-');
				$str = $result.' %';
				break;
			case 'time':			
				if (isset($arr['total']) === true)
					return('-');
				$str = dwho_sec_to_time($result);
				break;
			default:
				$str = 'null_data';
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
			switch ($axetype)
			{
				case 'day':
					$hour_range = $this->_data_custom['hour_range'];
					$interval = $hour_range['interval'];
					$date = dwho_change_date_format($interval['dbeg'],'Y-m-d H:i:s','D, d M Y');
					$return .= $date;
					break;
				case 'week':
					$week_range = $this->_data_custom['week_range'];
					$from = $week_range['from'];
					$to = $week_range['to'];
					$return .= $this->bbf('week_number',date('W',$from));
					$return .= ' => ';
					$return .= date('Y-m-d',$from).' - '.date('Y-m-d',$to);
					break;
				case 'month':
					break;
				case 'year':
					break;
				case 'type':
				default:
					$return .= '';
			}
			$return .= '</p>';
		}
		
		return( $return );
	}
	
	public function render_html($chkbox=true,$rowname=true)
	{		
		$url = &$this->_tpl->get_module('url');		

		$return = '<form action="#" name="fm-stats-list" method="post" accept-charset="utf-8">';
		$return .= '<table cellspacing="0" cellpadding="0" border="0">';
		
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
			$nb_cols = count($cols) + $nbcolsup;
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
		foreach ($this->_data_table as $row => $cols)
		{
			$return .= '<tbody id="disp">';
			$return .= '<tr class="fm-paragraph l-infos-'.(($c % 2) + 1).'on2" title="'.dwho_alttitle($cols['identity']).'">';
			$nbcolsup = 0;
			if ($chkbox === true)
			{
				$return .= '<td class="td-left"><input type="checkbox" name="stats[]" id="it-stats-0" class="it-checkbox" value="1" /></td>';
				$nbcolsup++;
			}	
			if ($rowname === true)
			{
				$bbf = array();
				$identity = $cols['identity'];
				if (is_array($cols['identity']) === true)
				{
					$identity = $cols['identity'][0];
					$bbf = $cols['identity'][1];
				}
				$return .= '<td class="txt-left">';
				if ($this->_data_custom['axetype'] === 'type')
					$return .= $url->href_html($this->bbf($identity,$bbf),$this->_baseurl,array('axetype' => 'day','key' => $cols['key']));
				else 
					$return .= $this->bbf($identity,$bbf);
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
				if (empty($colvalue) === true)
				{
					$return .= '<td>no_data</td>';
					continue;
				}
				if ($i < ($nb_cols - $nbcolsup))
					$return .= '<td class="td-center">'.$this->eval_result_data($colvalue).'</td>';
				else
					$return .= '<td class="td-right">'.$this->eval_result_data($colvalue).'</td>';
			}
			$return .= '</tr>';
			$return .= '</tbody>';
			$c++;
		}
		
		$return .= '<tfoot>'; 
		$return .= '<tr> ';
		$return .= '<td class="txt-left">Total</td>';
		$i = 0;			
		foreach ($this->_data_foot as $colname => $colvalue)
		{
			$i++;
			if (in_array($colname,$this->_ignore_col) === true)
				continue;
			if (empty($colvalue) === true)
			{
				$return .= '<td>no_data</td>';
				continue;
			}
			if ($i < ($nb_cols - 1))
				$return .= '<td class="td-center">'.$this->eval_result_data($colvalue).'</td>';
			else
				$return .= '<td class="td-right">'.$this->eval_result_data($colvalue).'</td>';
		}
		$return .= '</tr> ';
		$return .= '</tfoot>';
		
		$return .= '</table>';
		$return .= '</form>';
		
		return( $return );
	}
	
	public function gener_graph($type,$name)
	{
		require_once(DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'pchart.inc');
		
		$dir = PCHART_PATH_IMG.$this->_name;
		
		if (dwho_file::is_d($dir) === false
		&& mkdir($dir,0775) === false)
			die('ERR: set rwx mode to '.$dir);
		
		switch($type)
		{
			case 't1':
				$this->gener_graph_t1($name);
				break;
			default:
				$this->gener_graph_t1($name);
		}
	}
	
	public function get_graph($name)
	{
		return( '<img src="'.$this->_basedir.$this->_name.DIRECTORY_SEPARATOR.$name.'.png" alt="" />' );
	}
	
	private function gener_graph_t1($name)
	{		
		$pfonts = PCHART_PATH_ROOT.'fonts'.DIRECTORY_SEPARATOR;
		$plib = PCHART_PATH_ROOT.'class'.DIRECTORY_SEPARATOR;
		dwho_load_lib_pchart($plib);
		
		$MyData = new pData();
		
		$nbDataTable = count($this->_data_table);
		
		$abcisse_label = array();
		foreach ($this->_data_table as $row => $cols)
			array_push($abcisse_label,$row);
			
		asort($abcisse_label);
		$MyData->AddPoints($abcisse_label,$this->_name);
		$MyData->setAbscissa($this->_name);
		
		$lsdata = array();
		foreach ($this->_data_table as $row => $cols)
		{
			$colsk = array_keys($cols);
			$colsv = array_values($cols);
			for ($i=0;$i<count($cols);$i++)
			{			
				$colk = &$colsk[$i];
				$colv = &$colsv[$i];		
						
				if($colv['format'] !== 'int')
					continue;
				
				if (isset($lsdata[$colk]) === false)
					$lsdata[$colk] = array();
				
				if (empty($colv) === true)
					array_push($lsdata[$colk],0);
				else
				{
					if (($val = $this->eval_result_data($colv)) === null
					|| is_numeric($val) === false)
						array_push($lsdata[$colk],0);
					else
						array_push($lsdata[$colk],$val);
				}
			}
		}
		
		foreach ($lsdata as $k => $v)
		{
			$label = '&nbsp;';
			if (is_null($k) === false)
				$label = $this->bbf('col_'.$k);
				
			# <acronym title="Durée moyenne de WRAPUP">DMWU</acronym>			
			$label = preg_replace('/<+\s*\/*\s*([A-Z][A-Z0-9]*)\b[^>]*\/*\s*>+/i','',$label);
	 		$MyData->AddPoints($v,$label);
		}
		
		$graph_w = 750;
		$graph_h = (int) ($nbDataTable * 200);
		# X1,Y1 is the top left corner of the bounding box.
		$graph_area_tl_w = (int) ($graph_w - ($graph_w - 80));
		$graph_area_tl_h = (int) ($graph_h - ($graph_h - 30));
		# X2,Y2 is the borrom right corner of the bounding box.
		$graph_area_br_w = (int) ($graph_w - 20);
		$graph_area_br_h = (int) ($graph_h - 20);
		
		/* Create the pChart object */
		$myPicture = new pImage($graph_w,$graph_h,$MyData); 
		$myPicture->drawGradientArea(0,0,$graph_w,$graph_h,DIRECTION_VERTICAL,array("StartR"=>240,"StartG"=>240,"StartB"=>240,"EndR"=>180,"EndG"=>180,"EndB"=>180,"Alpha"=>100)); 
		$myPicture->drawGradientArea(0,0,$graph_w,$graph_h,DIRECTION_HORIZONTAL,array("StartR"=>240,"StartG"=>240,"StartB"=>240,"EndR"=>180,"EndG"=>180,"EndB"=>180,"Alpha"=>20)); 
		$myPicture->setFontProperties(array("FontName"=>$pfonts."verdana.ttf","FontSize"=>6)); 
		
		/* Draw the chart scale */
		$myPicture->setGraphArea($graph_area_tl_w,$graph_area_tl_h,$graph_area_br_w,$graph_area_br_h);
		#$myPicture->setGraphArea(100,30,680,180);
		$myPicture->drawScale(array("CycleBackground"=>TRUE,"DrawSubTicks"=>TRUE,"GridR"=>0,"GridG"=>0,"GridB"=>0,"GridAlpha"=>10,"Pos"=>SCALE_POS_TOPBOTTOM));		
		$myPicture->setShadow(TRUE,array("X"=>1,"Y"=>1,"R"=>0,"G"=>0,"B"=>0,"Alpha"=>10));
		
		/* Draw the chart */
		$myPicture->drawBarChart(array("DisplayPos"=>LABEL_POS_INSIDE,"DisplayValues"=>TRUE,"Rounded"=>TRUE,"Surrounding"=>30));
		
		/* Write the legend */
		$myPicture->drawLegend(15,5,array("Style"=>LEGEND_NOBORDER,"Mode"=>LEGEND_HORIZONTAL)); 

		$myPicture->Render(PCHART_PATH_IMG.$this->_name.DIRECTORY_SEPARATOR.$name.'.png');
	}	
	
	public function reset_all()
	{
		$this->_name			= '';
		$this->_col_struct		= '';
		$this->_struct			= array();
		$this->_data			= array();
		$this->_data_custom		= array();
		$this->_data_table		= array();
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