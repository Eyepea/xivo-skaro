<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2011  Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.If not, see <http://www.gnu.org/licenses/>.
#

$form = &$this->get_module('form');
$url = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

$conf = $this->get_var('conf');
$listconf = $this->get_var('listconf');
$listaxetype = $this->get_var('listaxetype');
$axetype = $this->get_var('axetype');
$infocal = $this->get_var('infocal');
$element = $this->get_var('element');
$objectkey = $this->get_var('objectkey');
$listobject = $this->get_var('listobject');

?>
<script type="text/javascript">
<!--
<?php if($listaxetype !== null): ?>
	var lsaxetype = new Array('<?=implode('\', \'',$listaxetype)?>');
<?php endif; ?>
<?php if($axetype !== null): ?>
	var axetype = '<?=$axetype?>';
<?php endif; ?>
	var fm_bt_wait_sb = '<?=$this->bbf('fm-wait-submit')?>';
<?php if($conf !== null) :?>
	var dp_min_date = '<?=$conf['dbegcache']?>-01';
<?php else: ?>
	var dp_min_date = null;
<?php endif; ?>
<?php
	if(((int) $dend = $conf['dendcache']) !== 0) :
		$dend = dwho_date::all_to_unixtime($dend);
		$lastday = dwho_date::get_lastday_for_month(date('Y',$dend),date('m',$dend));
?>
	var dp_max_date = '<?=date('Y-m-d',$lastday)?>';
<?php else: ?>
	var dp_max_date = null;
<?php endif; ?>
//-->
</script>

<dl>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name_statistics');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
		<dl>
<?php
if(xivo_user::chk_acl_section('statistics/call_center') === true):
?>
			<dt><?=$this->bbf('mn_left_ti_call_center')?></dt>
<?php
	if(xivo_user::chk_acl('settings') === true):
		if(xivo_user::chk_acl('settings','configuration') === true):
?>
			<dd id="mn-settings--configuration">
				<?=$url->href_html($this->bbf('mn_left_configuration_call_center'),
						'statistics/call_center/settings/configuration','act=list');?>
			</dd>
<?php
		endif;
	endif;
	if(xivo_user::chk_acl('data') === true):

		$pi = $_SERVER['PATH_INFO'];
		$params = array();
		if (is_null($axetype) === false)
			$params['axetype'] = $axetype;
		if (is_null($conf) === false)
			$params['confid'] = $conf['id'];
		if(isset($objectkey))
			$params['key'] = $objectkey;
		if (is_null($infocal) === false):
			$params['dbeg'] = $infocal['dbeg'];
			$params['dend'] = $infocal['dend'];
			if (isset($infocal['dday']) === true)
				$params['dday'] = $infocal['dday'];
			if (isset($infocal['dweek']) === true)
				$params['dweek'] = $infocal['dweek'];
			if (isset($infocal['dmonth']) === true)
				$params['dmonth'] = $infocal['dmonth'];
			if (isset($infocal['dyear']) === true)
				$params['dyear'] = $infocal['dyear'];
		endif;
?>
			<dd id="mn-data--stats1">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-1'),
						'statistics/call_center/data/stats1',(($pi == '/stats1') ? null : $params));?>
			</dd>
			<dd id="mn-data--stats2">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-2'),
						'statistics/call_center/data/stats2',(($pi == '/stats2') ? null : $params));?>
			</dd>
			<?php /*
			<dd id="mn-data--stats3">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-3'),
						'statistics/call_center/data/stats3',(($pi == '/stats3') ? null : $params));?>
			</dd>
			*/  ?>
			<dd id="mn-data--stats4">
				<?=$url->href_html($this->bbf('mn_left_statistics_call_center-4'),
						'statistics/call_center/data/stats4',(($pi == '/stats4') ? null : $params));?>
			</dd>
<?php
	endif;
endif;
?>
		</dl>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
</dl>

<?php
if($this->get_var('showdashboard_call_center') === true):
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
							'id'		=> 'it-confid',
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
	if($conf && $listobject && $axetype !== 'type'):
		foreach ($listobject as $k => &$v)
			$v['identity'] = dwho_trunc(&$v['identity'],25,'...',5);
?>
			<div id="it-cal-object" class="fm-paragraph">
<?php
				echo	$form->select(array('name'	=> 'key',
							'id'		=> 'it-key',
							'paragraph'	=> false,
							'browse'	=> 'key',
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
	if($conf && $listobject && $axetype !== 'type'):
?>
			<div id="d-conf-axetype" class="fm-paragraph">
			<?=$this->bbf('conf_axetype')?>
			<?php
				echo	$form->select(array('name'	=> 'axetype',
							'id'		=> 'it-axetype',
							'paragraph'	=> false,
							'browse'	=> 'axetype',
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
						<input type="text" name="dbeg" id="it-dbeg" value="<?=$infocal['dbeg']?>" size="8" />
					</div>
					<div class="fm-desc-inline">
						<label id="lb-dend" for="it-dend-type"><?=$this->bbf('fm_dend')?></label>
						<input type="text" name="dend" id="it-dend" value="<?=$infocal['dend']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-day" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-day"><?=$this->bbf('fm_dday')?></label>
						<input type="text" name="dday" id="it-dday" value="<?=$infocal['dday']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-week" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-week"><?=$this->bbf('fm_dweek')?></label>
						<input type="text" name="dweek" id="it-dweek" value="<?=$infocal['dweek']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-month" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-month"><?=$this->bbf('fm_dmonth')?></label>
						<input type="text" name="dmonth" id="it-dmonth" value="<?=$infocal['dmonth']?>" size="8" />
					</div>
				</div>
			</div>
			<div id="it-cal-year" class="b-nodisplay">
				<div class="fm-paragraph fm-multifield">
					<div class="fm-desc-inline">
						<label id="lb-dbeg" for="it-dbeg-year"><?=$this->bbf('fm_dyear')?></label>
						<input type="text" name="dyear" id="it-dyear" value="<?=$infocal['dyear']?>" size="4" />
					</div>
				</div>
			</div>
			<div class="fm-desc-inline">
				<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
			</div>
<?php
	endif;
?>
		</form>
		</div>
<?php
	if($conf):
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
		<fieldset style="padding: 1px;">
			<legend><?=$this->bbf('bench_dashboard')?></legend>
			<?=dwho_second_to($this->get_var('bench'),2).' - '.dwho_byte_to($this->get_var('mem_info'))?>
		</fieldset>
</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
<?php
endif;
?>