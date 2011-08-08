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

  $form = &$this->get_module('form');
	$url = &$this->get_module('url');

	$type         = $this->get_var('type');
	$info         = $this->get_var('info');
	$ctipresences = $this->get_var($type);

	$thresholds   = array('ctipresence'=> 1, 'nonctipresence'=> 0);
	$threshold    = $thresholds[$type];

	if($ctipresences !== false):
?>

<div id="sb-list">
<?php
	$dtype = "$type-disp";
  $count = $info['queuefeatures'][$type]?count($info['queuefeatures'][$type]):0;
	$errdisplay = '';
?>
	<p>&nbsp;</p>
	<div class="sb-list">
		<table>
			<thead>
			<tr class="sb-top">

				<th class="th-left"><?=$this->bbf($type.'_col1');?></th>
				<th class="th-center"><?=$this->bbf($type.'_col2');?></th>
				<th class="th-right th-rule">
					<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									  $this->bbf('col_add'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$dtype.'\',this); return(dwho.dom.free_focus());"',
							   $this->bbf('col_add'));?>
				</th>
			</tr>
			</thead>
			<tbody id="<?=$dtype?>">
		<?php
		if($count > 0):
			for($i = 0;$i < $count;$i++):

		?>
			<tr class="fm-paragraph<?=$errdisplay?>">
				<td class="td-left">
	<?php
					echo	$form->select(array(
							'name'		=> "$type-name[]",
							'id'		=> "it-$type-name[$i]",
							'key'		=> 'name',
							'altkey'	=> 'id',
							'empty'		=> true,
							'optgroup'	=> array(
								'key'		=> 'presence_name', 
								'unique' 	=> true,
							),
						  'selected'	=> $info['queuefeatures'][$type][$i][0]['id'],
							'error'      	=> $this->bbf_args('error_generic', $this->get_var('error',$type,$i,'name'))
						),
						$ctipresences);
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'	=> "$type-weight[]",
								   'id'		=> false,
								   'label'	=> false,
								   'size'	=> 3,
								   'key'	=> false,
									 'default'	=> $threshold,
								   'value'	 => $info['queuefeatures'][$type][$i][1],
								   'error'   => $this->bbf_args('error_generic',$this->get_var('error', $type, $i, 'weight'))));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$dtype.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$dtype.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>

		<?php
			endfor;
		endif;
		?>
			</tbody>
			<tfoot>
			<tr id="no-<?=$dtype?>"<?=($count > 0 ? ' class="b-nodisplay"' : '')?>>
				<td colspan="5" class="td-single"><?=$this->bbf('no_'.$dtype);?></td>
			</tr>
			</tfoot>
		</table>
		<table class="b-nodisplay">
			<tbody id="ex-<?=$dtype?>">
			<tr class="fm-paragraph">
				<td class="td-left">
	<?php
					echo	$form->select(array(
							'name'		=> "$type-name[]",
							'id'		=> "it-$type-name[]",
							'key'		=> 'name',
							'altkey'	=> 'id',
							'label'     => false,
							'empty'		=> true,
							'optgroup'	=> array(
								'key'		=> 'presence_name', 
								'unique' 	=> true,
							),
						),
						$ctipresences);
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'	=> "$type-weight[]",
								   'id'		=> false,
								   'label'	=> false,
								   'size'	=> 3,
								   'key'	=> false,
								   'default'	=> $threshold));
	 ?>
				</td>

				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$dtype.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$dtype.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$dtype.'-delete'));?>
				</td>
			</tr>
			</tbody>
		</table>
	</div>
</div>






<?php
	endif;
?>
