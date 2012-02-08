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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

$form = &$this->get_module('form');

$info = $this->get_var('info');
$element = $this->get_var('element');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;
?>
<fieldset>
<legend><?=$this->bbf('fld_general')?></legend>
<?php
echo	$form->text(array('desc'	=> $this->bbf('fm_name'),
			  'name'	=> 'name',
			  'labelid'	=> 'name',
			  'size'	=> 15,
			  'default'	=> $element['name']['default'],
			  'value'	=> $info['name'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'name')))),

	$form->text(array('desc'	=> $this->bbf('fm_host'),
			  'name'	=> 'host',
			  'labelid'	=> 'host',
			  'size'	=> 15,
			  'default'	=> $element['host']['default'],
			  'value'	=> $info['host'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'host'))));
?>
</fieldset>
<fieldset>
<legend><?=$this->bbf('fld_webservices')?></legend>
<?php
echo    $form->text(array('desc'	=> $this->bbf('fm_ws_login'),
			  'name'	=> 'ws_login',
			  'labelid'	=> 'ws_login',
			  'size'	=> 15,
			  'default'	=> $element['ws_login']['default'],
			  'value'	=> $info['ws_login'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'ws_login')))),

	$form->text(array('desc'	=> $this->bbf('fm_ws_pass'),
			  'name'	=> 'ws_pass',
			  'labelid'	=> 'ws_pass',
			  'size'	=> 15,
			  'default'	=> $element['ws_pass']['default'],
			  'value'	=> $info['ws_pass'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'ws_pass')))),

	$form->text(array('desc'	=> $this->bbf('fm_ws_port'),
			  'name'	=> 'ws_port',
			  'labelid'	=> 'ws_port',
			  'default'	=> $element['ws_port']['default'],
			  'value'	=> $info['ws_port'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'ws_port')))),

	$form->checkbox(array('desc'	=> $this->bbf('fm_ws_ssl'),
			  'name'	=> 'ws_ssl',
			  'labelid'	=> 'ws_ssl',
			  'default'	=> $element['ws_ssl']['default'],
			  'checked'	=> $info['ws_ssl'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'ws_ssl'))));
?>
</fieldset>
<fieldset>
<legend><?=$this->bbf('fld_cti')?></legend>
<?php
echo    $form->text(array('desc'	=> $this->bbf('fm_cti_login'),
			  'name'	=> 'cti_login',
			  'labelid'	=> 'cti_login',
			  'size'	=> 15,
			  'default'	=> $element['cti_login']['default'],
			  'value'	=> $info['cti_login'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'cti_login')))),

	$form->text(array('desc'	=> $this->bbf('fm_cti_pass'),
			  'name'	=> 'cti_pass',
			  'labelid'	=> 'cti_pass',
			  'size'	=> 15,
			  'default'	=> $element['cti_pass']['default'],
			  'value'	=> $info['cti_pass'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'cti_pass')))),

	$form->text(array('desc'	=> $this->bbf('fm_cti_port'),
			  'name'	=> 'cti_port',
			  'labelid'	=> 'cti_port',
			  'default'	=> $element['cti_port']['default'],
			  'value'	=> $info['cti_port'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'cti_port')))),

	$form->checkbox(array('desc'	=> $this->bbf('fm_cti_ssl'),
			  'name'	=> 'cti_ssl',
			  'labelid'	=> 'cti_ssl',
			  'default'	=> $element['cti_ssl']['default'],
			  'checked'	=> $info['cti_ssl'],
			  'error'	=> $this->bbf_args('error',
				   $this->get_var('error', 'cti_ssl'))));
?>
</fieldset>
<div class="fm-paragraph fm-description">
	<p>
		<label id="lb-description" for="it-description"><?=$this->bbf('fm_description');?></label>
	</p>
	<?=$form->textarea(array('paragraph'	=> false,
				 'label'	=> false,
				 'name'		=> 'description',
				 'id'		=> 'it-description',
				 'cols'		=> 60,
				 'rows'		=> 5,
				 'default'	=> $element['description']['default']),
			   $info['description']);?>
</div>
