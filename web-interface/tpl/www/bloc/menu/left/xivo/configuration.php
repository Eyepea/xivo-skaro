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
	if(xivo_user::chk_acl('manage') === true):
		echo '<dl><dt>',$this->bbf('mn_left_ti_manage'),'</dt>';

		if(xivo_user::chk_acl('manage','user') === true):
			echo	'<dd id="mn-manage--user">',
				$url->href_html($this->bbf('mn_left_manage-user'),
						'xivo/configuration/manage/user',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('manage','entity') === true):
			echo	'<dd id="mn-manage--entity">',
				$url->href_html($this->bbf('mn_left_manage-entity'),
						'xivo/configuration/manage/entity',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('manage','directories') === true):
			echo	'<dd id="mn-manage--directories">',
				$url->href_html($this->bbf('mn_left_manage-directories'),
						'xivo/configuration/manage/directories',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('manage','accesswebservice') === true):
			echo	'<dd id="mn-manage--accesswebservice">',
				$url->href_html($this->bbf('mn_left_manage-accesswebservice'),
						'xivo/configuration/manage/accesswebservice',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('manage','certificate') === true):
			echo	'<dd id="mn-manage--certificate">',
				$url->href_html($this->bbf('mn_left_manage-certificate'),
						'xivo/configuration/manage/certificate',
						'act=list'),
				'</dd>';
		endif;

		echo '</dl>';
	endif;

	if(xivo_user::chk_acl('network') === true):
		echo '<dl><dt>',$this->bbf('mn_left_ti_network'),'</dt>';

		if(xivo_user::chk_acl('network','interface') === true):
			echo	'<dd id="mn-network--interface">',
				$url->href_html($this->bbf('mn_left_network-interface'),
						'xivo/configuration/network/interface',
						'act=list'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('network','resolvconf') === true):
			echo	'<dd id="mn-network--resolvconf">',
				$url->href_html($this->bbf('mn_left_network-resolvconf'),
						'xivo/configuration/network/resolvconf'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('network','mail') === true):
			echo	'<dd id="mn-network--mail">',
				$url->href_html($this->bbf('mn_left_network-mail'),
						'xivo/configuration/network/mail'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('network','dhcp') === true):
			echo	'<dd id="mn-network--dhcp">',
				$url->href_html($this->bbf('mn_left_network-dhcp'),
						'xivo/configuration/network/dhcp'),
				'</dd>';
		endif;

		echo '</dl>';
	endif;

	if(xivo_user::chk_acl('support') === true):
		echo '<dl><dt>',$this->bbf('mn_left_ti_support'),'</dt>';

		if(xivo_user::chk_acl('support','xivo') === true):
			echo	'<dd id="mn-support--xivo">',
				$url->href_html($this->bbf('mn_left_support-xivo'),
						'xivo/configuration/support/xivo'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('support','alerts') === true):
			echo	'<dd id="mn-support--alerts">',
				$url->href_html($this->bbf('mn_left_support-alerts'),
						'xivo/configuration/support/alerts'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('support','limits') === true):
			echo	'<dd id="mn-support--limits">',
				$url->href_html($this->bbf('mn_left_support-limits'),
						'xivo/configuration/support/limits'),
				'</dd>';
		endif;

		echo '</dl>';
	endif;

	if(xivo_user::chk_acl('provisioning') === true):
		echo '<dl><dt>',$this->bbf('mn_left_ti_provisioning'),'</dt>';

		if(xivo_user::chk_acl('provisioning','general') === true):
			echo	'<dd id="mn-provisioning--general">',
				$url->href_html($this->bbf('mn_left_provisioning-general'),
						'xivo/configuration/provisioning/general'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('provisioning','configregistrar') === true):
			echo	'<dd id="mn-provisioning--configregistrar">',
				$url->href_html($this->bbf('mn_left_provisioning-configregistrar'),
						'xivo/configuration/provisioning/configregistrar'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('provisioning','configdevice') === true):
			echo	'<dd id="mn-provisioning--configdevice">',
				$url->href_html($this->bbf('mn_left_provisioning-configdevice'),
						'xivo/configuration/provisioning/configdevice'),
				'</dd>';
		endif;

		if(xivo_user::chk_acl('provisioning','plugin') === true):
			echo	'<dd id="mn-provisioning--plugin">',
				$url->href_html($this->bbf('mn_left_provisioning-plugin'),
						'xivo/configuration/provisioning/plugin'),
				'</dd>';
		endif;

		echo '</dl>';
	endif;

	if(xivo_user::chk_acl('controlsystem') === true):
		echo '<dl><dt>',$this->bbf('mn_left_ti_controlsystem'),'</dt>';

		if(xivo_user::chk_acl('controlsystem','network') === true):
			$class_network = file_exists('/var/lib/pf-xivo-web-interface/network.reload')?'active':false;

			echo	'<dd id="mn-controlsystem--network">',
				$url->href_html($this->bbf('mn_left_controlsystem-network'),
						'xivo/configuration/controlsystem/network',
						null,
						'onclick="return(confirm(\''.$dhtml->escape($this->bbf('controlsystem_network_confirm')).'\'));"',
						null,
						false,
						'&amp;',
						true,
						true,
						true,
						null,
						$class_network);
		endif;

		if(xivo_user::chk_acl('controlsystem','commonconf') === true):
			$class_commonconf = file_exists('/var/lib/pf-xivo-web-interface/commonconf.reload')?'active':false;

			echo	'<dd id="mn-controlsystem--commonconf">',
				 $url->href_html($this->bbf('mn_left_controlsystem-commonconf'),
						'xivo/configuration/controlsystem/commonconf',
						null,
						'onclick="return(confirm(\''.$dhtml->escape($this->bbf('controlsystem_commonconf_confirm')).'\'));"',
						null,
						false,
						'&amp;',
						true,
						true,
						true,
						null,
						$class_commonconf);
		endif;

		echo '</dl>';
	endif;
?>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
</dl>
