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

$info    = $this->get_var('info');
$error   = $this->get_var('error');
$element = $this->get_var('element');

$voicemail_list = $this->get_var('voicemail_list');
$agent_list = $this->get_var('agent_list');
$profileclient_list = $this->get_var('profileclient_list');
$rightcall = $this->get_var('rightcall');
$schedules    = $this->get_var('schedules');
$parking_list = $this->get_var('parking_list');

if(empty($info['userfeatures']['voicemailid']) === true):
	$voicemail_identity = false;
elseif(($voicemail_identity = (string) $this->get_var('voicemail','identity')) === ''):
	$voicemail_identity = $this->get_var('voicemail','fullname');
endif;

if(($outcallerid = (string) $info['userfeatures']['outcallerid']) === ''
|| in_array($outcallerid,$element['userfeatures']['outcallerid']['value'],true) === true):
	$outcallerid_custom = false;
else:
	$outcallerid_custom = true;
endif;

$line_nb = 0;
$line_list = false;

if(dwho_issa('linefeatures',$info) === true):
	$context_js = array();

	if(($line_nb = count($info['linefeatures'])) > 0):
		$line_list = $info['linefeatures'];
		$context_js[] = 'dwho.dom.set_table_list(\'operator_line\','.$line_nb.');';
	endif;

	if(isset($context_js[0]) === true):
		$dhtml = &$this->get_module('dhtml');
		$dhtml->write_js($context_js);
	endif;
endif;

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_userfeatures_firstname'),
				  'name'	=> 'userfeatures[firstname]',
				  'labelid'	=> 'userfeatures-firstname',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['firstname']['default'],
				  'value'	=> $info['userfeatures']['firstname'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'firstname')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_lastname'),
				  'name'	=> 'userfeatures[lastname]',
				  'labelid'	=> 'userfeatures-lastname',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['lastname']['default'],
				  'value'	=> $info['userfeatures']['lastname'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'lastname')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_loginclient'),
				  'name'	=> 'userfeatures[loginclient]',
				  'labelid'	=> 'userfeatures-loginclient',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['loginclient']['default'],
				  'value'	=> $info['userfeatures']['loginclient'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'loginclient')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_passwdclient'),
				  'name'	=> 'userfeatures[passwdclient]',
				  'labelid'	=> 'userfeatures-passwdclient',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['passwdclient']['default'],
				  'value'	=> $info['userfeatures']['passwdclient'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'passwdclient')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_mobilephonenumber'),
				  'name'	=> 'userfeatures[mobilephonenumber]',
				  'labelid'	=> 'userfeatures-mobilephonenumber',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['mobilephonenumber']['default'],
				  'value'	=> $info['userfeatures']['mobilephonenumber'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'mobilephonenumber')) ));

	if($schedules === false):
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_schedules'),
					'service/ipbx/call_management/schedule',
					'act=add'),
			'</div>';
	else:
		echo $form->select(array('desc'	=> $this->bbf('fm_user_schedule'),
				    'name'	    => 'schedule_id',
				    'labelid'	  => 'schedule_id',
						'key'	      => 'name',
						'altkey'    => 'id',
						'empty'     => true,
				    'selected'	=> $this->get_var('schedule_id')),
			      $schedules);
	endif;


		echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_ringseconds'),
				    'name'	=> 'userfeatures[ringseconds]',
				    'labelid'	=> 'userfeatures-ringseconds',
				    'key'	=> false,
				    'bbf'	=> 'fm_userfeatures_ringseconds-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['userfeatures']['ringseconds']['default'],
				    'selected'	=> $info['userfeatures']['ringseconds']),
			      $element['userfeatures']['ringseconds']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_userfeatures_simultcalls'),
				    'name'	=> 'userfeatures[simultcalls]',
				    'labelid'	=> 'userfeatures-simultcalls',
				    'key'	=> false,
				    'default'	=> $element['userfeatures']['simultcalls']['default'],
				    'selected'	=> $info['userfeatures']['simultcalls']),
			      $element['userfeatures']['simultcalls']['value']);

	if(($moh_list = $this->get_var('moh_list')) !== false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_musiconhold'),
					    'name'	=> 'userfeatures[musiconhold]',
					    'labelid'	=> 'userfeatures-musiconhold',
					    'empty'	=> true,
					    'key'	=> 'category',
					    'invalid'	=> ($this->get_var('act') === 'edit'),
					    'default'	=> ($this->get_var('act') === 'add' ? $element['userfeatures']['musiconhold']['default'] : null),
					    'selected'	=> $info['userfeatures']['musiconhold']),
				      $moh_list);
	endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_language'),
				    'name'	=> 'userfeatures[language]',
				    'labelid'	=> 'userfeatures-language',
				    'empty'	=> true,
				    'key'	=> false,
				    'default'	=> $element['userfeatures']['language']['default'],
				    'selected'	=> $this->get_var('info','userfeatures','language')),
			      $element['userfeatures']['language']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_userfeatures_timezone'),
				    'name'	=> 'userfeatures[timezone]',
				    'labelid'	=> 'userfeatures-timezone',
				    'empty'	=> true,
				    'key'	=> false,
