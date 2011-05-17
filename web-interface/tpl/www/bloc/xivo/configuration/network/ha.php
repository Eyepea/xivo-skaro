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

$info     = $this->get_var('info');
//var_dump($info);
$status   = $this->get_var('status');

if(($fm_save = $this->get_var('fm_save')) === true):
	$dhtml->write_js('xivo_form_result(true,\'' .$dhtml->escape($this->bbf('fm_success-save')).'\');');
elseif($fm_save === false):
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>
<div class="b-infos b-form">
<h3 class="sb-top xspan">
	<span class="span-left">&nbsp;</span>
	<span class="span-center"><?=$this->bbf('title_content_name');?></span>
	<span class="span-right">&nbsp;</span>
</h3>

<div class="sb-smenu">
	<ul>
		<li id="dwsm-tab-1"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-first');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#first"><?=$this->bbf('smenu_status');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-network');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#network"><?=$this->bbf('smenu_network');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-3"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-services',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center"><a href="#services"><?=$this->bbf('smenu_services');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
<?php /*
		<li id="dwsm-tab-4"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-last',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center"><a href="#last"><?=$this->bbf('smenu_params');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
			</li>
 */
?>
	</ul>
</div>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8">

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_netaddr'),
				  'name'	=> 'ha[netaddr]',
				  'labelid'	=> 'netaddr',
				  'size'	=> 15,
			    'help'    => $this->bbf('fm_help-ha_netaddr'),
				  'value'	=> $this->get_var('info', 'ha', 'netaddr'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_netmask'),
				  'name'	=> 'ha[netmask]',
				  'labelid'	=> 'netmask',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'ha', 'netmask'))),
				  
	$form->text(array('desc'	=> $this->bbf('fm_ha_mcast'),
				  'name'	=> 'ha[mcast]',
				  'labelid'	=> 'mcast',
				  'size'	=> 15,
					'value'	=> $this->get_var('info', 'ha', 'mcast')));
?>
	<fieldset id="fld-node1">
		<legend><?=$this->bbf('fld-node1');?></legend>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_node1_name'),
				  'name'	=> 'ha[node1_name]',
				  'labelid'	=> 'node1_name',
				  'size'	=> 15,
			    'help'    => $this->bbf('fm_help-ha_node1_name'),
				  'value'	=> $this->get_var('info', 'ha', 'node1_name'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_node1_ip'),
				  'name'	=> 'ha[node1_ip]',
				  'labelid'	=> 'node1_ip',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'ha', 'node1_ip')));
?>		  
	</fieldset>
	<fieldset id="fld-node2">
		<legend><?=$this->bbf('fld-node2');?></legend>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_node2_name'),
				  'name'	=> 'ha[node2_name]',
				  'labelid'	=> 'node2_name',
				  'size'	=> 15,
			    'help'    => $this->bbf('fm_help-ha_node2_name'),
				  'value'	=> $this->get_var('info', 'ha', 'node2_name'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_node2_ip'),
				  'name'	=> 'ha[node2_ip]',
				  'labelid'	=> 'node2_ip',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'ha', 'node2_ip')));
?>		  
	</fieldset>


</div>

<div id="z-sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_status'),
	              'class'   => 'readonly',
				  'size'	=> 20,
				  'readonly'=> true,
			      'help'    => $this->bbf('fm_help-ha_status'),
				  'value'	=> $this->bbf_args('ha_status', $status)));

?></div>

