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
$url = &$this->get_module('url');

$info = $this->get_var('info');
$error = $this->get_var('error');

$plugininstalled = $this->get_var('plugininstalled');
$listline = $this->get_var('listline');
$element = $this->get_var('element');

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_config_label'),
				  'name'	=> 'config[label]',
				  'labelid'	=> 'config-label',
				  'size'	=> 25,
				  'value'	=> $this->get_var('info','config','label'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'label')) )),

		$form->select(array('desc'	=> $this->bbf('fm_config_language'),
				    'name'		=> 'config[locale]',
				    'labelid'	=> 'config-locale',
				    'empty'		=> true,
				    'key'		=> false,
				    'default'	=> $element['config']['locale']['default'],
				    'selected'	=> $this->get_var('info','config','locale')),
			      $element['config']['locale']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_config_timezone'),
				    'name'		=> 'config[timezone]',
				    'labelid'	=> 'config-timezone',
				    'empty'		=> true,
				    'key'		=> false,
				    'selected'	=> $this->get_var('info','config','timezone')),
			      array_keys(dwho_i18n::get_timezone_list())),

		$form->select(array('desc'	=> $this->bbf('fm_config_protocol'),
				    'name'	=> 'config[protocol]',
				    'labelid'	=> 'config-protocol',
				    'empty'	=> true,
				    'key'	=> false,
				    'selected'	=> $this->get_var('info','config','protocol')),
			      $element['config']['protocol']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_config_config_encryption_enabled'),
				      'name'	=> 'config[config_encryption_enabled]',
				      'labelid'	=> 'config-config_encryption_enabled',
				      'default'	=> $element['config']['config_encryption_enabled']['default'],
				      'checked'	=> $this->get_var('info','config','config_encryption_enabled'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_config_ntp_enabled'),
				      'name'	=> 'config[ntp_enabled]',
				      'labelid'	=> 'config-ntp_enabled',
				      'default'	=> $element['config']['ntp_enabled']['default'],
				      'checked'	=> $this->get_var('info','config','ntp_enabled'))),

		$form->text(array('desc'	=> $this->bbf('fm_config_ntp_ip'),
				  'name'	=> 'config[ntp_ip]',
				  'labelid'	=> 'config-ntp_ip',
				  'size'	=> 15,
				  'default'	=> $element['config']['ntp_ip']['default'],
				  'value'	=> $this->get_var('info','config','ntp_ip'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'ntp_ip')) )),

		$form->select(array('desc'	=> $this->bbf('fm_config_sip_dtmf_mode'),
				    'name'	=> 'config[sip_dtmf_mode]',
				    'labelid'	=> 'config-sip_dtmf_mode',
				    'empty'	=> true,
				    'key'	=> false,
				    'selected'	=> $this->get_var('info','config','sip_dtmf_mode')),
			      $element['config']['sip_dtmf_mode']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_config_admin_username'),
				  'name'	=> 'config[admin_username]',
				  'labelid'	=> 'config-admin_username',
				  'size'	=> 15,
				  'default'	=> $element['config']['admin_username']['default'],
				  'value'	=> $this->get_var('info','config','admin_username'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'admin_username')) )),

		$form->text(array('desc'	=> $this->bbf('fm_config_admin_password'),
				  'name'	=> 'config[admin_password]',
				  'labelid'	=> 'config-admin_password',
				  'size'	=> 15,
				  'default'	=> $element['config']['admin_password']['default'],
				  'value'	=> $this->get_var('info','config','admin_password'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'admin_password')) )),

		$form->text(array('desc'	=> $this->bbf('fm_config_user_username'),
				  'name'	=> 'config[user_username]',
				  'labelid'	=> 'config-user_username',
				  'size'	=> 15,
				  'default'	=> $element['config']['user_username']['default'],
				  'value'	=> $this->get_var('info','config','user_username'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'user_username')) )),

		$form->text(array('desc'	=> $this->bbf('fm_config_user_password'),
				  'name'	=> 'config[user_password]',
				  'labelid'	=> 'config-user_password',
				  'size'	=> 15,
				  'default'	=> $element['config']['user_password']['default'],
				  'value'	=> $this->get_var('info','config','user_password'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'user_password')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_config_sip_subscribe_mwi'),
				      'name'	=> 'config[sip_subscribe_mwi]',
				      'labelid'	=> 'config-sip_subscribe_mwi',
				      'default'	=> $element['config']['sip_subscribe_mwi']['default'],
				      'checked'	=> $this->get_var('info','config','sip_subscribe_mwi')));
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-userfeatures-description" for="it-userfeatures-description"><?=$this->bbf('fm_userfeatures_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph' => false,
					 'label'	=> false,
					 'name'		=> 'config[_comment]',
					 'id'		=> 'it-config-_comment',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['config']['_comment']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', '_comment', 'description')) ),
				   $this->get_var('info','config','_comment'));?>
	</div>
