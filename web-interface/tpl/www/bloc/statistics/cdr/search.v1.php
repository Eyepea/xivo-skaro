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

$form = &$this->get_module('form');
$url = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

$element = $this->get_var('element');
$result = $this->get_var('result');
$info = $this->get_var('info');

?>
<div id="sr-cdr" class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
		<form action="#" method="post" accept-charset="utf-8">
		<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
		<?=$form->hidden(array('name' => 'act','value' => 'search'))?>		
		<div class="fm-paragraph fm-desc-inline">
			<div class="fm-multifield">
		<?php
			echo	$form->text(array('desc'	=> $this->bbf('fm_dbeg'),
						  'paragraph'	=> false,
						  'name'	=> 'dbeg',
						  'labelid'	=> 'dbeg',
						  'default'	=> dwho_i18n::strftime_l('%Y-%m-%d',null),
						  'value'	=> $info['dbeg']));
		?>
			</div>
			<div class="fm-multifield">
		<?php
			echo	$form->text(array('desc'	=> $this->bbf('fm_dend'),
						  'paragraph'	=> false,
						  'name'	=> 'dend',
						  'labelid'	=> 'dend',
						  'value'	=> $info['dend']));
		?>
			</div>
		</div>
		<?=$form->submit(array('name' => 'submit','id' => 'it-submit','value' => $this->bbf('fm_bt-search')))?>		
		</form>
		
		<div id="cdr-container" class='tabcontainer'>  
		    <div id='general-info'> 
		        <table id="mygrid"></table> 
				<div id="pager"></div> 
		    </div> 		 
		</div>
	</div>
	
	<script type="text/javascript">
<?php
	if ($result !== false) :
?>
		var config = {"altRows": true, 
			"rowList": [10, 25, 50, 100], 
			"jsonReader": {"repeatitems": false}, 
			"viewrecords": true, 
			"autowidth": true, 
			"shrinkToFit": true, 
			"height": "auto", 
			"mtype": "GET", 
			"caption": "<?=$this->bbf('table-call_record_details');?>", 
			"datatype": "json", 
			"gridview": true, 
			"forcefit": true, 
			"url": "/statistics/ui.php/cdr/search?dbeg=<?=$info['dbeg']?>&dend=<?=$info['dend']?>", 
			"rowNum": 10, 
			"pager": "#pager",
			"colModel": 
			[
				{"index": "calldate", "label": "Date", "editable": true, "name": "calldate", "width": 50}, 
				{"index": "channel", "label": "Channel", "editable": true, "name": "channel", "width": 50}, 
				{"index": "src", "label": "Source", "editable": true, "name": "src", "width": 50}, 
				{"index": "clid", "label": "CLID", "editable": true, "name": "clid", "width": 50}, 
				{"index": "dst", "label": "Destination", "editable": true, "name": "dst", "width": 50}, 
				{"index": "disposition", "label": "Disposition", "editable": true, "name": "disposition", "width": 50}, 
				{"index": "duration", "label": "Dur\u00e9e", "editable": true, "name": "duration", "width": 50}, 
				{"index": "accountcode", "label": "Accountcode", "editable": true, "name": "accountcode", "width": 50}
			]};
	
		$(function (){
	        $("#mygrid").jqGrid(config).navGrid('#pager', 
				{ add: false, edit: false, del: false, view: true },
	        	{}, // edit options
	        	{}, // add options
	       		{}, // del options 
		        { multipleSearch:true, closeOnEscape:true },// search options 
		        { jqModal:true,  closeOnEscape:true } // view options
	        ).filterToolbar({ stringResult: true,searchOnEnter : false });
	    });
    
<?php 
	endif;
?>
		$.datepicker.setDefaults({
			currentText: 'Now',
			changeYear: true,
			firstDay: 1,
			selectOtherMonths: true,
			dayNamesMin: xivo_date_day_min,
			ayNamesShort: xivo_date_day_short,
			dayNames: xivo_date_day,
			monthNames: xivo_date_month,
			monthNamesShort: xivo_date_month_short,
			nextText: xivo_date_next,
			prevText: xivo_date_prev,
			showAnim: 'fold',
			showMonthAfterYear: true
		});
		
		$("#it-dbeg").datepicker({
			dateFormat: 'yy-mm-dd',
			altFormat: 'yy-mm-dd',
		});
		
		$("#it-dend").datepicker({
			dateFormat: 'yy-mm-dd',
			altFormat: 'yy-mm-dd',
		});
	</script>
		
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>