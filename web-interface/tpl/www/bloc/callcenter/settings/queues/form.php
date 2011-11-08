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

$element         = $this->get_var('element');
$info            = $this->get_var('info');
$user            = $this->get_var('user');
$agentgroup      = $this->get_var('agentgroup');
$agent           = $this->get_var('agent');
$pannounce       = $this->get_var('pannounce');
$moh_list        = $this->get_var('moh_list');
$announce_list   = $this->get_var('announce_list');
$context_list    = $this->get_var('context_list');
$schedules       = $this->get_var('schedules');
$defaultrules    = $this->get_var('defaultrules');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_queuefeatures_name'),
				  'name'	=> 'queuefeatures[name]',
				  'labelid' => 'queuefeatures-name',
				  'size'	=> 15,
				  'default'	=> $element['queuefeatures']['name']['default'],
				  'value'	=> $this->get_var('info','queuefeatures','name'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queuefeatures','name')))),

		$form->text(array('desc'	=> $this->bbf('fm_queuefeatures_displayname'),
				  'name'	=> 'queuefeatures[displayname]',
				  'labelid' => 'queuefeatures-displayname',
				  'size'	=> 15,
				  'default'	=> $element['queuefeatures']['displayname']['default'],
				  'value'	=> $this->get_var('info','queuefeatures','displayname'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queuefeatures','displayname')))),

		$form->text(array('desc'	=> $this->bbf('fm_queuefeatures_number'),
				  'name'	=> 'queuefeatures[number]',
				  'labelid' => 'queuefeatures-number',
				  'size'	=> 15,
				  'default'	=> $element['queuefeatures']['number']['default'],
				  'value'	=> $this->get_var('info','queuefeatures','number'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queuefeatures','number')))),

		$form->select(array('desc'	=> $this->bbf('fm_queue_strategy'),
				    'name'	=> 'queue[strategy]',
				    'labelid' => 'queue-strategy',
						'help' => $this->bbf('hlp_fm_queue-strategy'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_strategy-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['strategy']['default'],
				    'selected'	=> $this->get_var('info','queue','strategy')),
			      $element['queue']['strategy']['value']);

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_queuefeatures_context'),
				    'name'	=> 'queuefeatures[context]',
				    'labelid' => 'queuefeatures-context',
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['queuefeatures']['context']['default'],
				    'selected'	=> $this->get_var('info','queuefeatures','context')),
			      $context_list);
else:
	echo	'<div id="fd-queuefeatures-context" class="txt-center">',
		$url->href_htmln($this->bbf('create_context'),
				'service/ipbx/system_management/context',
				'act=add'),
		'</div>';
endif;

if($moh_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_queue_musicclass'),
				    'name'	=> 'queue[musicclass]',
				    'labelid' => 'queue-musicclass',
						'help' => $this->bbf('hlp_fm_queue-musicclass'),
				    'empty'	=> true,
				    'key'	=> 'category',
				    'invalid'	=> ($this->get_var('act') === 'edit'),
				    'default'	=> ($this->get_var('act') === 'add' ? $element['queue']['musicclass']['default'] : null),
				    'selected'	=> $this->get_var('info','queue','musicclass')),
			      $moh_list);
endif;

if($announce_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_queue_announce'),
				    'name'	=> 'queue[announce]',
				    'labelid' => 'queue-announce',
						'help' => $this->bbf('hlp_fm_queue-announce'),
				    'empty'	=> true,
				    'default'	=> $element['queue']['announce']['default'],
				    'selected'	=> $this->get_var('info','queue','announce')),
			      $announce_list);
else:
	echo	'<div class="txt-center">',
		$url->href_htmln($this->bbf('add_announce'),
				'service/ipbx/pbx_services/sounds',
				array('act'	=> 'list',
				      'dir'	=> 'acd')),
		'</div>';
endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_callerid_mode'),
				    'name'	=> 'callerid[mode]',
				    'labelid' => 'callerid-mode',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_callerid_mode-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['callerid']['mode']['default'],
				    'selected'	=> $this->get_var('info','callerid','mode')),
			      $element['callerid']['mode']['value'],
			      'onchange="xivo_ast_chg_callerid_mode(this);"'),

		$form->text(array('desc'	=> '&nbsp;',
				  'name'	=> 'callerid[callerdisplay]',
				  'labelid' => 'callerid-callerdisplay',
				  'size'	=> 15,
				  'notag'	=> false,
				  'default'	=> $element['callerid']['callerdisplay']['default'],
				  'value'	=> $this->get_var('info','callerid','callerdisplay'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','callerid','callerdisplay')))),

		$form->text(array('desc'	=> $this->bbf('fm_queuefeatures_preprocess-subroutine'),
				  'name'	=> 'queuefeatures[preprocess_subroutine]',
				  'labelid' => 'queuefeatures-preprocess-subroutine',
				  'size'	=> 15,
				  'default'	=> $element['queuefeatures']['preprocess_subroutine']['default'],
				  'value'	=> $this->get_var('info','queuefeatures','preprocess_subroutine'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queuefeatures','preprocess_subroutine'))));
?>
</div>

<div id="sb-part-announce" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_queue_announce-frequency'),
				    'name'	=> 'queue[announce-frequency]',
				    'labelid' => 'queue-announce-frequency',
						'help' => $this->bbf('hlp_fm_queue-announce-frequency'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_announce-frequency-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'default'	=> $element['queue']['announce-frequency']['default'],
				    'selected'	=> $this->get_var('info','queue','announce-frequency')),
			      $element['queue']['announce-frequency']['value']),

     $form->select(array('desc'  => $this->bbf('fm_queue_min-announce-frequency'),
            'name'    => 'queue[min-announce-frequency]',
            'labelid' => 'queue-min-announce-frequency',
						'help' => $this->bbf('hlp_fm_queue-min-announce-frequency'),
            'key'     => false,
            'bbf'     => 'time-opt',
            'bbfopt'  => array('argmode' => 'paramvalue',
                 'time' => array('from'=>'second', 'format'=>'%M%s')),
            'help'    => $this->bbf('hlp_fm_queue_min-announce-frequency'),
            'selected'  => $this->get_var('info','queue','min-announce-frequency'),
            'default' => $element['queue']['min-announce-frequency']['default']),
         $element['queue']['min-announce-frequency']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_announce-holdtime'),
				    'name'	=> 'queue[announce-holdtime]',
				    'labelid' => 'queue-announce-holdtime',
						'help' => $this->bbf('hlp_fm_queue-announce-holdtime'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_announce-holdtime-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['announce-holdtime']['default'],
				    'selected'	=> $this->get_var('info','queue','announce-holdtime')),
				$element['queue']['announce-holdtime']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_announce_holdtime'),
				      'name'	=> 'queuefeatures[announce_holdtime]',
				      'labelid' => 'queuefeatures-announce_holdtime',
				      'default'	=> $element['queuefeatures']['announce_holdtime']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','announce_holdtime'))),

		$form->select(array('desc'	=> $this->bbf('fm_queue_announce-round-seconds'),
				    'name'	=> 'queue[announce-round-seconds]',
				    'labelid' => 'queue-announce-round-seconds',
					'help' => $this->bbf('hlp_fm_queue-announce-round-seconds'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_announce-round-seconds-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['announce-round-seconds']['default'],
				    'selected'	=> $this->get_var('info','queue','announce-round-seconds')),
			      $element['queue']['announce-round-seconds']['value']),

     $form->select(array('desc'  => $this->bbf('fm_queue_announce-position'),
            'name'    => 'queue[announce-position]',
            'labelid' => 'queue-announce-position',
					'help' => $this->bbf('hlp_fm_queue-announce-position'),
            'key'   => false,
            'bbf'   => 'fm_queue_announce-position-opt',
            'bbfopt'  => array('argmode' => 'paramvalue'),
            'help'    => $this->bbf('hlp_fm_queue_announce-position'),
            'selected'  => $this->get_var('info','queue','announce-position'),
            'default' => $element['queue']['announce-position']['default']),
         $element['queue']['announce-position']['value']),

    $form->select(array('desc'  => $this->bbf('fm_queue_announce-position-limit'),
            'name'     => 'queue[announce-position-limit]',
            'labelid' => 'queue-announce-position-limit',
					'help' => $this->bbf('hlp_fm_queue-announce-position-limit'),
            'key'      => false,
            'help'     => $this->bbf('hlp_fm_queue_announce-position-limit'),
            'selected' => $this->get_var('info','queue','announce-position-limit'),
            'default'  => $element['queue']['announce-position-limit']['default']),
        $element['queue']['announce-position-limit']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-youarenext'),
				    'name'	=> 'queue[queue-youarenext]',
				    'labelid' => 'queue-queue-youarenext',
					'help' => $this->bbf('hlp_fm_queue-queue-youarenext'),
				    'empty'	=> $this->bbf('fm_queue_queue-youarenext-opt','default'),
				    'default'	=> $element['queue']['queue-youarenext']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-youarenext')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-thereare'),
				    'name'	=> 'queue[queue-thereare]',
				    'labelid' => 'queue-queue-thereare',
					'help' => $this->bbf('hlp_fm_queue-queue-thereare'),
				    'empty'	=> $this->bbf('fm_queue_queue-thereare-opt','default'),
				    'default'	=> $element['queue']['queue-thereare']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-thereare')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-callswaiting'),
				    'name'	=> 'queue[queue-callswaiting]',
				    'labelid' => 'queue-queue-callswaiting',
					'help' => $this->bbf('hlp_fm_queue-queue-callswaiting'),
				    'empty'	=> $this->bbf('fm_queue_queue-callswaiting-opt','default'),
				    'default'	=> $element['queue']['queue-callswaiting']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-callswaiting')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-holdtime'),
				    'name'	=> 'queue[queue-holdtime]',
				    'labelid' => 'queue-queue-holdtime',
					'help' => $this->bbf('hlp_fm_queue-queue-holdtime'),
				    'empty'	=> $this->bbf('fm_queue_queue-holdtime-opt','default'),
				    'default'	=> $element['queue']['queue-holdtime']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-holdtime')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-minutes'),
				    'name'	=> 'queue[queue-minutes]',
				    'labelid' => 'queue-queue-minutes',
					'help' => $this->bbf('hlp_fm_queue-queue-minutes'),
				    'empty'	=> $this->bbf('fm_queue_queue-minutes-opt','default'),
				    'default'	=> $element['queue']['queue-minutes']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-minutes')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-seconds'),
				    'name'	=> 'queue[queue-seconds]',
				    'labelid' => 'queue-queue-seconds',
					'help' => $this->bbf('hlp_fm_queue-queue-seconds'),
				    'empty'	=> $this->bbf('fm_queue_queue-seconds-opt','default'),
				    'default'	=> $element['queue']['queue-seconds']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-seconds')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-thankyou'),
				    'name'	=> 'queue[queue-thankyou]',
				    'labelid' => 'queue-queue-thankyou',
					'help' => $this->bbf('hlp_fm_queue-queue-thankyou'),
				    'empty'	=> $this->bbf('fm_queue_queue-thankyou-opt','default'),
				    'default'	=> $element['queue']['queue-thankyou']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-thankyou')),
			      $announce_list),

		$form->select(array('desc'	=> $this->bbf('fm_queue_queue-reporthold'),
				    'name'	=> 'queue[queue-reporthold]',
				    'labelid' => 'queue-queue-reporthold',
					'help' => $this->bbf('hlp_fm_queue-queue-reporthold'),
				    'empty'	=> $this->bbf('fm_queue_queue-reporthold-opt','default'),
				    'default'	=> $element['queue']['queue-reporthold']['default'],
				    'selected'	=> $this->get_var('info','queue','queue-reporthold')),
			      $announce_list);

	if(empty($announce_list) === false):
?>
<div id="pannouncelist" class="fm-paragraph fm-multilist">
	<p>
		<label id="lb-pannouncelist" for="it-pannouncelist" onclick="dwho_eid('it-pannouncelist').focus();">
			<?=$this->bbf('fm_queue_periodic-announce');?>
		</label>
	</p>
				<?=$form->input_for_ms('pannouncelist',$this->bbf('ms_seek'))?>
	<div class="slt-outlist">
<?php
		echo	$form->select(array('name'	=> 'pannouncelist',
					    'label'	=> false,
					    'id'	=> 'it-pannouncelist',
					    'multiple'	=> true,
					    'size'	=> 5,
					    'paragraph'	=> false),
				      $pannounce['list']);
?>
	</div>

	<div class="inout-list">
		<a href="#"
		   onclick="dwho.form.move_selected('it-pannouncelist',
						  'it-queue-periodic-announce');
			    return(dwho.dom.free_focus());"
		   title="<?=$this->bbf('bt_inpannounce');?>">
			<?=$url->img_html('img/site/button/arrow-left.gif',
					  $this->bbf('bt_inpannounce'),
					  'class="bt-inlist" id="bt-inpannounce" border="0"');?></a><br />
		<a href="#"
		   onclick="dwho.form.move_selected('it-queue-periodic-announce',
						  'it-pannouncelist');
			    return(dwho.dom.free_focus());"
		   title="<?=$this->bbf('bt_outpannounce');?>">
			<?=$url->img_html('img/site/button/arrow-right.gif',
					  $this->bbf('bt_outpannounce'),
					  'class="bt-outlist" id="bt-outpannounce" border="0"');?></a>
	</div>

	<div class="slt-inlist">
<?php
		echo	$form->select(array('name'	=> 'queue[periodic-announce][]',
					    'label'	=> false,
					    'id'	=> 'it-queue-periodic-announce',
					    'multiple'	=> true,
					    'size'	=> 5,
					    'paragraph'	=> false),
				      $pannounce['slt']);
?>
		<div class="bt-updown">
			<a href="#"
			   onclick="dwho.form.order_selected('it-queue-periodic-announce',1);
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_uppannounce');?>">
				<?=$url->img_html('img/site/button/arrow-up.gif',
						  $this->bbf('bt_uppannounce'),
						  'class="bt-uplist" id="bt-uppannounce" border="0"');?></a><br />
			<a href="#"
			   onclick="dwho.form.order_selected('it-queue-periodic-announce',-1);
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_downpannounce');?>">
				<?=$url->img_html('img/site/button/arrow-down.gif',
						  $this->bbf('bt_downpannounce'),
						  'class="bt-downlist" id="bt-downpannounce" border="0"');?></a>
		</div>
	</div>
</div>
<div class="clearboth"></div>
<?php
	else:
		echo	$form->select(array('desc'	=> $this->bbf('fm_queue_periodic-announce'),
					    'name'	=> 'queue[periodic-announce]',
					    'labelid' => 'queue-periodic-announce',
					'help' => $this->bbf('hlp_fm_queue-periodic-announce'),
					    'empty'	=> $this->bbf('fm_queue_periodic-announce-opt','default'),
					    'default'	=> $element['queue']['periodic-announce']['default']));
	endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_queue_periodic-announce-frequency'),
				    'name'	=> 'queue[periodic-announce-frequency]',
				    'labelid' => 'queue-periodic-announce-frequency',
					'help' => $this->bbf('hlp_fm_queue-periodic-announce-frequency'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_announce-frequency-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'default'	=> $element['queue']['periodic-announce-frequency']['default'],
				    'selected'	=> $this->get_var('info','queue','periodic-announce-frequency')),
			      $element['queue']['periodic-announce-frequency']['value']);

  echo $form->checkbox(array('desc'  => $this->bbf('fm_queue_random-periodic-announce'),
              'name'    => 'queue[random-periodic-announce]',
              'labelid' => 'queue-random-periodic-announce',
					'help' => $this->bbf('hlp_fm_queue-random-periodic-announce'),
              'help'    => $this->bbf('hlp_fm_queue_random-periodic-announce'),
              'checked' => $this->get_var('info','queue','random-periodic-announce'),
              'default' => $element['queue']['random-periodic-announce']['default']));

