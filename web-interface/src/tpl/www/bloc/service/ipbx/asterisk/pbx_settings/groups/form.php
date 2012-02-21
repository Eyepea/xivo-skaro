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
$user = $this->get_var('user');
$rightcall = $this->get_var('rightcall');
$moh_list = $this->get_var('moh_list');
$context_list = $this->get_var('context_list');
$schedules    = $this->get_var('schedules');

if(dwho_has_len($user['list']) === true):
	$user_suggest = $this->get_var('user','fullname');
else:
	$user_suggest = null;
endif;

$dhtml = &$this->get_module('dhtml');
$dhtml->write_js('var xivo_fm_user_suggest = \''.$dhtml->escape($user_suggest).'\';');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first" class="b-nodisplay">
<?php

if (is_null($this->get_var('error','groupfeatures','number')))
	$err_number = $this->get_var('error','extenumbers');
else
	$err_number = $this->get_var('error','groupfeatures','number');
	   		
	echo	$form->text(array('desc'	=> $this->bbf('fm_groupfeatures_name'),
				  'name'	=> 'groupfeatures[name]',
				  'labelid'	=> 'groupfeatures-name',
				  'size'	=> 15,
				  'default'	=> $element['groupfeatures']['name']['default'],
				  'value'	=> $this->get_var('info','groupfeatures','name'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','groupfeatures','name')))),
					   		
		$form->text(array('desc'	=> $this->bbf('fm_groupfeatures_number'),
				  'name'	=> 'groupfeatures[number]',
				  'labelid'	=> 'groupfeatures-number',
				  'size'	=> 15,
				  'default'	=> $element['groupfeatures']['number']['default'],
				  'value'	=> $this->get_var('info','groupfeatures','number'),
				  'error'	=> $this->bbf_args('error',$err_number))),

		$form->select(array('desc'	=> $this->bbf('fm_queue_strategy'),
				    'name'	    => 'queue[strategy]',
				    'labelid'	=> 'queue-strategy',
				    'key'	    => false,
				    'bbf'	    => 'fm_queue_strategy-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['strategy']['default'],
				  	'selected'	=> $this->get_var('info','queue','strategy')),
			      $element['queue']['strategy']['value']);

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_groupfeatures_context'),
				    'name'	=> 'groupfeatures[context]',
				    'labelid'	=> 'groupfeatures-context',
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['groupfeatures']['context']['default'],
				  	'selected'	=> $this->get_var('info','groupfeatures','context')),
			      $context_list);
else:
	echo	'<div id="fd-groupfeatures-context" class="txt-center">',
		$url->href_htmln($this->bbf('create_context'),
				'service/ipbx/system_management/context',
				'act=add'),
		'</div>';
endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_groupfeatures_timeout'),
				    'name'	=> 'groupfeatures[timeout]',
				    'labelid'	=> 'groupfeatures-timeout',
				    'key'	=> false,
				    'bbf'	=> 'fm_groupfeatures_timeout-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['groupfeatures']['timeout']['default'],
				  	'selected'	=> $this->get_var('info','groupfeatures','timeout')),
			      $element['groupfeatures']['timeout']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_timeout'),
				    'name'	=> 'queue[timeout]',
				    'labelid'	=> 'queue-timeout',
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_timeout-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['timeout']['default'],
				    'selected'	=> (isset($info['queue']['timeout']) === true ? (int) $info['queue']['timeout'] : null)),
			      $element['queue']['timeout']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queue_ringinuse'),
				    'name'	=> 'queue[ringinuse]',
				    'labelid'	=> 'queue-ringinuse',
				    'default'	=> $element['queue']['ringinuse']['default'],
					'checked'	=> $this->get_var('info','queue','ringinuse')));

if($moh_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_queue_musicclass'),
				    'name'	=> 'queue[musicclass]',
				    'labelid'	=> 'queue-musicclass',
				    'empty'	=> true,
				    'key'	=> 'category',
				    'invalid'	=> ($this->get_var('act') === 'edit'),
				    'default'	=> ($this->get_var('act') === 'add' ? $element['queue']['musicclass']['default'] : null),
				  	'selected'	=> $this->get_var('info','queue','musicclass')),
			      $moh_list);
endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_callerid_mode'),
				    'name'	=> 'callerid[mode]',
				    'labelid'	=> 'callerid-mode',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_callerid_mode-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['callerid']['mode']['default'],
				    'selected'	=> $info['callerid']['mode']),
			      $element['callerid']['mode']['value'],
			      'onchange="xivo_ast_chg_callerid_mode(this);"'),

		$form->text(array('desc'	=> '&nbsp;',
				  'name'	=> 'callerid[callerdisplay]',
				  'labelid'	=> 'callerid-callerdisplay',
				  'size'	=> 15,
				  'notag'	=> false,
				  'default'	=> $element['callerid']['callerdisplay']['default'],
				  'value'	=> $this->get_var('info','callerid','callerdisplay'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','callerid','callerdisplay')))),

		$form->text(array('desc'	=> $this->bbf('fm_groupfeatures_preprocess-subroutine'),
				  'name'	=> 'groupfeatures[preprocess_subroutine]',
				  'labelid'	=> 'groupfeatures-preprocess-subroutine',
				  'size'	=> 15,
				  'default'	=> $element['groupfeatures']['preprocess_subroutine']['default'],
				  'value'	=> $this->get_var('info','groupfeatures','preprocess_subroutine'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','groupfeatures','preprocess_subroutine'))));
?>
</div>

<div id="sb-part-user" class="b-nodisplay">
<?php
	if($user['list'] !== false):
?>
<div id="userlist" class="fm-paragraph fm-description">
		<?=$form->jq_select(array('paragraph'	=> false,
					 	'label'		=> false,
            			'name'    	=> 'user[]',
						'id' 		=> 'user',
						'key'		=> 'identity',
				       	'altkey'	=> 'id',
            			'selected'  => $user['slt']),
					$user['list']);?>
</div>
<div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_user'),
					'service/ipbx/pbx_settings/users',
					'act=add'),
			'</div>';
	endif;
?>
</div>

<div id="sb-part-application" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_groupfeatures_transfer-user'),
				    'name'	    => 'groupfeatures[transfer_user]',
				    'labelid'	=> 'groupfeatures-transfer-user',
				    'default'	=> $element['groupfeatures']['transfer_user']['default'],
					'checked'	=> $this->get_var('info','groupfeatures','transfer_user'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_groupfeatures_transfer-call'),
				    'name'	    => 'groupfeatures[transfer_call]',
				    'labelid'	=> 'groupfeatures-transfer-call',
				    'default'	=> $element['groupfeatures']['transfer_call']['default'],
					'checked'	=> $this->get_var('info','groupfeatures','transfer_call'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_groupfeatures_write-caller'),
				    'name'	=> 'groupfeatures[write_caller]',
				    'labelid'	=> 'groupfeatures-write-caller',
				    'default'	=> $element['groupfeatures']['write_caller']['default'],
					'checked'	=> $this->get_var('info','groupfeatures','write_caller'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_groupfeatures_write-calling'),
				    'name'	    => 'groupfeatures[write_calling]',
				    'labelid'	=> 'groupfeatures-write-calling',
				    'default'	=> $element['groupfeatures']['write_calling']['default'],
					'checked'	=> $this->get_var('info','groupfeatures','write_calling')));
?>
</div>

<div id="sb-part-rightcall" class="b-nodisplay">
<?php
	if($rightcall['list'] !== false):
?>
    <div id="rightcalllist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'rightcall[]',
    						'id' 		=> 'it-rightcall',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $rightcall['slt']),
    					$rightcall['list']);?>
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

<div id="sb-part-dialaction" class="b-nodisplay">
	<fieldset id="fld-dialaction-noanswer">
		<legend><?=$this->bbf('fld-dialaction-noanswer');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'noanswer'));
?>
	</fieldset>

	<fieldset id="fld-dialaction-busy">
		<legend><?=$this->bbf('fld-dialaction-busy');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'busy'));
?>
	</fieldset>

	<fieldset id="fld-dialaction-congestion">
		<legend><?=$this->bbf('fld-dialaction-congestion');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'congestion'));
?>
	</fieldset>

	<fieldset id="fld-dialaction-chanunavail">
		<legend><?=$this->bbf('fld-dialaction-chanunavail');?></legend>
<?php
		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'chanunavail'));
?>
	</fieldset>
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
		echo $form->select(array('desc'	=> $this->bbf('fm_group_schedule'),
				    'name'	    => 'schedule_id',
				    'labelid'	  => 'schedule_id',
						'key'	      => 'name',
						'altkey'    => 'id',
						'empty'     => true,
				    'selected'	=> $this->get_var('schedule_id')),
			      $schedules);
	endif;
?>
</div>
