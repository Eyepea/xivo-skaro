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

$act = $this->get_var('act');
$idconf = $this->get_var('ifconf');
$conf = $this->get_var('conf');
$listtype = $this->get_var('listtype');
$dbeg = $this->get_var('dbeg');
$dend = $this->get_var('dend');

$dencache = ($dend != 0) ? $this->bbf('fm_description_cache-with_end',array($dend)) : $this->bbf('fm_description_cache-without_end'); 

?>
	
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name',array($conf['name']));?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
		<div class="sb-list">		
		
		<p>
			<label id="lb-description" for="it-description"><?=$this->bbf('fm_description_cache',array($dbeg,$dencache));?></label>
		</p>				
				
		<form action="" method="get" accept-charset="utf-8">
			<?=$form->hidden(array('name' => 'act','value'	=> $act))?>
			<?=$form->hidden(array('name' => 'idconf','value'	=> $idconf))?>
			<?php
				echo	$form->select(array('desc' => $this->bbf('conf_axetype'),
								'name'		=> 'type',
							    'id'		=> 'it-conf-type',
							    'browse'	=> 'type',
				  				'labelid'	=> 'type',
							    'empty'		=> $this->bbf('fm_type-default'),
				    			'key'		=> false,
							    'bbf'		=> 'fm_type-opt',
							    'bbfopt'	=> array('argmode'	=> $listtype),
							    'selected'	=> $this->get_var('type')),
						      	$listtype);
			?>
		</form>
		
		<fieldset id="it-cache-generation" class="tab_cache_generation b-nodisplay">
			<legend><?=$this->bbf('cache_generation_processing');?></legend>
			<h1><?=$this->bbf('wait_during_traitment');?></h1>
			<p><h1 id="restitle"></h1></p>
			<p><div id="resprogressbar"></div></p>
			<p><div id="rescache"></div></p>
			<p><div id="rescachetotal"></div></p>
			<p><div id="resend"></div></p>
		</fieldset>
		<fieldset id="it-cache-success" class="tab_cache_generation b-nodisplay">
			<legend><?=$this->bbf('legend-cache_generation_success');?></legend>
			<h1><?=$this->bbf('cache_generation_success');?></h1>
			<p><h1 id="ressuccess"></h1></p>
		</fieldset>
		
<?php 
	if (($type = $this->get_var('type')) !== null
	&& ($list = $this->get_var('list'.$type)) !== null
	&& ($nb = count($list)) !== 0):
?>
		<table cellspacing="0" cellpadding="0" border="0" id="t-list-obj">
		<thead>
		<tr class="sb-top">
			<th class="th-left"><?=$this->bbf('col_cache_name')?></th>
			<th class="th-center"><?=$this->bbf('col_cache_status')?></th>
			<th class="th-right"><?=$this->bbf('col_action')?></th>
		</tr>
		</thead>
		<tbody id="disp">
<?php 
		for ($i=0;$i<$nb;$i++):
			$ref = $list[$i];
				
			$id = $ref['id'];
			$key = $ref['key'];
			$name = $ref['name'];
			$identity = $ref['identity'];
			if (is_array($key) === true)
			{
				$key = $ref['key'][0];
				$name = $ref['name'][0];
				$identity = $ref['identity'][0];
			}
			
			$basecache = DWHO_PATH_CACHE_STATS.DWHO_SEP_DIR.'cache';
			$dir = $basecache.DWHO_SEP_DIR.
					$idconf.DWHO_SEP_DIR.
					$type.DWHO_SEP_DIR.
					$key;
			
			if (($r = dwho_file::read_d($dir,'file',FILE_R_OK)) === false):
			    $infoscache = $this->bbf('cache_noexist');
			else:
			    sort($r);
				
			    $nbfile = count($r);
			    
			    $filefisrt = $r[0];
			    $filelast = $r[$nbfile-1];
			    
			    $tree = array();
			    foreach($r as $file)
			    {
			        array_push($tree,$file);
			    }
			    
			    $infoscache = $this->bbf('cache_exist-nbfile',array($nbfile));
		    endif;
			
			#if (dwho_file::is_f($file) === false
?>
		<tr class="l-infos-<?=(($i % 2) + 1)?>on2" title="<?=dwho_alttitle($identity)?>">
			<td class="td-left"><?=$identity?></td>
			<td class="td-center">&nbsp;<?=$infoscache?></td>
			<td class="td-right">
				<form action="#" method="post" accept-charset="utf-8" 
					onsubmit="init_cache();make_gener_cache('<?=$id?>');return(false);">					
					<input type="submit" name="genercache" value="<?=$this->bbf('bt-cache_generation',array($identity))?>" />					
				</form>
			</td>
		</tr>
<?php 
		endfor; 
