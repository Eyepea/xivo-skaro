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

?>
	<div class="sb-smenu">
		<ul>
			<li id="dwsm-tab-1"
				class="dwsm-blur"
				onclick="dwho_submenu.select(this,'sb-part-first');"
				onmouseout="dwho_submenu.blur(this);"
				onmouseover="dwho_submenu.focus(this);">
				<div class="tab">
					<span class="span-center"><a href="#first"><?=$this->bbf('smenu_general');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-2"
				class="dwsm-blur"
				onclick="dwho_submenu.select(this,'sb-part-workweek');"
				onmouseout="dwho_submenu.blur(this);"
				onmouseover="dwho_submenu.focus(this);">
				<div class="tab">
					<span class="span-center"><a href="#workweek"><?=$this->bbf('smenu_workweek');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-4"
				class="dwsm-blur"
				onclick="dwho_submenu.select(this,'sb-part-queue');"
				onmouseout="dwho_submenu.blur(this);"
				onmouseover="dwho_submenu.focus(this);">
				<div class="tab">
					<span class="span-center"><a href="#queue"><?=$this->bbf('smenu_queue');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-5"
				class="dwsm-blur"
				onclick="dwho_submenu.select(this,'sb-part-qos');"
				onmouseout="dwho_submenu.blur(this);"
				onmouseover="dwho_submenu.focus(this);">
				<div class="tab">
					<span class="span-center"><a href="#qos"><?=$this->bbf('smenu_qos');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
<?php
	if (xivo_user::get_info('meta') === 'root'):
?>
			<li id="dwsm-tab-6"
				class="dwsm-blur"
				onclick="dwho_submenu.select(this,'sb-part-agent');"
				onmouseout="dwho_submenu.blur(this);"
				onmouseover="dwho_submenu.focus(this);">
				<div class="tab">
					<span class="span-center"><a href="#agents"><?=$this->bbf('smenu_agents');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-7"
				class="dwsm-blur-last"
				onclick="dwho_submenu.select(this,'sb-part-last',1);"
				onmouseout="dwho_submenu.blur(this,1);"
				onmouseover="dwho_submenu.focus(this,1);">
				<div class="tab">
					<span class="span-center"><a href="#last"><?=$this->bbf('smenu_permissions');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
<?php
	else:
?>
			<li id="dwsm-tab-6"
				class="dwsm-blur-last"
				onclick="dwho_submenu.select(this,'sb-part-agent',1);"
				onmouseout="dwho_submenu.blur(this,1);"
				onmouseover="dwho_submenu.focus(this,1);">
				<div class="tab">
					<span class="span-center"><a href="#agents"><?=$this->bbf('smenu_agents');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
<?php
	endif;
?>
		</ul>
	</div>
