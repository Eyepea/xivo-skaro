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

require_once(dwho_file::joinpath(DWHO_PATH_ROOT,'file.inc'));

class xivo_jqplot
{
	private	 $_plugins		= array();
	private	 $_pluginloaded	= array();
	private	 $_data_table	= array();
	private	 $_data_foot	= array();
	private	 $_data_row		= array();
	private	 $_result		= array();
	
	public function __construct()
	{			
		if (dwho_file::is_d_rx(DWHO_LOCATION_SCRIPT) === false)
			die('ERR: Failed to load script dir '.DWHO_LOCATION_SCRIPT);
		
		$jqplot_dir = dwho_file::joinpath(DWHO_LOCATION_SCRIPT,'js','jqplot');
			
		if (dwho_file::is_d_rx($jqplot_dir) === false)
			die('ERR: Failed to load root dir jqplot '.$jqplot_dir);

		$jqplot_dir_plugins = dwho_file::joinpath($jqplot_dir,'plugins');
			
		if (dwho_file::is_d_rx($jqplot_dir_plugins) === false)
			die('ERR: Failed to load plugins dir jqplot '.$jqplot_dir_plugins);		
		
		$this->_plugins = $this->init_path_plugins($jqplot_dir_plugins);
	}
	
	private function init_path_plugins($libdir)
	{
	    $r = dwho_file::read_d($libdir,'file',FILE_R_OK);
	    sort($r);	    
	    $tree = array();
	    foreach($r as $file)
	        if(ereg('.min.js',$file))
	            array_push($tree,dwho_file::joinpath($libdir,$file));
	    return($tree);
	}	
	
	private function load_plugin($name)
	{
		$ls_plugins = $this->_plugins;
		while ($ls_plugins)
		{
			$plugin = array_shift($ls_plugins);
			if (preg_match('/jqplot.'.$name.'/i',$plugin) === 1
			&& isset($this->_pluginloaded[$name]) === false)
				$this->_pluginloaded[$name] = strstr($plugin, 'js/jqplot');
		}
		return(true);
	}
	
	public function write_js_loaded_plugin($dhtml)
	{
		foreach($this->_pluginloaded as $plugin)
			$dhtml->set_js($plugin);
	}
	
	public function init_data_full($ts)
	{
		$this->_data_row = $ts->get_data_rows();
		$this->_data_table = $ts->get_data_table();
		$this->_data_foot = $ts->get_data_foot();
	}
	
	private function add_result($key, $content)
	{
		$this->_result[$key] = $content;
	}
	
	public function get_result($key)
	{
		if (isset($this->_result[$key]) === true)
			echo $this->_result[$key];
	}
	
	public function gener_graph($type,$box,$title)
	{		
		if (empty($this->_data_table) === true)
			return(false);
		
		switch($type)
		{
			case 'pie':
				$this->gener_graph_pie($box,$title);
				break;
			case 'queue_perf':
				$this->gener_graph_queue_perf($box,$title);
				break;
			case 'prod_agent':
				$this->gener_graph_prod_agent($box,$title);
				break;
			case 'agent_stacked_total_time':
				$this->gener_graph_agent_stacked_total_time($box,$title);
				break;				
			case 'agent_stacked_average_time':
				$this->gener_graph_agent_stacked_average_time($box,$title);
				break;
			case 'agent_perf':
				$this->gener_graph_agent_perf($box,$title);
				break;
			case 'period_pie_connect':
				$this->gener_graph_period_pie_connect($box,$title);
				break;
			case 'period_pie_abandon':
				$this->gener_graph_period_pie_abandon($box,$title);
				break;
			default:
		}
	}
	