# no default value => take general value
#				    'default'		=> $element['userfeatures']['timezone']['default'],
				    'selected'	=> $this->get_var('info','userfeatures','timezone')),
			      array_keys(dwho_i18n::get_timezone_list())),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_callerid'),
				  'name'	=> 'userfeatures[callerid]',
				  'labelid'	=> 'userfeatures-callerid',
				  'value'	=> $this->get_var('info','userfeatures','callerid'),
				  'size'	=> 15,
				  'notag'	=> false,
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'callerid')) )),

		$form->select(array('desc'	=> $this->bbf('fm_userfeatures_outcallerid'),
				    'name'	=> 'userfeatures[outcallerid-type]',
				    'labelid'	=> 'userfeatures-outcallerid-type',
				    'key'	=> false,
				    'bbf'	=> 'fm_userfeatures_outcallerid-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> ($outcallerid_custom === true ? 'custom' : $outcallerid)),
			      $element['userfeatures']['outcallerid-type']['value']),

		$form->text(array('desc'	=> '&nbsp;',
				  'name'	=> 'userfeatures[outcallerid-custom]',
				  'labelid'	=> 'userfeatures-outcallerid-custom',
				  'value'	=> ($outcallerid_custom === true ? $outcallerid : ''),
				  'size'	=> 15,
				  'notag'	=> false,
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'outcallerid-custom')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_preprocess-subroutine'),
				  'name'	=> 'userfeatures[preprocess_subroutine]',
				  'labelid'	=> 'userfeatures-preprocess-subroutine',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['preprocess_subroutine']['default'],
				  'value'	=> $info['userfeatures']['preprocess_subroutine'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'preprocess_subroutine')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_ringintern'),
				  'name'	=> 'userfeatures[ringintern]',
				  'labelid'	=> 'userfeatures-ringintern',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['ringintern']['default'],
				  'value'	=> $info['userfeatures']['ringintern'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'ringintern')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_ringextern'),
				  'name'	=> 'userfeatures[ringextern]',
				  'labelid'	=> 'userfeatures-ringextern',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['ringextern']['default'],
				  'value'	=> $info['userfeatures']['ringextern'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'ringextern')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_ringgroup'),
				  'name'	=> 'userfeatures[ringgroup]',
				  'labelid'	=> 'userfeatures-ringgroup',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['ringgroup']['default'],
				  'value'	=> $info['userfeatures']['ringgroup'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'ringgroup')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_ringforward'),
				  'name'	=> 'userfeatures[ringforward]',
				  'labelid'	=> 'userfeatures-ringforward',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['ringforward']['default'],
				  'value'	=> $info['userfeatures']['ringforward'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'ringforward')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_rightcallcode'),
				  'name'	=> 'userfeatures[rightcallcode]',
				  'labelid'	=> 'userfeatures-rightcallcode',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['rightcallcode']['default'],
				  'value'	=> $info['userfeatures']['rightcallcode'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'rightcallcode')) ));
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-userfeatures-alarmclock" for="it-userfeatures-alarmclock"><?=$this->bbf('fm_userfeatures_alarmclock');?></label>
<?php
	echo $form->select(array('paragraph'	=> false,
				  'name'	=> 'userfeatures[alarmclock_hour]',
				  'labelid'	=> 'userfeatures-alarmclock_hour',
				    'empty'	=> true,
				    'key'	=> false,
				    'default'	=> $element['userfeatures']['alarmclock_hour']['default'],
				    'selected'	=> $this->get_var('info','userfeatures','alarmclock_hour'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'alarmclock_hour'))),
			      $element['userfeatures']['alarmclock_hour']['value']),

		$form->select(array('paragraph'	=> false,
				  'name'	=> 'userfeatures[alarmclock_minute]',
				  'labelid'	=> 'userfeatures-alarmclock_minute',
				    'empty'	=> true,
				    'key'	=> false,
				    'default'	=> $element['userfeatures']['alarmclock_minute']['default'],
				    'selected'	=> $this->get_var('info','userfeatures','alarmclock_minute'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'alarmclock_minute'))),
			      $element['userfeatures']['alarmclock_minute']['value']);
