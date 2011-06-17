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

$info         = $this->get_var('info');
$element      = $this->get_var('element');
$list         = $this->get_var('list');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>


<div id="sb-part-first" class="b-nodisplay">
<?php
echo	$form->text(array('desc'	=> $this->bbf('fm_pickup_name'),
			  'name'	=> 'pickup[name]',
			  'labelid'	=> 'pickup-name',
			  'size'	=> 15,
			  'default'	=> $element['pickup']['name']['default'],
			  'value'	=> $this->get_var('info','pickup','name'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'pickup', 'name')) ));
?>

	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-pickup-description" for="it-pickup-description"><?=$this->bbf('fm_pickup_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'pickup[description]',
					 'id'		=> 'it-pickup-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['pickup']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'pickup', 'description')) ),
				   $this->get_var('info','pickup','description'));?>
	</div>

</div>


<div id="sb-part-members" class="b-nodisplay">
	<fieldset id="fld-members-groups">
		<legend><?=$this->bbf('fld-members-groups');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/call_management/pickup/member',
			array('membertype'	=> 'groups', 'category' => 'member'));
?>
	</fieldset>

	<fieldset id="fld-members-queues">
		<legend><?=$this->bbf('fld-members-queues');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/call_management/pickup/member',
			array('membertype'	=> 'queues', 'category' => 'member'));
?>
	</fieldset>

	<fieldset id="fld-members-users">
		<legend><?=$this->bbf('fld-members-users');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/call_management/pickup/member',
			array('membertype'	=> 'users', 'category' => 'member'));
?>
	</fieldset>
</div>

<div id="sb-part-interceptors" class="b-nodisplay">
	<fieldset id="fld-interceptors-groups">
		<legend><?=$this->bbf('fld-interceptors-groups');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/call_management/pickup/member',
			array('membertype'	=> 'groups', 'category' => 'pickup'));
?>
	</fieldset>

	<fieldset id="fld-interceptors-queues">
		<legend><?=$this->bbf('fld-interceptors-queues');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/call_management/pickup/member',
			array('membertype'	=> 'queues', 'category' => 'pickup'));
?>
	</fieldset>

	<fieldset id="fld-interceptors-users">
		<legend><?=$this->bbf('fld-interceptors-users');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/call_management/pickup/member',
			array('membertype'=> 'users', 'category' => 'pickup'));
?>
	</fieldset>
</div>
