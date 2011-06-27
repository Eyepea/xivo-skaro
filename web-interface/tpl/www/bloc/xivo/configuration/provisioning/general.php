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

?>

<div class="b-infos b-form">
<h3 class="sb-top xspan">
	<span class="span-left">&nbsp;</span>
	<span class="span-center"><?=$this->bbf('title_content_name');?></span>
	<span class="span-right">&nbsp;</span>
</h3>

<div class="sb-content">

<fieldset id="fld-registrar">
	<legend><?=$this->bbf('fld_provd_server');?></legend>
	
<?php
if (($params = $this->get_var('info','configure')) !== false
&& is_array($params) === true):

    $uri = '/xivo/configuration/ui.php/provisioning/configure';

	foreach($params as $k => $v):

		if (isset($v['links'][0]) === false
		|| isset($v['links'][0]['href']) === false
		|| ($href = $v['links'][0]['href']) === '')
			continue;
?>
<div id="res-<?=$k?>"></div>
<?php
	echo	$form->hidden(array('name'	=> 'href',
			  'id'	    => 'href-'.$k,
			  'value'	=> $href));
	echo	$form->hidden(array('name'	=> 'uri',
			  'id'	    => 'uri-'.$k,
			  'value'	=> $uri));
	echo	$form->text(array('desc' => $this->bbf('fm_configure_'.$k),
			  'name'	=> $k,
			  'id'		=> 'configure-ajax',
			  'size'	=> strlen($v['value']),
			  'value'	=> $v['value'],
			  'help'	=> $v['description']));
?>
<?php
	endforeach;
endif;
?>
</fieldset>

<form action="#" method="post" accept-charset="utf-8">

<div id="sb-part-first">
<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value'	=> DWHO_SESS_ID));?>
<?=$form->hidden(array('name' => 'fm_send','value' => 1));?>
<fieldset id="fld-registrar">
	<legend><?=$this->bbf('fld_provd_general_configuration');?></legend>
<?php
	echo $form->text(array('desc'	=> $this->bbf('fm_provd_net4_ip'),
				  'name'	=> 'provd[net4_ip]',
				  'labelid'	=> 'provd-net4_ip',
				  'size'	  	=> 16,
				  'value'	  	=> $this->get_var('info','provd','net4_ip'),
				  'error'   	=> $this->bbf_args('error', $this->get_var('error','provd','net4_ip')))),
	
	$form->text(array('desc'	=> $this->bbf('fm_provd_http_port'),
				  'name'	=> 'provd[http_port]',
				  'labelid'	=> 'provd-http_port',
				  'size'	  	=> 4,
				  'value'	  	=> $this->get_var('info','provd','http_port'),
				  'error'   	=> $this->bbf_args('error', $this->get_var('error','provd','provd_http_port')))),
	
	$form->checkbox(array('desc'	=> $this->bbf('fm_provd_dhcp_integration'),
				      'name'	=> 'provd[dhcp_integration]',
				      'labelid'	=> 'provd-dhcp_integration',
				      'checked'	=> $this->get_var('info','provd','dhcp_integration')));
?>
</fieldset>

<fieldset id="fld-registrar">
	<legend><?=$this->bbf('fld_provd_rest_configuration');?></legend>
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_provd_net4_ip_rest'),
				  'name'	=> 'provd[net4_ip_rest]',
				  'labelid'	=> 'provd-net4_ip_rest',
				  'size'	  	=> 16,
				  'value'	  	=> $this->get_var('info','provd','net4_ip_rest'),
				  'error'   	=> $this->bbf_args('error', $this->get_var('error','provd','net4_ip_rest')))),
	
	$form->checkbox(array('desc'	=> $this->bbf('fm_provd_private'),
				      'name'	=> 'provd[private]',
				      'labelid'	=> 'provd-private',
				      'checked'	=> $this->get_var('info','provd','private'))),
	
	$form->text(array('desc'	=> $this->bbf('fm_provd_username'),
				  'name'		=> 'provd[username]',
				  'labelid'		=> 'provd-username',
				  'size'	  	=> 12,
				  'value'	  	=> $this->get_var('info','provd','username'),
				  'error'   	=> $this->bbf_args('error', $this->get_var('error','provd','username')))),
	
	$form->text(array('desc'	=> $this->bbf('fm_provd_password'),
				  'name'		=> 'provd[password]',
				  'labelid'		=> 'provd-password',
				  'size'	  	=> 12,
				  'value'	  	=> $this->get_var('info','provd','password'),
				  'error'   	=> $this->bbf_args('error', $this->get_var('error','provd','password')))),
	
	$form->checkbox(array('desc'	=> $this->bbf('fm_provd_secure_rest'),
				      'name'	=> 'provd[secure]',
				      'labelid'	=> 'provd-secure',
				      'checked'	=> $this->get_var('info','provd','secure'))),
	
	$form->text(array('desc'	=> $this->bbf('fm_provd_rest_port'),
				  'name'		=> 'provd[rest_port]',
				  'labelid'		=> 'provd-rest_port',
				  'size'	  	=> 4,
				  'value'	  	=> $this->get_var('info','provd','rest_port'),
				  'error'   	=> $this->bbf_args('error', $this->get_var('error','provd','rest_port'))));
	
	
?>
</fieldset>
</div>
<?=$form->submit(array('name' => 'submit','id' => 'it-submit','value' => $this->bbf('fm_bt-save')));?>
</form>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
