<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
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
$dhtml = &$this->get_module('dhtml');

if(($fm_save = $this->get_var('fm_save')) === true)
	$dhtml->write_js('xivo_form_result(true,\''.$dhtml->escape($this->bbf('fm_success-save')).'\');');
elseif($fm_save === false)
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	
	<div class="sb-content">
		<form action="#" method="post" accept-charset="utf-8">
<?php
		echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
					    'value'	=> DWHO_SESS_ID)),

			$form->hidden(array('name'	=> 'fm_send',
					    'value'	=> 1)),

			$form->hidden(array('name'	=> 'act',
					    'value'	=> 'qos'));
?>
				<p>
					<label id="lb-description" for="it-description"><?=$this->bbf('fm_description_stats_queue_qos');?></label>
				</p>
<?php
	if(($list = $this->get_var('ls_queue')) === false 
	|| ($nb = count($list)) === 0):
?>
				<?=$this->bbf('no_displays');?>
<?php
	else:
		for($i = 0;$i < $nb;$i++):
			$ref = &$list[$i];
			
	echo	$form->text(array('desc'	=> $this->bbf('fm-queue_name-',$ref['name']),
				  'name'	=> 'stats_qos['.$ref['id'].']',
				  'labelid'	=> $ref['name'],
				  'size'	=> 5,
				  'default'	=> 0,
				  'value'	=> $ref['stats_qos']));

		endfor;
	endif;
	
		echo	$form->submit(array('name'	=> 'submit',
					    'id'	=> 'it-submit',
					    'value'	=> $this->bbf('fm_bt-save')));
?>
		</form>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
