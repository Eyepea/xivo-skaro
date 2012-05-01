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

$form = &$this->get_module('form');
$url = &$this->get_module('url');

$element = $this->get_var('element');
$info = $this->get_var('info');

$profileclientlist = $this->get_var('profileclientlist');
$contextavail = $this->get_var('contextavail');
$screens = $this->get_var('screens');
$systrays = $this->get_var('systrays');
$informations = $this->get_var('informations');

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_sheetactions_name'),
				  'name'	=> 'sheetactions[name]',
				  'labelid'	=> 'sheetactions-name',
				  'size'	=> 15,
				  'default'	=> $element['sheetactions']['name']['default'],
				  'value'	=> $info['sheetactions']['name']));

#	echo	$form->text(array('desc'	=> $this->bbf('fm_sheetactions_whom'),
#				  'name'	=> 'sheetactions[whom]',
#				  'labelid'	=> 'sheetactions-whom',
#				  'size'	=> 15,
#				  'default'	=> $element['sheetactions']['whom']['default'],
#				  'value'	=> $info['sheetactions']['whom']));

	echo    $form->checkbox(array('desc' => $this->bbf('fm_sheetactions_focus'),
						'name' => 'sheetactions[focus]',
						'labelid' => 'sheetactions_focus',
						'checked' => $info['sheetactions']['focus']));

?>

	<br />
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-description" for="it-description"><?=$this->bbf('fm_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'    => false,
					 'label'    => false,
					 'name'     => 'sheetactions[description]',
					 'id'       => 'it-description',
					 'cols'     => 60,
					 'rows'     => 5,
					 'default'  => $element['sheetactions']['description']['default']),
				   $info['sheetactions']['description']);?>
	</div>
</div>
<div id="sb-part-screens" class="b-nodisplay">
<!-- ///////////////////////////////// SCREENS ///////////////////////////// -->

<?=$form->checkbox(array('desc'	=> $this->bbf('fm_sheetactions_disable'),
	'name'		=> 'sheetactions[disable]',
	'checked'		=> $info['sheetactions']['disable'],
	'id'		=> 'it-sheetactions-disable',
	'default'	=> !$element['sheetactions']['disable']['default']));?>
<?php
	$type = 'screens';
	$count = count($screens);
	$errdisplay = '';
	echo	$form->text(array('desc'	=> $this->bbf('fm_sheetactions_qtui'),
				  'name'	=> 'sheetactions[sheet_qtui]',
				  'labelid'	=> 'sheetactions-qtui',
				  'size'	=> 30,
				  'default'	=> $element['sheetactions']['sheet_qtui']['default'],
				  'value'	=> $info['sheetactions']['sheet_qtui']));

