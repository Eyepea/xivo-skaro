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

$listconf = $this->get_var('listconf');
$infocal = $this->get_var('infocal');

?>
<script type="text/javascript" src="<?=$this->file_time($this->url('js/xivo_toolbar.js'));?>"></script>

<?php /*

<div id="sr-stats" class="">
<form action="#" method="post" accept-charset="utf-8">
<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value'	=> DWHO_SESS_ID))?>
<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
<?=$form->hidden(array('name' => 'act','value' => 'datecal'))?>
	<div id="fm-cal" class="fm-paragraph fm-desc-inline">
		<div class="fm-multifield">
			<?=$this->bbf('fm_dbeg')?>
			<label id="lb-dbeg" for="it-dbeg">
				<input type="text" name="datecal[dbeg]" id="it-dbeg" value="<?=$infocal['dbeg']?>" size="10"
					onclick="dwho_eid('cal-dend').style.display = 'none';
						xivo_calendar_display('cal-dbeg','it-dbeg');"
					onmouseover="xivo_calendar_body();"
					onmouseout="xivo_calendar_body('cal-dbeg','it-dbeg');"
				 />
			</label>
			<input type="text" name="datecal[hbeg]" id="it-hbeg" value="<?=$infocal['hbeg']?>" size="4" />
		</div>
		<div id="cal-dbeg"
		     class="b-nodisplay"
		     onmouseover="xivo_calendar_body();"
		     onmouseout="xivo_calendar_body('cal-dbeg','it-dbeg');">
		</div>
		<div class="fm-multifield">
			<?=$this->bbf('fm_dend')?>
			<label id="lb-dend" for="it-dend">
				<input type="text" name="datecal[dend]" id="it-dend" value="<?=is_null($infocal['dend'])?dwho_i18n::strftime_l('%Y-%m-%d',null):$infocal['dend']?>" size="10"
				   onclick="dwho_eid('cal-dbeg').style.display = 'none';
					    xivo_calendar_display('cal-dend','it-dend');"
				   onmouseover="xivo_calendar_body();"
				   onmouseout="xivo_calendar_body('cal-dend','it-dend');"
				 />
			</label>
			<input type="text" name="datecal[hend]" id="it-hend" value="<?=is_null($infocal['hend'])?dwho_i18n::strftime_l('%H:%I',null):$infocal['hend']?>" size="4" />
		</div>
		<div id="cal-dend"
		     class="b-nodisplay"
		     onmouseover="xivo_calendar_body();"
		     onmouseout="xivo_calendar_body('cal-dend','it-dend');">
		</div>		
		<input type="submit" id="it-submit" value="<?=$this->bbf('fm_bt-cal')?>" />
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

<script type="text/javascript">
dwho.dom.set_onload(function()
{
	dwho.dom.add_event('change',
			   dwho_eid('it-toolbar-conf'),
			   function(){this.form.submit();});
});
</script>

*/ ?>