?>
</div>

<div id="sb-part-member" class="b-nodisplay">
	<fieldset id="fld-user">
		<legend><?=$this->bbf('fld-users');?></legend>
<?php
	if($user['list'] !== false):
?>
    <div id="userlist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'user[]',
    						'id' 		=> 'it-user',
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
					'callcenter/settings/users',
					'act=add'),
			'</div>';
	endif;
?>
	</fieldset>
	<fieldset id="fld-agent">
		<legend><?=$this->bbf('fld-agents');?></legend>
<?php
	if($agentgroup['list'] !== false):
?>
    <div id="agentgrouplist" class="fm-paragraph fm-description">
			<p>
				<label id="lb-agentlist" for="it-agentlist">
					<?=$this->bbf('fm_agentgroup');?>
				</label>
			</p>
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'agentgroup[]',
    						'id' 		=> 'it-agentgroup',
						    'browse'	=> 'agentgroup',
    						'key'		=> 'name',
    				       	'altkey'	=> 'id',
                			'selected'  => $agentgroup['slt']),
    					$agentgroup['list']);?>
    </div>
    <div class="clearboth"></div>
<?php
		if($agent['list'] !== false):
?>
    <div id="agentlist" class="fm-paragraph fm-description">
			<p>
				<label id="lb-agentlist" for="it-agentlist">
					<?=$this->bbf('fm_agent');?>
				</label>
			</p>
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'agent[]',
    						'id' 		=> 'it-agent',
						    'browse'	=> 'agentfeatures',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $agent['slt']),
    					$agent['list']);?>
    </div>
    <div class="clearboth"></div>