<div id="sb-part-services" class="b-nodisplay">
<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name'	=> 'fm_send',
				    'value'	=> 1)),

		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_service_asterisk'),
				      'name'		=> 'service[asterisk][active]',
				      'labelid'		=> 'ha_asterisk',
				      'checked'		=> $info['service']['asterisk']['active'],
						)),
	
		'<fieldset id="fld-svc-asterisk">',
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_asterisk_monitor'),
					'name'		=> 'service[asterisk][monitor]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','asterisk','monitor'))),
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_asterisk_timeout'),
					'name'		=> 'service[asterisk][timeout]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','asterisk','timeout'))),
		'</fieldset>',


		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_service_lighttpd'),
				      'name'		=> 'service[lighttpd][active]',
				      'labelid'		=> 'ha_lighttpd',
				      'checked'		=> $info['service']['lighttpd']['active'],
						)),
	
		'<fieldset id="fld-svc-lighttpd">',
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_lighttpd_monitor'),
					'name'		=> 'service[lighttpd][monitor]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','lighttpd','monitor'))),
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_lighttpd_timeout'),
					'name'		=> 'service[lighttpd][timeout]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','lighttpd','timeout'))),
		'</fieldset>',

		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_service_dhcp'),
				      'name'		=> 'service[dhcp][active]',
				      'labelid'		=> 'ha_dhcp',
				      'checked'		=> $info['service']['dhcp']['active'],
						)),
	
		'<fieldset id="fld-svc-dhcp">',
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_dhcp_monitor'),
					'name'		=> 'service[dhcp][monitor]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','dhcp','monitor'))),
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_dhcp_timeout'),
					'name'		=> 'service[dhcp][timeout]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','dhcp','timeout'))),
		'</fieldset>',

		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_service_ntp'),
				      'name'		=> 'service[ntp][active]',
				      'labelid'		=> 'ha_ntp',
				      'checked'		=> $info['service']['ntp']['active'],
						)),
	
		'<fieldset id="fld-svc-ntp">',
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_ntp_monitor'),
					'name'		=> 'service[ntp][monitor]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','ntp','monitor'))),
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_ntp_timeout'),
					'name'		=> 'service[ntp][timeout]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','ntp','timeout'))),
		'</fieldset>',

		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_service_csync'),
				      'name'		=> 'service[csync][active]',
				      'labelid'		=> 'ha_csync',
				      'checked'		=> $info['service']['csync']['active'],
						)),
	
		'<fieldset id="fld-svc-csync">',
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_csync_monitor'),
					'name'		=> 'service[csync][monitor]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','csync','monitor'))),
		$form->text(array(
	        'desc'    => $this->bbf('fm_ha_service_csync_timeout'),
					'name'		=> 'service[csync][timeout]',
					'size'	  => 4,
					'value'   => $this->get_var('info', 'service','csync','timeout'))),
		'</fieldset>';
?>
</div>

<div id="sb-part-network" class="b-nodisplay">
<?php
		echo $form->text(array(
	        'desc'    => $this->bbf('fm_ha_cluster_name'),
					'name'		=> 'ha[cluster_name]',
					'size'	  => 25,
					'value'   => $this->get_var('info','ha','cluster_name'))),

		$form->checkbox(array('desc'		=> $this->bbf('fm_ha_cluster_group'),
				      'name'		=> 'ha[cluster_group]',
				      'labelid'		=> 'ha_cluster_group',
				      'checked'		=> $info['ha']['cluster_group'],
						));

    $this->file_include('bloc/xivo/configuration/network/ha/peer');
?>
</div>

<div id="z-sb-part-last" class="b-nodisplay">
<?php
		/*
	echo	$form->text(array('desc'	=> $this->bbf('fm_ha_alert_emails'),
				  'name'	=> 'alert_emails',
				  'labelid'	=> 'alert_emails',
				  'size'	=> 15,
			      'help'    => $this->bbf('fm_help-ha_alert_emails'),
				  'value'	=> $this->get_var('info', 'global', 'alert_emails'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_serial'),
				  'name'	=> 'serial',
				  'labelid'	=> 'serial',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'global', 'serial'))),
				  
	$form->text(array('desc'	=> $this->bbf('fm_ha_authkeys'),
				  'name'	=> 'authkeys',
				  'labelid'	=> 'authkeys',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'global', 'authkeys'))),

    // bcast, mcast, ucast
	$form->select(array(
	        'desc'      => $this->bbf('fm_ha_com_mode'),
			'name'		=> 'com_mode',
			'id'		=> "it-pf-ha-com_mode",
			'empty'		=> false,
			'key'		=> false,
			'selected'	=> $this->get_var('info', 'global', 'com_mode'),
    		'error'    	=> $this->bbf_args	('error_pf_ha_com_mode', 
		    $this->get_var('error', 'pf_ha_com_mode'))),
	$commodes);
		 */
?>
<br/>

<fieldset id="fld-group">
	<legend><?=$this->bbf('fm_ha_user_title');?></legend>
<div>
<?php
		/*
    echo $form->text(array('desc'	=> $this->bbf('fm_ha_user'),
				  'name'	=> 'user',
				  'labelid'	=> 'user',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'global', 'user'))),

	$form->text(array('desc'	=> $this->bbf('fm_ha_password'),
				  'name'	=> 'password',
				  'labelid'	=> 'password',
				  'size'	=> 15,
					'value'	=> $this->get_var('info', 'global', 'password')));
		 */
?>
</div>
</fieldset>

<fieldset id="fld-group">
	<legend><?= $this->bbf('fm_ha_dest_user_title') ?></legend>
<div>
<?php
		/*
	echo $form->text(array('desc'	=> $this->bbf('fm_ha_dest_user'),
				  'name'	=> 'dest_user',
				  'labelid'	=> 'dest_user',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info', 'global', 'dest_user'))),
				  
	$form->text(array('desc'	=> $this->bbf('fm_ha_dest_password'),
				  'name'	=> 'dest_password',
				  'labelid'	=> 'dest_password',
				  'size'	=> 15,
					'value'	=> $this->get_var('info', 'global', 'dest_password')));
		 */
?>
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
