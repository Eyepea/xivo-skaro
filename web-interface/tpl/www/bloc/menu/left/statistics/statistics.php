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
	if(xivo_user::chk_acl('call_center', 'configuration', 'service/statistics') === true):
?>
			<dt><?=$this->bbf('mn_left_ti_configuration_call_center');?></dt>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_configuration_call_center'),
						   'statistics/call_center/configuration','act=list');?>
			</dd>
			<dd id="mn-2">
				<?=$url->href_html($this->bbf('mn_left_configuration_call_center-qos'),
						   'statistics/call_center/configuration','act=qos');?>
			</dd>
<?php
	endif;
?>
<?php
	if(xivo_user::chk_acl('call_center', 'data', 'service/statistics') === true):
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
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-4'),
						   'statistics/call_center/stats4');?>
			</dd>
			<dd id="mn-4">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-3'),
						   'statistics/call_center/stats3');?>
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
		<form action="<?=$_SERVER['PHP_SELF']?>" method="post" accept-charset="utf-8">
			<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value'	=> DWHO_SESS_ID))?>
			<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
			<?=$form->hidden(array('name' => 'act','value' => 'datecal'))?>
			<div id="it-cal-conf" class="fm-paragraph">
		<?php
				echo	$form->select(array('name'	=> 'confid',
							    'id'		=> 'it-toolbar-conf',
							    'paragraph'	=> false,
							    'browse'	=> 'conf',
							    'empty'		=> $this->bbf('toolbar_fm_conf'),
							    'key'		=> 'name',
							    'altkey'	=> 'id',
							    'selected'	=> $this->get_var('confid')),
						      	$listconf);
		?>
			</div>
<?php
	if(is_null($this->get_var('listobject')) === false
	&& is_null($this->get_var('conf','axetype')) === false
	&& $this->get_var('conf','axetype') !== 'type'):
?>
			<div id="it-cal-object" class="fm-paragraph">	
			<?php
				echo	$form->select(array('name'	=> 'key',
							    'id'		=> 'it-conf-key',
							    'paragraph'	=> false,
							    'browse'	=> 'key',
				  				'labelid'	=> 'key',
				    			'key'		=> 'name',
					   			'altkey'	=> 'id',
							    'selected'	=> $this->get_var('objectkey')),
						      	$this->get_var('listobject'));
			?>
			</div>
<?php
	elseif(($value = $this->get_var('conf','objectkey')) !== null):
		echo $form->hidden(array('name' => 'key','value' => $value));
	endif;
?>
<?php
	if(is_null($this->get_var('listobject')) === false
	&& is_null($this->get_var('conf','axetype')) === false
	&& $this->get_var('conf','axetype') !== 'type'):
?>
			<div class="fm-paragraph">	
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
							    'selected'	=> $this->get_var('conf','axetype')),
						      	$listaxetype);
			?>
			</div>
<?php
	else:
		echo $form->hidden(array('name' => 'axetype','value' => 'type'));
	endif;