?>
	<p>&nbsp;</p>
	<div class="sb-list">
		<table>
			<thead>
			<tr class="sb-top">
				<th class="th-left">&nbsp;</th>
				<th class="th-center"><?=$this->bbf('col_1');?></th>
				<th class="th-center"><?=$this->bbf('col_2');?></th>
				<th class="th-center"><?=$this->bbf('col_3');?></th>
				<th class="th-center"><?=$this->bbf('col_4');?></th>
				<th class="th-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									  $this->bbf('col_add'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this); return(dwho.dom.free_focus());"',
							   $this->bbf('col_add'));?>
				</th>
			</tr>
			</thead>
			<tbody id="<?=$type?>">
		<?php
		if($count > 0):
			$i=0;
			foreach($screens as $v)
			{

		?>
			<tr class="fm-paragraph<?=$errdisplay?>">
				<td class="td-left txt-center">
				<?=$form->checkbox(array('name'	=> 'screencol5['.$i.']',
					'checked'	=> !$v[4],
					'label'		=> false,
					'id'		=> false,
					'default'	=> 1,
					'paragraph'	=> false));?>
				</td>
				<td class="txt-center">
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'screencol1['.$i.']',
								   'id'			=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'value'		=> $v[0],
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
		echo $form->select(array('paragraph'	=> false,
				    'name'	=> 'screencol2['.$i.']',
				    'empty'	=> true,
				    'key'	=> false,
#				    'default'		=> $element['userfeatures']['timezone']['default'],
				    'selected'	=> $v[1]),
			      array("title", "text","url","urlx", "picture", "phone", "form"));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'screencol3['.$i.']',
								   'id'			=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'value'		=> $v[2],
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'screencol4['.$i.']',
								   'id'			=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'value'		=> $v[3],
								   'default'	=> ''));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$type.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>

		<?php
			$i++;
			}
		endif;
		?>
			</tbody>
			<tfoot>
			<tr id="no-<?=$type?>"<?=($count > 0 ? ' class="b-nodisplay"' : '')?>>
				<td colspan="8" class="td-single"><?=$this->bbf('no_'.$type);?></td>
			</tr>
			</tfoot>
		</table>
		<table class="b-nodisplay">
			<tbody id="ex-<?=$type?>">
			<tr class="fm-paragraph">
				<td class="td-left txt-center">
				<?=$form->checkbox(array('name'	=> 'screencol5[]',
					'label'		=> false,
					'id'		=> false,
					'checked'	=> 1,
					'default'	=> 1));?>
				</td>
				<td class="txt-center">
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'screencol1[]',
								   'id'			=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php

		echo  $form->select(array('paragraph'	=> false,
				    'name'	=> 'screencol2[]',
				    'empty'	=> true,
				    'key'	=> false),
			      array("title", "text","url","urlx", "picture", "phone", "form"));

	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'screencol3[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'screencol4[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$type.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>
			</tbody>
		</table>
	</div>
</div>
<div id="sb-part-systrays" class="b-nodisplay">

<!-- ///////////////////////////////// SYSTRAYS ///////////////////////////// -->
<?php
	$type = 'systrays';
	$count = count($systrays);
	$errdisplay = '';
?>
	<p>&nbsp;</p>
	<div class="sb-list">
		<table>
			<thead>
			<tr class="sb-top">

				<th class="th-left"><?=$this->bbf('col_1');?></th>
				<th class="th-center"><?=$this->bbf('col_2');?></th>
				<th class="th-center"><?=$this->bbf('col_3');?></th>
				<th class="th-center"><?=$this->bbf('col_4');?></th>
				<th class="th-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									  $this->bbf('col_add'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this); return(dwho.dom.free_focus());"',
							   $this->bbf('col_add'));?>
				</th>
			</tr>
			</thead>
			<tbody id="<?=$type?>">
		<?php
		if($count > 0):
			foreach($systrays as $v)
			{

		?>
			<tr class="fm-paragraph<?=$errdisplay?>">
				<td class="td-left txt-center">
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'systrayscol1[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'value'		=> $v[0],
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
		echo $form->select(array('paragraph'	=> false,
				    'name'	=> 'systrayscol2[]',
				    'empty'	=> true,
				    'key'	=> false,
				    'selected'	=> $v[1]),
			      array("title","body"));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'systrayscol3[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'value'		=> $v[2],
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'systrayscol4[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'value'		=> $v[3],
								   'default'	=> ''));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$type.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>

		<?php
			}
		endif;
		?>
			</tbody>
			<tfoot>
			<tr id="no-<?=$type?>"<?=($count > 0 ? ' class="b-nodisplay"' : '')?>>
				<td colspan="7" class="td-single"><?=$this->bbf('no_'.$type);?></td>
			</tr>
			</tfoot>
		</table>
		<table class="b-nodisplay">
			<tbody id="ex-<?=$type?>">
			<tr class="fm-paragraph">
				<td class="td-left txt-center">
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'systrayscol1[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
		echo $form->select(array('paragraph'	=> false,
				    'name'	=> 'systrayscol2[]',
				    'empty'	=> true,
				    'key'	=> false),
			      array("title","body"));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'systrayscol3[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'systrayscol4[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 15,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$type.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>
			</tbody>
		</table>
	</div>
</div>
<div id="sb-part-last" class="b-nodisplay">

<!-- ///////////////////////////////// INFORMATIONS ///////////////////////////// -->
<?php
	$type = 'informations';
	$count = count($informations);
	$errdisplay = '';
?>
	<p>&nbsp;</p>
	<div class="sb-list">
		<table>
			<thead>
			<tr class="sb-top">

<!--				<th class="th-left"><?=$this->bbf('col_1');?></th> -->
<!-- 				<th class="th-center"><?=$this->bbf('col_2');?></th> -->
<!-- 				<th class="th-center"><?=$this->bbf('col_3');?></th> -->
				<th class="th-center"><?=$this->bbf('col_4');?></th>
				<th class="th-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									  $this->bbf('col_add'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this); return(dwho.dom.free_focus());"',
							   $this->bbf('col_add'));?>
				</th>
			</tr>
			</thead>
			<tbody id="<?=$type?>">
		<?php
		if($count > 0):
			foreach($informations as $v)
			{

		?>
			<tr class="fm-paragraph<?=$errdisplay?>">
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'infoscol4[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 75,
								   'key'		=> false,
								   'value'		=> $v[3],
								   'default'	=> ''));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$type.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>

		<?php
			}
		endif;
		?>
			</tbody>
			<tfoot>
			<tr id="no-<?=$type?>"<?=($count > 0 ? ' class="b-nodisplay"' : '')?>>
				<td colspan="7" class="td-single"><?=$this->bbf('no_'.$type);?></td>
			</tr>
			</tfoot>
		</table>
		<table class="b-nodisplay">
			<tbody id="ex-<?=$type?>">
			<tr class="fm-paragraph">
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
								   'name'		=> 'infoscol4[]',
								   'id'		=> false,
								   'label'		=> false,
								   'size'		=> 75,
								   'key'		=> false,
								   'default'	=> ''));
	 ?>
				</td>
				<td class="td-right">
					<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
									  $this->bbf('opt_'.$type.'-delete'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\''.$type.'\',this,1); return(dwho.dom.free_focus());"',
							   $this->bbf('opt_'.$type.'-delete'));?>
				</td>
			</tr>
			</tbody>
		</table>
	</div>
</div>

