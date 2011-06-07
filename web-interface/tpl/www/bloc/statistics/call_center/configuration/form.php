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
#

$form = &$this->get_module('form');
$url = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

$listqos = $this->get_var('listqos');
$incall = $this->get_var('incall');
$queue = $this->get_var('queue');
$group = $this->get_var('group');
$agent = $this->get_var('agent');
$user = $this->get_var('user');
$info = $this->get_var('info');
$element = $this->get_var('element');

if($this->get_var('fm_save') === false)
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');

?>
<script type="text/javascript">
	var listqos = new Object();
<?php
if (is_null($listqos) === false
&& empty($listqos) === false)
	foreach($listqos as $k => $v)
		echo "listqos[$k] = $v;\n";
?>
	var translation = new Object();
	translation['queue'] = '<?=addslashes($this->bbf('queue'))?>';
	translation['group'] = '<?=addslashes($this->bbf('group'))?>';
</script>
				
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
				  'error'	=> $this->bbf_args('error',$this->get_var('error','stats_conf','name')) ));

	echo	$form->text(array('desc'	=> $this->bbf('fm_default_delta'),
				  'name'	=> 'stats_conf[default_delta]',
				  'labelid'	=> 'name',
				  'size'	=> 12,
				  'help'	=> $this->bbf('hlp_fm_default_delta'),
				  'default'	=> $element['stats_conf']['default_delta']['default'],
				  'value'	=> $info['stats_conf']['default_delta'],
				  'error'	=> $this->bbf_args('error',$this->get_var('error','stats_conf','default_delta')) ));
	
	echo	$form->checkbox(array('desc' => $this->bbf('fm_conf_homepage'),
				  'name'	=> 'stats_conf[homepage]',
				  'labelid'	=> 'homepage',
				  'checked'	=> $info['stats_conf']['homepage']));
?>
			<fieldset id="stats_conf_cache_period">
				<legend><?=$this->bbf('cache_during_period');?></legend>
						<p>
							<label id="lb-description" for="it-description"><?=$this->bbf('fm_description_cache');?></label>
						</p>
<?php
		echo	$form->text(array('desc'	=> $this->bbf('fm_dbegcache'),
					  'name'	=> 'stats_conf[dbegcache]',
					  'labelid'	=> 'name',
					  'size'	=> 6,
					  'default'	=> $element['stats_conf']['dbegcache']['default'],
					  'value'	=> $info['stats_conf']['dbegcache'],
					  'error'	=> $this->bbf_args('error',$this->get_var('error','stats_conf','dbegcache')) ));

		echo	$form->text(array('desc'	=> $this->bbf('fm_dendcache'),
					  'name'	=> 'stats_conf[dendcache]',
					  'labelid'	=> 'name',
					  'size'	=> 6,
					  'help'	=> $this->bbf('hlp_fm_dendcache'),
					  'default'	=> $element['stats_conf']['dendcache']['default'],
					  'value'	=> $info['stats_conf']['dendcache'],
					  'error'	=> $this->bbf_args('error',$this->get_var('error','stats_conf','dendcache')) ));
?>
			</fieldset>
			<fieldset id="stats_conf_workhour">
				<legend><?=$this->bbf('stats_conf_workhour');?></legend>
<?php
    echo $form->text(array('desc'	=> $this->bbf('fm_hour_start'),
    				  'name'	    => 'stats_conf[hour_start]',
    				  'labelid'	    => 'stats_conf-hour_start',
    				  'size'	    => 5,
    				  'readonly'	=> true,
    				  'value'	    => $this->get_var('info','stats_conf','hour_start'),
    				  'error'	    => $this->bbf_args('error',
    				$this->get_var('error', 'stats_conf', 'hour_start'))));
    				
    echo $form->text(array('desc'	=> $this->bbf('fm_hour_end'),
    				  'name'	    => 'stats_conf[hour_end]',
    				  'labelid'	    => 'stats_conf-hour_end',
    				  'size'	    => 5,
    				  'readonly'	=> true,
    				  'value'	    => $this->get_var('info','stats_conf','hour_end'),
    				  'error'	    => $this->bbf_args('error',
    				$this->get_var('error', 'stats_conf', 'hour_end'))));
