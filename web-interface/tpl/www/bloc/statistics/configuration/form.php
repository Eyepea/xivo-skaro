<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
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
#
$form = &$this->get_module('form');

$info = $this->get_var('info');
$element = $this->get_var('element');

#var_dump($info);
#var_dump($this->get_var('error'));

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>
			<div id="sb-part-first" class="b-nodisplay">
				<p>
					<label id="lb-description" for="it-description"><?=$this->bbf('fm_description_general');?></label>
				</p>				
<?php
	
	echo	$form->text(array('desc'	=> $this->bbf('fm_name'),
				  'name'	=> 'stats_conf[name]',
				  'labelid'	=> 'name',
				  'size'	=> 20,
				  'default'	=> $element['stats_conf']['name']['default'],
				  'value'	=> $info['stats_conf']['name'],
				  'error'		=> $this->bbf_args('error',$this->get_var('error','stats_conf','name')) ));
?>
	<fieldset id="stats_conf_workhour">
		<legend><?=$this->bbf('stats_conf_workhour');?></legend>
		<div class="b-form">
			<table>
			<tr>
				<td>
<?php	
	echo	$form->select(array('desc'	=> $this->bbf('fm_hour_start'),
				    'name'	=> 'workhour_start[h]',
				    'labelid'	=> 'hour_start',
				    'key'	=> false,
				    'default'	=> $element['stats_conf']['workhour']['h']['default'],
				    'selected'	=> $this->get_var('workhour_start','h'),
				 	'error'	=> $this->bbf_args('error',$this->get_var('error','workhour_start','h'))),
			      $element['stats_conf']['workhour']['h']);
?>
				</td>
				<td>
<?php
	echo	$form->select(array('desc'	=> '',
				    'name'	=> 'workhour_start[m]',
				    'labelid'	=> 'hour_start',
				    'key'	=> false,
				    'default'	=> $element['stats_conf']['workhour']['m']['default'],
				    'selected'	=> $this->get_var('workhour_start','m')),
			      $element['stats_conf']['workhour']['m']);
?>
				</td>
			</tr>
			<tr>
				<td>
<?php	
	echo	$form->select(array('desc'	=> $this->bbf('fm_hour_end'),
				    'name'	=> 'workhour_end[h]',
				    'labelid'	=> 'workhour_end',
				    'key'	=> false,
				    'default'	=> $element['stats_conf']['workhour']['h']['default'],
				    'selected'	=> $this->get_var('workhour_end','h'),
				 	'error'	=> $this->bbf_args('error',$this->get_var('error','workhour_end','h'))),
			      $element['stats_conf']['workhour']['h']);
?>
				</td>
				<td>
<?php
	echo	$form->select(array('desc'	=> '',
				    'name'	=> 'workhour_end[m]',
				    'labelid'	=> 'workhour_end',
				    'key'	=> false,
				    'default'	=> $element['stats_conf']['workhour']['m']['default'],
				    'selected'	=> $this->get_var('workhour_end','m')),
			      $element['stats_conf']['workhour']['m']);
?>
				</td>
			</tr>
			</table>
		</div>
	</fieldset>
	<fieldset id="stats_conf_period">
		<legend><?=$this->bbf('stats_conf_period');?></legend>
<?php	
	for($i = 1;$i < 6;$i++):
	
	echo	$form->text(array('desc'	=> $this->bbf('fm_period'.$i),
					  'name'	=> 'stats_conf[period'.$i.']',
					  'labelid'	=> $info['period'.$i],
					  'size'	=> 5,
					  'default'	=> $element['stats_conf']['period'.$i]['default'],
					  'value'	=> $info['stats_conf']['period'.$i],
				 	  'error'	=> $this->bbf_args('error',$this->get_var('error','stats_conf','period'.$i)) ));
	
	endfor;
?>
	</fieldset>
			<div class="fm-paragraph fm-description">
				<p>
					<label id="lb-description" for="it-description"><?=$this->bbf('fm_description');?></label>
				</p>
				<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'stats_conf[description]',
					 'id'		=> 'it-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['stats_conf']['description']['default']),
						   $info['description']);?>
			</div>
			</div>
			
			<div id="sb-part-workweek" class="b-nodisplay">
<?php
	
	echo	$form->checkbox(array('desc' => $this->bbf('fm_workweek_monday'),
				  'name'	=> 'stats_conf[monday]',
				  'labelid'	=> 'monday',
				  'checked'	=> $info['stats_conf']['monday'])),
	
	$form->checkbox(array('desc' => $this->bbf('fm_workweek_tuesday'),
				  'name'	=> 'stats_conf[tuesday]',
				  'labelid'	=> 'tuesday',
				  'checked'	=> $info['stats_conf']['tuesday'])),
	
	$form->checkbox(array('desc' => $this->bbf('fm_workweek_wednesday'),
				  'name'	=> 'stats_conf[wednesday]',
				  'labelid'	=> 'wednesday',
				  'checked'	=> $info['stats_conf']['wednesday'])),
	
	$form->checkbox(array('desc' => $this->bbf('fm_workweek_thursday'),
				  'name'	=> 'stats_conf[thursday]',
				  'labelid'	=> 'thursday',
				  'checked'	=> $info['stats_conf']['thursday'])),
	
	$form->checkbox(array('desc' => $this->bbf('fm_workweek_friday'),
				  'name'	=> 'stats_conf[friday]',
				  'labelid'	=> 'friday',
				  'checked'	=> $info['stats_conf']['friday'])),
	
	$form->checkbox(array('desc' => $this->bbf('fm_workweek_saturday'),
				  'name'	=> 'stats_conf[saturday]',
				  'labelid'	=> 'saturday',
				  'checked'	=> $info['stats_conf']['saturday'])),
	
	$form->checkbox(array('desc' => $this->bbf('fm_workweek_sunday'),
				  'name'	=> 'stats_conf[sunday]',
				  'labelid'	=> 'sunday',
				  'checked'	=> $info['stats_conf']['sunday']));
				   
?>
			</div>
			
			<div id="sb-part-last" class="b-nodisplay">
				<p>
					<label id="lb-description" for="it-description"><?=$this->bbf('fm_description_queue_qos');?></label>
				</p>
<?php
	if(($list = $this->get_var('ls_queue')) === false 
	|| ($nb = count($list)) === 0):
?>
				<?=$this->bbf('no_displays');?>
<?php
	else:
		for($i = 0;$i < $nb;$i++):
			$ref = &$list[$i];
			
	echo	$form->text(array('desc'	=> $ref['name'],
				  'name'	=> 'stats_qos['.$ref['id'].']',
				  'labelid'	=> $ref['name'],
				  'size'	=> 5,
				  'default'	=> 0,
				  'value'	=> $ref['stats_qos']));

		endfor;
	endif;
?>
			</div>