?>
		</tbody>
		<tfoot>
		<tr>
			<td class="td-left">&nbsp;</td>
			<td class="td-center">&nbsp;</td>
			<td class="td-right">
				<form action="#" method="post" accept-charset="utf-8" 
					onsubmit="init_cache();make_gener_cache();return(false);">				
					<input type="submit" name="genercache" value="<?=$this->bbf('bt-cache_generation_all')?>" />					
				</form>
			</td>
		</tr>
		</tfoot>
		</table>
<?php endif; ?>
		</div>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
<script type="text/javascript">	
dwho.dom.set_onload(function() {
	dwho.dom.add_event('change',
			   dwho_eid('it-conf-type'),
			   function(){this.form.submit();});
});
<?php 
if (($type = $this->get_var('type')) !== null
&& ($listmonth = $this->get_var('listmonth')) !== null) :
	
	$js_listmonth_firstday = array();
	$js_listmonth_lastday = array();
	$js_listmonth_timestamp = array();

	foreach ($listmonth as $month)
	{
		array_push($js_listmonth_firstday,$month['time']);
		array_push($js_listmonth_timestamp,date('Y-m-d',$month['time']));
		$lastday = mktime(23, 59, 59, date('m',$month['time']) + 1, 0, date('Y',$month['time']));
		array_push($js_listmonth_lastday,$lastday);
	}

?>
var listmonthtimestamp = new Array('<?=implode('\',\'',$js_listmonth_timestamp)?>');
var listmonthfirstday = new Array('<?=implode('\',\'',$js_listmonth_firstday)?>');
var listmonthlastday = new Array('<?=implode('\',\'',$js_listmonth_lastday)?>');
this.total = listmonthtimestamp.length;

function init_cache()
{
	this.counter = 0;
	this.start = this.start2 = (new Date).getTime();
	this.avg = new Array();
	dwho_eid('t-list-obj').style.display = 'none';
	dwho_eid('it-cache-generation').style.display = 'block'; 
}

function xivo_gener_cache(idconf,dbeg,dend,type,idtype)
{	
	new dwho.http('/statistics/call_center/ui.php/genercache/',
				{'callbackcomplete': function() { make_gener_cache(idtype); },
				'method': 'post',
				'cache': false},
				{'idconf': idconf,'dbeg': dbeg,'dend': dend,'type': type,'idtype': idtype},
				true);	
	 this.counter++;
}

function make_gener_cache(idtype)
{	
	var pct = ( (this.counter / this.total) * 100);
	$(function() {
		$( "#resprogressbar" ).progressbar({
			value: pct
		});
	});
	
	if (this.counter >= this.total)
	{
		gener_on_success();
		return;
	}
	
	idtype = (typeof idtype == 'undefined') ? null : idtype;
	var objectProcessing = (idtype == null) ? '<?=$this->bbf('object_all')?>' : idtype;

	var i = this.counter;
	var dprocess = listmonthtimestamp[i];
	var date = dprocess.split('-');
	var year = date[0];
	var day = date[2];
	var month = date[1];
	var humandate = year + '-' + month;// + '-' + day;
	
	var diff = (new Date).getTime() - this.start;
	var diff2 = (new Date).getTime() - this.start2;
	this.avg.push(diff2);
	
	//dwho_eid('restitle').innerHTML = '<?=$this->bbf('object_processing')?> ' + objectProcessing;
	var info = '';
	info += '<p>';
	info += '<b>' + humandate + '</b> <?=$this->bbf('in_progress')?>';
	info += '........... ';
	info += ' <?=$this->bbf('process_last_time_traitment')?> ' + (diff2 / 1000) + 's';
	info += '</p>';
	dwho_eid('rescache').innerHTML = info;

	var rescachetotal = '';
	var total_time = Math.round(diff / 1000);
	rescachetotal += '<?=$this->bbf('process_total_time')?> ' + total_time + 's';
	rescachetotal += '<br>';
	var remaining_time = Math.round((average(this.avg) * (this.total - this.counter)) / 1000);
	rescachetotal += '<?=$this->bbf('process_remaining_time')?> ' + remaining_time + 's';
	dwho_eid('rescachetotal').innerHTML = rescachetotal;

	xivo_gener_cache('<?=$idconf?>',listmonthfirstday[i],listmonthlastday[i],'<?=$type?>',idtype);
	
	this.start2 = (new Date).getTime();
}

function average(arr)
{
   var items =arr.length
   var sum = 0
   for (i = 0; i < items;i++)
      sum += arr[i]
   return (sum/items)
}

function gener_on_success()
{
	dwho_eid('it-cache-generation').style.display = 'none'; 
	dwho_eid('it-cache-success').style.display = 'block'; 
	//dwho_eid('t-list-obj').style.display = 'block';
	//dwho_eid('ressuccess').innerHTML = info;
}

<?php 
endif;
?>
</script>