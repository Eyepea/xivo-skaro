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

$url = &$this->get_module('url');

$basedir = $this->get_var('basedir');
$table_total = $this->get_var('table_total');
$table_time = $this->get_var('table_time');
$table_average = $this->get_var('table_average');
$table_percent = $this->get_var('table_percent');
$xivo_statistics = $this->get_var('xivo_statistics');

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
		<div class="sb-list"> 
			<p><?=$table_total?></p>
			<!-- 
			<p>&nbsp;</p>
	 		<p class="stats-graph-img">
	 			<?=$xivo_statistics->get_graph('stats_total')?>
	  		</p>
	  		-->
			<p><?=$table_time?></p>
			<!-- 
			<p>&nbsp;</p>
	 		<p class="stats-graph-img">
	 			<?=$xivo_statistics->get_graph('stats_time')?>
	  		</p>
	  		-->
			<p><?=$table_average?></p>
			<!-- 
			<p>&nbsp;</p>
	 		<p class="stats-graph-img">
	 			<?=$xivo_statistics->get_graph('stats_average')?>
	  		</p>
	  		-->
			<p><?=$table_percent?></p>
			<!-- 
			<p>&nbsp;</p>
	 		<p class="stats-graph-img">
	 			<?=$xivo_statistics->get_graph('stats_percent')?>
	  		</p>
	  		-->
   	 	</div>
    </div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>