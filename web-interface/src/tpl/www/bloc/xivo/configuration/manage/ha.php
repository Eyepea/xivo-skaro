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

$element = $this->get_var('element');

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8">
<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value' => DWHO_SESS_ID))?>
<?=$form->hidden(array('name' => 'fm_send','value' => 1))?>
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_ha_node_type'),
					'name'		=> 'node_type',
					'labelid'	=> 'node_type',
					'bbf'		=> 'fm_ha_node_type-opt',
					'bbfopt'	=> array('argmode' => 'paramvalue'),
					'key'		=> false,
					'selected'	=> $this->get_var('info','node_type'),
					'error'   	=> $this->bbf_args('error', $this->get_var('error','ha','node_type'))),
				$element['node_type']['value']);
?>

<fieldset id="fld-infos">
	<legend id="fld-legend_master"><?=$this->bbf('fld_ha_part_master');?></legend>
	<legend id="fld-legend_slave"><?=$this->bbf('fld_ha_part_slave');?></legend>
<?php
	echo 	$form->text(array('desc'	=> $this->bbf('fm_remote_address'),
					'name'	    => 'remote_address',
					'labelid'	=> 'remote_address',
					'size'	  	=> 15,
					'value'	  	=> $this->get_var('info','remote_address'),
					'error'   	=> $this->bbf_args('error', $this->get_var('error','ha','remote_address'))));
?>
</fieldset>

<?=$form->submit(array('name' => 'submit', 'id' => 'it-submit', 'value' => $this->bbf('fm_bt-save')));?>
</form>

</div>

	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
