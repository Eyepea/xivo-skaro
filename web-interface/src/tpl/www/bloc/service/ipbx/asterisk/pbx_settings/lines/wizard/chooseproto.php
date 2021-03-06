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

?>
<div id="sr-users" class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_wizard_choose_proto');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
		<div class="logo_proto">
			<?=$url->href_html('SIP',
					'service/ipbx/pbx_settings/lines',
					array('act'=>'add','proto'=>'sip'),
					null,
					$this->bbf('toolbar_opt_add'));?>
			</div>
		<div class="logo_proto">
			<?=$url->href_html('IAX',
					'service/ipbx/pbx_settings/lines',
					array('act'=>'add','proto'=>'iax'),
					null,
					$this->bbf('toolbar_opt_add'));?>
			</div>
		<div class="logo_proto">
			<?=$url->href_html('SCCP',
					'service/ipbx/pbx_settings/lines',
					array('act'=>'add','proto'=>'sccp'),
					null,
					$this->bbf('toolbar_opt_add'));?>
			</div>
		<div class="logo_proto">
			<?=$url->href_html('CUSTOM',
					'service/ipbx/pbx_settings/lines',
					array('act'=>'add','proto'=>'custom'),
					null,
					$this->bbf('toolbar_opt_add'));?>
			</div>
		<div class="clearboth"></div>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>