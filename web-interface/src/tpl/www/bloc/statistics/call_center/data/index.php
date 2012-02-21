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
$form = &$this->get_module('form');

$listconf = $this->get_var('listconf');
$table_general = $this->get_var('table_general');
$xivo_jqplot = $this->get_var('xivo_jqplot');

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
<?php
/*
		<form action="<?=$_SERVER['PHP_SELF']?>" method="get" accept-charset="utf-8">
			<div id="d-conf-list" class="fm-paragraph">
			<?=$this->bbf('fm_home_call_center_select_conf')?>
<?php
				echo	$form->select(array('name'	=> 'confid',
							    'id'		=> 'it-confid',
							    'paragraph'	=> false,
							    'browse'	=> 'conf',
							    'empty'		=> $this->bbf('toolbar_fm_conf'),
							    'key'		=> 'name',
							    'altkey'	=> 'id',
							    'class'		=> 'fm-selected-conf',
							    'selected'	=> $this->get_var('confid')),
						      	$listconf);
?>
			</div>
		</form>
		
			<h4>&nbsp;</h4>
*/
?>
		<div class="sb-list">
			<?=$table_general?>
   	 	</div>
		<?=$xivo_jqplot->get_result('chart1');?>
    </div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>