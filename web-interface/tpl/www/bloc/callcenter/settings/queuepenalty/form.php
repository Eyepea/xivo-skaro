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

$form    = &$this->get_module('form');
$url     = $this->get_module('url');

$info    = $this->get_var('info');
$element = $this->get_var('element');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

	$penalties    = array();
	if (is_array($info) && array_key_exists('changes', $info))
		$penalties = $info['changes'];

	$signs        = array('+','-','=');
?>

<div id="sb-part-first" class="b-nodisplay">
<?php
echo	$form->text(array('desc'	=> $this->bbf('fm_queuepenalty_name'),
			  'name'	=> 'queuepenalty[name]',
			  'labelid'	=> 'queuepenalty-name',
			  'size'	=> 15,
			  'default'	=> $element['queuepenalty']['name']['default'],
			  'value'	=> $info['queuepenalty']['name'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'queuepenalty', 'name')) ));
?>

	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-queuepenalty-description" for="it-queuepenalty-description"><?=$this->bbf('fm_queuepenalty_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'queuepenalty[description]',
					 'id'		=> 'it-queuepenalty-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['queuepenalty']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'queuepenalty', 'description')) ),
				   $info['queuepenalty']['description']);?>
	</div>
</div>

<div id="sb-part-penalties" class="b-nodisplay">
<div id="sb-list">
<?php
	$dtype = "disp";
  $count = count($penalties);
	$errdisplay = '';
?>
	<p>&nbsp;</p>
	<div class="sb-list">
		<table>
			<thead>
			<tr class="sb-top">

				<th class="th-left"><?=$this->bbf('queuepenalty_col1');?></th>
				<th class="th-center"><?=$this->bbf('queuepenalty_col2');?></th>
				<th class="th-center"><?=$this->bbf('queuepenalty_col3');?></th>
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
					echo $form->text(array('paragraph'	=> false,
								   'name'	   => "queuepenalty_seconds[$i]",
								   'id'      => false,
								   'label'   => false,
								   'size'	   => 3,
								   'key'	   => false,
									 'default' => '',
									 'error'	=> $this->bbf_args('error',$this->get_var('error','queuepenaltychange',$i,'seconds')),
								   'value'   => $penalties[$i]['seconds']));
	?>
					</td>
					<td>
	<?php
					echo	$form->select(array(
							'name'		=> "queuepenalty_maxp_sign[]",
							'id'	  	=> "it-maxp_sign[$i]",
							'key'	  	=> false,
							'label'   => false,
							'empty'		=> true,
							'paragraph' => false,
							'selected'  => $penalties[$i]['maxp_sign']
						),
						$signs),

					$form->text(array('paragraph'	=> false,
								   'name'	   => "queuepenalty_maxp_value[$i]",
								   'id'		   => false,
								   'label'	 => false,
								   'size'	   => 3,
								   'key'	   => false,
									 'default' => '',
									 'error'	=> $this->bbf_args('error',$this->get_var('error','queuepenaltychange',$i,'maxp_value')),
								   'value'   => $penalties[$i]['maxp_value']));
	 ?>
				</td>
				<td>
	<?php
					echo	$form->select(array(
							'name'		=> "queuepenalty_minp_sign[$i]",
							'id'	  	=> "it-minp_sign[$i]",
							'key'	  	=> false,
							'label'   => false,
							'empty'		=> true,
							'paragraph' => false,
							'selected'  => $penalties[$i]['minp_sign']
						),
						$signs),

					$form->text(array('paragraph'	=> false,
								   'name'	   => "queuepenalty_minp_value[$i]",
								   'id'		   => false,
								   'label'	 => false,
								   'size'	   => 3,
								   'key'	   => false,
									 'default' => '',
									 'error'	=> $this->bbf_args('error',$this->get_var('error','queuepenaltychange',$i,'minp_value')),
								   'value'   => $penalties[$i]['minp_value']));
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
					echo $form->text(array('paragraph'	=> false,
								   'name'	   => "queuepenalty_seconds[]",
								   'id'      => false,
								   'label'   => false,
								   'size'	   => 3,
								   'key'	   => false,
									 'default' => ''));
	?>
					</td>
					<td>
	<?php
					echo	$form->select(array(
							'name'		=> "queuepenalty_maxp_sign[]",
							'id'	  	=> "it-maxp_sign[]",
							'key'	  	=> false,
							'label'   => false,
							'empty'		=> true,
							'paragraph' => false
						),
						$signs),

					$form->text(array('paragraph'	=> false,
								   'name'	   => "queuepenalty_maxp_value[]",
								   'id'		   => false,
								   'label'	 => false,
								   'size'	   => 3,
								   'key'	   => false,
								   'default' => ''));
	 ?>
				</td>
				<td>
	<?php
					echo	$form->select(array(
							'name'		=> "queuepenalty_minp_sign[]",
							'id'	  	=> "it-minp_sign[]",
							'key'	  	=> false,
							'label'   => false,
							'empty'		=> true,
							'paragraph' => false
						),
						$signs),

					$form->text(array('paragraph'	=> false,
								   'name'	   => "queuepenalty_minp_value[]",
								   'id'		   => false,
								   'label'	 => false,
								   'size'	   => 3,
								   'key'	   => false,
								   'default' => ''));
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
</div>
