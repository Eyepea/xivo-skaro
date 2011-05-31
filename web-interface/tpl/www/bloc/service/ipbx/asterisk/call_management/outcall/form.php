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

$element = $this->get_var('element');
$context_list = $this->get_var('context_list');

$dundipeer = $this->get_var('dundipeer');
$outcalltrunk = $this->get_var('outcalltrunk');
$rightcall    = $this->get_var('rightcall');
$schedules    = $this->get_var('schedules');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_outcall_name'),
				  'name'	=> 'outcall[name]',
				  'labelid'	=> 'outcall-name',
				  'size'	=> 15,
				  'default'	=> $element['outcall']['name']['default'],
				  'value'	=> $this->get_var('info','outcall','name'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'outcall', 'name')) ));

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_outcall_context'),
				    'name'	=> 'outcall[context]',
				    'labelid'	=> 'outcall-context',
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['outcall']['context']['default'],
				    'selected'	=> $this->get_var('info','outcall','context')),
			      $context_list);
else:
	echo	'<div id="fd-outcall-context" class="txt-center">',
		$url->href_htmln($this->bbf('create_context'),
				'service/ipbx/system_management/context',
				'act=add'),
		'</div>';
endif;

	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_outcall_useenum'),
				      'name'	=> 'outcall[useenum]',
				      'labelid'	=> 'useenum',
				      'checked'	=> $this->get_var('info','outcall','useenum'),
				      'default'	=> $element['outcall']['useenum']['default']));

	echo	$form->text(array('desc'	=> $this->bbf('fm_outcall_routing'),
				  'name'	=> 'outcall[routing]',
				  'labelid'	=> 'outcall-routing',
				  'size'	=> 15,
				  'default'	=> $element['outcall']['routing']['default'],
				  'value'	=> $this->get_var('info','outcall','routing'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'outcall', 'routing')) ));
?>

<?php
if($dundipeer['list'] !== false):
?>
<div id="dundipeerlist" class="fm-paragraph fm-description">
	<p>
		<label id="lb-dundipeer" for="it-dundipeer"><?=$this->bbf('fm_dundipeer');?></label>
	</p>
		<?=$form->jq_select(array('paragraph'	=> false,
					 	'label'		=> false,
            			'name'    	=> 'outcalldundipeer[]',
						'id' 		=> 'outcalldundipeer',
						'key'		=> 'include',
				       	'altkey'	=> 'id',
            			'selected'  => $dundipeer['slt']),
					$dundipeer['list']);?>
</div>
<div class="clearboth"></div>
<?php
else:
	echo	'<div class="txt-center">',
		$url->href_htmln($this->bbf('create_dundipeer'),
				'service/ipbx/dundi/peers',
				'act=add'),
		'</div>';
endif;
?>
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_outcall_internal'),
				      'name'	=> 'outcall[internal]',
				      'labelid'	=> 'internal',
				      'checked'	=> $this->get_var('info','outcall','internal'),
				      'default'	=> $element['outcall']['internal']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_outcall_preprocess-subroutine'),
				  'name'	=> 'outcall[preprocess_subroutine]',
				  'labelid'	=> 'outcall-preprocess-subroutine',
				  'size'	=> 15,
				  'default'	=> $element['outcall']['preprocess_subroutine']['default'],
				  'value'	=> $this->get_var('info','outcall','preprocess_subroutine'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'outcall', 'preprocess_subroutine')) )),

		$form->select(array('desc'	=> $this->bbf('fm_outcall_hangupringtime'),
				    'name'	=> 'outcall[hangupringtime]',
				    'labelid'	=> 'outcall-hangupringtime',
				    'key'	=> false,
				    'bbf'	=> 'fm_outcall_hangupringtime-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'default'	=> $element['outcall']['hangupringtime']['default'],
				    'selected'	=> $this->get_var('info','outcall','hangupringtime')),
			      $element['outcall']['hangupringtime']['value']);

