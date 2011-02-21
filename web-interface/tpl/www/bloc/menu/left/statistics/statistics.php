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

$conf = $this->get_var('conf');
$listconf = $this->get_var('listconf');
$listaxetype = $this->get_var('listaxetype');
$infocal = $this->get_var('infocal');
$element = $this->get_var('element');

?>
<dl>
<?php
	if(xivo_user::chk_acl_section('service/statistics/call_center') === true):
?>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name_call_center');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
		<dl>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_home_call_center'),
						   'statistics/call_center/index');?>
			</dd>
<?php
	if(xivo_user::chk_acl_section('service/statistics/call_center/configuration') === true):
?>
			<dt><?=$this->bbf('mn_left_ti_configuration_call_center');?></dt>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_configuration_call_center'),
						   'statistics/call_center/configuration','act=list');?>
			</dd>
<?php
	endif;
?>
<?php
	if(xivo_user::chk_acl_section('service/statistics/call_center/data') === true):
?>
			<dt><?=$this->bbf('mn_left_ti_statistics_call_center');?></dt>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-1'),
						   'statistics/call_center/stats1');?>
			</dd>
			<dd id="mn-2">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-2'),
						   'statistics/call_center/stats2');?>
			</dd>
			<dd id="mn-3">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-3'),
						   'statistics/call_center/stats3');?>
			</dd>
			<dd id="mn-4">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-4'),
						   'statistics/call_center/stats4');?>
			</dd>
			<dd id="mn-5">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-5'),
						   'statistics/call_center/stats5');?>
			</dd>
<?php
	endif;
?>
		</dl>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
<?php
	endif;
?>
<?php
	if(xivo_user::chk_acl_section('service/statistics/cdr') === true):
?>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name_cdr');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
		<dl>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_home_cdr'),
						   'statistics/cdr/index');?>
			</dd>
		</dl>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
<?php
	endif;
?>
</dl>

<?php
	if(is_null($this->get_var('showdashboard')) === false):
?>
<div id="dashboard">
	<div class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name_dashboard');?></span>
		<span class="span-right">&nbsp;</span>
	</div>
	<div class="sb-content">
		<div id="sr-stats" class="">
		<div id="it-loading" class="b-nodisplay" style="position: absolute;width: 75px;height: 75px;margin-left: 50px;">
			<img alt="loading" src="/img/site/loading.gif" width="75" height="75" />
		</div>
		<form action="<?=$_SERVER['PHP_SELF']?>" method="get" accept-charset="utf-8" onsubmit="fm_chk();">
			<div id="d-conf-list" class="fm-paragraph">
<?php
				echo	$form->select(array('name'	=> 'confid',
							    'id'		=> 'it-conf-list',
							    'paragraph'	=> false,
							    'browse'	=> 'conf',
							    'empty'		=> $this->bbf('toolbar_fm_conf'),
							    'key'		=> 'name',
							    'altkey'	=> 'id',
							    'class'		=> 'fm-selected-conf',
							    'selected'	=> $this->get_var('confid')),
						      	$listconf);
?>
			</div>
<?php
	if(is_null($this->get_var('listobject')) === false
	&& is_null($this->get_var('axetype')) === false
	&& $this->get_var('axetype') !== 'type'):	
		$listobject = $this->get_var('listobject');
		foreach ($listobject as $k => &$v)
			$v['identity'] = dwho_trunc(&$v['identity'],25,'...',5);
?>
			<div id="it-cal-object" class="fm-paragraph">
<?php
				echo	$form->select(array('name'	=> 'key',
							    'id'		=> 'it-conf-key',
							    'paragraph'	=> false,
							    'browse'	=> 'key',
				  				'labelid'	=> 'key',
				    			'key'		=> 'identity',
					   			'altkey'	=> 'keyfile',
							    'class'		=> 'fm-selected-obj',
							    'selected'	=> $this->get_var('objectkey')),
						      	$listobject);
?>
			</div>
<?php
	elseif(($value = $this->get_var('objectkey')) !== null):
		echo $form->hidden(array('name' => 'key','value' => $value));
	endif;
?>
<?php	
	if(is_null($this->get_var('listobject')) === false
	&& is_null($this->get_var('axetype')) === false
	&& $this->get_var('axetype') !== 'type'):
?>
			<div id="d-conf-axetype" class="fm-paragraph">	
			<?=$this->bbf('conf_axetype')?>
			<?php
				echo	$form->select(array('name'	=> 'axetype',
							    'id'		=> 'it-conf-axetype',
							    'paragraph'	=> false,
							    'browse'	=> 'axetype',
				  				'labelid'	=> 'axetype',
							    'empty'		=> $this->bbf('fm_axetype-default'),
				    			'key'		=> false,
							    'bbf'		=> 'fm_axetype-opt',
							    'bbfopt'	=> array('argmode'	=> $listaxetype),
							    'selected'	=> $this->get_var('axetype')),
						      	$listaxetype);
			?>
			</div>
<?php
	else:
		echo $form->hidden(array('name' => 'axetype','value' => 'type'));
	endif;
	
	if(is_null($conf) === false && $conf !== false):
