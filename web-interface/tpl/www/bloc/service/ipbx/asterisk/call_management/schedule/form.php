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

$info         = $this->get_var('info');
$element      = $this->get_var('element');
$list         = $this->get_var('list');
$context_list = $this->get_var('context_list');
$timezones    = $this->get_var('timezones');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

echo	$form->text(array('desc'	=> $this->bbf('fm_schedule_name'),
			  'name'	=> 'schedule[name]',
			  'labelid'	=> 'schedule-name',
			  'size'	=> 15,
			  'default'	=> $element['schedule']['name']['default'],
			  'value'	=> $info['schedule']['name'],
				  'error'	=> $this->bbf_args('error',
			  		$this->get_var('error', 'schedule', 'name')) )),

      $form->select(array('desc' => $this->bbf('fm_schedule_timezone'),
				  'name'     => 'schedule[timezone]',
			    'key'      => false,
			    'default'  => $element['schedule']['timezone']['default'],
					'selected' => $info['schedule']['timezone']),
				$timezones);


	// oneped hours
	$type = 'disp';
	$opened = $info['opened'];
	$count = $opened?count($opened):0;
	$errdisplay = '';
?>
	<div class="sb-list">
	<fieldset id="fld-opened-hours">
		<legend><?=$this->bbf('fld-opened-hours');?></legend>

		<table cellspacing="0" cellpadding="0" border="0">
			<thead>
			<tr class="sb-top">

				<th class="th-left"><?=$this->bbf('fm_col_hours');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_weekdays');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_monthdays');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_months');?></th>
				<th class="th-right th-rule">
					<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									  $this->bbf('col_add'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="dwho.dom.make_table_list(\'disp\',this); return(dwho.dom.free_focus());"',
							   $this->bbf('col_add'));?>
				</th>
			</tr>
			</thead>
			<tbody id="disp">
		<?php
		if($count > 0):
			for($i = 0;$i < $count;$i++):

		?>
			<tr class="fm-paragraph<?=$errdisplay?>">
				<td class="td-left">
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'opened[hours][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'value'		=> $opened[$i]['hours'],
							       'default'	=> '',
										 'error'		=> $this->bbf_args('opened', $this->get_var('error', 'opened', $i, 'hours'))));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'opened[weekdays][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'value'		=> $opened[$i]['weekdays'],
							       'default'	=> '',
										 'error'		=> $this->bbf_args('opened', $this->get_var('error', 'opened', $i, 'weekdays'))));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'opened[monthdays][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'value'		=> $opened[$i]['monthdays'],
							       'default'	=> '',
										 'error'		=> $this->bbf_args('opened', $this->get_var('error', 'opened', $i, 'monthdays'))));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'opened[months][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'value'	=> $opened[$i]['months'],
							       'default'	=> '',
			               'error'		=> $this->bbf_args('opened', $this->get_var('error', 'opened', $i, 'months'))));
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
			endfor;
		endif;
		?>
			</tbody>
			<tfoot>
			<tr id="no-<?=$type?>"<?=($count > 0 ? ' class="b-nodisplay"' : '')?>>
				<td colspan="5" class="td-single"><?=$this->bbf('no_'.$type);?></td>
			</tr>
			</tfoot>
		</table>
		<table class="b-nodisplay" cellspacing="0" cellpadding="0" border="0">
			<tbody id="ex-<?=$type?>">
			<tr class="fm-paragraph">
				<td class="td-left">
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'opened[hours][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'opened[weekdays][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'opened[monthdays][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'opened[months][]',
							       'id'		  => false,
							       'label'	=> false,
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
  </fieldset>
	</div>


<?php
	// closed hours
	$type = 'disp2';
	$closed = array();
	$count = $closed?count($closed):0;
	$errdisplay = '';
?>
	<div class="sb-list">
	<fieldset id="fld-closed-hours">
		<legend><?=$this->bbf('fld-closed-hours');?></legend>
<?php
		// dialactions
		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
			array('event'	=> 'schedule_fallback'));
?>

		<table cellspacing="0" cellpadding="0" border="0">
			<thead>
			<tr class="sb-top">

				<th class="th-left"><?=$this->bbf('fm_col_hours');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_weekdays');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_monthdays');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_months');?></th>
				<th class="th-center"><?=$this->bbf('fm_col_action');?></th>
				<th class="th-right th-rule">
					<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									  $this->bbf('col_add'),
									  'border="0"'),
							   '#',
							   null,
							   'onclick="xivo_ast_schedule_add_closed_action(\'disp2\',this); return(dwho.dom.free_focus());"',
							   $this->bbf('col_add'));?>
				</th>
			</tr>
			</thead>
			<tbody id="disp2">
		<?php
		if($count > 0):
			for($i = 0;$i < $count;$i++):

		?>
			<tr class="fm-paragraph<?=$errdisplay?>">
				<td class="td-left">
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'closed[hours][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'value'		=> $closed[$i]['weekdays'],
							       'default'	=> '',
										 'error'		=> $this->bbf_args('closed', $this->get_var('error', 'closed', $i, 'weekdays'))));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'closed[weekdays][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'value'		=> $closed[$i]['weekdays'],
							       'default'	=> '',
										 'error'		=> $this->bbf_args('closed', $this->get_var('error', 'closed', $i, 'weekdays'))));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'closed[monthdays][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'value'		=> $closed[$i]['monthdays'],
							       'default'	=> '',
										 'error'		=> $this->bbf_args('closed', $this->get_var('error', 'closed', $i, 'monthdays'))));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'closed[months][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'value'	=> $closed[$i]['months'],
							       'default'	=> '',
			               'error'		=> $this->bbf_args('closed', $this->get_var('error', 'closed', $i, 'months'))));
	 ?>
				</td>
				<td>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
			array('event'	=> "fallback[$i]"));
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
			endfor;
		endif;
		?>
			</tbody>
			<tfoot>
			<tr id="no-<?=$type?>"<?=($count > 0 ? ' class="b-nodisplay"' : '')?>>
				<td colspan="6" class="td-single"><?=$this->bbf('no_'.$type);?></td>
			</tr>
			</tfoot>
		</table>
		<table class="b-nodisplay" cellspacing="0" cellpadding="0" border="0">
			<tbody id="ex-<?=$type?>">
			<tr class="fm-paragraph">
				<td class="td-left">
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'	  	=> 'closed[hours][]',
							       'id'	    	=> false,
							       'label'  	=> false,
							       'size'	   	=> 15,
							       'key'	    => false,
							       'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'closed[weekdays][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'closed[monthdays][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'default'	=> ''));
	 ?>
				</td>
				<td>
	<?php
					echo $form->text(array('paragraph'	=> false,
							       'name'		=> 'closed[months][]',
							       'id'		  => false,
							       'label'	=> false,
							       'size'		=> 15,
							       'key'		=> false,
							       'default'	=> ''));
	 ?>
				</td>
				<td id="onclosed-time-dialaction">
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
  </fieldset>
	</div>


</div>

