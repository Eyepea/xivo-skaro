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
			<dd id="mn-4">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-4'),
						   'statistics/call_center/stats4');?>
			</dd>
			<dd id="mn-3">
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

<div id="dashboard">
	<div class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name_dashboard');?></span>
		<span class="span-right">&nbsp;</span>
	</div>
	<div class="sb-content">
		<div id="sr-stats" class="">
		<form action="#" method="post" accept-charset="utf-8">
		<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value'	=> DWHO_SESS_ID))?>
		<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
		<?=$form->hidden(array('name' => 'act','value' => 'datecal'))?>
			<div id="fm-cal" class="fm-paragraph fm-multifield">
				<div class="fm-desc-inline">
					<label id="lb-dbeg" for="it-dbeg"><?=$this->bbf('fm_dbeg')?></label>
					<input type="text" name="datecal[dbeg]" id="it-dbeg" value="<?=$infocal['dbeg']?>" size="10"
						onclick="dwho_eid('cal-dend').style.display = 'none';
							xivo_calendar_display('cal-dbeg','it-dbeg');"
						onmouseover="xivo_calendar_body();"
						onmouseout="xivo_calendar_body('cal-dbeg','it-dbeg');"
					 />
					<input type="text" name="datecal[hbeg]" id="it-hbeg" value="<?=$infocal['hbeg']?>" size="4" />
				</div>
				<div id="cal-dbeg"
				     class="b-nodisplay"
				     onmouseover="xivo_calendar_body();"
				     onmouseout="xivo_calendar_body('cal-dbeg','it-dbeg');">
				</div>
				<div class="fm-desc-inline">
					<label id="lb-dend" for="it-dend"><?=$this->bbf('fm_dend')?></label>
					<input type="text" name="datecal[dend]" id="it-dend" value="<?=is_null($infocal['dend'])?dwho_i18n::strftime_l('%Y-%m-%d',null):$infocal['dend']?>" size="10"
					   onclick="dwho_eid('cal-dbeg').style.display = 'none';
						    xivo_calendar_display('cal-dend','it-dend');"
					   onmouseover="xivo_calendar_body();"
					   onmouseout="xivo_calendar_body('cal-dend','it-dend');"
					 />
					<input type="text" name="datecal[hend]" id="it-hend" value="<?=is_null($infocal['hend'])?dwho_i18n::strftime_l('%H:%I',null):$infocal['hend']?>" size="4" />
				</div>
				<div id="cal-dend"
				     class="b-nodisplay"
				     onmouseover="xivo_calendar_body();"
				     onmouseout="xivo_calendar_body('cal-dend','it-dend');">
				</div>
				<div class="fm-desc-inline">
					<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
				</div>
			</div>
		</form>
		</div>
		
		<form action="#" method="post" accept-charset="utf-8">
		<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value' => DWHO_SESS_ID));?>
		<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
		<?=$form->hidden(array('name' => 'act','value' => 'conf'))?>
			<div class="fm-paragraph">	
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
		</form>
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
	dwho.dom.add_event('change',
			   dwho_eid('it-toolbar-conf'),
			   function(){this.form.submit();});
});
</script>