<?php
		else:
			echo	'<div id="create-agent" class="txt-center">',
					$url->href_htmln($this->bbf('create_agent'),
							'callcenter/settings/agents',
							'act=addagent'),
				'</div>';
		endif;

	else:
		echo	'<div class="txt-center">',
				$url->href_htmln($this->bbf('create_agent-group'),
						'callcenter/settings/agents',
						'act=add'),
			'</div>';
	endif;
?>
	</fieldset>
</div>

<div id="sb-part-application" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_queuefeatures_timeout'),
				    'name'	=> 'queuefeatures[timeout]',
				    'labelid' => 'queuefeatures-timeout',
				    'key'	=> false,
				    'bbf'	=> 'fm_queuefeatures_timeout-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'default'	=> $element['queuefeatures']['timeout']['default'],
				    'selected'	=> $this->get_var('info','queuefeatures','timeout')),
			      $element['queuefeatures']['timeout']['value']),

     $form->select(array('desc'  => $this->bbf('fm_queue_timeoutpriority'),
            'name'    => 'queue[timeoutpriority]',
            'labelid' => 'queue-timeoutpriority',
					'help' => $this->bbf('hlp_fm_queue-timeoutpriority'),
            'key'   => false,
            'bbf'   => 'fm_queue_timeoutpriority-opt',
            'bbfopt'  => array('argmode' => 'paramvalue'),
            'help'    => $this->bbf('hlp_fm_queue_timeoutpriority'),
            'selected'  => $this->get_var('info','queue','timeoutpriority'),
            'default' => $element['queue']['timeoutpriority']['default']),
         $element['queue']['timeoutpriority']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_data-quality'),
				      'name'	=> 'queuefeatures[data_quality]',
				      'labelid' => 'queuefeatures-data-quality',
				      'default'	=> $element['queuefeatures']['data_quality']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','data_quality'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_hitting-callee'),
				      'name'	=> 'queuefeatures[hitting_callee]',
				      'labelid' => 'queuefeatures-hitting-callee',
				      'default'	=> $element['queuefeatures']['hitting_callee']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','hitting_callee'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_hitting-caller'),
				      'name'	=> 'queuefeatures[hitting_caller]',
				      'labelid' => 'queuefeatures-hitting-caller',
				      'default'	=> $element['queuefeatures']['hitting_caller']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','hitting_caller'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_retries'),
				      'name'	=> 'queuefeatures[retries]',
				      'labelid' => 'queuefeatures-retries',
				      'default'	=> $element['queuefeatures']['retries']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','retries'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_ring'),
				      'name'	=> 'queuefeatures[ring]',
				      'labelid' => 'queuefeatures-ring',
				      'default'	=> $element['queuefeatures']['ring']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','ring'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_transfer-user'),
				      'name'	=> 'queuefeatures[transfer_user]',
				      'labelid' => 'queuefeatures-transfer-user',
				      'default'	=> $element['queuefeatures']['transfer_user']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','transfer_user'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_transfer-call'),
				      'name'	=> 'queuefeatures[transfer_call]',
				      'labelid' => 'queuefeatures-transfer-call',
				      'default'	=> $element['queuefeatures']['transfer_call']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','transfer_call'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_write-caller'),
				      'name'	=> 'queuefeatures[write_caller]',
				      'labelid' => 'queuefeatures-write-caller',
				      'default'	=> $element['queuefeatures']['write_caller']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','write_caller'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queuefeatures_write-calling'),
				      'name'	=> 'queuefeatures[write_calling]',
				      'labelid' => 'queuefeatures-write-calling',
				      'default'	=> $element['queuefeatures']['write_calling']['default'],
				      'checked'	=> $this->get_var('info','queuefeatures','write_calling')));
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