</div>
<div id="sb-part-advanced" class="b-nodisplay">
<fieldset>
	<legend><?=$this->bbf('fld-device-sip_config')?></legend>
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_config_sip_transport'),
				    'name'	=> 'config[sip_transport]',
				    'labelid'	=> 'config-sip_transport',
				    'empty'	=> true,
				    'key'	=> false,
				    'selected'	=> $this->get_var('info','config','sip_transport'),
				  'legend'	=> $this->get_var('configdevice','raw_config','sip_transport'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'sip_transport')) ),
			      $element['config']['sip_transport']['value']);
?>
</fieldset>
<fieldset>
	<legend><?=$this->bbf('fld-device-srtp_config')?></legend>
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_config_sip_srtp_mode'),
				  'name'	=> 'config[sip_srtp_mode]',
				  'labelid'	=> 'config-sip_srtp_mode',
				  'key'	=> false,
				  'selected'	=> $this->get_var('info','config','sip_srtp_mode'),
				  'legend'	=> $this->get_var('configdevice','raw_config','sip_srtp_mode'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'sip_srtp_mode')) ),
			      $element['config']['sip_srtp_mode']['value']);
?>
</fieldset>
<fieldset>
	<legend><?=$this->bbf('fld-device-vlan_config')?></legend>
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_config_vlan_enabled'),
				      'name'	=> 'config[vlan_enabled]',
				      'labelid'	=> 'config-vlan_enabled',
				      'default'	=> $element['config']['vlan_enabled']['default'],
				      'checked'	=> $this->get_var('info','config','vlan_enabled'))),

		$form->text(array('desc'	=> $this->bbf('fm_config_vlan_id'),
				  'name'	=> 'config[vlan_id]',
				  'labelid'	=> 'config-vlan_id',
				  'size'	=> 4,
				  'default'	=> $element['config']['vlan_id']['default'],
				  'value'	=> $this->get_var('info','config','vlan_id'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'vlan_id')) )),

		$form->select(array('desc'	=> $this->bbf('fm_config_vlan_priority'),
				    'name'	=> 'config[vlan_priority]',
				    'labelid'	=> 'config-vlan_priority',
				    'empty'	=> true,
				    'key'	=> false,
				    'selected'	=> $this->get_var('info','config','vlan_priority')),
			      $element['config']['vlan_priority']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_config_vlan_pc_port_id'),
				  'name'	=> 'config[vlan_pc_port_id]',
				  'labelid'	=> 'config-vlan_pc_port_id',
				  'size'	=> 4,
				  'default'	=> $element['config']['vlan_pc_port_id']['default'],
				  'value'	=> $this->get_var('info','config','vlan_pc_port_id'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'vlan_pc_port_id')) ));
?>
</fieldset>
<fieldset>
	<legend><?=$this->bbf('fld-device-syslog_config')?></legend>
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_config_syslog_enabled'),
				      'name'	=> 'config[syslog_enabled]',
				      'labelid'	=> 'config-syslog_enabled',
				      'default'	=> $element['config']['syslog_enabled']['default'],
				      'checked'	=> $this->get_var('info','config','syslog_enabled'))),

		$form->text(array('desc'	=> $this->bbf('fm_config_syslog_ip'),
				  'name'	=> 'config[syslog_ip]',
				  'labelid'	=> 'config-syslog_ip',
				  'size'	=> 15,
				  'default'	=> $element['config']['syslog_ip']['default'],
				  'value'	=> $this->get_var('info','config','syslog_ip'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'syslog_ip')) )),

		$form->text(array('desc'	=> $this->bbf('fm_config_syslog_port'),
				  'name'	=> 'config[syslog_port]',
				  'labelid'	=> 'config-syslog_port',
				  'size'	=> 4,
				  'default'	=> $element['config']['syslog_port']['default'],
				  'value'	=> $this->get_var('info','config','syslog_port'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'config', 'syslog_port')) )),

		$form->select(array('desc'	=> $this->bbf('fm_config_syslog_level'),
				    'name'		=> 'config[syslog_level]',
				    'labelid'	=> 'config-syslog_level',
				    'key'		=> false,
				  	'default'	=> $element['config']['syslog_level']['default'],
				    'selected'	=> $this->get_var('info','config','syslog_level')),
			      $element['config']['syslog_level']['value']);
?>
</fieldset>
</div>