	private function gener_graph_pie($box,$title)
	{
		$this->load_plugin('pieRenderer');
		
		$listfield = array('connect','abandon','on_close','on_saturation','on_hungup','on_guide','on_number');
		
		$data = $this->_data_foot;
		$pie = '[';
		$datakey = array_keys($data);
		while ($data)
		{
			$colname = array_shift($datakey);
			$colvalue = array_shift($data); 
			if (in_array($colname,$listfield) === false)
				continue;
			$row = $this->bbf('col_'.$colname);
			$fieldname = preg_replace('/<+\s*\/*\s*([A-Z][A-Z0-9]*)\b[^>]*\/*\s*>+/i','',$row);
			$pie .= '[\''.$fieldname.'\','.$colvalue['result'].']';
			if (count($data) > 0)
				$pie .= ', ';
		}
		$pie .= ']';
		
		ob_start();
		
		echo '<div class="sb-graph">
			<div class="jqPlot" id="'.$box.'" style="height:240px; width:340px;margin: auto"></div>				
		</div>';
		echo "\n\n";
		
		echo "<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;
			line1 = $pie;
			plot1 = $.jqplot('$box', [line1], 
			{
				grid:{
		            drawGridlines:true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
			    legend: {show:true},
			    title: '".$this->bbf($title)."',
			    seriesDefaults: 
			    {
			    	renderer: $.jqplot.PieRenderer, 
			    	trendline:{show:true},
			    	rendererOptions: 
			    	{
			    		padding: 8, 
			    		showDataLabels: true,
			    		sliceMargin: 2, 
			    		startAngle: -90,
						dataLabelPositionFactor: 0.9,
						dataLabelNudge: 0,
						dataLabelThreshold: 1
					}					
				},
	   			cursor:{show: false}
			});
		</script> \n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function gener_graph_queue_perf($box,$title)
	{
		$this->load_plugin('barRenderer');
		$this->load_plugin('categoryAxisRenderer');
		$this->load_plugin('logAxisRenderer');
		$this->load_plugin('canvasAxisTickRenderer');
		$this->load_plugin('canvasTextRenderer');
		$this->load_plugin('pointLabels');
		$this->load_plugin('highlighter');
		$this->load_plugin('cursor');
		
		$data_table = $this->_data_table;
		$listrow = $this->_data_row;
		$listrow = array_shift($listrow);
			
		# array for ticks label
		$list_ticks = array();
		foreach ($listrow as $row)
			array_push($list_ticks,$row['identity']);
		
		$listatw = array();
		$listhome_rated = array();
		$listqos = array();
		foreach ($data_table as $colname => $colvalue)
		{
			array_push($listhome_rated,$colvalue['home_rated']['result']);
			array_push($listqos,$colvalue['qos']['result']);
			array_push($listatw,$colvalue['average_time_waiting']['result']);
		}
		
		$axex = $this->build_js_list($listatw,'valuewithindex',true);
		$axey1 = $this->build_js_list($listhome_rated,'value',true);
		$axey2 = $this->build_js_list($listqos,'value',true);
		
		ob_start();
		
		echo '<div class="sb-graph">
			<div class="jqPlot" id="'.$box.'" style="height:290px; width:640px;margin-left: 100px;"></div>				
		</div>';
		echo "\n\n";
		
		echo "<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;
			line1 = $axex;
			line2 = $axey1;
			line3 = $axey2;

			plot3 = $.jqplot('$box', [line1, line2, line3], 
			{
				grid:
				{
		            drawGridlines: true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
				legend: 
				{
					show: true, 
					location: 'ne', 
					xoffset: 630 , 
					yoffset: 0
				},		
			    title: '".$this->bbf($title)."',			        
			    axes: 
			    {
			        xaxis: 
			        { 
			        	renderer: $.jqplot.CategoryAxisRenderer, 
			        	ticks: ['".implode('\', \'',$list_ticks)."'],
						tickRenderer: $.jqplot.CanvasAxisTickRenderer,
						tickOptions: 
						{
			                formatString: '%d', 
			                fontSize: '10pt', 
			                fontFamily: 'Arial', 
			                angle: -30
			            }
					},
			        yaxis: 
			        { 
			        	autoscale: true, 
			        	tickOptions:{formatString: '%d%%'},
			        	min: 0
					},
			        y2axis:
			        { 
			        	autoscale: true, 
			        	tickOptions:{formatString: '%ss.'},
			        	min: 0
					}
				},			      
			    series:
			    [
			        {	
			        	label: 'TMA', 
			        	renderer: $.jqplot.BarRenderer,
			        	rendererOptions:{barMargin: 5},
			        	xaxis: 'xaxis', 
			        	yaxis: 'y2axis'
					},
			        {
			        	label: 'TA',
	        			highlighter:{show: false},
			        	pointLabels:{show: false}
					}, 
			        {
			        	label: 'QOS', 
			        	pointLabels:{show: false}
					}
			    ],
	   			cursor:{show: false}
			});
			</script>\n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function gener_graph_prod_agent($box,$title)
	{		
		$this->load_plugin('barRenderer');
		$this->load_plugin('categoryAxisRenderer');
		$this->load_plugin('canvasAxisTickRenderer');
		$this->load_plugin('canvasTextRenderer');
		$this->load_plugin('pointLabels');
		
		$data_table = $this->_data_table;
		$listrow = $this->_data_row;
		$listrow = array_shift($listrow);
			
		# array for ticks label
		$list_ticks = array();
		foreach ($listrow as $row)
			array_push($list_ticks,$row['identity']);
		
		$listprod = array();
		foreach ($data_table as $colname => $colvalue)
			array_push($listprod,$colvalue['productivity']['result']);
		
		$axex = $this->build_js_list($listprod,'valuewithindex',true);
		
		ob_start();
		
		echo '
		<div class="sb-graph">
			<div class="jqPlot" id="'.$box.'" style="height:290px; width:650px;margin-left: 100px;"></div>				
		</div>';
		echo "\n\n";
		
		echo "
		<script type=\"text/javascript\">	
			$.jqplot.config.enablePlugins = true;
			line1 = $axex;
			plot2 = $.jqplot('$box', [line1], 
			{
				grid:
				{
		            drawGridlines: true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
			    legend:
			    {
			    	show: true,
			    	location: 'se',
			    	xoffset: 670
				},
			    title:'".$this->bbf($title)."',
			    seriesDefaults:{
			        renderer:$.jqplot.BarRenderer, 
			        rendererOptions:{barPadding: 1, barMargin: 5}
			    },
			    series:
			    [
			        {label:'".$this->bbf('col_productivity')."'}
			    ],
			    axes:
			    {
			        xaxis:
			        {
			        	renderer: $.jqplot.CategoryAxisRenderer, 
			        	ticks: ['".implode('\', \'',$list_ticks)."'],
						tickRenderer: $.jqplot.CanvasAxisTickRenderer,
						tickOptions: 
						{
			                formatString: '%d', 
			                fontSize: '10pt', 
			                fontFamily: 'Arial', 
			                angle: -30
			            }
			        },
			        yaxis:
			        {
			        	autoscale: true, 
			        	tickOptions:{formatString: '%d%%'},
			        	min: 0
			        }
			    },
			    cursor:{show: false}
			});
		</script>\n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function gener_graph_agent_stacked_total_time($box,$title)
	{
		$this->load_plugin('categoryAxisRenderer');
		$this->load_plugin('barRenderer');
		$this->load_plugin('pointLabels');
		$this->load_plugin('canvasAxisTickRenderer');
		$this->load_plugin('canvasTextRenderer');
		
		$data_table = $this->_data_table;
		$listrow = $this->_data_row;
		$listrow = array_shift($listrow);
			
		# array for ticks label
		$list_ticks = array();
		foreach ($listrow as $row)
			array_push($list_ticks,$row['identity']);
			
		$listlogin = $listavailable = $listpause = $listtraitment = array();
		foreach ($data_table as $colname => $colvalue)
		{
			$login_time = $colvalue['login']['result'];
			
			$available_time_pct = 0;
			if (($available_time = $colvalue['available']['result']) !== 0
			&& $login_time !== 0)
				$available_time_pct = ($available_time / $login_time * 100);
			array_push($listavailable,$available_time_pct);
			
			$pause_time_pct = 0;
			if (($pause_time = $colvalue['pause']['result']) !== 0
			&& $login_time !== 0)
				$pause_time_pct = ($pause_time / $login_time * 100);
			array_push($listpause,$pause_time_pct);
			
			$traitment_time_pct = 0;
			if (($traitment_time = $colvalue['traitment']['result']) !== 0
			&& $login_time !== 0)
				$traitment_time_pct = ($traitment_time / $login_time * 100);
			array_push($listtraitment,$traitment_time_pct);
		}
		
		$line2 = $this->build_js_list($listavailable,'value',true);
		$line3 = $this->build_js_list($listpause,'value',true);
		$line4 = $this->build_js_list($listtraitment,'value',true);
		
		ob_start();
		
		echo '
		<div class="sb-graph">
			<div class="jqPlot" id="'.$box.'" style="height:290px; width:650px;margin-left: 100px;"></div>				
		</div>';
		echo "\n\n";
		
		echo "
		<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;	
			line2 = $line2;
			line3 = $line3;
			line4 = $line4;
			plot4 = $.jqplot('$box', [line2, line3, line4], 
			{
				grid:
				{
		            drawGridlines: true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
				legend:
				{
					show: true,				
					location: 'ne', 
					xoffset: 670
				},
				title:'".$this->bbf($title)."',
			    stackSeries: true, 
			    seriesDefaults: 
			    {
			        renderer: $.jqplot.BarRenderer,
			        rendererOptions:{barMargin: 10},  
		            pointLabels:{stackedValue: false},
		            shadow: false
			    },
			    series:
			    [
			        {
			        	label:'".$this->bbf('col_available')."',
			        	pointLabels:{ypadding: -15}
					},
			        {
			        	label:'".$this->bbf('col_pause')."',
			        	pointLabels:{ypadding: 0}
					},
			        {
			        	label:'".$this->bbf('col_traitment')."',
			        	pointLabels:{ypadding: -15}
					}
			    ],
			    axes: 
			    {
			        xaxis:
			        {
				       	renderer: $.jqplot.CategoryAxisRenderer, 
				       	ticks: ['".implode('\', \'',$list_ticks)."'],
						tickRenderer: $.jqplot.CanvasAxisTickRenderer,
						tickOptions: 
						{
			                formatString:'%s', 
			                fontSize:'10pt', 
			                fontFamily:'Arial', 
			                angle:-30
			            }
					},
			        yaxis:{
				        autoscale: true,                 
				        ticks:[0, 100], 
               			tickOptions:{formatString: '%d\%'}		        
					}
			    },
			    cursor:{show: false},
				highlighter:{show: false}			    
			});
		</script>\n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function gener_graph_agent_stacked_average_time($box,$title)
	{
		$this->load_plugin('barRenderer');
		#$this->load_plugin('categoryAxisRenderer');
		$this->load_plugin('canvasAxisTickRenderer');
		$this->load_plugin('canvasTextRenderer');
		
		$data_table = $this->_data_table;
		$listrow = $this->_data_row;
		$listrow = array_shift($listrow);
			
		# array for ticks label
		$list_ticks = array();
		foreach ($listrow as $row)
			array_push($list_ticks,$row['identity']);
			
		$listdata = $data_table;
			
		$listlogin = $listavailable = $listpause = $listtraitment = array();
		foreach ($data_table as $colname => $colvalue)
		{
			/*
			$available_time_pct = 0;
			if (($available_time = $colvalue['dmt']['result']) !== 0)
				$available_time_pct = ($available_time / $login_time * 100);
			array_push($listavailable,$available_time_pct);
			
			$pause_time_pct = 0;
			if (($pause_time = $colvalue['dmmeg']['result']) !== 0)
				$pause_time_pct = ($pause_time / $login_time * 100);
			array_push($listpause,$pause_time_pct);
			
			$traitment_time_pct = 0;
			if (($traitment_time = $colvalue['dmwu']['result']) !== 0)
				$traitment_time_pct = ($traitment_time / $login_time * 100);
			array_push($listtraitment,$traitment_time_pct);
			*/
		}
		
		$line2 = $this->build_js_list($listavailable,'value',true);
		$line3 = $this->build_js_list($listpause,'value',true);
		$line4 = $this->build_js_list($listtraitment,'value',true);
		
		ob_start();
		
		echo '
		<div class="sb-graph">
			<div class="jqPlot" id="'.$box.'" style="height:290px; width:650px;margin-left: 100px;"></div>				
		</div>';
		echo "\n\n";
		
		echo "
		<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;
			line2 = $line2;
			line3 = $line3;
			line4 = $line4;
			plot4 = $.jqplot('$box', [line2, line3, line4], {
				legend:{
					show:true, 
					location:'ne', 
					xoffset:650
				},
				title:'".$this->bbf($title)."',
			    stackSeries: true, 
			    seriesDefaults: {
			        renderer: $.jqplot.BarRenderer,
			        rendererOptions:{barMargin: 10}, 
			        pointLabels:{stackedValue: true}
			    },
			    series:
			    [
			        {label:'".$this->bbf('col_available')."'},
			        {label:'".$this->bbf('col_pause')."'},
			        {label:'".$this->bbf('col_traitment')."'}
			    ],
			    axes: 
			    {
			        xaxis:
			        {
				       	renderer: $.jqplot.CategoryAxisRenderer, 
				       	ticks: ['".implode('\', \'',$list_ticks)."'],
					},
			        yaxis:{
				        autoscale:true, 
			        	tickOptions: {formatString:'%d%%'},
			        	min: 0,
			        	max: 100
					}
			    },
			    cursor: {show: false},
				highlighter: {show:false}				
			});
		</script>\n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function gener_graph_agent_perf($box,$title)
	{		
		$this->load_plugin('barRenderer');
		$this->load_plugin('pointLabels');
		$this->load_plugin('highlighter');
		$this->load_plugin('cursor');
		$this->load_plugin('categoryAxisRenderer');
		$this->load_plugin('canvasAxisTickRenderer');
		$this->load_plugin('canvasTextRenderer');
		
		$data_table = $this->_data_table;
		$listrow = $this->_data_row;
		$listrow = array_shift($listrow);
			
		# array for ticks label
		$list_ticks = array();
		foreach ($listrow as $row)
			array_push($list_ticks,$row['identity']);
		
		$listprod = $listconnect = $listtransfer = $listringnoanswer = array();
		foreach ($data_table as $colname => $colvalue)
		{
			array_push($listprod,$colvalue['productivity']['result']);
			array_push($listconnect,$colvalue['connect']['result']);
			array_push($listtransfer,$colvalue['transfer']['result']);
			array_push($listringnoanswer,$colvalue['ringnoanswer']['result']);
		}
		
		$axey = $this->build_js_list($listprod,'valuewithindex',true);
		$axex1 = $this->build_js_list($listconnect,'value',true);
		$axex2 = $this->build_js_list($listtransfer,'value',true);
		$axex3 = $this->build_js_list($listringnoanswer,'value',true);
		
		ob_start();
		
		echo '
		<div class="sb-graph">
			<div class="jqPlot" id="chart2" style="height:290px; width:640px;margin-left: 100px;"></div>					
		</div>';
		echo "\n\n";
		
		echo "
		<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;
			line1 = $axey;
			line2 = $axex1;
			line3 = $axex2;
			line4 = $axex3;
			plot2 = $.jqplot('chart2', [ line2, line3, line4, line1 ], 
			{        
				grid:
				{
		            drawGridlines: true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
			    legend:
			    {
			    	show: true,				
					location: 'ne', 
					xoffset: 630
				},
			    title: '".$this->bbf($title)."',	
			    seriesDefaults:
			    {
			        rendererOptions:
			        {
			        	barPadding: 0,
			        	barMargin: 5
					},
            		breakOnNull: true			        
			    },
			    series:
			    [
			        {
				        label: '".$this->bbf('col_connect')."',
				        renderer: $.jqplot.BarRenderer,
						highlighter:{show: false}
					}, 
			        {
			        	label: '".$this->bbf('col_transfer')."',
				        renderer: $.jqplot.BarRenderer,
						highlighter:{show: false}
					}, 
			        {
			        	label: '".$this->bbf('col_ringnoanswer')."',
				        renderer: $.jqplot.BarRenderer,
						highlighter:{show: false},
			            markerOptions:{show: false}          
					}, 
			        { 
			        	label: '".$this->bbf('col_productivity')."',
			        	xaxis: 'xaxis', 
			        	yaxis: 'y2axis',
			        	renderer: $.CategoryAxisRenderer, 
			        	pointLabels:{show: false},
            			highlighter:{show: true}
					}
			    ],
			    axes:
			    {
			        xaxis:
			        {
			        	renderer: $.jqplot.CategoryAxisRenderer,
			        	ticks:['".implode('\', \'',$list_ticks)."'],
						tickRenderer: $.jqplot.CanvasAxisTickRenderer,
						tickOptions: 
						{
			                formatString: '%s', 
			                fontSize: '10pt', 
			                fontFamily: 'Arial', 
			                angle: -30
			            }
			        }, 
			        yaxis: 
			        { 
			        	autoscale: true,
			        	min: 0,
            			tickOptions:{formatString: '%.0f'}
					},
			        y2axis: 
			        { 
			        	autoscale: true,
			        	tickOptions:{formatString: '%d%%'},
			        	min: 0
					}
			    },
			    cursor:{show: false},
			    highlighter:{bringSeriesToFront: true}			    
			});
		</script>\n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();	
	}
	
	private function gener_graph_period_pie_abandon($box,$title)
	{
		$this->load_plugin('pieRenderer');
		
		$data = $this->_data_foot;
		$pie = '[';
		$datakey = array_keys($data);
		while ($data)
		{
			$colname = array_shift($datakey);
			$colvalue = array_shift($data);
			if (ereg('aperiod',$colname) === false)
				continue;
			$row = $this->bbf('col_'.$colname);
			$fieldname = preg_replace('/<+\s*\/*\s*([A-Z][A-Z0-9]*)\b[^>]*\/*\s*>+/i','',$row);
			$pie .= '[\''.$fieldname.'\','.$colvalue['result'].']';
			if (count($data) > 0)
				$pie .= ', ';
		}
		$pie .= ']';
		
		ob_start();
		
		echo '<div class="jqPlot" id="'.$box.'" style="height:240px; width:340px;margin-left: 350px"></div>';
		echo "\n\n";
		
		echo "<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;
			line1 = $pie;
			plot1 = $.jqplot('$box', [line1], 
			{
				grid:{
		            drawGridlines:true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
			    legend: {show:true},
			    title: '".$this->bbf($title)."',
			    seriesDefaults: 
			    {
			    	renderer: $.jqplot.PieRenderer, 
			    	trendline:{show:true},
			    	rendererOptions: 
			    	{
			    		padding: 8, 
			    		showDataLabels: true,
			    		sliceMargin: 2, 
			    		startAngle: -90,
						dataLabelPositionFactor: 0.9,
						dataLabelNudge: 0,
						dataLabelThreshold: 1
					}					
				},
	   			cursor:{show: false}
			});
		</script> \n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function gener_graph_period_pie_connect($box,$title)
	{
		$this->load_plugin('pieRenderer');
		
		$data = $this->_data_foot;
		$pie = '[';
		$datakey = array_keys($data);
		while ($data)
		{
			$colname = array_shift($datakey);
			$colvalue = array_shift($data);
			if (ereg('tperiod',$colname) === false)
				continue;
			$row = $this->bbf('col_'.$colname);
			$fieldname = preg_replace('/<+\s*\/*\s*([A-Z][A-Z0-9]*)\b[^>]*\/*\s*>+/i','',$row);
			$pie .= '[\''.$fieldname.'\','.$colvalue['result'].']';
			if (count($data) > 0)
				$pie .= ', ';
		}
		$pie .= ']';
		
		ob_start();
		
		echo '<div class="jqPlot" id="'.$box.'" style="height:240px; width:340px;margin-left: 0px;float:left;"></div>';
		echo "\n\n";
		
		echo "<script type=\"text/javascript\">
			$.jqplot.config.enablePlugins = true;
			line1 = $pie;
			plot1 = $.jqplot('$box', [line1], 
			{
				grid:{
		            drawGridlines:true,
		            background: '#ffffff',
		            borderWidth: 0,
		            shadow: false
		        },
			    legend: {show:true},
			    title: '".$this->bbf($title)."',
			    seriesDefaults: 
			    {
			    	renderer: $.jqplot.PieRenderer, 
			    	trendline:{show:true},
			    	rendererOptions: 
			    	{
			    		padding: 8, 
			    		showDataLabels: true,
			    		sliceMargin: 2, 
			    		startAngle: -90,
						dataLabelPositionFactor: 0.9,
						dataLabelNudge: 0,
						dataLabelThreshold: 1
					}					
				},
	   			cursor:{show: false}
			});
		</script> \n\n";
		
		$this->add_result($box, ob_get_contents());

		ob_end_clean();
	}
	
	private function build_js_list($list,$type,$intval=false)
	{		
		$nb = count($list);
		$return = '[';
		switch($type)
		{
			case 'valuewithindex':
				$listvalue = array_values($list);
				for($i=0;$i<$nb;$i++)
				{
					$value = &$listvalue[$i];
					$value = ($intval !== false) ? intval($value) : $value;
					$return .= '['.($i+1).','.$value.']';
					$return .= ($i < ($nb-1)) ? ', ' : '';
				}
				break;
			case 'keywithvalue':
				$listkey = array_keys($list);
				$listvalue = array_values($list);
				for($i=0;$i<$nb;$i++)
				{
					$key = &$listkey[$i];
					$value = &$listvalue[$i];
					$key = (is_numeric($key)) ? $key : '\''.$key.'\'';
					$value = (is_numeric($value)) ? $value : '\''.$value.'\'';
					$value = ($intval !== false) ? intval($value) : $value;
					$return .= '['.$key.','.$value.']';
					$return .= ($i < ($nb-1)) ? ', ' : '';
				}
				break;
			case 'key':
				$list = array_keys($list);
				for($i=0;$i<$nb;$i++)
				{
					$value = &$list[$i];
					$value = ($intval !== false) ? intval($value) : $value;
					$return .= $value;
					$return .= ($i < ($nb-1)) ? ', ' : '';
				}
				break;
			case 'value':
				$list = array_values($list);
				for($i=0;$i<$nb;$i++)
				{
					$value = &$list[$i];
					$value = ($intval !== false) ? intval($value) : $value;
					$return .= $value;
					$return .= ($i < ($nb-1)) ? ', ' : '';
				}
				break;
			default:
				$return = '';
		}
		$return .= ']';
		
		return($return);
	}
	
	private function bbf($str,$args=array())
	{
		return addslashes(dwho_i18n::babelfish($str,$args));
	}
}

?>
