<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Proformatique <technique@proformatique.com>
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

$url  = &$this->get_module('url');

?>
<dl>
	<dt>
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('mn_left_name');?></span>
		<span class="span-right">&nbsp;</span>
	</dt>
	<dd>
		<dl>
			<dt><?=$this->bbf('mn_left_ti_configuration');?></dt>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_configuration'),
						   'statistics/configuration','act=list');?>
			</dd>
			<dt><?=$this->bbf('mn_left_ti_general');?></dt>
			<dd id="mn-1">
				<?=$url->href_html($this->bbf('mn_left_statistics-1'),
						   'statistics/stats1');?>
			</dd>
			<dd id="mn-2">
				<?=$url->href_html($this->bbf('mn_left_statistics-2'),
						   'statistics/stats2');?>
			</dd>
			<dd id="mn-3">
				<?=$url->href_html($this->bbf('mn_left_statistics-3'),
						   'statistics/stats3');?>
			</dd>
		</dl>
	</dd>
	<dd class="b-nosize">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</dd>
</dl>
