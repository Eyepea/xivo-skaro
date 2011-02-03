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

define('PCHART_PATH_ROOT',dwho_file::joinpath(DWHO_PATH_ROOT,'pchart','current'));
define('PCHART_IMG_DIR',dwho_file::joinpath('img','graphs','pchart'));

# cache dir
if (dwho_file::is_d(DWHO_PATH_CACHE_PCHART) === false
&& mkdir(DWHO_PATH_CACHE_PCHART, 0775, true) === false)
	die('ERR: set rwx mode for www-data to '.DWHO_PATH_CACHE_PCHART);

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'file.inc'));

class pChart
{
	private	 $_path		= array('cache'	=>	'',
								'fonts'	=>	'',
								'lib'	=>	'');
	
	public function __construct()
	{		
		$path = &$this->_path;
		
		$path['cache'] = dwho_file::joinpath(DWHO_PATH_CACHE_PCHART);
		$path['fonts'] = dwho_file::joinpath(PCHART_PATH_ROOT,'fonts');
		$path['lib'] = dwho_file::joinpath(PCHART_PATH_ROOT,'class');
			
		if (dwho_file::is_d_rx($path['cache']) === false)
			die('ERR: Failed to load cache dir pchart '.$path['cache']);
		
		if (dwho_file::is_d_rx($path['lib']) === false)
			die('ERR: Failed to load lib dir pchart '.$path['lib']);
			
		if (dwho_file::is_d_rx($path['fonts']) === false)
			die('ERR: Failed to load fonts dir pchart '.$path['fonts']);
			
		$this->load_lib($path['lib']);		
	}
	
	private function load_lib($libdir)
	{
	    $r = dwho_file::read_d($libdir,'file',FILE_R_OK);
	    sort($r);
	    
	    $tree = array();
	    foreach($r as $file)
	    {
	        if(ereg('.class.php',$file)) 
	        {
	            require_once(dwho_file::joinpath($libdir,$file));
	            array_push($tree,$libdir.$file);
	        }
	    }
	
	    return($tree);
	}
	
	public function gener_graph($type,$name)
	{
		
		switch($type)
		{
			case 't1':
				$this->gener_graph_t1($name);
				break;
			default:
				$this->gener_graph_t1($name);
		}
	}
	
	private function gener_graph_t1($name)
	{
		$data = $this->build_data_t1();
		$this->write_graph_t1($name, $data);
	}
	
	private function build_data_t1()
	{		
		$myData = new pData();
		
		$abcisse_label = array();
		foreach ($this->_data_table as $row => $cols)
			array_push($abcisse_label,$row);
			
		asort($abcisse_label);
		$myData->AddPoints($abcisse_label,$this->_name);
		$myData->setAbscissa($this->_name);
		
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
	 		$myData->AddPoints($v,$label);
		}
		
		/*		
		$coltitle = $this->_data_table;		
		$coltitlekey = array_keys($coltitle);		
		while ($coltitle)
		{	
			$titlecolskey = array_shift($coltitlekey);
			$listcols = array_shift($coltitle);
			$listcolskey = array_keys($listcols);
		
			var_dump($listcolskey);
			
			$lsdata = array();
			while ($listcols)
			{
				$cols = array_shift($listcols);
				$colskey = array_shift($listcolskey);
						
				if($cols['format'] !== 'int')
					continue;
					
				if (in_array($colskey,$this->_ignore_col) === true)
						continue;
				
				if (($val = $this->eval_result_data($cols)) === null
				|| is_numeric($val) === false)
					array_push($lsdata,0);
				else
					array_push($lsdata,$val);
			}
			$label = '&nbsp;';
			# <acronym title="Durée moyenne de WRAPUP">DMWU</acronym>
			if (is_null($titlecolskey) === false)
				$label = preg_replace('/<+\s*\/*\s*([A-Z][A-Z0-9]*)\b[^>]*\/*\s*>+/i','',$this->bbf('col_'.$titlecolskey));
				
	 		$myData->AddPoints($lsdata,$label);
		}
			
		var_dump($lsdata);
		
		*/
		return($myData);
	}
	
	private function write_graph_t1($name,$data)
	{
		$pchart_conf = &$this->_pchart_conf;		
		$root_path = $pchart_conf['path'];
		$fonts_path = $pchart_conf['fonts'];
		
		$name = $name.'-'.$this->_xs->get_axetype();
		$filepath = dwho_file::joinpath($root_path,$name).'.png';
		
		var_dump($filepath);
		
		return;
		
		$settingsCache = array();
		$settingsCache['CacheFolder'] = $root_path;
		
		/* Create the cache object */
		$myCache = new pCache($settingsCache);
		 
		/* Compute the hash linked to the chart data */
		$ChartHash = $myCache->getHash($data);
		 
		/* Test if we got this hash in our cache already */
		if ($myCache->isInCache($ChartHash))
		{
			/* If we have it, get the picture from the cache! */
			$myCache->saveFromCache($ChartHash,$filepath);
			return(true);
		}
		
		$nbDataTable = count($this->_data_table);
		$graph_w = 750;
		$graph_h = (int) ($nbDataTable * 200);
		# X1,Y1 is the top left corner of the bounding box.
		$graph_area_tl_w = (int) ($graph_w - ($graph_w - 80));
		$graph_area_tl_h = (int) ($graph_h - ($graph_h - 30));
		# X2,Y2 is the borrom right corner of the bounding box.
		$graph_area_br_w = (int) ($graph_w - 20);
		$graph_area_br_h = (int) ($graph_h - 20);
		
		/* Create the pChart object */
		$myPicture = new pImage($graph_w,$graph_h,$data); 
		$myPicture->drawGradientArea(0,0,$graph_w,$graph_h,DIRECTION_VERTICAL,array("StartR"=>240,"StartG"=>240,"StartB"=>240,"EndR"=>180,"EndG"=>180,"EndB"=>180,"Alpha"=>100)); 
		$myPicture->drawGradientArea(0,0,$graph_w,$graph_h,DIRECTION_HORIZONTAL,array("StartR"=>240,"StartG"=>240,"StartB"=>240,"EndR"=>180,"EndG"=>180,"EndB"=>180,"Alpha"=>20)); 
		$myPicture->setFontProperties(array("FontName"=>$fonts_path."/verdana.ttf","FontSize"=>6)); 
		
		/* Draw the chart scale */
		$myPicture->setGraphArea($graph_area_tl_w,$graph_area_tl_h,$graph_area_br_w,$graph_area_br_h);
		$myPicture->drawScale(array("CycleBackground"=>TRUE,"DrawSubTicks"=>TRUE,"GridR"=>0,"GridG"=>0,"GridB"=>0,"GridAlpha"=>10,"Pos"=>SCALE_POS_TOPBOTTOM));		
		$myPicture->setShadow(TRUE,array("X"=>1,"Y"=>1,"R"=>0,"G"=>0,"B"=>0,"Alpha"=>10));
		
		/* Draw the chart */
		$myPicture->drawBarChart(array("DisplayPos"=>LABEL_POS_INSIDE,"DisplayValues"=>TRUE,"Rounded"=>TRUE,"Surrounding"=>30));
		
		/* Write the legend */
		$myPicture->drawLegend(15,5,array("Style"=>LEGEND_NOBORDER,"Mode"=>LEGEND_HORIZONTAL)); 
		
		/* Push the rendered picture to the cache */
		$myCache->writeToCache($ChartHash,$myPicture);

		$myPicture->Render($filepath);
		return(true);
	}
}

?>