?>
		</p>
	</div>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-userfeatures-pitch" for="it-userfeatures-pitch"><?=$this->bbf('fm_userfeatures_pitch');?></label>
<?php
	echo $form->select(array('paragraph'	=> false,
				  'name'	=> 'userfeatures[pitchdirection]',
				  'labelid'	=> 'userfeatures-pitchdirection',
				    'empty'	=> true,
				    'key'	=> false,
		           'bbf'       => 'fm_userfeatures_pitchdirection-opt',
							 'bbfopt'	   => array('argmode' => 'paramvalue'),
				    'default'	=> $element['userfeatures']['pitchdirection']['default'],
				    'selected'	=> $this->get_var('info','userfeatures','pitchdirection'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'pitchdirection'))),
			      $element['userfeatures']['pitchdirection']['value']),

		$form->select(array('paragraph'	=> false,
				  'name'	=> 'userfeatures[pitch]',
				  'labelid'	=> 'userfeatures-pitch',
				    'empty'	=> true,
				    'key'	=> false,
		           'bbf'       => 'fm_userfeatures_pitch-opt',
							 'bbfopt'	   => array('argmode' => 'paramvalue'),
				    'default'	=> $element['userfeatures']['pitch']['default'],
				    'selected'	=> $this->get_var('info','userfeatures','pitch'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'userfeatures', 'pitch'))),
			      $element['userfeatures']['pitch']['value']);
?>
		</p>
	</div>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-userfeatures-description" for="it-userfeatures-description"><?=$this->bbf('fm_userfeatures_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph' => false,
					 'label'	=> false,
					 'name'		=> 'userfeatures[description]',
					 'id'		=> 'it-userfeatures-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['userfeatures']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'description')) ),
				   $info['userfeatures']['description']);?>
	</div>
</div>

<div id="sb-part-lines" class="b-nodisplay">

<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_entity'),
				    'name'		=> 'userfeatures[entityid]',
				    'labelid'	=> 'userfeatures-entityid',
				    'help'		=> $this->bbf('hlp_fm_userfeatures_entity'),
				    'key'		=> 'displayname',
				    'altkey'	=> 'id',
	           		'selected'  => $info['userfeatures']['entityid']),
			      $this->get_var('entity_list'));

if($line_list !== false):
		echo $form->hidden(array('name' => 'userfeatures[entityid]','value' => $info['userfeatures']['entityid']));
?>
<script>
	dwho_eid('it-userfeatures-entityid').disabled = "disabled";
</script>
<?php
endif;
?>
	<div class="sb-list">
<?php
	$this->file_include('bloc/service/ipbx/asterisk/pbx_settings/users/line',
			    array('count'	=> $line_nb,
					  'list'	=> $line_list));
?>
	</div>

</div>