<div id="sb-part-advanced" class="b-nodisplay">
<?php

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_queue_context'),
				    'name'	=> 'queue[context]',
				    'labelid' => 'queue-context',
					'help' => $this->bbf('hlp_fm_queue-context'),
				    'empty'	=> true,
				    'key'	=> 'identity',
				    'altkey'	=> 'name',
				    'default'	=> $element['queue']['context']['default'],
				    'selected'	=> $this->get_var('info','queue','context')),
			      $context_list);
endif;

	echo	$form->text(array('desc'	=> $this->bbf('fm_queue_servicelevel'),
				  'name'	=> 'queue[servicelevel]',
				  'labelid' => 'queue-servicelevel',
					'help' => $this->bbf('hlp_fm_queue-servicelevel'),
				  'size'	=> 15,
				  'default'	=> $element['queue']['servicelevel']['default'],
				  'value'	=> $this->get_var('info','queue','servicelevel'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queue','servicelevel')))),

		$form->select(array('desc'	=> $this->bbf('fm_queue_timeout'),
				    'name'	=> 'queue[timeout]',
				    'labelid' => 'queue-timeout',
					'help' => $this->bbf('hlp_fm_queue-timeout'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_timeout-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'error'	=> $this->get_var('error','queue','timeout'),
				    'default'	=> $element['queue']['timeout']['default'],
				    'selected'	=> $this->get_var('info','queue','timeout')),
			      $element['queue']['timeout']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_retry'),
				    'name'	=> 'queue[retry]',
				    'labelid' => 'queue-retry',
					'help' => $this->bbf('hlp_fm_queue-retry'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_retry-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'error'	=> $this->get_var('error','queue','retry'),
				    'default'	=> $element['queue']['retry']['default'],
				    'selected'	=> $this->get_var('info','queue','retry')),
			      $element['queue']['retry']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_weight'),
				    'name'	=> 'queue[weight]',
				    'labelid' => 'queue-weight',
					'help' => $this->bbf('hlp_fm_queue-weight'),
				    'key'	=> false,
				    'default'	=> $element['queue']['weight']['default'],
				    'error'	=> $this->get_var('error','queue','weight'),
				    'selected'	=> $this->get_var('info','queue','weight')),
			      $element['queue']['weight']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_wrapuptime'),
				    'name'	=> 'queue[wrapuptime]',
				    'labelid' => 'queue-wrapuptime',
					'help' => $this->bbf('hlp_fm_queue-wrapuptime'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_wrapuptime-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'error'	=> $this->get_var('error','queue','warpuptime'),
				    'default'	=> $element['queue']['wrapuptime']['default'],
				    'selected'	=> $this->get_var('info','queue','wrapuptime')),
			      $element['queue']['wrapuptime']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_queue_maxlen'),
				  'name'	=> 'queue[maxlen]',
				  'labelid' => 'queue-maxlen',
					'help' => $this->bbf('hlp_fm_queue-maxlen'),
				  'size'	=> 5,
				  'default'	=> $element['queue']['maxlen']['default'],
				  'value'	=> $this->get_var('info','queue','maxlen'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queue','maxlen')))),

		$form->select(array('desc'	=> $this->bbf('fm_queue_monitor-type'),
				    'name'	=> 'queue[monitor-type]',
				    'labelid' => 'queue-monitor-type',
					'help' => $this->bbf('hlp_fm_queue-monitor-type'),
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_monitor-type-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['monitor-type']['default'],
				    'selected'	=> $this->get_var('info','queue','monitor-type')),
			      $element['queue']['monitor-type']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_queue_monitor-format'),
				    'name'	=> 'queue[monitor-format]',
				    'labelid' => 'queue-monitor-format',
					'help' => $this->bbf('hlp_fm_queue-monitor-format'),
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'ast_format_name_info',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['monitor-format']['default'],
				    'selected'	=> $this->get_var('info','queue','monitor-format')),
			      $element['queue']['monitor-format']['value']),

     $form->jq_select(array('desc'  => $this->bbf('fm_queue_joinempty'),
            'name'    => 'queue[joinempty][]',
						'labelid' => 'queue-joinempty',
						'class'   => 'multiselect',
						'multiple' => true,
						'key'			=> false,
            'selected'  => $this->get_var('info','queue','joinempty'),
            'default' => $element['queue']['joinempty']['default']),
				$element['queue']['joinempty']['value']),

     $form->jq_select(array('desc'  => $this->bbf('fm_queue_leavewhenempty'),
            'name'    => 'queue[leavewhenempty][]',
						'labelid' => 'queue-leavewhenempty',
						'class'   => 'multiselect',
						'multiple' => true,
						'key'   => false,
            'selected'  => $this->get_var('info','queue','leavewhenempty'),
            'default' => $element['queue']['leavewhenempty']['default']),
				$element['queue']['leavewhenempty']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queue_ringinuse'),
				      'name'	=> 'queue[ringinuse]',
				      'labelid' => 'queue-ringinuse',
					'help' => $this->bbf('hlp_fm_queue-ringinuse'),
				      'default'	=> $element['queue']['ringinuse']['default'],
				      'checked'	=> $this->get_var('info','queue','ringinuse'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queue_eventwhencalled'),
				      'name'	=> 'queue[eventwhencalled]',
				      'labelid' => 'queue-eventwhencalled',
					'help' => $this->bbf('hlp_fm_queue-eventwhencalled'),
				      'default'	=> $element['queue']['eventwhencalled']['default'],
				      'checked'	=> $this->get_var('info','queue','eventwhencalled')),
				'disabled="disabled"'),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queue_eventmemberstatus'),
				      'name'	=> 'queue[eventmemberstatus]',
				      'labelid' => 'queue-eventmemberstatus',
					'help' => $this->bbf('hlp_fm_queue-eventmemberstatus'),
				      'default'	=> $element['queue']['eventmemberstatus']['default'],
				      'checked'	=> $this->get_var('info','queue','eventmemberstatus')),
				'disabled="disabled"'),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queue_reportholdtime'),
				      'name'	=> 'queue[reportholdtime]',
				      'labelid' => 'queue-reportholdtime',
					'help' => $this->bbf('hlp_fm_queue-reportholdtime'),
				      'default'	=> $element['queue']['reportholdtime']['default'],
				      'checked'	=> $this->get_var('info','queue','reportholdtime'))),

		$form->select(array('desc'	=> $this->bbf('fm_queue_memberdelay'),
				    'name'	=> 'queue[memberdelay]',
				    'labelid' => 'queue-memberdelay',
					'help' => $this->bbf('hlp_fm_queue-memberdelay'),
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_memberdelay-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['memberdelay']['default'],
				    'selected'	=> $this->get_var('info','queue','memberdelay')),
			      $element['queue']['memberdelay']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_queue_timeoutrestart'),
				      'name'	=> 'queue[timeoutrestart]',
				      'labelid' => 'queue-timeoutrestart',
					'help' => $this->bbf('hlp_fm_queue-timeoutrestart'),
				      'default'	=> $element['queue']['timeoutrestart']['default'],
							'checked' => $this->get_var('info','queue','timeoutrestart')));

		// asterisk 1.8 fields
    echo $form->checkbox(array('desc'  => $this->bbf('fm_queue_autofill'),
              'name'    => 'queue[autofill]',
              'labelid' => 'queue-autofill',
              'help'    => $this->bbf('hlp_fm_queue_autofill'),
              'checked' => $this->get_var('info','queue','autofill'),
              'default' => $element['queue']['autofill']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_queue_autopause'),
              'name'    => 'queue[autopause]',
              'labelid' => 'queue-autopause',
              'help'    => $this->bbf('hlp_fm_queue_autopause'),
              'checked' => $this->get_var('info','queue','autopause'),
              'default' => $element['queue']['autopause']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_queue_setinterfacevar'),
              'name'    => 'queue[setinterfacevar]',
              'labelid' => 'queue-setinterfacevar',
              'help'    => $this->bbf('hlp_fm_queue_setinterfacevar'),
              'checked' => $this->get_var('info','queue','setinterfacevar'),
              'default' => $element['queue']['setinterfacevar']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_queue_setqueueentryvar'),
              'name'    => 'queue[setqueueentryvar]',
              'labelid' => 'queue-setqueueentryvar',
              'help'    => $this->bbf('hlp_fm_queue_setqueueentryvar'),
              'checked' => $this->get_var('info','queue','setqueueentryvar'),
              'default' => $element['queue']['setqueueentryvar']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_queue_setqueuevar'),
              'name'    => 'queue[setqueuevar]',
              'labelid' => 'queue-setqueuevar',
              'help'    => $this->bbf('hlp_fm_queue_setqueuevar'),
              'checked' => $this->get_var('info','queue','setqueuevar'),
              'default' => $element['queue']['setqueuevar']['default'])),

    $form->text(array('desc'  => $this->bbf('fm_queue_membermacro'),
            'name'     => 'queue[membermacro]',
            'labelid'  => 'queue-membermacro',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_queue_membermacro'),
            'required' => false,
            'value'    => $this->get_var('info','queue','membermacro'),
            'default'  => $element['queue']['membermacro']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'membermacro')) )),

		$form->select(array('desc'	=> $this->bbf('fm_queue_defaultrule'),
				    'name'	    => 'queue[defaultrule]',
				    'labelid'	  => 'queue-defaultrule',
						'key'	      => 'name',
						'altkey'    => 'id',
						'empty'     => true,
            'help'     => $this->bbf('hlp_fm_queue_defaultrule'),
				    'selected'	=> $this->get_var('info','queue','defaultrule')),
			$defaultrules);

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
		echo $form->select(array('desc'	=> $this->bbf('fm_queue_schedule'),
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
<div id="sb-part-diversion" class="b-nodisplay">
	<fieldset id="fld-diversion-ctipresence">
		<legend><?=$this->bbf('fld-diversion-ctipresence');?></legend>
<?php
		$this->file_include('bloc/callcenter/settings/queues/ctipresence',
			array('type'	=> 'ctipresence'));
		echo '<br/>';

		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'qctipresence'));
