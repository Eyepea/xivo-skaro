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

$form    = &$this->get_module('form');
$dhtml   = &$this->get_module('dhtml');

$element = $this->get_var('element');

?>

<div id="sb-part-first">
<?php
	if ($this->get_var('act') === 'edit'):
		echo $form->hidden(array('name'	  => 'config[id]',
				  'value'	  => $this->get_var('info','id')));
?>
	<p id="fd-config-id" class="fm-paragraph">
		<span class="fm-desc clearboth">
			<label for="it-config-id"><?=$this->bbf('fm_config-id')?></label>
		</span>
		&nbsp; 	<?=$this->get_var('info','id')?>
	</p>
<?php
	else:
		echo $form->text(array('desc'	=> $this->bbf('fm_config-id'),
				  'name'	  => 'config[id]',
				  'labelid'	=> 'config-id',
				  'size'	  => 15,
				  'value'	  => $this->get_var('info','id'),
				  'error'   => $this->bbf_args('error', $this->get_var('error', 'id')) ));
	endif;
	
		echo $form->text(array('desc'	=> $this->bbf('fm_config-displayname'),
				  'name'	  => 'config[displayname]',
				  'labelid'	=> 'config-displayname',
				  'size'	  => 15,
				  'value'	  => $this->get_var('info','displayname'),
				  'error'   => $this->bbf_args('error', $this->get_var('error', 'displayname')) ));
?>
<fieldset id="fld-registrar">
	<legend><?=$this->bbf('fld_registrar');?></legend>
<?php
		echo $form->text(array('desc'	=> $this->bbf('fm_config-registrar_main'),
				  'name'	  => 'config[registrar_main]',
				  'labelid'	=> 'config-registrar_main',
				  'size'	  => 15,
				  'value'	  => $this->get_var('info','registrar_main'),
				  'error'   => $this->bbf_args('error', $this->get_var('error', 'registrar_main')) )),

		$form->text(array('desc'	=> $this->bbf('fm_config-registrar_backup'),
				  'name'	  => 'config[registrar_backup]',
				  'labelid'	=> 'config-registrar_backup',
				  'size'	  => 15,
				  'value'	  => $this->get_var('info','registrar_backup'),
				  'error'   => $this->bbf_args('error', $this->get_var('error', 'registrar_backup'))
				));
?>
</fieldset>

<fieldset id="fld-proxy">
	<legend><?=$this->bbf('fld_proxy');?></legend>
<?php
		echo $form->text(array('desc'	=> $this->bbf('fm_config-proxy_main'),
				  'name'	  => 'config[proxy_main]',
				  'labelid'	=> 'config-proxy_main',
				  'size'	  => 15,
				  'value'	  => $this->get_var('info','proxy_main'),
				  'error'   => $this->bbf_args('error', $this->get_var('error', 'proxy_main')) )),

		$form->text(array('desc'	=> $this->bbf('fm_config-proxy_backup'),
				  'name'	  => 'config[proxy_backup]',
				  'labelid'	=> 'config-proxy_backup',
				  'size'	  => 15,
				  'value'	  => $this->get_var('info','proxy_backup'),
				  'error'   => $this->bbf_args('error', $this->get_var('error', 'proxy_backup')) ));?>
</fieldset>
</div>