<div id="sb-part-voicemail" class="b-nodisplay">
<?php
	echo    $form->select(array('desc' => $this->bbf('fm_userfeatures_voicemailtype'),
			           'name'      => 'userfeatures[voicemailtype]',
			           'labelid'   => 'userfeatures-voicemailtype',
			           'key'       => false,
			           'empty'     => $this->bbf('fm_userfeatures_voicemailtype-opt(none)'),
			           'bbf'       => 'fm_userfeatures_voicemailtype-opt',
								 'bbfopt'	   => array('argmode' => 'paramvalue'),
			           'selected'  => $info['userfeatures']['voicemailtype'],
			           'default'   => $element['userfeatures']['voicemailtype']['default']),
			       $element['userfeatures']['voicemailtype']['value']),

		$form->hidden(array('name'	=> 'userfeatures[voicemailid]',
				    'id'	=> 'it-userfeatures-voicemailid',
				    'value'	=> $info['userfeatures']['voicemailid'])),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_option'),
				    'name'		=> 'voicemail-option',
				    'labelid'	=> 'voicemail-option',
				    'empty'		=> $voicemail_identity,
				    'key'		=> false,
				    'bbf'		=> 'fm_voicemail_option-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> $this->get_var('info','voicemail-option')),
			      $element['voicemail']['option']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_suggest'),
				  'name'	=> 'voicemail-suggest',
				  'labelid'	=> 'voicemail-suggest',
				  'size'	=> 20,
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'voicemail', 'suggest')) )),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_fullname'),
				  'name'	=> 'voicemail[fullname]',
				  'labelid'	=> 'voicemail-fullname',
				  'size'	=> 15,
				  'default'	=> $element['voicemail']['fullname']['default'],
				  'value'	=> $this->get_var('voicemail','fullname'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'voicemail', 'fullname')) )),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_mailbox'),
				  'name'	=> 'voicemail[mailbox]',
				  'labelid'	=> 'voicemail-mailbox',
				  'size'	=> 10,
				  'default'	=> $element['voicemail']['mailbox']['default'],
				  'value'	=> $this->get_var('voicemail','mailbox'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'voicemail', 'mailbox')) )),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_password'),
				  'name'	=> 'voicemail[password]',
				  'labelid'	=> 'voicemail-password',
				  'size'	=> 10,
				  'default'	=> $element['voicemail']['password']['default'],
				  'value'	=> $this->get_var('voicemail','password'),
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'voicemail', 'password')) )),

		$form->text(array('desc'	=> $this->bbf('fm_voicemail_email'),
				  'name'	=> 'voicemail[email]',
				  'labelid'	=> 'voicemail-email',
				  'size'	=> 15,
				  'value'	=> $this->get_var('voicemail','email'),
				  'default'	=> $element['voicemail']['email']['default'],
				  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'voicemail', 'email')) ));

	if(($tz_list = $this->get_var('tz_list')) !== false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_voicemail_tz'),
					    'name'	=> 'voicemail[tz]',
					    'labelid'	=> 'voicemail-tz',
					    'key'	=> 'name',
					    'default'	=> $element['voicemail']['tz']['default'],
					    'selected'	=> $this->get_var('voicemail','tz')),
				      $tz_list);
	endif;

	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_voicemailfeatures_skipcheckpass'),
				      'name'	=> 'voicemailfeatures[skipcheckpass]',
				      'labelid'	=> 'voicemailfeatures-skipcheckpass',
				      'default'	=> $element['voicemailfeatures']['skipcheckpass']['default'],
				      'checked'	=> $this->get_var('info','voicemailfeatures','skipcheckpass'))),

		$form->select(array('desc'	=> $this->bbf('fm_voicemail_attach'),
				    'name'	=> 'voicemail[attach]',
				    'labelid'	=> 'voicemail-attach',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['voicemail']['attach']['default'],
				    'selected'	=> $this->get_var('voicemail','attach')),
			      $element['voicemail']['attach']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_voicemail_deletevoicemail'),
				      'name'	=> 'voicemail[deletevoicemail]',
				      'labelid'	=> 'voicemail-deletevoicemail',
				      'default'	=> $element['voicemail']['deletevoicemail']['default'],
				      'checked'	=> $this->get_var('voicemail','deletevoicemail')));
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

