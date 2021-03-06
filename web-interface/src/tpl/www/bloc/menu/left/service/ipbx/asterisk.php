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

$url = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

?>
<dl>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
<?php
	if(xivo_user::chk_acl('general_settings') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_generalsettings'),'</dt>';

		if(xivo_user::chk_acl('general_settings','sip') === true):
			echo	'<dd id="mn-general-settings--sip">',
				$url->href_html($this->bbf('mn_left_generalsettings-sip'),
						'service/ipbx/general_settings/sip'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('general_settings','iax') === true):
			echo	'<dd id="mn-general-settings--iax">',
				$url->href_html($this->bbf('mn_left_generalsettings-iax'),
						'service/ipbx/general_settings/iax'),
				'</dd>';
		endif;
/*
		if(xivo_user::chk_acl('general_settings','dundi') === true):
			echo	'<dd id="mn-general-settings--dundi">',
				$url->href_html($this->bbf('mn_left_generalsettings-dundi'),
						'service/ipbx/general_settings/dundi'),
				'</dd>';
		endif;
*/
/*
		if(xivo_user::chk_acl('general_settings','dahdi') === true):
			echo	'<dd id="mn-general-settings--dahdi">',
				$url->href_html($this->bbf('mn_left_generalsettings-dahdi'),
						'service/ipbx/general_settings/dahdi'),
				'</dd>';
		endif;
*/
		if(xivo_user::chk_acl('general_settings','voicemail') === true):
			echo	'<dd id="mn-general-settings--voicemail">',
				$url->href_html($this->bbf('mn_left_generalsettings-voicemail'),
						'service/ipbx/general_settings/voicemail'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('general_settings','phonebook') === true):
			echo	'<dd id="mn-general-settings--phonebook">',
				$url->href_html($this->bbf('mn_left_generalsettings-phonebook'),
						'service/ipbx/general_settings/phonebook'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('general_settings','advanced') === true):
			echo	'<dd id="mn-general-settings--advanced">',
				$url->href_html($this->bbf('mn_left_generalsettings-advanced'),
						'service/ipbx/general_settings/advanced'),
				'</dd>';
		endif;
/*
		if(xivo_user::chk_acl('general_settings','outboundmwi') === true):
			echo	'<dd id="mn-general-settings--outboundmwi">',
				$url->href_html($this->bbf('mn_left_generalsettings-outboundmwi'),
						'service/ipbx/general_settings/outboundmwi'),
				'</dd>';
		endif;
*/
		echo	'</dl>';
	endif;

	if(xivo_user::chk_acl('pbx_settings') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_pbxsettings'),'</dt>';

		if(xivo_user::chk_acl('pbx_settings','devices') === true):
			echo	'<dd id="mn-pbx-settings--devices">',
				$url->href_html($this->bbf('mn_left_pbxsettings-devices'),
						'service/ipbx/pbx_settings/devices',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_settings','lines') === true):
			echo	'<dd id="mn-pbx-settings--lines">',
				$url->href_html($this->bbf('mn_left_pbxsettings-lines'),
						'service/ipbx/pbx_settings/lines',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_settings','users') === true):
			echo	'<dd id="mn-pbx-settings--users">',
				$url->href_html($this->bbf('mn_left_pbxsettings-users'),
						'service/ipbx/pbx_settings/users',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_settings','groups') === true):
			echo	'<dd id="mn-pbx-settings--groups">',
				$url->href_html($this->bbf('mn_left_pbxsettings-groups'),
						'service/ipbx/pbx_settings/groups',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_settings','voicemail') === true):
			echo	'<dd id="mn-pbx-settings--voicemail">',
				$url->href_html($this->bbf('mn_left_pbxsettings-voicemail'),
						'service/ipbx/pbx_settings/voicemail',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_settings','meetme') === true):
			echo	'<dd id="mn-pbx-settings--meetme">',
				$url->href_html($this->bbf('mn_left_pbxsettings-meetme'),
						'service/ipbx/pbx_settings/meetme',
						'act=list'),
				'</dd>';
		endif;

	echo	'</dl>';
	endif;

	if(xivo_user::chk_acl('call_management') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_callmanagement'),'</dt>';

		if(xivo_user::chk_acl('call_management','incall') === true):
			echo	'<dd id="mn-call-management--incall">',
				$url->href_html($this->bbf('mn_left_callmanagement-incall'),
						'service/ipbx/call_management/incall',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('call_management','outcall') === true):
			echo	'<dd id="mn-call-management--outcall">',
				$url->href_html($this->bbf('mn_left_callmanagement-outcall'),
						'service/ipbx/call_management/outcall',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('call_management','rightcall') === true):
			echo	'<dd id="mn-call-management--rightcall">',
				$url->href_html($this->bbf('mn_left_callmanagement-rightcall'),
						'service/ipbx/call_management/rightcall',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('call_management','callfilter') === true):
			echo	'<dd id="mn-call-management--callfilter">',
				$url->href_html($this->bbf('mn_left_callmanagement-callfilter'),
						'service/ipbx/call_management/callfilter',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('call_management','pickup') === true):
			echo	'<dd id="mn-call-management--pickup">',
				$url->href_html($this->bbf('mn_left_callmanagement-pickup'),
						'service/ipbx/call_management/pickup',
						'act=list'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('call_management','schedule') === true):
			echo	'<dd id="mn-call-management--schedule">',
				$url->href_html($this->bbf('mn_left_callmanagement-schedule'),
						'service/ipbx/call_management/schedule',
						'act=list'),
				'</dd>';
		endif;
/*
		if(xivo_user::chk_acl('call_management','voicemenu') === true):
			echo	'<dd id="mn-call-management--voicemenu">',
				$url->href_html($this->bbf('mn_left_callmanagement-voicemenu'),
						'service/ipbx/call_management/voicemenu',
						'act=list'),
				'</dd>';
		endif;
*/
		if(xivo_user::chk_acl('call_management','cel') === true):
			echo	'<dd id="mn-call_management--cel">',
				$url->href_html($this->bbf('mn_left_callmanagement-cel'),
						'service/ipbx/call_management/cel'),
				'</dd>';
		endif;
		echo	'</dl>';
	endif;

	if(xivo_user::chk_acl('trunk_management') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_trunkmanagement'),'</dt>';

		if(xivo_user::chk_acl('trunk_management','sip') === true):
			echo	'<dd id="mn-trunk-management--sip">',
				$url->href_html($this->bbf('mn_left_trunkmanagement-sip'),
						'service/ipbx/trunk_management/sip',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('trunk_management','iax') === true):
			echo	'<dd id="mn-trunk-management--iax">',
				$url->href_html($this->bbf('mn_left_trunkmanagement-iax'),
						'service/ipbx/trunk_management/iax',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('trunk_management','custom') === true):
			echo	'<dd id="mn-trunk-management--custom">',
				$url->href_html($this->bbf('mn_left_trunkmanagement-custom'),
						'service/ipbx/trunk_management/custom',
						'act=list'),
				'</dd>';
		endif;

		echo	'</dl>';
	endif;
/*
	if(xivo_user::chk_acl('dundi') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_dundi'),'</dt>';

		if(xivo_user::chk_acl('dundi','mappings') === true):
			echo	'<dd id="mn-dundi--mappings">',
				$url->href_html($this->bbf('mn_left_dundi-mappings'),
						'service/ipbx/dundi/mappings'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('dundi','peers') === true):
			echo	'<dd id="mn-dundi--peers">',
				$url->href_html($this->bbf('mn_left_dundi-peers'),
						'service/ipbx/dundi/peers'),
				'</dd>';
		endif;

		echo	'</dl>';
	endif;
*/
	/*
	if(xivo_user::chk_acl('cost_center') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_cost_center'),'</dt>';

		if(xivo_user::chk_acl('cost_center','operator') === true):
			echo	'<dd id="mn-cost_center--operator">',
				$url->href_html($this->bbf('mn_left_cost_center-operator'),
						'service/ipbx/cost_center/operator',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('cost_center','servicesgroup') === true):
			echo	'<dd id="mn-cost_center--servicesgroup">',
				$url->href_html($this->bbf('mn_left_cost_center-servicesgroup'),
						'service/ipbx/cost_center/servicesgroup',
						'act=list'),
				'</dd>';
		endif;

		echo	'</dl>';
	endif;
*/
	if(xivo_user::chk_acl('pbx_services') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_pbxservices'),'</dt>';

		if(xivo_user::chk_acl('pbx_services','sounds') === true):
			echo	'<dd id="mn-pbx-services--sounds">',
				$url->href_html($this->bbf('mn_left_pbx_services-sounds'),
						'service/ipbx/pbx_services/sounds',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_services','musiconhold') === true):
			echo	'<dd id="mn-pbx-services--musiconhold">',
				$url->href_html($this->bbf('mn_left_pbx_services-musiconhold'),
				'service/ipbx/pbx_services/musiconhold',
				'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_services','extenfeatures') === true):
			echo	'<dd id="mn-pbx-services--extenfeatures">',
				$url->href_html($this->bbf('mn_left_pbx_services-extenfeatures'),
						'service/ipbx/pbx_services/extenfeatures'),
						'</dd>';
		endif;

		if(xivo_user::chk_acl('pbx_services','paging') === true):
			echo	'<dd id="mn-pbx-services--paging">',
				$url->href_html($this->bbf('mn_left_pbx_services-paging'),
						'service/ipbx/pbx_services/paging'),
						'</dd>';
		endif;


/* COMMENTED
		if(xivo_user::chk_acl('pbx_services','parkinglot') === true):
			echo	'<dd id="mn-pbx-services--parkinglot">',
				$url->href_html($this->bbf('mn_left_pbx_services-parkinglot'),
						'service/ipbx/pbx_services/parkinglot'),
						'</dd>';
		endif;
 */

		if(xivo_user::chk_acl('pbx_services','phonebook') === true):
			echo	'<dd id="mn-pbx-services--phonebook">',
				$url->href_html($this->bbf('mn_left_pbx_services-phonebook'),
						'service/ipbx/pbx_services/phonebook',
						'act=list'),
				'</dd>';
		endif;

		echo	'</dl>';
	endif;

	if(xivo_user::chk_acl('system_management') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_systemmanagement'),'</dt>';

		if(xivo_user::chk_acl('system_management','backupfiles') === true):
			echo	'<dd id="mn-system-management--backupfiles">',
				$url->href_html($this->bbf('mn_left_systemmanagement-backupfiles'),
				'service/ipbx/system_management/backupfiles',
				'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('system_management','configfiles') === true):
			echo	'<dd id="mn-system-management--configfiles">',
				$url->href_html($this->bbf('mn_left_systemmanagement-configfiles'),
				'service/ipbx/system_management/configfiles',
				'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('system_management','context') === true):
			echo	'<dd id="mn-system-management--context">',
				$url->href_html($this->bbf('mn_left_systemmanagement-context'),
				'service/ipbx/system_management/context',
				'act=list'),
				'</dd>';
		endif;
/* LDAP - COMMENTED
		if(xivo_user::chk_acl('system_management','ldapfilter') === true):
			echo	'<dd id="mn-system-management--ldapfilter">',
				$url->href_html($this->bbf('mn_left_systemmanagement-ldapfilter'),
						'service/ipbx/system_management/ldapfilter',
						'act=list'),
						'</dd>';
		endif;
 */
		echo	'</dl>';
	endif;

	if(xivo_user::chk_acl('control_system') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_controlsystem'),'</dt>';

		if(xivo_user::chk_acl('control_system','logfiles') === true):
			echo	'<dd id="mn-control-system--logfiles">',
				$url->href_html($this->bbf('mn_left_controlsystem-logfiles'),
						'service/ipbx/control_system/logfiles',
						'act=list'),
						'</dd>';
		endif;

		if(xivo_user::chk_acl('control_system','reload') === true):
			echo	'<dd id="mn-control-system--reload">',
				$url->href_html($this->bbf('mn_left_controlsystem-ipbxreload',
							   XIVO_SRE_IPBX_LABEL),
						'service/ipbx/control_system/reload',
						null,
						'onclick="return(confirm(\''.$dhtml->escape($this->bbf('controlsystem_ipbxreload_confirm',
												       XIVO_SRE_IPBX_LABEL)).'\'));"'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('control_system','restart') === true):
			echo	'<dd id="mn-control-system--restart">',
				$url->href_html($this->bbf('mn_left_controlsystem-ipbxrestart',
							   XIVO_SRE_IPBX_LABEL),
						'service/ipbx/control_system/restart',
						null,
						'onclick="return(confirm(\''.$dhtml->escape($this->bbf('controlsystem_ipbxrestart_confirm',
												       XIVO_SRE_IPBX_LABEL)).'\'));"'),
				'</dd>';
		endif;

		echo	'</dl>';
	endif;
?>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
</dl>
