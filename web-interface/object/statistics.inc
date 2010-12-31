<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
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

class xivo_statistics
{
	private  $_name			= '';
	private  $_data			= array();
	private  $_data_custom	= array();
	private  $_result		= array();
	private  $_data_table	= array();
	private  $_prepare_rows	= array();
	private  $_prepare_cols	= array();
	private	 $_var_to_eval	= array();
							
	public function __construct()
	{
	}
	
	public function reset()
	{
		$this->_data_custom		= array();
		$this->_data_table		= array();
		$this->_result			= array();
		$this->_prepare_rows	= array();
		$this->_prepare_cols	= array();
		$this->_var_to_eval		= array();
		$this->_counter			= array();
	}
	
	public function set_name($name)
	{			
		$this->_name = $name;
	}
	
	public function get_name()
	{			
		return($this->_name);
	}
	
	public function set_data_custom($key,$arr)
	{
		if(is_array($arr) === false 
		|| ($nb = count($arr)) === 0)
			return(false);
			
		$this->_data_custom[$key] = $arr;
	}
	
	public function set_rows($key,$arr,$field) 
	{
		if(is_array($arr) === false 
		|| ($nb = count($arr)) === 0)
			return(false);
		else
		{
			$this->_prepare_rows[$key] = array();
			$tmp = array();
			for($i = 0;$i < $nb;$i++)
			{
				$ref  = &$arr[$i];
				if (isset($ref[$field]) === false)
					return(false);
				array_push($tmp, $ref[$field]);
			}
			$this->_prepare_rows[$key] = $tmp;
			return(true);
		}		
	}
	
	public function add_col($label,$type,$expression,$format='int',$order=null) 
	{		
		$ref = &$this->_prepare_cols;
		$arr = array();
		$arr['label'] = $label;
		$arr['type'] = $type;
		$arr['expression'] = $expression;
		$arr['format'] = $format;
		$arr['order'] = $order;
		array_push($ref, $arr);
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
		|| ($data_cols = $this->get_data_cols()) === false)
			return(false);
			
		$row_key = array_shift(array_keys($data_rows));
		$row_value = $data_rows[$row_key];
		$data_table = &$this->_data_table;				
		$nb_row_value = count($row_value);
			