?>
<?php
if($outcalltrunk['list'] !== false):
?>
<div id="outcalltrunklist" class="fm-paragraph fm-description">
	<p>
		<label id="lb-outcalltrunk" for="it-outcalltrunk"><?=$this->bbf('fm_outcalltrunk');?></label>
	</p>
		<?=$form->jq_select(array('paragraph'	=> false,
					 	'label'		=> false,
            			'name'    	=> 'outcalltrunk[]',
						'id' 		=> 'outcalltrunk',
						'key'		=> 'identity',
				       	'altkey'	=> 'id',
            			'selected'  => $outcalltrunk['slt']),
					$outcalltrunk['list']);?>
</div>
<div class="clearboth"></div>
<?php
else:
	echo	'<div class="txt-center">',
		$url->href_htmln($this->bbf('create_trunk'),
				'service/ipbx/trunk_management/sip',
				'act=add'),
		'</div>';
endif;
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-outcall-description" for="it-outcall-description"><?=$this->bbf('fm_outcall_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'outcall[description]',
					 'id'		=> 'outcall-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['outcall']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'outcall', 'description')) ),
				   $this->get_var('info','outcall','description'));?>
	</div>
</div>

<div id="sb-part-exten" class="b-nodisplay">
	<div class="sb-list">
<?php $this->file_include('bloc/service/ipbx/asterisk/call_management/outcall/exten'); ?>
	</div>
</div>

<div id="sb-part-rightcalls" class="b-nodisplay">
<?php
	if($rightcall['list'] !== false):
?>
	<div id="rightcalllist" class="fm-paragraph fm-multilist">
				<?=$form->input_for_ms('rightcalllist',$this->bbf('ms_seek'))?>
		<div class="slt-outlist">
			<?=$form->select(array('name'		=> 'rightcalllist',
					       'label'		=> false,
					       'id'		=> 'it-rightcalllist',
					       'browse'		=> 'rightcall',
					       'key'		=> 'identity',
					       'altkey'		=> 'id',
					       'multiple'	=> true,
					       'paragraph'	=> false),
					 $rightcall['list']);?>
		</div>

		<div class="inout-list">

			<a href="#"
			   onclick="dwho.form.move_selected('it-rightcalllist','it-rightcall');
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_inrightcall');?>">
				<?=$url->img_html('img/site/button/arrow-left.gif',
						  $this->bbf('bt_inrightcall'),
						  'class="bt-inlist" id="bt-inrightcall" border="0"');?></a><br />
			<a href="#"
			   onclick="dwho.form.move_selected('it-rightcall','it-rightcalllist');
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_outrightcall');?>">
				<?=$url->img_html('img/site/button/arrow-right.gif',
						  $this->bbf('bt_outrightcall'),
						  'class="bt-outlist" id="bt-outrightcall" border="0"');?></a>
		</div>

		<div class="slt-inlist">
			<?=$form->select(array('name'		=> 'rightcall[]',
					       'label'		=> false,
					       'id'		=> 'it-rightcall',
					       'browse'		=> 'rightcall',
					       'key'		=> 'identity',
					       'altkey'		=> 'id',
					       'multiple'	=> true,
					       'size'		=> 5,
					       'paragraph'	=> false),
					 $rightcall['slt']);?>
		</div>
	</div>
	<div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_rightcall'),
					'service/ipbx/call_management/rightcall',
					'act=add'),
			'</div>';
	endif;
?>
</div>


<div id="sb-part-schedule" class="b-nodisplay">
<?php
	if($schedules === false):
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_schedules'),
					'service/ipbx/call_management/schedule',
					'act=add'),
			'</div>';
	else:
		echo $form->select(array('desc'	=> $this->bbf('fm_outcall_schedule'),
				    'name'	    => 'schedule_id',
				    'labelid'	  => 'schedule_id',
						'key'	      => 'name',
						'altkey'    => 'id',
						'empty'     => true,
				   // 'default'  	=> $element['schedule_id']['default'],
				    'selected'	=> $this->get_var('schedule_id')),
			      $schedules);
	endif;
?>
</div>