?>
			<div id="it-cal-type" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-type"><?=$this->bbf('fm_dbeg')?></label>
						<input type="text" name="dbeg" id="it-dbeg-type" value="<?=$infocal['dbeg']?>" size="8" />
					</div>
					<div class="fm-desc-inline">
						<label id="lb-dend" for="it-dend-type"><?=$this->bbf('fm_dend')?></label>
						<input type="text" name="dend" id="it-dend-type" value="<?=$infocal['dend']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-day" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-day"><?=$this->bbf('fm_dday')?></label>
						<input type="text" name="dday" id="it-dbeg-day" value="<?=$infocal['dday']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-week" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-week"><?=$this->bbf('fm_dweek')?></label>
						<input type="text" name="dweek" id="it-dbeg-week" value="<?=$infocal['dweek']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-month" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-month"><?=$this->bbf('fm_dmonth')?></label>
						<input type="text" name="dmonth" id="it-dbeg-month" value="<?=$infocal['dmonth']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-year" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-year"><?=$this->bbf('fm_dyear')?></label>
						<input type="text" name="dyear" id="it-dbeg-year" value="<?=$infocal['dyear']?>" size="4" />
					</div>
				</div>
			</div>
			<div class="fm-desc-inline">
				<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
			</div>
<script type="text/javascript">

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
	showMonthAfterYear: true,
	showWeek: true,
	weekHeader: 'W'
});

$("#it-dbeg-type").datepicker({
	dateFormat: 'yy-mm-dd',
	altFormat: 'yy-mm-dd',
});
$("#it-dend-type").datepicker({
	dateFormat: 'yy-mm-dd',
	altFormat: 'yy-mm-dd',
});
$("#it-dbeg-day").datepicker({
	dateFormat: 'yy-mm-dd',
	altFormat: 'yy-mm-dd',
});
$("#it-dbeg-week").datepicker({
	dateFormat: 'yy-mm-dd',
	altFormat: 'yy-mm-dd',
});
$("#it-dbeg-month").datepicker({
	dateFormat: 'yy-mm',
	altFormat: 'yy-mm',
});

</script>
<?php
	endif;
?>
		</form>
		</div>
<?php
	if(is_null($conf) === false && $conf !== false):
	$dbeg = $conf['dbegcache'];
	$dend = $conf['dendcache'];
	$dencache = ($dend != 0) ? $this->bbf('hlp_fm_conf_period_cache-with_end',array($dend)) : $this->bbf('hlp_fm_conf_period_cache-without_end');
?>
		<fieldset>
			<legend><?=$this->bbf('title_conf_cache_period')?></legend>
			<?=$this->bbf('conf_cache_period',array($dbeg,$dencache))?>
		</fieldset>
		<fieldset>
			<legend><?=$this->bbf('conf_time_range')?></legend>
			<?=substr($conf['hour_start'],0,5)?> - <?=substr($conf['hour_end'],0,5)?>
		</fieldset>
		<fieldset>
			<legend><?=$this->bbf('conf_workweek')?></legend>
		<?php
			$workweek = $conf['workweek'];
			
			foreach ($workweek as $day => $val) :
				$day = strtoupper(substr($this->bbf($day),0,3));
				if ($val === true)
					echo '<i>'.$day.'</i> ';
				else
					echo '<i class="barre">'.$day.'</i> ';
			endforeach;
		?>
		</fieldset>
<?php
	endif;
?>
		<fieldset>
			<legend><?=$this->bbf('bench_dashboard')?></legend>
			<?=dwho_second_to($this->get_var('bench'),2), ' - ', dwho_byte_to($this->get_var('mem_info'))?>
		</fieldset>    
    </div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>

<script type="text/javascript">	
function fm_chk(){
	dwho_eid('it-submit').disabled = true;
	dwho_eid('it-submit').value = '<?=$this->bbf('fm-wait-submit')?>';
	dwho_eid('it-loading').style.display = 'block';
};
dwho.dom.set_onload(function()
{
<?php
	if(is_null($conf) === true || $conf === false):
?>
	dwho.dom.add_event('change',
			   dwho_eid('it-conf-list'),
			   function(){this.form.submit();});
<?php
	endif;
?>	
	var lsaxetype = new Array('<?=implode('\', \'',$listaxetype)?>');
	dwho.dom.add_event('change',
			   dwho_eid('it-conf-axetype'),
			   function(){
		   			var form = this.form;
		   			for(var i=0;i<form.elements.length;i++)
			   		{
		   				var formElement = form.elements[i];
		   				var name = formElement.name;
		   				var value = formElement.value;
		   				if (name == 'axetype'
			   			&& dwho_eid('it-cal-'+value) != false)
		   				{
		   					for(var u=0;u<lsaxetype.length;u++)
		   					{
			   					var divtohide = dwho_eid('it-cal-'+lsaxetype[u]);
			   					if (divtohide)
			   					{
			   						divtohide.style.display = 'none';
				   					if (lsaxetype[u] == 'type')
				   						dwho_eid('it-cal-object').style.display = 'none';
			   					}
		   					}
		   					var divtoshow = dwho_eid('it-cal-'+value);
		   					if (divtoshow)
		   					{
		   						divtoshow.style.display = 'block';
			   					if (value != 'type')
			   						dwho_eid('it-cal-object').style.display = 'block';
		   					}
		   				}
			   		}
				});

	for(var u=0;u<lsaxetype.length;u++)
	{
		var divtoshow = dwho_eid('it-cal-'+lsaxetype[u]);
		if (lsaxetype[u] == '<?=$this->get_var('axetype')?>'
		&& divtoshow)
			divtoshow.style.display = 'block';
	}
});
</script>
<?php
	endif;
?>