<div id="sb-part-service" class="b-nodisplay">
	<fieldset id="fld-client">
		<legend><?=$this->bbf('fld-client');?></legend>
<?php

	echo 	$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enableclient'),
				      'name'	=> 'userfeatures[enableclient]',
				      'labelid'	=> 'userfeatures-enableclient',
				      'default'	=> $element['userfeatures']['enableclient']['default'],
				      'checked'	=> $info['userfeatures']['enableclient']));

	if(is_array($profileclient_list) === true && empty($profileclient_list) === false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_profileclient'),
					    'name'	=> 'userfeatures[profileclient]',
					    'labelid'	=> 'userfeatures-profileclient',
					    'default'	=> $element['userfeatures']['profileclient']['default'],
					    'selected'	=> $info['userfeatures']['profileclient']),
				      $profileclient_list);
	endif;
?>
	</fieldset>

	<fieldset id="fld-services">
		<legend><?=$this->bbf('fld-services');?></legend>
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enablehint'),
				      'name'	=> 'userfeatures[enablehint]',
				      'labelid'	=> 'userfeatures-enablehint',
				      'default'	=> $element['userfeatures']['enablehint']['default'],
				      'checked'	=> $info['userfeatures']['enablehint'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enablevoicemail'),
				      'name'	=> 'userfeatures[enablevoicemail]',
				      'labelid'	=> 'userfeatures-enablevoicemail',
				      'default'	=> $element['userfeatures']['enablevoicemail']['default'],
				      'checked'	=> $info['userfeatures']['enablevoicemail'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enablexfer'),
				      'name'	=> 'userfeatures[enablexfer]',
				      'labelid'	=> 'userfeatures-enablexfer',
				      'default'	=> $element['userfeatures']['enablexfer']['default'],
				      'checked'	=> $info['userfeatures']['enablexfer'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enableautomon'),
				      'name'	=> 'userfeatures[enableautomon]',
				      'labelid'	=> 'userfeatures-enableautomon',
				      'default'	=> $element['userfeatures']['enableautomon']['default'],
				      'checked'	=> $info['userfeatures']['enableautomon'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_callrecord'),
				      'name'	=> 'userfeatures[callrecord]',
				      'labelid'	=> 'userfeatures-callrecord',
				      'default'	=> $element['userfeatures']['callrecord']['default'],
				      'checked'	=> $info['userfeatures']['callrecord'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_incallfilter'),
				      'name'	=> 'userfeatures[incallfilter]',
				      'labelid'	=> 'userfeatures-incallfilter',
				      'default'	=> $element['userfeatures']['incallfilter']['default'],
				      'checked'	=> $info['userfeatures']['incallfilter'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enablednd'),
				      'name'	=> 'userfeatures[enablednd]',
				      'labelid'	=> 'userfeatures-enablednd',
				      'default'	=> $element['userfeatures']['enablednd']['default'],
				      'checked'	=> $info['userfeatures']['enablednd'])),

		$form->select(array('desc'	=> $this->bbf('fm_userfeatures_bsfilter'),
				    'name'	=> 'userfeatures[bsfilter]',
				    'labelid'	=> 'userfeatures-bsfilter',
				    'key'	=> false,
				    'bbf'	=> 'fm_userfeatures_bsfilter-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['userfeatures']['bsfilter']['default'],
				    'selected'	=> $info['userfeatures']['bsfilter']),
			      $element['userfeatures']['bsfilter']['value']);

	if($agent_list !== false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_agentid'),
					    'name'	=> 'userfeatures[agentid]',
					    'labelid'	=> 'userfeatures-agentid',
					    'empty'	=> true,
					    'key'	=> 'identity',
					    'altkey'	=> 'id',
					    'default'	=> $element['userfeatures']['agentid']['default'],
					    'selected'	=> $info['userfeatures']['agentid']),
				      $agent_list);
	else:
		echo	'<div id="fd-userfeatures-agentid" class="txt-center">',
			$url->href_htmln($this->bbf('create_agent'),
					'service/ipbx/call_center/agents',
					array('act'	=> 'addagent',
					      'group'	=> 1)),
			'</div>';
	endif;
?>
	</fieldset>

	<fieldset id="fld-callforwards">
		<legend><?=$this->bbf('fld-callforwards');?></legend>
<?php

	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enablerna'),
				      'name'	=> 'userfeatures[enablerna]',
				      'labelid'	=> 'userfeatures-enablerna',
				      'default'	=> $element['userfeatures']['enablerna']['default'],
				      'checked'	=> $info['userfeatures']['enablerna'])),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_destrna'),
				  'name'	=> 'userfeatures[destrna]',
				  'labelid'	=> 'userfeatures-destrna',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['destrna']['default'],
				  'value'	=> $info['userfeatures']['destrna'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'destrna')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enablebusy'),
				      'name'	=> 'userfeatures[enablebusy]',
				      'labelid'	=> 'userfeatures-enablebusy',
				      'default'	=> $element['userfeatures']['enablebusy']['default'],
				      'checked'	=> $info['userfeatures']['enablebusy'])),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_destbusy'),
				  'name'	=> 'userfeatures[destbusy]',
				  'labelid'	=> 'userfeatures-destbusy',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['destbusy']['default'],
				  'value'	=> $info['userfeatures']['destbusy'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'destbusy')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_userfeatures_enableunc'),
				      'name'	=> 'userfeatures[enableunc]',
				      'labelid'	=> 'userfeatures-enableunc',
				      'default'	=> $element['userfeatures']['enableunc']['default'],
				      'checked'	=> $info['userfeatures']['enableunc'])),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_destunc'),
				  'name'	=> 'userfeatures[destunc]',
				  'labelid'	=> 'userfeatures-destunc',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['destunc']['default'],
				  'value'	=> $info['userfeatures']['destunc'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'destunc')) ));
