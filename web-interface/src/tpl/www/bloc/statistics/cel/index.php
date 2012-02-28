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

$url     = &$this->get_module('url');

$table_trunk = $this->get_var('table_trunk');
$table_intern = $this->get_var('table_intern');
$top10_call_duration_intern = $this->get_var('top10_call_duration_intern');
$top10_call_duration_in = $this->get_var('top10_call_duration_in');
$top10_call_duration_out = $this->get_var('top10_call_duration_out');
$top10_call_nb_intern = $this->get_var('top10_call_nb_intern');
$top10_call_nb_in = $this->get_var('top10_call_nb_in');
$top10_call_nb_out = $this->get_var('top10_call_nb_out');
$top10_call_price = $this->get_var('top10_call_price');
$axetype = $this->get_var('axetype');
$xivo_jqplot = $this->get_var('xivo_jqplot');

?>
<div class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
	<div class="sb-content">
		<div class="sb-list">
			<h4 class="txt-center"><?=$this->bbf('title_cel_calls_by_trunk');?></h4>

				<?=$table_trunk?>

				<div style="width:370px; float:right;">
					&nbsp;
				</div>
				<div style="width:370px; float:left;">
					<?=$table_intern?>
				</div>
				<div style="clear:both;"></div>

			<hr><hr><hr>
			<h4 class="txt-center"><?=$this->bbf('title_cel_top10_calls');?></h4>

				<div style="width:240px; float:right;">
					<?=$top10_call_nb_out?>
				</div>
				<div style="width:240px; float:right; margin-right:15px;">
					<?=$top10_call_nb_in?>
				</div>
				<div style="width:240px; float:left;">
					<?=$top10_call_nb_intern?>
				</div>
				<div style="clear:both;"></div>


				<div style="width:240px; float:right;">
					<?=$top10_call_duration_out?>
				</div>
				<div style="width:240px; float:right; margin-right:15px;">
					<?=$top10_call_duration_in?>
				</div>
				<div style="width:240px; float:left;">
					<?=$top10_call_duration_intern?>
				</div>
				<div style="clear:both;"></div>


				<div style="width:240px; float:right;">
					&nbsp;
				</div>
				<div style="width:240px; float:right; margin-right:15px;">
					&nbsp;
				</div>
				<div style="width:240px; float:left;">
					<?=$top10_call_price?>
				</div>
				<div style="clear:both;"></div>

		</div>
<?php
		$xivo_jqplot->get_result('chart1');
?>
    </div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>