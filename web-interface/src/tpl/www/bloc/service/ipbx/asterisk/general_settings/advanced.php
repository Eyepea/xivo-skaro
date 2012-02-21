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
$dhtml = &$this->get_module('dhtml');

$info    = $this->get_var('info');
$element = $this->get_var('element');
$error = $this->get_var('error');

if(($fm_save = $this->get_var('fm_save')) === true):
	$dhtml->write_js('xivo_form_result(true,\''.$dhtml->escape($this->bbf('fm_success-save')).'\');');
elseif($fm_save === false):
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

$error_js = array();
$error_nb = count($error['generalmeetme']);

for($i = 0;$i < $error_nb;$i++):
	$error_js[] = 'dwho.form.error[\'it-generalmeetme-'.$error['generalmeetme'][$i].'\'] = true;';
endfor;

if(isset($error_js[0]) === true)
	$dhtml->write_js($error_js);

?>
<div class="b-infos b-form">
<h3 class="sb-top xspan">
	<span class="span-left">&nbsp;</span>
	<span class="span-center"><?=$this->bbf('title_content_name');?></span>
	<span class="span-right">&nbsp;</span>
</h3>
<div class="sb-smenu">
	<ul>
		<li id="dwsm-tab-1"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-first');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#first"><?=$this->bbf('smenu_userinternal');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-agents');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#agents"><?=$this->bbf('smenu_agents');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-3"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-queues');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#queues"><?=$this->bbf('smenu_queues');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-4"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-meetme',1);"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#meetme"><?=$this->bbf('smenu_meetme');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-5"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-timezone');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#timezone"><?=$this->bbf('smenu_timezone');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-6"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-dundi',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center">
					<a href="#dundi"><?=$this->bbf('smenu_dundi');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	</ul>
</div>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8">

<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),
		$form->hidden(array('name'	=> 'fm_send',
				    'value'	=> 1));
?>

<div id="sb-part-first" class="b-nodisplay">
	<?=$form->checkbox(array('desc'		=> $this->bbf('fm_userinternal_guest'),
				 'name'		=> 'userinternal[guest]',
				 'labelid'	=> 'userinternal-guest',
				 'help'		=> $this->bbf('hlp_fm_userinternal_guest'),
				 'checked'	=> $this->get_var('info','userinternal','guest')));?>
</div>