?>
	</fieldset>
	<fieldset id="fld-diversion-nonctipresence">
		<legend><?=$this->bbf('fld-diversion-nonctipresence');?></legend>
<?php
		$this->file_include('bloc/callcenter/settings/queues/ctipresence',
			array('type'	=> 'nonctipresence'));
		echo '<br/>';

		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'qnonctipresence'));
?>
	</fieldset>
	<fieldset id="fld-diversion-waittime">
		<legend><?=$this->bbf('fld-diversion-waittime');?></legend>
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_queuefeatures_waittime'),
				    'name'	=> 'queuefeatures[waittime]',
				    'labelid' => 'queuefeatures-waittime',
						'key'	=> false,
						'empty' => true,
				    'bbf'	=> 'fm_queuefeatures_timeout-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
				    'default'	=> $element['queuefeatures']['waittime']['default'],
				    'selected'	=> $this->get_var('info','queuefeatures','waittime')),
				$element['queuefeatures']['waittime']['value']);

		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'qwaittime'));
?>
	</fieldset>
	<fieldset id="fld-diversion-waitratio">
		<legend><?=$this->bbf('fld-diversion-waitratio');?></legend>
<?php
  echo $form->text(array('desc'  => $this->bbf('fm_queuefeatures_waitratio'),
            'name'     => 'queuefeatures[waitratio]',
            'labelid'  => 'queuefeatures-waitratio',
            'size'     => 15,
            'help'     => $this->bbf('hlp_fm_queuefeatures_waitratio'),
            'required' => false,
            'value'    => $this->get_var('info','queuefeatures','waitratio'),
            'default'  => $element['queuefeatures']['waitratio']['default'],
            'error'    => $this->bbf_args('error',
        $this->get_var('error', 'waitratio')) ));

		$this->file_include('bloc/service/ipbx/asterisk/dialaction/all',
				    array('event'	=> 'qwaitratio'));
?>
	</fieldset>
</div>
