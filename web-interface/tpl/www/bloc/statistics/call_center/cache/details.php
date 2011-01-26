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

$url = &$this->get_module('url');
$form = &$this->get_module('form');
$dhtml = &$this->get_module('dhtml');
$dhtml->write_js('');

$idconf = $this->get_var('ifconf');
$conf = $this->get_var('conf');
$dbeg = $this->get_var('dbeg');
$dend = $this->get_var('dend');

$js_listmonth_firstday = array();
$js_listmonth_lastday = array();
$js_listmonth_timestamp = array();

if (($listmonth = $this->get_var('listmonth')) === false
|| count($listmonth) === 0
|| is_null($conf) === true)
	return;
	
	
		
		/*
    $r = dwho_file::read_d($libdir,'file',FILE_R_OK);
    sort($r);
    
    $tree = array();
    foreach($r as $file)
    {
        if(ereg('.class',$file)) {
            require_once($libdir.$file);
            array_push($tree,$libdir.$file);
        }
    }

    return($tree);
    */

foreach ($listmonth as $month)
{
	array_push($js_listmonth_firstday,$month['time']);
	array_push($js_listmonth_timestamp,date('Y-m-d',$month['time']));
	$lastday = mktime(23, 59, 59, date('m',$month['time']) + 1, 0, date('Y',$month['time']));
	array_push($js_listmonth_lastday,$lastday);
#	var_dump(date('Y-m-d H:i:s',$month['time']));
#	var_dump(date('Y-m-d H:i:s',$lastday));
}

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name',array($conf['name']));?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
		<div class="sb-list"> 
		<form action="#" method="post" accept-charset="utf-8" 
			onsubmit="make_gener_cache();return(false);">
			
			<input type="submit" name="genercache" value="gener" />
			
		</form>
		
		<div id="rescache" style="border:1px solid black;">
			
		</div>
		
		
		<?php
			echo 	$url->href_html($this->bbf('cache_manage_queue'),
						'statistics/call_center/configuration',
						array('act'	=> 'cache',
						      'id'	=> $idconf,
							  'type'=> 'queue'));
			echo 	$url->href_html($this->bbf('cache_manage_agent'),
						'statistics/call_center/configuration',
						array('act'	=> 'cache',
						      'id'	=> $idconf,
							  'type'=> 'agent'));
			echo 	$url->href_html($this->bbf('cache_manage_period'),
						'statistics/call_center/configuration',
						array('act'	=> 'cache',
						      'id'	=> $idconf,
							  'type'=> 'period'));
		?>	
		
		<form action="" method="get" accept-charset="utf-8">
			<input type="submit" name="genercache" value="gener" />
		</form>

		<p>
		<?=$this->bbf('date_history_cache',
		array(date('Y-m-d',$this->get_var('dbeg')),
		date('Y-m-d',$this->get_var('dend'))));?>
		</p>
		
		
		<table cellspacing="0" cellpadding="0" border="0">
		<thead>
		<tr class="sb-top">
			<th class="th-left"><?=$this->bbf('col_cache_date')?></th>
			<th class="th-center"><?=$this->bbf('col_cache_datefile')?></th>
			<th class="th-right"><?=$this->bbf('col_action')?></th>
		</tr>
		</thead>
		<tbody id="disp">
		<?php 
		
			#$file = XIVO_PATH_ROOT.'/cache/'.$idconf.'/'.$type.'/'.$key.'/'.$year.$month.'.db';	
		
			dwho_file::read_d('');
		
			$nbmonth = count($js_listmonth_timestamp);
			for($i=0;$i<$nbmonth;$i++): 
				$ref = &$js_listmonth_timestamp[$i];
							
				#if (dwho_file::is_f($file) === false
		?>
		<tr class="fm-paragraph l-infos-<?=(($i % 2) + 1)?>on2" title="<?=dwho_alttitle('lol')?>">
			<td class="td-left">&nbsp;</td>
			<td class="td-center">&nbsp;</td>
			<td class="td-right">&nbsp;</td>
		</tr>
		<?php endfor; ?>
		</tbody>
		</table>		
		
		</div>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
<script>

//xivo_date_month

var listmonthtimestamp = new Array('<?=implode('\',\'',$js_listmonth_timestamp)?>');
var listmonthfirstday = new Array('<?=implode('\',\'',$js_listmonth_firstday)?>');
var listmonthlastday = new Array('<?=implode('\',\'',$js_listmonth_lastday)?>');
this.total = listmonthtimestamp.length;
this.counter = 0;
this.start = this.start2 = (new Date).getTime();

function xivo_gener_cache(idconf,dbeg,dend)
{
	new dwho.http('/statistics/call_center/ui.php/genercache/',
				{'callbackcomplete': function() { make_gener_cache(); },
				'method': 'post',
				'cache': false},
				{'idconf': idconf,'dbeg': dbeg,'dend': dend},
				true);	
	 this.counter++;
}

function make_gener_cache()
{
	if (this.counter >= this.total)
		return;

	var i = this.counter;	
	var dprocess = listmonthtimestamp[i];
	var date = dprocess.split('-');
	var year = date[0];
	var day = date[2];
	var month = date[1];
	var humandate = year + '-' + month;// + '-' + day;
	
	var diff = (new Date).getTime() - this.start;
	var diff2 = (new Date).getTime() - this.start2;

	var info = '<p>';
	info += humandate + ' en cours ........... traitement du mois:' + (diff2 / 1000) + 's total:' + (diff / 1000) + 's';
	info += '</p>';
	dwho_eid('rescache').innerHTML += info;

	xivo_gener_cache('<?=$idconf?>',listmonthfirstday[i],listmonthlastday[i]);
	this.start2 = (new Date).getTime();
}

</script>