?>
			</fieldset>
			<fieldset id="stats_conf_period">
				<legend><?=$this->bbf('stats_conf_period');?></legend>
<?php
	for($i=1;$i<6;$i++):

	echo	$form->text(array('desc'	=> $this->bbf('fm_period'.$i),
					  'name'	=> 'stats_conf[period'.$i.']',
					  'labelid'	=> 'period'.$i,
					  'size'	=> 5,
					  'help'		=> $this->bbf('hlp_fm_period'),
					  'required'	=> false,
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
						   $info['stats_conf']['description']);?>
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

			<div id="sb-part-incall" class="b-nodisplay">
<?php
	if(isset($incall['list']) === true
	&& $incall['list'] !== false):
?>
        <div id="incalllist" class="fm-paragraph fm-description">
        		<?=$form->jq_select(array('paragraph'	=> false,
        					 	'label'		=> false,
                    			'name'    	=> 'incall[]',
        						'id' 		=> 'it-incall',
        						'key'		=> 'identity',
        				       	'altkey'	=> 'id',
                    			'selected'  => $incall['slt']),
        					$incall['list']);?>
        </div>
        <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_incall'),
					'service/ipbx/call_center/incalls',
					'act=add'),
			'</div>';
	endif;
?>
			</div>

			<div id="sb-part-queue" class="b-nodisplay">

			<fieldset>
			<legend><?=$this->bbf('queue')?></legend>
<?php
	if(isset($queue['list']) === true
	&& $queue['list'] !== false):
?>
        <div id="queuelist" class="fm-paragraph fm-description">
        		<?=$form->jq_select(array('paragraph'	=> false,
        					 	'label'		=> false,
                    			'name'    	=> 'queue[]',
        						'id' 		=> 'it-queue',
        						'key'		=> 'identity',
        				       	'altkey'	=> 'id',
                    			'selected'  => $queue['slt']),
        					$queue['list']);?>
        </div>
        <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_queue'),
					'service/ipbx/call_center/queues',
					'act=add'),
			'</div>';
	endif;
?>
			</fieldset>
			<fieldset>
			<legend><?=$this->bbf('group')?></legend>
<?php
	if(isset($group['list']) === true
	&& $group['list'] !== false):
?>
        <div id="grouplist" class="fm-paragraph fm-description">
        		<?=$form->jq_select(array('paragraph'	=> false,
        					 	'label'		=> false,
                    			'name'    	=> 'group[]',
        						'id' 		=> 'it-group',
        						'key'		=> 'identity',
        				       	'altkey'	=> 'id',
                    			'selected'  => $group['slt']),
        					$group['list']);?>
        </div>
        <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_group'),
					'service/ipbx/pbx_settings/groups',
					'act=add'),
			'</div>';
	endif;
?>
			</fieldset>
			</div>

			<div id="sb-part-qos" class="b-nodisplay">
				<p class="txt-center">
					<label id="lb-description" for="it-description"><?=$this->bbf('fm_description_stats_queue_qos');?></label>
				</p>
				<div id="it-listqueueqos"></div>
				<div id="it-listgroupqos"></div>
			</div>

			<div id="sb-part-last" class="b-nodisplay">

			<fieldset>
			<legend><?=$this->bbf('agent')?></legend>
<?php
	if($agent['list'] !== false):
?>
        <div id="agentlist" class="fm-paragraph fm-description">
        		<?=$form->jq_select(array('paragraph'	=> false,
        					 	'label'		=> false,
                    			'name'    	=> 'agent[]',
        						'id' 		=> 'it-agent',
        						'key'		=> 'identity',
        				       	'altkey'	=> 'id',
                    			'selected'  => $agent['slt']),
        					$agent['list']);?>
        </div>
        <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_agent'),
					'service/ipbx/call_center/agents',
					'act=add'),
			'</div>';
	endif;
?>
			</fieldset>
			<fieldset>
			<legend><?=$this->bbf('user')?></legend>
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
					'service/ipbx/pbx_settings/users',
					'act=add'),
			'</div>';
	endif;
?>
</fieldset>
			</div>