?>
			<div id="it-cal-type" class="b-nodisplay">
			<?php if (array_key_exists('dbeg',$infocal) === true && array_key_exists('dend',$infocal) === true): ?>
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-type"><?=$this->bbf('fm_dbeg')?></label>
						<input type="text" name="datecal[dbeg]" id="it-dbeg-type" value="<?=is_null($infocal['dbeg'])?dwho_i18n::strftime_l('%Y-%m-%d',null):$infocal['dbeg']?>" size="8"
							onclick="dwho_eid('cal-dend-type').style.display = 'none';
								xivo_calendar_display('cal-dbeg-type','it-dbeg-type');"
							onmouseover="xivo_calendar_body();"
							onmouseout="xivo_calendar_body('cal-dbeg-type','it-dbeg-type');"
						 />
						 <!-- 
						<input type="text" name="datecal[hbeg]" id="it-hbeg" value="<?=is_null($infocal['hbeg'])?'00:00':$infocal['hbeg']?>" size="4" /> 
						-->
					</div>
					<div id="cal-dbeg-type"
					     class="b-nodisplay"
					     onmouseover="xivo_calendar_body();"
					     onmouseout="xivo_calendar_body('cal-dbeg-type','it-dbeg-type');">
					</div>
					<div class="fm-desc-inline">
						<label id="lb-dend" for="it-dend-type"><?=$this->bbf('fm_dend')?></label>
						<input type="text" name="datecal[dend]" id="it-dend-type" value="<?=is_null($infocal['dend'])?dwho_i18n::strftime_l('%Y-%m-%d',null):$infocal['dend']?>" size="8"
						   onclick="dwho_eid('cal-dbeg-type').style.display = 'none';
							    xivo_calendar_display('cal-dend-type','it-dend-type');"
						   onmouseover="xivo_calendar_body();"
						   onmouseout="xivo_calendar_body('cal-dend-type','it-dend-type');"
						 />
						 <!-- 
						<input type="text" name="datecal[hend]" id="it-hend" value="<?=is_null($infocal['hend'])?dwho_i18n::strftime_l('%H:%I',null):$infocal['hend']?>" size="4" />
						 -->
					</div>
					<div id="cal-dend-type"
					     class="b-nodisplay"
					     onmouseover="xivo_calendar_body();"
					     onmouseout="xivo_calendar_body('cal-dend-type','it-dend-type');">
					</div>
					<div class="fm-desc-inline">
						<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
					</div>
				</div>
			<?php endif; ?>
			</div>
			<div id="it-cal-day" class="b-nodisplay">
			<?php if (array_key_exists('dday',$infocal) === true): ?>
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-day"><?=$this->bbf('fm_dday')?></label>
						<input type="text" name="datecal[dday]" id="it-dbeg-day" value="<?=is_null($infocal['dday'])?dwho_i18n::strftime_l('%Y-%m-%d',null):$infocal['dday']?>" size="8"
							onclick="xivo_calendar_display('cal-dbeg-day','it-dbeg-day');"
							onmouseover="xivo_calendar_body();"
							onmouseout="xivo_calendar_body('cal-dbeg-day','it-dbeg-day');"
						 />
					</div>
					<div id="cal-dbeg-day"
					     class="b-nodisplay"
					     onmouseover="xivo_calendar_body();"
					     onmouseout="xivo_calendar_body('cal-dbeg-day','it-dbeg-day');">
					</div>
					<div class="fm-desc-inline">
						<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
					</div>
				</div>
			<?php endif; ?>
			</div>
			<div id="it-cal-week" class="b-nodisplay">
			<?php if (array_key_exists('dweek',$infocal) === true): ?>
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-week"><?=$this->bbf('fm_dweek')?></label>
						<input type="text" name="datecal[dweek]" id="it-dbeg-week" value="<?=is_null($infocal['dweek'])?dwho_i18n::strftime_l('%Y-%m-%d',null):$infocal['dweek']?>" size="8"
							onclick="xivo_calendar_display('cal-dbeg-week','it-dbeg-week');"
							onmouseover="xivo_calendar_body();"
							onmouseout="xivo_calendar_body('cal-dbeg-week','it-dbeg-week');"
						 />
					</div>
					<div id="cal-dbeg-week"
					     class="b-nodisplay"
					     onmouseover="xivo_calendar_body();"
					     onmouseout="xivo_calendar_body('cal-dbeg-week','it-dbeg-week');">
					</div>
					<div class="fm-desc-inline">
						<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
					</div>
				</div>
			<?php endif; ?>
			</div>
			<div id="it-cal-month" class="b-nodisplay">
			<?php if (array_key_exists('dmonth',$infocal) === true): ?>
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-month"><?=$this->bbf('fm_dmonth')?></label>
						<input type="text" name="datecal[dmonth]" id="it-dbeg-month" value="<?=is_null($infocal['dmonth'])?dwho_i18n::strftime_l('%Y-%m',null):$infocal['dmonth']?>" size="8"
							onclick="xivo_calendar_display('cal-dbeg-month','it-dbeg-month');"
							onmouseover="xivo_calendar_body();"
							onmouseout="xivo_calendar_body('cal-dbeg-month','it-dbeg-month');"
						 />
					</div>
					<div id="cal-dbeg-month"
					     class="b-nodisplay"
					     onmouseover="xivo_calendar_body();"
					     onmouseout="xivo_calendar_body('cal-dbeg-month','it-dbeg-month');">
					</div>
					<div class="fm-desc-inline">
						<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
					</div>
				</div>
			<?php endif; ?>
			</div>
			<div id="it-cal-year" class="b-nodisplay">
			<?php if (array_key_exists('dyear',$infocal) === true): ?>
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-year"><?=$this->bbf('fm_dyear')?></label>
						<input type="text" name="datecal[dyear]" id="it-dbeg-year" value="<?=is_null($infocal['dyear'])?dwho_i18n::strftime_l('%Y',null):$infocal['dyear']?>" size="4" />
					</div>
					<div class="fm-desc-inline">
						<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
					</div>
				</div>
			<?php endif; ?>
			</div>
		</form>
		</div>
<?php
	if($conf !== false):
?>
		<p class="paragraph">
			<?=$this->bbf('conf_time_range')?> <?=substr($conf['hour_start'],0,5)?> - <?=substr($conf['hour_end'],0,5)?>
		</p>
		<p class="paragraph">
		<?=$this->bbf('conf_workweek')?>
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
		</p>
<?php
	endif;
?>

<?php 
$bench = $this->get_var('bench');
echo dwho_second_to($bench,2);
?>
    
    </div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
		
<script type="text/javascript">
dwho.dom.set_onload(function()
{
<?php
	if(is_null($this->get_var('conf')) === false
	&& $this->get_var('conf') === false):
?>
	dwho.dom.add_event('change',
			   dwho_eid('it-toolbar-conf'),
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
		if (lsaxetype[u] == '<?=$this->get_var('conf','axetype')?>'
		&& divtoshow)
			divtoshow.style.display = 'block';
	}
});
</script>
<?php
	endif;
?>