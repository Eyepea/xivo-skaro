<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2012  Avencall
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

$info = $this->get_var('info');

?>

<div class="b-infos b-form">
<h3 class="sb-top xspan">
	<span class="span-left">&nbsp;</span>
	<span class="span-center"><?=$this->bbf('title_content_name');?></span>
	<span class="span-right">&nbsp;</span>
</h3>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8" onsubmit="dwho.form.select('it-directories');">

<div id="sb-part-first">
<?php
echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name'	=> 'fm_send',
				    'value'	=> 1));
?>
	<fieldset id="cti-contexts_services">
		<legend><?=$this->bbf('cti-contexts-directories');?></legend>
		<div id="contexts_services" class="fm-paragraph fm-multilist">
			<?=$form->input_for_ms('directorieslist',$this->bbf('ms_seek'))?>
			<div class="slt-outlist">
<?php
				echo    $form->select(array('name'  => 'directorieslist',
							'label' => false,
							'id'    => 'it-directorieslist',
							'key'   => 'name',
							'altkey'    => 'id',
							'multiple'  => true,
							'size'  => 5,
							'paragraph' => false),
							$info['directoriz']['list']);
?>
			</div>
			<div class="inout-list">
				<a href="#"
				onclick="dwho.form.move_selected('it-directorieslist','it-directories');
				return(dwho.dom.free_focus());"
				title="<?=$this->bbf('bt_inaccess_contexts');?>">
				<?=$url->img_html('img/site/button/arrow-left.gif',
						$this->bbf('bt_inaccess_contexts'),
						'class="bt-inlist" id="bt-inaccess_contexts" border="0"');?></a><br />

				<a href="#"
				onclick="dwho.form.move_selected('it-directories','it-directorieslist');
				return(dwho.dom.free_focus());"
				title="<?=$this->bbf('bt_outaccess_contexts');?>">
				<?=$url->img_html('img/site/button/arrow-right.gif',
						$this->bbf('bt_outaccess_contexts'),
						'class="bt-outlist" id="bt-outaccess_contexts" border="0"');?></a>
			</div>
			<div class="slt-inlist">
<?php
				echo    $form->select(array('name'  => 'directories[]',
						'label' => false,
						'id'    => 'it-directories',
						'key'	=> 'name',
						'altkey'    => 'id',
						'multiple'  => true,
						'size'  => 5,
						'paragraph' => false),
					$info['directoriz']['slt']);
?>
			</div>
		</div>
	</fieldset>
</div>
<?php

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