		for ($t=0;$t<$nb_row_value;$t++)
		{
			$rowlabel = &$row_value[$t];
			
			if (isset($data_table[$rowlabel]) === false)
				$data_table[$rowlabel] = array();
					
			$row_data_table = &$data_table[$rowlabel];
							
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
					
				$rs = 0;
				switch($type) 
				{
					case 'direct':
						
						$val = $this->eval_expression($expression,$rowlabel);
						
						if (is_array($val) === false)
							break;
							
						$format = $val['type'];
						$rs = $val['result'];
						
						break;
					case 'expression':
						
						$std = '#^{([\w,:/\[\]]+)}([/+*\-]{1}){([\w,:/\[\]]+)}#i';
						$stdif = '#^if\({([\w,:]+)}([><=]{1}){([\w,:\[\]:]+)}\)=([\w]+)([/+*\-]{0,1})([a-z]*)#i';						
						$multif = '#^if\(([\w,:><=\[\]\}\{&\|]+)\)=([\w]+)([/+*\-]{0,1})([a-z]*)#i';
							
						# {custom:agent,agent/[number],calltime}/{custom:agent,agent/[number],logintime}
						if(preg_match($std,$expression,$out) === 1)
						{
							$val1 = $this->eval_expression($out[1],$rowlabel);
							if (is_array($val1) === true)
								$val1 = $val1['result'];
								
							$val2 = $this->eval_expression($out[3],$rowlabel);
							if (is_array($val2) === true)
								$val2 = $val2['result'];
								
							$rs = $this->eval_calculator($val1,$val2,$out[2]);
						}
						break;
					default:
				}
				
				$result = $this->get_result_formated($format,$rs);
				$row_data_table[$label]['expression'] = $expression;
				$row_data_table[$label]['format'] = $format;
				$row_data_table[$label]['result'] = $result;
			}
		}
		#var_dump('###################################################');
		
		return(false);
	}
	
	private function eval_calculator($val1,$val2,$operator)
	{							
		switch($operator)
		{
			case '/':
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
			if (preg_match('#^\[([a-z]+)\]#i',$key,$dcsout) === 1)
				array_push($tmp,$customevalvar);
			elseif (preg_match('#^([\w/]+)\[([a-z]+)\]#i',$key,$dcsout) === 1)
				array_push($tmp,$dcsout[1].$customevalvar);
			else
				array_push($tmp,$key);
		}
		
		$var = call_user_func_array(array($this, 'eval_var'), $tmp);
		
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
  
	private function get_result_formated($format,$str)
	{		
		switch ($format)
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
				$str = $result.' %';
				break;
			case 'time':
				$str = dwho_sec_to_human($result,false);
				break;
			default:
				$str = 'null_data';
		}		
		return($str);
	}
	
	public function gener()
	{
		$this->init_data_table();
	}
	
	public function render_html()
	{
		$return = '';
		$return .= '<table class="sb-statistics" border=1 width=100%>';		
		
		$y=0;
		foreach ($this->_data_table as $row => $cols)
		{
			if ($y===0)
			{
				$return .= '<tr>';
				$return .= '<td>&nbsp;</td>';	
				foreach ($cols as $colname => $colvalue)
					$return .= '<td>'.$colname.'</td>';
				$return .= '</tr>';
			}
			$y++;
		}
		
		#$return .= '<td>&nbsp;</td>';
		foreach ($this->_data_table as $row => $cols)
		{
			$return .= '<tr>';
			$return .= '<td>'.$row.'</td>';	
				foreach ($cols as $colname => $colvalue)
				{
					if (empty($colvalue) === true)
					{
						$return .= '<td>no_data</td>';
						continue;
					}
					
					$return .= '<td>'.$this->eval_result_data($colvalue).'</td>';
				}
			$return .= '</tr>';
		}
		
		$return .= '</table>';
		
		return( $return );
	}
	
	public function render_graph()
	{
		require(DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'pchart.inc');		
		
		$glibpchart = DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'pchart/class/';
		dwho_load_lib_pchart($glibpchart);
			
		$gfontspchart = DWHO_PATH_ROOT.DIRECTORY_SEPARATOR.'pchart/fonts/';
		
		$name = $this->_name;
		$gdir = XIVO_PATH_ROOT.DIRECTORY_SEPARATOR.'www/img/graphs/pchart/';
		
		if (is_dir($gdir) === false
		&& mkdir($gdir, 0775, true) === false)
			die('ERR: set rwx mode to '.$gdir);
		
		$basedir = '/img/graphs/pchart/'.$name.'/';
				
		// Dataset definition 
		$DataSet = new pData;
		
		/*
		// Generate some data...  
		$DataSet->AddPoint(array("queue8001","queue8002","queue8003"),"Serie1");  
		$DataSet->AddPoint(array(32,54,80),"aa");  
		$DataSet->AddPoint(array(1,1,2),"bb"); 
		$DataSet->AddPoint(array(84,25,65),"cc"); 
		  
		// This will mark both Serie1 & Serie2 as "graphable"  
		$DataSet->AddSerie("aa");  
		$DataSet->AddSerie("bb"); 
		$DataSet->AddSerie("cc");  
		  
		// Set Serie as abcisse label  
		$DataSet->SetAbsciseLabelSerie("Serie1");
		*/
		$abcisse_label = array();
		foreach ($this->_data_table as $row => $cols)
			array_push($abcisse_label,$row);
			
		$DataSet->AddPoint($abcisse_label,"Serie1");
		
		var_dump($abcisse_label);
		
		$i=0;
		foreach ($this->_data_table as $row => $cols)
		{
			$tmp = array();
			foreach ($cols as $colname => $colvalue)
			{
				if (empty($colvalue) === true)
					array_push($tmp,0);
				else
				{
					if (($val = $this->eval_result_data($colvalue)) === null
					|| is_numeric($val) === false)
						array_push($tmp,0);
					else
						array_push($tmp,$val);
				}
			}
			var_dump($tmp);
	 			$DataSet->AddPoint($tmp,$colname);
				var_dump($colname);
				 		$i++;
		}
		
		$i=0;
		foreach ($this->_data_table as $row => $cols)
		{
			foreach ($cols as $colname => $colvalue)
			{
				if($i===0){
					$DataSet->AddSerie($colname);
					var_dump($colname);
					
				}
	 			$i++;
			}
		}
				
		$DataSet->SetAbsciseLabelSerie("Serie1");
		
		/*
		$DataSet->AddPoint(array(1,2,3,4),'serie-lol');
		$DataSet->AddPoint(array(5,6,7,8),'serie-lol2');
		$DataSet->AddAllSeries();
		$DataSet->SetAbsciseLabelSerie();
		$DataSet->SetSerieName('lol','serie-lol');
		$DataSet->SetSerieName('lol2','serie-lol2');
		*/
		
		// Initialise the graph
		$Test = new pChart(800,230);		 
		#$Test->setFixedScale(0,100);
		$Test->setFontProperties($gfontspchart."tahoma.ttf",8);
		$Test->setGraphArea(50,30,700,200);
		
		$Test->drawFilledRoundedRectangle(7,7,710,223,5,240,240,240);
		$Test->drawRoundedRectangle(5,5,710,225,5,230,230,230);
		
		$Test->drawGraphArea(255,255,255,TRUE);
		$Test->drawScale($DataSet->GetData(),$DataSet->GetDataDescription(),SCALE_NORMAL,150,150,150,TRUE,0,2,TRUE);
		$Test->drawGrid(4,TRUE,230,230,230,50);
		
		// Draw the 0 line
		$Test->setFontProperties($gfontspchart."tahoma.ttf",6);
		$Test->drawTreshold(0,143,55,72,TRUE,TRUE);
		
		// Draw the bar graph
		$Test->drawBarGraph($DataSet->GetData(),$DataSet->GetDataDescription(),TRUE,80);
		
		// Finish the graph
		$Test->setFontProperties($gfontspchart."tahoma.ttf",8);
		$Test->drawLegend(700,15,$DataSet->GetDataDescription(),255,255,255);
		$Test->setFontProperties($gfontspchart."tahoma.ttf",10);
		$Test->drawTitle(50,22,$name,50,50,50,585);
		#$Test->Stroke();
		$Test->Render($gdir.$name.'.png');
		
	}	

}

?>