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

$url = &$this->get_module('url');
$statistics = &$this->get_module('statistics');

$basedir = $this->get_var('basedir');
$queue_log = $this->get_var('queue_log');
$conf = $this->get_var('conf');
$ls_queue = $this->get_var('ls_queue');
$table1 = $this->get_var('table1');

#var_dump($statistics);

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
	
<?php

echo $table1->render_html();

#var_dump($queue_log);
#var_dump($conf);
#var_dump($ls_queue);
/*
 		<img src="<?=$basedir?>example2.png" />
 		<img src="<?=$basedir?>Naked.png" />
 */
 ?>
 		<img src="<?=$basedir?><?=$table1->get_name()?>.png" />
    </div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>

