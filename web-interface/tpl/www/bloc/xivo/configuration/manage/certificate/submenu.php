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

if ($this->get_var('act') == 'edit' && $this->get_var('info', 'autosigned') === false) {
	$display_issuer_tab = true;
} else {
	$display_issuer_tab = false;
}

if ($display_issuer_tab === true) {
	$class_suffix = '';
	$onaction_suffix = '';
} else {
	$class_suffix = '-last';
	$onaction_suffix = ',1';
}

?>
<div class="sb-smenu">
	<ul>
		<li id="dwsm-tab-1"
			class="dwsm-blur<?= $class_suffix ?>"
			onclick="dwho_submenu.select(this,'sb-part-first'<?= $onaction_suffix ?>);"
			onmouseout="dwho_submenu.blur(this<?= $onaction_suffix ?>);"
			onmouseover="dwho_submenu.focus(this<?= $onaction_suffix ?>);">
			<div class="tab">
				<span class="span-center"><a href="#first"><?=$this->bbf('smenu_general');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	<?php
		if ($display_issuer_tab === true):
	?>
		<li id="dwsm-tab-2"
			class="dwsm-blur-last"
			onclick="dwho_submenu.select(this,'sb-part-issuer',1);"
			onmouseout="dwho_submenu.blur(this,1);"
			onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center"><a href="#issuer"><?=$this->bbf('smenu_issuers');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	<?php
		endif;
	?>
	</ul>
</div>
