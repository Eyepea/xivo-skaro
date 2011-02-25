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
			<li id="dwsm-tab-1" class="dwsm-blur" onclick="dwho_submenu.select(this,'sb-part-first');" onmouseout="dwho_submenu.blur(this);" onmouseover="dwho_submenu.focus(this);">
				<div class="tab"><span class="span-center"><a href="#first"><?=$this->bbf('smenu_general');?></a></span></div><span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-2" class="dwsm-blur" onclick="dwho_submenu.select(this,'sb-part-announce');" onmouseout="dwho_submenu.blur(this);" onmouseover="dwho_submenu.focus(this);">
				<div class="tab"><span class="span-center"><a href="#announce"><?=$this->bbf('smenu_announces');?></a></span></div><span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-3" class="dwsm-blur" onclick="dwho_submenu.select(this,'sb-part-member');" onmouseout="dwho_submenu.blur(this);" onmouseover="dwho_submenu.focus(this);">
				<div class="tab"><span class="span-center"><a href="#member"><?=$this->bbf('smenu_members');?></a></span></div><span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-4" class="dwsm-blur" onclick="dwho_submenu.select(this,'sb-part-application');" onmouseout="dwho_submenu.blur(this);" onmouseover="dwho_submenu.focus(this);">
				<div class="tab"><span class="span-center"><a href="#application"><?=$this->bbf('smenu_application');?></a></span></div><span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-5" class="dwsm-blur" onclick="dwho_submenu.select(this,'sb-part-dialaction');" onmouseout="dwho_submenu.blur(this);" onmouseover="dwho_submenu.focus(this);">
				<div class="tab"><span class="span-center"><a href="#dialaction"><?=$this->bbf('smenu_dialaction');?></a></span></div><span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-6" class="dwsm-blur" onclick="dwho_submenu.select(this,'sb-part-advanced/');" onmouseout="dwho_submenu.blur(this);" onmouseover="dwho_submenu.focus(this);">
				<div class="tab"><span class="span-center"><a href="#advanced"><?=$this->bbf('smenu_advanced');?></a></span></div><span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-7"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-schedule');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
				<div class="tab">
					<span class="span-center"><a href="#schedule"><?=$this->bbf('smenu_schedule');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
			<li id="dwsm-tab-8"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-diversion',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
				<div class="tab">
					<span class="span-center"><a href="#diversion"><?=$this->bbf('smenu_diversion');?></a></span>
				</div>
				<span class="span-right">&nbsp;</span>
			</li>
		</ul>
	</div>