?>
	</fieldset>
</div>

<div id="sb-part-queueskills" class="b-nodisplay">
<?php
	$this->file_include('bloc/service/ipbx/asterisk/pbx_settings/users/queueskills');
?>
</div>

<div id="sb-part-groups" class="b-nodisplay">
<?php
	$this->file_include('bloc/service/ipbx/asterisk/pbx_settings/users/groups');
?>
</div>

<div id="sb-part-funckeys" class="b-nodisplay">
<?php
	$this->file_include('bloc/service/ipbx/asterisk/pbx_settings/users/phonefunckey');
?>
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
					       'size'		=> 5,
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

<div id="sb-part-advanced" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_userfeatures_outcallerid'),
				    'name'	=> 'userfeatures[outcallerid-type]',
				    'labelid'	=> 'userfeatures-outcallerid-type',
				    'key'	=> false,
				    'bbf'	=> 'fm_userfeatures_outcallerid-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'selected'	=> ($outcallerid_custom === true ? 'custom' : $outcallerid)),
			      $element['userfeatures']['outcallerid-type']['value']),

		$form->text(array('desc'	=> '&nbsp;',
				  'name'	=> 'userfeatures[outcallerid-custom]',
				  'labelid'	=> 'userfeatures-outcallerid-custom',
				  'value'	=> ($outcallerid_custom === true ? $outcallerid : ''),
				  'size'	=> 15,
				  'notag'	=> false,
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'outcallerid-custom')) )),

		$form->text(array('desc'	=> $this->bbf('fm_userfeatures_preprocess-subroutine'),
				  'name'	=> 'userfeatures[preprocess_subroutine]',
				  'labelid'	=> 'userfeatures-preprocess-subroutine',
				  'size'	=> 15,
				  'default'	=> $element['userfeatures']['preprocess_subroutine']['default'],
				  'value'	=> $info['userfeatures']['preprocess_subroutine'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'preprocess_subroutine')) ));

?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-userfeatures-description" for="it-userfeatures-description"><?=$this->bbf('fm_userfeatures_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'userfeatures[description]',
					 'id'		=> 'it-userfeatures-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['userfeatures']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'userfeatures', 'description')) ),
				   $info['userfeatures']['description']);?>
	</div>
</div>

<div id="sb-part-schedule" class="b-nodisplay">
</div>
