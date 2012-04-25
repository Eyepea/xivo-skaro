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

$url   = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

?>
<dl>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_ti_ctisettings');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
<?php
	if(xivo_user::chk_acl_section('service/cti/general_settings') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_generalsettings'),'</dt>';

		if(xivo_user::chk_acl('cti', 'general_settings/general', 'service') === true):
			echo	'<dd id="mn-general">',
				$url->href_html($this->bbf('mn_left_ctisettings-general'),
					'cti/general'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','general_settings/profiles', 'service') === true):
			echo	'<dd id="mn-profiles">',
				$url->href_html($this->bbf('mn_left_ctisettings-profiles'),
					'cti/profiles'),
				'</dd>';
		endif;

		echo	'<dt>',$this->bbf('mn_left_ti_status'),'</dt>';

		if(xivo_user::chk_acl('cti', 'general_settings/presences', 'service') === true):
			echo	'<dd id="mn-presences">',
				$url->href_html($this->bbf('mn_left_ctisettings-presences'),
					'cti/presences'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','general_settings/phonehints', 'service') === true):
			echo	'<dd id="mn-phonehints">',
				$url->href_html($this->bbf('mn_left_ctisettings-phonehints'),
					'cti/phonehints'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','general_settings/channelstatus', 'service') === true):
			echo	'<dd id="mn-channelstatus">',
				$url->href_html($this->bbf('mn_left_ctisettings-channelstatus'),
					'cti/channelstatus'),
				'</dd>';
		endif;
	echo	'</dl>';
	endif;

	if(xivo_user::chk_acl_section('service/cti/directories') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_directories'),'</dt>';
		if(xivo_user::chk_acl('cti','directories/directories', 'service') === true):
			echo	'<dd id="mn-directories">',
				$url->href_html($this->bbf('mn_left_ctisettings-directories'),
					'cti/directories'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','directories/reversedirectories', 'service') === true):
			echo	'<dd id="mn-reversedirectories">',
				$url->href_html($this->bbf('mn_left_ctisettings-reversedirectories'),
					'cti/reversedirectories'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','directories/contexts', 'service') === true):
			echo	'<dd id="mn-contexts">',
				$url->href_html($this->bbf('mn_left_ctisettings-contexts'),
					'cti/contexts'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','directories/displays', 'service') === true):
			echo	'<dd id="mn-displays">',
				$url->href_html($this->bbf('mn_left_ctisettings-displays'),
					'cti/displays'),
				'</dd>';
		endif;
	echo	'</dl>';
	endif;

	if(xivo_user::chk_acl_section('service/cti/sheets') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_sheets'),'</dt>';
		if(xivo_user::chk_acl('cti','sheets/sheetactions', 'service') === true):
			echo	'<dd id="mn-sheetactions">',
				$url->href_html($this->bbf('mn_left_ctisettings-sheetactions'),
					'cti/sheetactions'),
				'</dd>';
		endif;
		if(xivo_user::chk_acl('cti','sheets/sheetevents', 'service') === true):
			echo	'<dd id="mn-sheetevents">',
				$url->href_html($this->bbf('mn_left_ctisettings-sheetevents'),
					'cti/sheetevents'),
				'</dd>';
		endif;
	echo	'</dl>';
	endif;

	if(xivo_user::chk_acl_section('service/cti/control_system') === true):
		echo	'<dl><dt>',$this->bbf('mn_left_ti_controlsystem'),'</dt>';
		if(xivo_user::chk_acl('cti','control_system/restart', 'service') === true):
			echo	'<dd id="mn-restart">',
				$url->href_html($this->bbf('mn_left_ctisettings-restart'),
					'cti/restart',
					null,
					'onclick="return(confirm(\''.
					$dhtml->escape($this->bbf('ctisettings_restart_confirm')).
					'\'));"'),
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
