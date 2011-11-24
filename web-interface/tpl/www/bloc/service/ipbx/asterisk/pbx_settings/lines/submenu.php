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

?>
<div class="sb-smenu">
	<ul>
		<li id="dwsm-tab-1"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-first')"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#first">
					<?=$this->bbf('smenu_general');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-signalling');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"
					><a href="#signalling"><?=$this->bbf('smenu_signalling');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
<?php
$num = 3;
$info    = $this->get_var('info');
if(isset($info['protocol']) === true
&& ($protocol = (string) dwho_ak('protocol',$info['protocol'],true)) !== ''
&& $protocol === 'sip'):
$num = 4;
?>
		<li id="dwsm-tab-3"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-t38');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center"><a href="#t38"><?=$this->bbf('smenu_t38');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
<?php
endif;
?>
		<li id="dwsm-tab-<?=$num?>"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-advanced');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#advanced"><?=$this->bbf('smenu_advanced');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-<?=$num+1?>"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-ipbxinfos',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center">
					<a href="#ipbxinfos"><?=$this->bbf('smenu_ipbxinfos');?></a></span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	</ul>
</div>