<div id="sb-part-agents" class="b-nodisplay">
<?php
		echo $form->checkbox(array('desc'	=> $this->bbf('fm_generalagents_multiplelogin'),
				      'name'	=> 'generalagents[multiplelogin]',
				      'labelid'	=> 'generalagents-multiplelogin',
				      'default'	=> $element['generalagents']['multiplelogin']['default'],
				      'help'	=> $this->bbf('hlp_fm_generalagents_multiplelogin'),
							'checked'	=> $this->get_var('generalagents','multiplelogin','var_val'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_agentoptions_endcall'),
				      'name'	=> 'agentoptions[endcall]',
				      'labelid'	=> 'agentoptions-endcall',
					    'help'	=> $this->bbf('hlp_fm_agentoptions_endcall'),
				      'default'	=> $element['agentoptions']['endcall']['default'],
				      'checked' => $info['agentoptions']['endcall']['var_val'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_agentoptions_autologoffunavail'),
				      'name'	=> 'agentoptions[autologoffunavail]',
				      'labelid'	=> 'agentoptions-autologoffunavail',
					    'help'	=> $this->bbf('hlp_fm_agentoptions_autologoffunavail'),
				      'default'	=> $element['agentoptions']['autologoffunavail']['default'],
				      'checked' => $info['agentoptions']['autologoffunavail']['var_val'])),

		$form->select(array('desc'	=> $this->bbf('fm_agentoptions_maxlogintries'),
				    'name'	=> 'agentoptions[maxlogintries]',
				    'labelid'	=> 'agentoptions-maxlogintries',
				    'key'	=> false,
				    'help'	=> $this->bbf('hlp_fm_agentoptions_maxlogintries'),
				    'bbf'	=> 'fm_agentoptions_maxlogintries-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['agentoptions']['maxlogintries']['default'],
				    'selected'	=> $info['agentoptions']['maxlogintries']['var_val']),
			      $element['agentoptions']['maxlogintries']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_agentoptions_updatecdr'),
				      'name'	=> 'agentoptions[updatecdr]',
				      'labelid'	=> 'agentoptions-updatecdr',
					    'help'	=> $this->bbf('hlp_fm_agentoptions_updatecdr'),
				      'default'	=> $element['agentoptions']['updatecdr']['default'],
				      'checked' => $info['agentoptions']['updatecdr']['var_val'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_agentoptions_recordagentcalls'),
				      'name'	=> 'agentoptions[recordagentcalls]',
				      'labelid'	=> 'agentoptions-recordagentcalls',
					    'help'	=> $this->bbf('hlp_fm_agentoptions_recordagentcalls'),
				      'default'	=> $element['agentoptions']['recordagentcalls']['default'],
				      'checked' => $info['agentoptions']['recordagentcalls']['var_val'])),

		$form->select(array('desc'	=> $this->bbf('fm_agentoptions_recordformat'),
				    'name'	=> 'agentoptions[recordformat]',
				    'labelid'	=> 'agentoptions-recordformat',
				    'key'	=> false,
				    'help'	=> $this->bbf('hlp_fm_agentoptions_recordformat'),
				    'bbf'	=> 'ast_format_name_info',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['agentoptions']['recordformat']['default'],
				    'selected'	=> $info['agentoptions']['recordformat']['var_val']),
			      $element['agentoptions']['recordformat']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_agentoptions_urlprefix'),
				  'name'	=> 'agentoptions[urlprefix]',
				  'labelid'	=> 'agentoptions-urlprefix',
				  'size'	=> 15,
			    'help'	=> $this->bbf('hlp_fm_agentoptions_urlprefix'),
				  'default'	=> $element['agentoptions']['urlprefix']['default'],
				  'value'	=> $info['agentoptions']['urlprefix']['var_val'])),

		$form->text(array('desc'	=> $this->bbf('fm_agentoptions_savecallsin'),
				  'name'	=> 'agentoptions[savecallsin]',
				  'labelid'	=> 'agentoptions-savecallsin',
				  'size'	=> 15,
			    'help'	=> $this->bbf('hlp_fm_agentoptions_savecallsin'),
				  'default'	=> $element['agentoptions']['savecallsin']['default'],
				  'value'	=> $info['agentoptions']['savecallsin']['var_val'])),

		$form->select(array('desc'	=> $this->bbf('fm_agentoptions_custom_beep'),
				    'name'	=> 'agentoptions[custom_beep]',
				    'labelid'	=> 'agentoptions-custom-beep',
				    'help'	=> $this->bbf('hlp_fm_agentoptions_custom_beep'),
				    'empty'	=> $this->bbf('fm_agentoptions_custom-beep-opt','default'),
				    'default'	=> $element['agentoptions']['custom_beep']['default'],
				    'selected'	=> $info['agentoptions']['custom_beep']['var_val']),
			      $this->get_var('beep_list')),

		$form->select(array('desc'	=> $this->bbf('fm_agentoptions_goodbye'),
				    'name'	=> 'agentoptions[goodbye]',
				    'labelid'	=> 'agentoptions-goodbye',
				    'help'	=> $this->bbf('hlp_fm_agentoptions_goodbye'),
				    'empty'	=> $this->bbf('fm_agentoptions_goodbye-opt','default'),
				    'default'	=> $element['agentoptions']['goodbye']['default'],
				    'selected'	=> $info['agentoptions']['goodbye']['var_val']),
			      $this->get_var('goodbye_list'));
?>
</div>

<div id="sb-part-queues" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_generalqueues_persistentmembers'),
				      'name'	=> 'generalqueues[persistentmembers]',
				      'labelid'	=> 'generalqueues-persistentmembers',
				      'default'	=> $element['generalqueues']['persistentmembers']['default'],
				      'help'	=> $this->bbf('hlp_fm_generalqueues_persistentmembers'),
				      'checked'	=> $this->get_var('generalqueues','persistentmembers','var_val'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_generalqueues_autofill'),
				      'name'	=> 'generalqueues[autofill]',
				      'labelid'	=> 'generalqueues-autofill',
				      'default'	=> $element['generalqueues']['autofill']['default'],
				      'help'	=> $this->bbf('hlp_fm_generalqueues_autofill'),
				      'checked'	=> $this->get_var('generalqueues','autofill','var_val'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_generalqueues_monitor-type'),
				      'name'	=> 'generalqueues[monitor-type]',
				      'labelid'	=> 'generalqueues-monitor-type',
				      'default'	=> $element['generalqueues']['monitor-type']['default'],
				      'help'	=> $this->bbf('hlp_fm_generalqueues_monitor-type'),
							'checked'	=> $this->get_var('generalqueues','monitor-type','var_val'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_generalqueues_updatecdr'),
				      'name'	=> 'generalqueues[updatecdr]',
				      'labelid'	=> 'generalqueues-updatecdr',
				      'default'	=> $element['generalqueues']['updatecdr']['default'],
				      'help'	=> $this->bbf('hlp_fm_generalqueues_updatecdr'),
				      'checked'	=> $this->get_var('generalqueues','updatecdr','var_val'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_generalqueues_shared_lastcall'),
				      'name'	=> 'generalqueues[shared_lastcall]',
				      'labelid'	=> 'generalqueues-shared_lastcall',
				      'default'	=> $element['generalqueues']['shared_lastcall']['default'],
				      'help'	=> $this->bbf('hlp_fm_generalqueues_shared_lastcall'),
				      'checked'	=> $this->get_var('generalqueues','shared_lastcall','var_val')));

?>
</div>

<div id="sb-part-meetme" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_generalmeetme_audiobuffers'),
				    'name'	=> 'generalmeetme[audiobuffers]',
				    'labelid'	=> 'generalmeetme-audiobuffers',
				    'key'	=> false,
				    'default'	=> $element['generalmeetme']['audiobuffers']['default'],
				    'help'	=> $this->bbf('hlp_fm_generalmeetme_audiobuffers'),
				    'selected'	=> $this->get_var('generalmeetme','audiobuffers','var_val')),
			      $element['generalmeetme']['audiobuffers']['value']),

    $form->checkbox(array('desc'  => $this->bbf('fm_generalmeetme_schedule'),
              'name'    => 'generalmeetme[schedule]',
              'labelid' => 'generalmeetme-schedule',
              'help'    => $this->bbf('hlp_fm_generalmeetme_schedule'),
              'checked' => $this->get_var('generalmeetme','schedule','var_val'),
              'default' => $element['generalmeetme']['schedule']['default'])),

    $form->checkbox(array('desc'  => $this->bbf('fm_generalmeetme_logmembercount'),
              'name'    => 'generalmeetme[logmembercount]',
              'labelid' => 'generalmeetme-logmembercount',
              'help'    => $this->bbf('hlp_fm_generalmeetme_logmembercount'),
              'checked' => $this->get_var('generalmeetme','logmembercount','var_val'),
              'default' => $element['generalmeetme']['logmembercount']['default'])),

     $form->select(array('desc'  => $this->bbf('fm_generalmeetme_fuzzystart'),
            'name'    => 'generalmeetme[fuzzystart]',
            'labelid' => 'generalmeetme-fuzzystart',
            'key'     => false,
            'bbf'     => 'time-opt',
            'bbfopt'  => array('argmode' => 'paramvalue',
                 'time' => array('from'=>'second', 'format'=>'%M%s')),
            'help'    => $this->bbf('hlp_fm_generalmeetme_fuzzystart'),
            'selected'  => $this->get_var('generalmeetme','fuzzystart','var_val'),
            'default' => $element['generalmeetme']['fuzzystart']['default']),
         $element['generalmeetme']['fuzzystart']['value']),

     $form->select(array('desc'  => $this->bbf('fm_generalmeetme_earlyalert'),
            'name'    => 'generalmeetme[earlyalert]',
            'labelid' => 'generalmeetme-earlyalert',
            'key'     => false,
            'bbf'     => 'time-opt',
            'bbfopt'  => array('argmode' => 'paramvalue',
                 'time' => array('from'=>'second', 'format'=>'%M%s')),
            'help'    => $this->bbf('hlp_fm_generalmeetme_earlyalert'),
            'selected'  => $this->get_var('generalmeetme','earlyalert','var_val'),
            'default' => $element['generalmeetme']['earlyalert']['default']),
         $element['generalmeetme']['earlyalert']['value']),

     $form->select(array('desc'  => $this->bbf('fm_generalmeetme_endalert'),
            'name'    => 'generalmeetme[endalert]',
            'labelid' => 'generalmeetme-endalert',
            'key'     => false,
            'bbf'     => 'time-opt',
            'bbfopt'  => array('argmode' => 'paramvalue',
                 'time' => array('from'=>'second', 'format'=>'%M%s')),
            'help'    => $this->bbf('hlp_fm_generalmeetme_endalert'),
            'selected'  => $this->get_var('generalmeetme','endalert','var_val'),
            'default' => $element['generalmeetme']['endalert']['default']),
         $element['generalmeetme']['endalert']['value']);
?>
</div>

<div id="sb-part-timezone" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_general_timezone'),
				    'name'     => 'general[timezone]',
				    'labelid'  => 'general-timezone',
				    'key'      => false,
				    //'default'  => $element['general']['timezone']['default'],
				    'help'     => $this->bbf('hlp_fm_general_timezone'),
				    'selected' => $this->get_var('general','timezone')),
			      $element['general']);
?>
</div>

<div id="sb-part-dundi" class="b-nodisplay">
<?php
		echo $form->checkbox(array('desc'	=> $this->bbf('fm_general_dundi'),
				  	'name'		  => 'general[dundi]',
						'labelid'	  => 'general-dundi',
					  'help'	  	=> $this->bbf('hlp_fm_general-dundi'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','general','dundi'),
			      'default'		=> $this->get_var('elements','generaldundi','dundi','default')));
?>
</div>

<?php
	echo	$form->submit(array('name'	=> 'submit',
				    'id'	=> 'it-submit',
				    'value'	=> $this->bbf('fm_bt-save')));
?>
</form>

	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
