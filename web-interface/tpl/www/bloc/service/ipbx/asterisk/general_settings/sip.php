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

$form = &$this->get_module('form');
$url = &$this->get_module('url');
$dhtml = &$this->get_module('dhtml');

$error = $this->get_var('error');
$element = $this->get_var('element');
$moh_list = $this->get_var('moh_list');
$context_list = $this->get_var('context_list');

if(($fm_save = $this->get_var('fm_save')) === true):
	$dhtml->write_js('xivo_form_result(true,\''.$dhtml->escape($this->bbf('fm_success-save')).'\');');
elseif($fm_save === false):
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

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
					<a href="#first"><?=$this->bbf('smenu_general');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-2"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-network');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#network"><?=$this->bbf('smenu_network');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-3"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-security');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#security"><?=$this->bbf('smenu_security');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-4"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-signalling');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#signalling"><?=$this->bbf('smenu_signalling');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-5"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-t38');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#t38"><?=$this->bbf('smenu_t38');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-6"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-jitterbuffer');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#jitterbuffer"><?=$this->bbf('smenu_jitterbuffer');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-7"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-default');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#default"><?=$this->bbf('smenu_default');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-8"
		    class="dwsm-blur"
		    onclick="dwho_submenu.select(this,'sb-part-realtime');"
		    onmouseout="dwho_submenu.blur(this);"
		    onmouseover="dwho_submenu.focus(this);">
			<div class="tab">
				<span class="span-center">
					<a href="#realtime"><?=$this->bbf('smenu_realtime');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
		<li id="dwsm-tab-9"
		    class="dwsm-blur-last"
		    onclick="dwho_submenu.select(this,'sb-part-internals',1);"
		    onmouseout="dwho_submenu.blur(this,1);"
		    onmouseover="dwho_submenu.focus(this,1);">
			<div class="tab">
				<span class="span-center">
					<a href="#internals"><?=$this->bbf('smenu_internals');?></a>
				</span>
			</div>
			<span class="span-right">&nbsp;</span>
		</li>
	</ul>
</div>

<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8" onsubmit="dwho.form.select('it-localnet'); dwho.form.select('it-codec');">

<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),
		$form->hidden(array('name'	=> 'fm_send',
				    'value'	=> 1));
?>

<div id="sb-part-first" class="b-nodisplay">

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_bindport'),
					  'name'		=> 'bindport',
					  'labelid'		=> 'bindport',
					  'help'		=> $this->bbf('hlp_fm_bindport'),
					  'required'	=> false,
					  'value'		=> $this->get_var('info','bindport','var_val'),
					  'default'		=> $element['bindport']['default'],
					  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'bindport')) )),

		$form->text(array('desc'	=> $this->bbf('fm_udpbindaddr'),
					  'name'		=> 'udpbindaddr',
					  'labelid'		=> 'udpbindaddr',
					  'size'		=> 15,
					  'help'		=> $this->bbf('hlp_fm_udpbindaddr'),
					  'required'	=> false,
					  'value'		=> $this->get_var('info','udpbindaddr','var_val'),
					  'default'		=> $element['udpbindaddr']['default'],
					  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'udpbindaddr')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_tcpenable'),
		      'name'		  => 'tcpenable',
		      'labelid'		=> 'tcpenable',
 				  'help'		  => $this->bbf('hlp_fm_tcpenable'),
  			  'required'	=> false,
		      'checked'		=> $this->get_var('info','tcpenable','var_val'),
		      'default'		=> $element['tcpenable']['default']),
		      'onclick="xivo_chg_attrib(\'ast_fm_tcpbindaddr\',
								\'it-tcpbindaddr\',
								Number((this.checked === false)));"'),

		$form->text(array('desc'	=> $this->bbf('fm_tcpbindaddr'),
					  'name'     => 'tcpbindaddr',
					  'labelid'  => 'tcpbindaddr',
					  'size'     => 15,
					  'help'     => $this->bbf('hlp_fm_tcpbindaddr'),
					  'required' => false,
					  'value'    => $this->get_var('info','tcpbindaddr','var_val'),
					  'default'  => $element['tcpbindaddr']['default'],
					  'error'    => $this->bbf_args('error',
						   $this->get_var('error', 'tcpbindaddr')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_videosupport'),
				      'name'		=> 'videosupport',
				      'labelid'		=> 'videosupport',
					  'help'		=> $this->bbf('hlp_fm_videosupport'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','videosupport','var_val'),
				      'default'		=> $element['videosupport']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_autocreatepeer'),
				      'name'		=> 'autocreatepeer',
				      'labelid'		=> 'autocreatepeer',
					  'help'		=> $this->bbf('hlp_fm_autocreatepeer'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','autocreatepeer','var_val'),
				      'default'		=> $element['autocreatepeer']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_allowguest'),
				      'name'		=> 'allowguest',
				      'labelid'		=> 'allowguest',
					  'help'		=> $this->bbf('hlp_fm_allowguest'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','allowguest','var_val'),
				      'default'		=> $element['allowguest']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_allowsubscribe'),
				      'name'		=> 'allowsubscribe',
				      'labelid'		=> 'allowsubscribe',
					  'help'		=> $this->bbf('hlp_fm_allowsubscribe'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','allowsubscribe','var_val'),
				      'default'		=> $element['allowsubscribe']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_allowoverlap'),
				      'name'		=> 'allowoverlap',
				      'labelid'		=> 'allowoverlap',
					  'help'		=> $this->bbf('hlp_fm_allowoverlap'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','allowoverlap','var_val'),
				      'default'		=> $element['allowoverlap']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_match_auth_username'),
			      'name'		  => 'match_auth_username',
			      'labelid'		=> 'match_auth_username',
					  'help'	  	=> $this->bbf('hlp_fm_match_auth_username'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','match_auth_username','var_val'),
			      'default'		=> $element['match_auth_username']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_promiscredir'),
				      'name'		=> 'promiscredir',
				      'labelid'		=> 'promiscredir',
					  'help'		=> $this->bbf('hlp_fm_promiscredir'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','promiscredir','var_val'),
				      'default'		=> $element['promiscredir']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_autodomain'),
				      'name'		=> 'autodomain',
				      'labelid'		=> 'autodomain',
					  'help'		=> $this->bbf('hlp_fm_autodomain'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','autodomain','var_val'),
				      'default'		=> $element['autodomain']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_domain'),
				  'name'		=> 'domain',
				  'labelid'		=> 'domain',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_domain'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','domain','var_val'),
				  'default'		=> $element['domain']['default'],
				  'error'		=> $this->bbf_args('error',
					   $this->get_var('error', 'domain')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_allowexternaldomains'),
				      'name'		=> 'allowexternaldomains',
				      'labelid'		=> 'allowexternaldomains',
					  'help'		=> $this->bbf('hlp_fm_allowexternaldomains'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','allowexternaldomains','var_val'),
				      'default'		=> $element['allowexternaldomains']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_usereqphone'),
				      'name'		=> 'usereqphone',
				      'labelid'		=> 'usereqphone',
					  'help'		=> $this->bbf('hlp_fm_usereqphone'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','usereqphone','var_val'),
				      'default'		=> $element['usereqphone']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_realm'),
				  'name'		=> 'realm',
				  'labelid'		=> 'realm',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_realm'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','realm','var_val'),
				  'default'		=> $element['realm']['default'],
				  'error'		=> $this->bbf_args('error',
					   $this->get_var('error', 'realm')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_alwaysauthreject'),
				      'name'		=> 'alwaysauthreject',
				      'labelid'		=> 'alwaysauthreject',
					  'help'		=> $this->bbf('hlp_fm_alwaysauthreject'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','alwaysauthreject','var_val'),
				      'default'		=> $element['alwaysauthreject']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_useragent'),
				  'name'		=> 'useragent',
				  'labelid'		=> 'useragent',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_useragent'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','useragent','var_val'),
				  'default'		=> $element['useragent']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'useragent')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_buggymwi'),
				      'name'		=> 'buggymwi',
				      'labelid'		=> 'buggymwi',
					  'help'		=> $this->bbf('hlp_fm_buggymwi'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','buggymwi','var_val'),
				      'default'		=> $element['buggymwi']['default']));

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_regcontext'),
				    'name'		=> 'regcontext',
				    'labelid'	=> 'regcontext',
				    'empty'		=> true,
				    'key'		=> 'identity',
				    'altkey'	=> 'name',
					'help'		=> $this->bbf('hlp_fm_regcontext'),
					'required'	=> false,
				    'default'	=> $element['regcontext']['default'],
				    'selected'	=> $this->get_var('info','regcontext','var_val')),
			      $context_list);
endif;
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_regextenonqualify'),
				      'name'		=> 'regextenonqualify',
				      'labelid'		=> 'regextenonqualify',
					  'help'		=> $this->bbf('hlp_fm_regextenonqualify'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','regextenonqualify','var_val'),
				      'default'		=> $element['regextenonqualify']['default']));


	echo	$form->text(array('desc'	=> $this->bbf('fm_callerid'),
				  'name'		=> 'callerid',
				  'labelid'		=> 'callerid',
				  'size'		=> 15,
				  'notag'		=> false,
				  'help'		=> $this->bbf('hlp_fm_callerid'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','callerid','var_val'),
				  'default'		=> $element['callerid']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'callerid')) )),

		$form->text(array('desc'	=> $this->bbf('fm_fromdomain'),
				  'name'		=> 'fromdomain',
				  'labelid'		=> 'fromdomain',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_fromdomain'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','fromdomain','var_val'),
				  'default'		=> $element['fromdomain']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'fromdomain')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_sipdebug'),
				      'name'		=> 'sipdebug',
				      'labelid'		=> 'sipdebug',
					  'help'		=> $this->bbf('hlp_fm_sipdebug'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','sipdebug','var_val'),
				      'default'		=> $element['sipdebug']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dumphistory'),
				      'name'		=> 'dumphistory',
				      'labelid'		=> 'dumphistory',
					  'help'		=> $this->bbf('hlp_fm_dumphistory'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','dumphistory','var_val'),
				      'default'		=> $element['dumphistory']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_recordhistory'),
				      'name'		=> 'recordhistory',
				      'labelid'		=> 'recordhistory',
					  'help'		=> $this->bbf('hlp_fm_recordhistory'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','recordhistory','var_val'),
				      'default'		=> $element['recordhistory']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_callevents'),
				      'name'		=> 'callevents',
				      'labelid'		=> 'callevents',
					  'help'		=> $this->bbf('hlp_fm_callevents'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','callevents','var_val'),
				      'default'		=> $element['callevents']['default']),
				'disabled="disabled"'),

		$form->checkbox(array('desc'	=> $this->bbf('fm_authfailureevents'),
				      'name'		=> 'authfailureevents',
				      'labelid'		=> 'authfailureevents',
					  'help'		=> $this->bbf('hlp_fm_authfailureevents'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','authfailureevents','var_val'),
				      'default'		=> $element['authfailureevents']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_tos-sip'),
				    'name'		=> 'tos_sip',
				    'labelid'	=> 'tos-sip',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_tos-sip'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','tos_sip','var_val'),
				    'default'	=> $element['tos_sip']['default']),
			      $element['tos_sip']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_tos-audio'),
				    'name'		=> 'tos_audio',
				    'labelid'	=> 'tos-audio',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_tos-audio'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','tos_audio','var_val'),
				    'default'	=> $element['tos_audio']['default']),
			      $element['tos_audio']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_tos-video'),
				    'name'		=> 'tos_video',
				    'labelid'	=> 'tos-video',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_tos-video'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','tos_video','var_val'),
				    'default'	=> $element['tos_video']['default']),
					$element['tos_video']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_tos-text'),
				    'name'		=> 'tos_text',
				    'labelid'	=> 'tos-text',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_tos-text'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','tos_text','var_val'),
				    'default'	=> $element['tos_text']['default']),
					$element['tos_text']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_cos-sip'),
				    'name'		=> 'cos_sip',
				    'labelid'	=> 'cos-sip',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_cos-sip'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','cos_sip','var_val'),
				    'default'	=> $element['cos_sip']['default']),
			      $element['cos_sip']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_cos-audio'),
				    'name'		=> 'cos_audio',
				    'labelid'	=> 'cos-audio',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_cos-audio'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','cos_audio','var_val'),
				    'default'	=> $element['cos_audio']['default']),
			      $element['cos_audio']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_cos-video'),
				    'name'		=> 'cos_video',
				    'labelid'	=> 'cos-video',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_cos-video'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','cos_video','var_val'),
				    'default'	=> $element['cos_video']['default']),
			      $element['cos_video']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_cos-text'),
				    'name'		=> 'cos_text',
				    'labelid'	=> 'cos-text',
				    'empty'		=> true,
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_cos-text'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','cos_text','var_val'),
				    'default'	=> $element['cos_text']['default']),
			      $element['cos_text']['value']);
?>
</div>

<div id="sb-part-network" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_externip'),
				  'name'		=> 'externip',
				  'labelid'		=> 'externip',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_externip'),
				  'value'		=> $this->get_var('info','externip','var_val'),
				  'default'		=> $element['externip']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'externip')) )),

		$form->text(array('desc'	=> $this->bbf('fm_externhost'),
				  'name'		=> 'externhost',
				  'labelid'		=> 'externhost',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_externhost'),
				  'value'		=> $this->get_var('info','externhost','var_val'),
				  'default'		=> $element['externhost']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'externhost')) )),

		$form->text(array('desc'	=> $this->bbf('fm_stunaddr'),
				  'name'		=> 'stunaddr',
				  'labelid'		=> 'stunaddr',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_stunaddr'),
				  'value'		=> $this->get_var('info','stunaddr','var_val'),
				  'default'		=> $element['stunaddr']['default'],
				  'error'		=> $this->bbf_args('error',
					$this->get_var('error', 'stunaddr')) )),

		$form->select(array('desc'	=> $this->bbf('fm_externrefresh'),
				    'name'		=> 'externrefresh',
				    'labelid'	=> 'externrefresh',
				    'key'		=> false,
				    'bbf'		=> 'fm_externrefresh-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 		'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
					'help'		=> $this->bbf('hlp_fm_externrefresh'),
				    'selected'	=> $this->get_var('info','externrefresh','var_val'),
				    'default'	=> $element['externrefresh']['default']),
			      $element['externrefresh']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_matchexterniplocally'),
				      'name'		=> 'matchexterniplocally',
				      'labelid'		=> 'matchexterniplocally',
					  'help'		=> $this->bbf('hlp_fm_matchexterniplocally'),
				      'checked'		=> $this->get_var('info','matchexterniplocally','var_val'),
				      'default'		=> $element['matchexterniplocally']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dynamic_exclude_static'),
				      'name'		=> 'dynamic_exclude_static',
				      'labelid'		=> 'dynamic_exclude_static',
					  'help'		=> $this->bbf('hlp_fm_dynamic_exclude_static'),
				      'checked'		=> $this->get_var('info','dynamic_exclude_static','var_val'),
				      'default'		=> $element['dynamic_exclude_static']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_contactdeny'),
				  'name'		=> 'contactdeny',
				  'labelid'		=> 'contactdeny',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_contactdeny'),
				  'value'		=> $this->get_var('info','contactdeny','var_val'),
				  'default'		=> $element['contactdeny']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'contactdeny')) )),

		$form->text(array('desc'	=> $this->bbf('fm_contactpermit'),
				  'name'		=> 'contactpermit',
				  'labelid'		=> 'contactpermit',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_contactpermit'),
				  'value'		=> $this->get_var('info','contactpermit','var_val'),
				  'default'		=> $element['contactpermit']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'contactpermit')) )),

		$form->text(array('desc'	=> $this->bbf('fm_outboundproxy'),
				  'name'		=> 'outboundproxy',
				  'labelid'		=> 'outboundproxy',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_outboundproxy'),
				  'value'		=> $this->get_var('info','outboundproxy','var_val'),
				  'default'		=> $element['outboundproxy']['default'],
				  'error'		=> $this->bbf_args('error',
						   $this->get_var('error', 'outboundproxy')) ));

?>

<div id="localnetlist" class="fm-paragraph fm-multilist">
	<p>
		<label id="lb-localnetlist" for="it-localnet">
			<?=$this->bbf('fm_localnet');?>
		</label>
	</p>
	<div class="slt-list">
		<?=$form->select(array('name'		=> 'localnet[]',
				       'label'		=> false,
				       'id'		=> 'it-localnet',
				       'key'		=> 'var_val',
				       'altkey'		=> 'var_val',
				       'multiple'	=> true,
				       'size'		=> 5,
				       'paragraph'	=> false),
				 $this->get_var('info','localnet'));?>
		<div class="bt-adddelete">
			<a href="#"
			   onclick="xivo_form_select_add_host_ipv4_subnet('it-localnet',
									  prompt('<?=$dhtml->escape($this->bbf('localnet_add'));?>'));
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_add-localnet');?>">
				<?=$url->img_html('img/site/button/mini/blue/add.gif',
						  $this->bbf('bt_add-localnet'),
						  'class="bt-addlist" id="bt-add-localnet" border="0"');?></a><br />
			<a href="#"
			   onclick="dwho.form.select_delete_entry('it-localnet');
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_delete-localnet');?>">
				<?=$url->img_html('img/site/button/mini/orange/delete.gif',
						  $this->bbf('bt_delete-localnet'),
						  'class="bt-deletelist" id="bt-del-localnet" border="0"');?></a>
		</div>
	</div>
</div>
<div class="clearboth"></div>
</div>

<div id="sb-part-security" class="b-nodisplay">
<?php
		echo $form->checkbox(array('desc'	=> $this->bbf('fm_tlsenable'),
		      'name'	  	=> 'tlsenable',
		      'labelid'		=> 'tlsenable',
 				  'help'  		=> $this->bbf('hlp_fm_tlsenable'),
		      'checked'		=> $this->get_var('info','tlsenable','var_val'),
					'default'		=> $element['tlsenable']['default']),
		      'onclick="xivo_chg_attrib(\'ast_fm_tlsbindaddr\',
								\'it-tlsbindaddr\',
								Number((this.checked === false)));"'),

		$form->text(array('desc'	=> $this->bbf('fm_tlsbindaddr'),
				  'name'	    => 'tlsbindaddr',
				  'labelid'   => 'tlsbindaddr',
				  'size'	    => 15,
				  'help'	   	=> $this->bbf('hlp_fm_tlsbindaddr'),
				  'required'  => false,
				  'value'		  => $this->get_var('info','tlsbindaddr','var_val'),
				  'default'	  => $element['tlsbindaddr']['default'],
					'error'		  => $this->bbf_args('error',	$this->get_var('error', 'tlsbindaddr'))
		)),

		//'<p class="fm-paragraph">',
    $form->select(array('desc'  => $this->bbf('fm_tlscertfile'),
            'name'    => 'tlscertfile',
            'labelid' => 'tlscertfile',
            //'paragraph'=> false,
            'key'     => false,
            'empty'   => true,
            'help'    => $this->bbf('hlp_fm_tlscertfile'),
            'selected'=> $this->get_var('info','tlscertfile','var_val'),
            'default' => $element['tlscertfile']['default']),
         $this->get_var('tlscertfiles')),

		/*
		$form->button(array('name'  => 'tlscertfile-add',
            'id'        => 'it-tlscertfile-add',
						'type'      => 'file',
            'paragraph' => false,
            'value'     => $this->bbf('fm_tlscertfile-add')),
            'onclick="alert(\'doit\');"'),
		'</p>',
		*/
    $form->select(array('desc'  => $this->bbf('fm_tlscafile'),
            'name'    => 'tlscafile',
            'labelid' => 'tlscafile',
            //'paragraph'=> false,
            'key'     => false,
            'empty'   => true,
            'help'    => $this->bbf('hlp_fm_tlscafile'),
            'selected'=> $this->get_var('info','tlscafile','var_val'),
            'default' => $element['tlscafile']['default']),
         $this->get_var('tlscafiles')),

/*
 * $form->select(array('desc'	=> $this->bbf('fm_tlscipher'),
				    'name'		 => 'tlscipher',
				    'labelid'	 => 'tlscipher',
				    'key'		   => false,
				    'bbf'		   => 'fm_tlscipher-opt',
				    'bbfopt'	 => array('argmode' => 'paramvalue'),
  					'help'		 => $this->bbf('hlp_fm_tlscipher'),
				    'selected' => $this->get_var('info','tlscipher','var_val'),
				    'default'	 => $element['tlscipher']['default']),
			      $element['tlscipher']['value']);
 */
		$form->checkbox(array('desc'	=> $this->bbf('fm_tlsdontverifyserver'),
				      'name'	  	=> 'tlsdontverifyserver',
				      'labelid'		=> 'tlsdontverifyserver',
  					  'help'  		=> $this->bbf('hlp_fm_tlsdontverifyserver'),
				      'checked'		=> $this->get_var('info','tlsdontverifyserver','var_val'),
							'default'		=> $element['tlsdontverifyserver']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_tlscipher'),
				  'name'		=> 'tlscipher',
				  'labelid'		=> 'tlscipher',
				  'size'		=> 15,
				  'help'		=> $this->bbf('hlp_fm_tlscipher'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','tlscipher','var_val'),
				  'default'		=> $element['tlscipher']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'tlscipher')) ));

?>
<div class="clearboth"></div>
</div>

<div id="sb-part-signalling" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_t1min'),
				    'name'		=> 't1min',
				    'labelid'	=> 't1min',
				    'key'		=> false,
				    'bbf'		=> 'fm_t1min-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_t1min'),
				    'selected'	=> $this->get_var('info','t1min','var_val'),
				    'default'	=> $element['t1min']['default']),
			      $element['t1min']['value']),

    $form->select(array('desc'  => $this->bbf('fm_timert1'),
            'name'      => 'timert1',
            'labelid'   => 'timert1',
            'key'       => false,
            'bbf'       => 'fm_t1min-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_timert1'),
            'selected'  => $this->get_var('info','timert1','var_val'),
            'default'   => $element['timert1']['default']),
         $element['timert1']['value']),

     $form->select(array('desc'  => $this->bbf('fm_timerb'),
            'name'      => 'timerb',
            'labelid'   => 'timerb',
            'key'       => false,
            'bbf'       => 'fm_t1min-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_timerb'),
            'selected'  => $this->get_var('info','timerb','var_val'),
            'default'   => $element['timerb']['default']),
         $element['timerb']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_relaxdtmf'),
				      'name'		=> 'relaxdtmf',
				      'labelid'		=> 'relaxdtmf',
					  'help'		=> $this->bbf('hlp_fm_relaxdtmf'),
				      'checked'		=> $this->get_var('info','relaxdtmf','var_val'),
				      'default'		=> $element['relaxdtmf']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_rfc2833compensate'),
				      'name'		=> 'rfc2833compensate',
				      'labelid'		=> 'rfc2833compensate',
					  'help'		=> $this->bbf('hlp_fm_rfc2833compensate'),
				      'checked'		=> $this->get_var('info','rfc2833compensate','var_val'),
				      'default'		=> $element['rfc2833compensate']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_compactheaders'),
				      'name'		=> 'compactheaders',
				      'labelid'		=> 'compactheaders',
					  'help'		=> $this->bbf('hlp_fm_compactheaders'),
				      'checked'		=> $this->get_var('info','compactheaders','var_val'),
				      'default'		=> $element['compactheaders']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_rtptimeout'),
				    'name'		=> 'rtptimeout',
				    'labelid'	=> 'rtptimeout',
				    'key'		=> false,
				    'bbf'		=> 'fm_rtptimeout-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_rtptimeout'),
				    'selected'	=> $this->get_var('info','rtptimeout','var_val'),
				    'default'	=> $element['rtptimeout']['default']),
			      $element['rtptimeout']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_rtpholdtimeout'),
				    'name'		=> 'rtpholdtimeout',
				    'labelid'	=> 'rtpholdtimeout',
				    'key'		=> false,
				    'bbf'		=> 'fm_rtptimeout-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_rtpholdtimeout'),
				    'selected'	=> $this->get_var('info','rtpholdtimeout','var_val'),
				    'default'	=> $element['rtpholdtimeout']['default']),
			      $element['rtpholdtimeout']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_rtpkeepalive'),
				    'name'		=> 'rtpkeepalive',
				    'labelid'	=> 'rtpkeepalive',
				    'key'		=> false,
				    'bbf'		=> 'fm_rtpkeepalive-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_rtpkeepalive'),
				    'selected'	=> $this->get_var('info','rtpkeepalive','var_val'),
				    'default'	=> $element['rtpkeepalive']['default']),
			      $element['rtpkeepalive']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_directrtpsetup'),
				      'name'		=> 'directrtpsetup',
				      'labelid'		=> 'directrtpsetup',
					  'help'		=> $this->bbf('hlp_fm_directrtpsetup'),
				      'checked'		=> $this->get_var('info','directrtpsetup','var_val'),
				      'default'		=> $element['directrtpsetup']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_notifymimetype'),
				  'name'		=> 'notifymimetype',
				  'labelid'		=> 'notifymimetype',
				  'size'		=> 35,
				  'help'		=> $this->bbf('hlp_fm_notifymimetype'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','notifymimetype','var_val'),
				  'default'		=> $element['notifymimetype']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'notifymimetype')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_srvlookup'),
				      'name'		=> 'srvlookup',
				      'labelid'		=> 'srvlookup',
					  'help'		=> $this->bbf('hlp_fm_srvlookup'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','srvlookup','var_val'),
				      'default'		=> $element['srvlookup']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_pedantic'),
				      'name'		=> 'pedantic',
				      'labelid'		=> 'pedantic',
					  'help'		=> $this->bbf('hlp_fm_pedantic'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','pedantic','var_val'),
				      'default'		=> $element['pedantic']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_minexpiry'),
				    'name'		=> 'minexpiry',
				    'labelid'	=> 'minexpiry',
				    'key'		=> false,
				    'bbf'		=> 'fm_expiry-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%H%M%s')),
					'help'		=> $this->bbf('hlp_fm_minexpiry'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','minexpiry','var_val'),
				    'default'	=> $element['minexpiry']['default']),
			      $element['minexpiry']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_maxexpiry'),
				    'name'		=> 'maxexpiry',
				    'labelid'	=> 'maxexpiry',
				    'key'		=> false,
				    'bbf'		=> 'fm_expiry-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%H%M%s')),
					'help'		=> $this->bbf('hlp_fm_maxexpiry'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','maxexpiry','var_val'),
				    'default'	=> $element['maxexpiry']['default']),
			      $element['maxexpiry']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_defaultexpiry'),
				    'name'		=> 'defaultexpiry',
				    'labelid'	=> 'defaultexpiry',
				    'key'		=> false,
				    'bbf'		=> 'fm_expiry-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%H%M%s')),
					'help'		=> $this->bbf('hlp_fm_defaultexpiry'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','defaultexpiry','var_val'),
				    'default'	=> $element['defaultexpiry']['default']),
					$element['defaultexpiry']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_mwiexpiry'),
				    'name'	  	=> 'mwiexpiry',
				    'labelid'  	=> 'mwiexpiry',
				    'key'	    	=> false,
				    'bbf'	    	=> 'fm_expiry-opt',
				    'bbfopt'  	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%H%M%s')),
  					'help'   		=> $this->bbf('hlp_fm_mwiexpiry'),
	   				'required'	=> false,
				    'selected'	=> $this->get_var('info','mwiexpiry','var_val'),
				    'default' 	=> $element['mwiexpiry']['default']),
			      $element['mwiexpiry']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_registertimeout'),
				    'name'		=> 'registertimeout',
				    'labelid'	=> 'registertimeout',
				    'key'		=> false,
				    'bbf'		=> 'fm_registertimeout-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
					'help'		=> $this->bbf('hlp_fm_registertimeout'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','registertimeout','var_val'),
				    'default'	=> $element['registertimeout']['default']),
			      $element['registertimeout']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_registerattempts'),
				    'name'		=> 'registerattempts',
				    'labelid'	=> 'registerattempts',
				    'key'		=> false,
				    'bbf'		=> 'fm_registerattempts-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_registerattempts'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','registerattempts','var_val'),
				    'default'	=> $element['registerattempts']['default']),
			      $element['registerattempts']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_notifyringing'),
				      'name'		=> 'notifyringing',
				      'labelid'		=> 'notifyringing',
					  'help'		=> $this->bbf('hlp_fm_notifyringing'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','notifyringing','var_val'),
				      'default'		=> $element['notifyringing']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_notifyhold'),
				      'name'		=> 'notifyhold',
				      'labelid'		=> 'notifyhold',
					  'help'		=> $this->bbf('hlp_fm_notifyhold'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','notifyhold','var_val'),
				      'default'		=> $element['notifyhold']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_notifycid'),
				      'name'		=> 'notifycid',
				      'labelid'		=> 'notifycid',
					  'help'		=> $this->bbf('hlp_fm_notifycid'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','notifycid','var_val'),
				      'default'		=> $element['notifycid']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_callcounter'),
				      'name'		=> 'callcounter',
				      'labelid'		=> 'callcounter',
					  'help'		=> $this->bbf('hlp_fm_callcounter'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','callcounter','var_val'),
				      'default'		=> $element['callcounter']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_allowtransfer'),
				      'name'		=> 'allowtransfer',
				      'labelid'		=> 'allowtransfer',
					  'help'		=> $this->bbf('hlp_fm_allowtransfer'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','allowtransfer','var_val'),
				      'default'		=> $element['allowtransfer']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_maxcallbitrate'),
				  'name'		=> 'maxcallbitrate',
				  'labelid'		=> 'maxcallbitrate',
				  'size'		=> 10,
				  'help'		=> $this->bbf('hlp_fm_maxcallbitrate'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','maxcallbitrate','var_val'),
				  'default'		=> $element['maxcallbitrate']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'maxcallbitrate')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_autoframing'),
				      'name'		=> 'autoframing',
				      'labelid'		=> 'autoframing',
					  'help'		=> $this->bbf('hlp_fm_autoframing'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','autoframing','var_val'),
				      'default'		=> $element['autoframing']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_prematuremedia'),
				      'name'		=> 'prematuremedia',
				      'labelid'		=> 'prematuremedia',
					  'help'		=> $this->bbf('hlp_fm_prematuremedia'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','prematuremedia','var_val'),
				      'default'		=> $element['prematuremedia']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_sdpsession'),
				  'name'		=> 'sdpsession',
				  'labelid'		=> 'sdpsession',
				  'size'		=> 10,
				  'help'		=> $this->bbf('hlp_fm_sdpsession'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','sdpsession','var_val'),
				  'default'		=> $element['sdpsession']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'sdpsession')) )),

		$form->text(array('desc'	=> $this->bbf('fm_sdpowner'),
				  'name'		=> 'sdpowner',
				  'labelid'		=> 'sdpowner',
				  'size'		=> 10,
				  'help'		=> $this->bbf('hlp_fm_sdpowner'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','sdpowner','var_val'),
				  'default'		=> $element['sdpowner']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'sdpowner')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_ignoresdpversion'),
				      'name'		=> 'ignoresdpversion',
				      'labelid'		=> 'ignoresdpversion',
					  'help'		=> $this->bbf('hlp_fm_ignoresdpversion'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','ignoresdpversion','var_val'),
				      'default'		=> $element['ignoresdpversion']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_shrinkcallerid'),
		      'name'		  => 'shrinkcallerid',
		      'labelid'		=> 'shrinkcallerid',
  			  'help'	  	=> $this->bbf('hlp_fm_shrinkcallerid'),
	   		  'required'	=> false,
		      'checked'		=> $this->get_var('info','shrinkcallerid','var_val'),
		      'default'		=> $element['shrinkcallerid']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_session-timers'),
			    'name'	  	=> 'session-timers',
			    'labelid'	  => 'session-timers',
			    'key'		    => false,
			    'bbf'		    => 'session-timers-opt',
			    'bbfopt'	  => array('argmode'	=> 'paramvalue'),
					'help'		  => $this->bbf('hlp_fm_session-timers'),
					'required'	=> false,
					'empty'     => true,
			    'selected'	=> $this->get_var('info','session-timers','var_val'),
			    'default'	  => $element['session-timers']['default']),
	      $element['session-timers']['value']),

     $form->select(array('desc'  => $this->bbf('fm_session-expires'),
            'name'      => 'session-expires',
            'labelid'   => 'session-expires',
            'key'       => false,
            'bbf'       => 'time-opt',
            'bbfopt'    => array('argmode' => 'paramvalue',
            'time'      => array('from'=>'second', 'format'=>'%M%s')),
            'help'      => $this->bbf('hlp_fm_session-expires'),
            'selected'  => $this->get_var('info','session-expires','var_val'),
            'default'   => $element['session-expires']['default']),
         $element['session-expires']['value']),

     $form->select(array('desc'  => $this->bbf('fm_session-minse'),
            'name'      => 'session-minse',
            'labelid'   => 'session-minse',
            'key'       => false,
            'bbf'       => 'time-opt',
            'bbfopt'    => array('argmode' => 'paramvalue',
            'time'      => array('from'=>'second', 'format'=>'%M%s')),
            'help'      => $this->bbf('hlp_fm_session-minse'),
            'selected'  => $this->get_var('info','session-minse','var_val'),
            'default'   => $element['session-minse']['default']),
         $element['session-minse']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_session-refresher'),
				    'name'		=> 'session-refresher',
				    'labelid'	=> 'session-refresher',
				    'key'		=> false,
				    'bbf'		=> 'refresher-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue'),
  					'help'		=> $this->bbf('hlp_fm_session-refresher'),
	  				'required'	=> false,
		  			'empty' => false,
				    'selected'	=> $this->get_var('info','session-refresher','var_val'),
				    'default'	=> $element['session-refresher']['default']),
			      $element['session-refresher']['value']),


		$form->checkbox(array('desc'	=> $this->bbf('fm_g726nonstandard'),
				      'name'		=> 'g726nonstandard',
				      'labelid'		=> 'g726nonstandard',
					  'help'		=> $this->bbf('hlp_fm_g726nonstandard'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','g726nonstandard','var_val'),
				      'default'		=> $element['g726nonstandard']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_codec-disallow'),
				    'name'	=> 'disallow',
				    'labelid'	=> 'disallow',
				    'key'	=> false,
				    'bbf'	=> 'fm_codec-disallow-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue')),
			      $element['disallow']['value']);
?>

<div id="codeclist" class="fm-paragraph fm-multilist">
	<p>
		<label id="lb-codeclist" for="it-codeclist">
			<?=$this->bbf('fm_codec-allow');?>
		</label>
	</p>
	<div class="slt-outlist">
<?php
	echo	$form->select(array('name'	=> 'codeclist',
				    'label'	=> false,
				    'id'	=> 'it-codeclist',
				    'multiple'	=> true,
				    'size'	=> 5,
				    'paragraph'	=> false,
				    'key'	=> false,
				    'bbf'	=> 'ast_codec_name_type',
				    'bbfopt'	=> array('argmode' => 'paramvalue')),
			       $element['allow']['value']);
?>
	</div>
	<div class="inout-list">
		<a href="#"
		   onclick="dwho.form.move_selected('it-codeclist',
						  'it-codec');
			    return(dwho.dom.free_focus());"
		   title="<?=$this->bbf('bt_incodec');?>">
			<?=$url->img_html('img/site/button/arrow-left.gif',
					  $this->bbf('bt_incodec'),
					  'class="bt-inlist" id="bt-incodec" border="0"');?></a><br />
		<a href="#"
		   onclick="dwho.form.move_selected('it-codec',
						  'it-codeclist');
			    return(dwho.dom.free_focus());"
		   title="<?=$this->bbf('bt_outcodec');?>">
			<?=$url->img_html('img/site/button/arrow-right.gif',
					  $this->bbf('bt_outcodec'),
					  'class="bt-outlist" id="bt-outcodec" border="0"');?></a>
	</div>
	<div class="slt-inlist">
		<?=$form->select(array('name'		=> 'allow[]',
				       'label'		=> false,
				       'id'		=> 'it-codec',
				       'multiple'	=> true,
				       'size'		=> 5,
				       'paragraph'		=> false,
				       'key'		=> false,
				       'bbf'		=> 'ast_codec_name_type',
				       'bbfopt'		=> array('argmode' => 'paramvalue')),
				 $this->get_var('info','allow','var_val'));?>
		<div class="bt-updown">
			<a href="#"
			   onclick="dwho.form.order_selected('it-codec',1);
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_upcodec');?>">
				<?=$url->img_html('img/site/button/arrow-up.gif',
						  $this->bbf('bt_upcodec'),
						  'class="bt-uplist" id="bt-upcodec" border="0"');?></a><br />
			<a href="#"
			   onclick="dwho.form.order_selected('it-codec',-1);
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_downcodec');?>">
				<?=$url->img_html('img/site/button/arrow-down.gif',
						  $this->bbf('bt_downcodec'),
						  'class="bt-downlist" id="bt-downcodec" border="0"');?></a>
		</div>
	</div>
</div>
<div class="clearboth"></div>
</div>

<div id="sb-part-t38" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_t38pt-udptl'),
				      'name'		=> 't38pt_udptl',
				      'labelid'		=> 't38pt-udptl',
					    'help'		=> $this->bbf('hlp_fm_t38pt-udptl'),
				  	  'required'	=> false,
				      'checked'		=> $this->get_var('info','t38pt_udptl','var_val'),
				      'default'		=> $element['t38pt_udptl']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_t38pt-usertpsource'),
				      'name'		=> 't38pt_usertpsource',
				      'labelid'		=> 't38pt-usertpsource',
		  			  'help'		=> $this->bbf('hlp_fm_t38pt-usertpsource'),
			  		  'required'	=> false,
				      'checked'		=> $this->get_var('info','t38pt_usertpsource','var_val'),
							'default'		=> $element['t38pt_usertpsource']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_faxdetect'),
				    'name'		=> 'faxdetect',
				    'labelid'	=> 'faxdetect',
				    'key'		=> false,
				    'bbf'		=> 'faxdetect-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
  					'help'		=> $this->bbf('hlp_fm_faxdetect'),
	  				'required'	=> false,
				    'selected'	=> $this->get_var('info','faxdetect','var_val'),
				    'default'	=> $element['faxdetect']['default']),
			      $element['faxdetect']['value']);

?>
</div>

<div id="sb-part-jitterbuffer" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_jbenable'),
				      'name'		=> 'jbenable',
				      'labelid'		=> 'jbenable',
					  'help'		=> $this->bbf('hlp_fm_jbenable'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','jbenable','var_val'),
				      'default'		=> $element['jbenable']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_jbforce'),
				      'name'		=> 'jbforce',
				      'labelid'		=> 'jbforce',
					  'help'		=> $this->bbf('hlp_fm_jbforce'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','jbforce','var_val'),
				      'default'		=> $element['jbforce']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_jbmaxsize'),
				    'name'		=> 'jbmaxsize',
				    'labelid'	=> 'jbmaxsize',
				    'key'		=> false,
				    'bbf'		=> 'fm_jbmaxsize-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_jbmaxsize'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','jbmaxsize','var_val'),
				    'default'	=> $element['jbmaxsize']['default']),
			      $element['jbmaxsize']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_jbresyncthreshold'),
				    'name'		=> 'jbresyncthreshold',
				    'labelid'	=> 'jbresyncthreshold',
				    'key'		=> false,
				    'bbf'		=> 'fm_jbresyncthreshold-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_jbresyncthreshold'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','jbresyncthreshold','var_val'),
				    'default'	=> $element['jbresyncthreshold']['default']),
			      $element['jbresyncthreshold']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_jbimpl'),
				    'name'		=> 'jbimpl',
				    'labelid'	=> 'jbimpl',
				    'key'		=> false,
				    'bbf'		=> 'fm_jbimpl-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_jbimpl'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','jbimpl','var_val'),
				    'default'	=> $element['jbimpl']['default']),
			      $element['jbimpl']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_jblog'),
				      'name'		=> 'jblog',
				      'labelid'		=> 'jblog',
					  'help'		=> $this->bbf('hlp_fm_jblog'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','jblog','var_val'),
				      'default'		=> $element['jblog']['default'])),

		$form->text(array('desc'	=> $this->bbf('fm_jbtargetextra'),
				  'name'		=> 'jbtargetextra',
				  'labelid'		=> 'jbtargetextra',
				  'help'		=> $this->bbf('hlp_fm_jbtargetextra'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','jbtargetextra','var_val'),
				  'default'		=> $element['jbtargetextra']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'jbtargetextra')) ));

?>
</div>

<div id="sb-part-default" class="b-nodisplay">
<?php

if($context_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_context'),
				    'name'		=> 'context',
				    'labelid'	=> 'context',
				    'empty'		=> true,
				    'key'		=> 'identity',
				    'altkey'	=> 'name',
					'help'		=> $this->bbf('hlp_fm_context'),
					'required'	=> false,
				    'default'	=> $element['context']['default'],
				    'selected'	=> $this->get_var('info','context','var_val')),
			      $context_list);
endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_nat'),
				    'name'		=> 'nat',
				    'labelid'	=> 'nat',
				    'key'		=> false,
				    'bbf'		=> 'fm_nat-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_nat'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','nat','var_val'),
				    'default'	=> $element['nat']['default']),
			      $element['nat']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_dtmfmode'),
				    'name'		=> 'dtmfmode',
				    'labelid'	=> 'dtmfmode',
				    'key'		=> false,
				    'bbf'		=> 'fm_dtmfmode-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_dtmfmode'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','dtmfmode','var_val'),
				    'default'	=> $element['dtmfmode']['default']),
			      $element['dtmfmode']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_qualify'),
				    'name'		=> 'qualify',
				    'labelid'	=> 'qualify',
				    'key'		=> false,
				    'bbf'		=> 'fm_qualify-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_qualify'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','qualify','var_val'),
				    'default'	=> $element['qualify']['default']),
					$element['qualify']['value']),

     $form->select(array('desc'  => $this->bbf('fm_qualifyfreq'),
            'name'      => 'qualifyfreq',
            'labelid'   => 'qualifyfreq',
            'key'       => false,
            'bbf'       => 'time-opt',
            'bbfopt'    => array('argmode' => 'paramvalue',
            'time'      => array('from'=>'second', 'format'=>'%M%s')),
            'help'      => $this->bbf('hlp_fm_qualifyfreq'),
            'selected'  => $this->get_var('info','qualifyfreq','var_val'),
            'default'   => $element['qualifyfreq']['default']),
         $element['qualifyfreq']['value']),

     $form->select(array('desc'  => $this->bbf('fm_qualifygap'),
            'name'      => 'qualifygap',
            'labelid'   => 'qualifygap',
            'key'       => false,
            'bbf'       => 'fm_qualify-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_qualifygap'),
            'selected'  => $this->get_var('info','qualifygap','var_val'),
            'default'   => $element['qualifygap']['default']),
         $element['qualifygap']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_qualifypeers'),
				    'name'		=> 'qualifypeers',
				    'labelid'	=> 'qualifypeers',
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_qualifypeers'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','qualifypeers','var_val'),
				    'default'	=> $element['qualifypeers']['default']),
			      $element['qualifypeers']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_useclientcode'),
				      'name'		=> 'useclientcode',
				      'labelid'		=> 'useclientcode',
					  'help'		=> $this->bbf('hlp_fm_useclientcode'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','useclientcode','var_val'),
				      'default'		=> $element['useclientcode']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_progressinband'),
				    'name'		=> 'progressinband',
				    'labelid'	=> 'progressinband',
				    'key'		=> false,
				    'bbf'		=> 'fm_progressinband-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_progressinband'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','progressinband','var_val'),
				    'default'	=> $element['progressinband']['default']),
			      $element['progressinband']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_language'),
				    'name'		=> 'language',
				    'labelid'	=> 'language',
				    'key'		=> false,
					'help'		=> $this->bbf('hlp_fm_language'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','language','var_val'),
				    'default'	=> $element['language']['default']),
			      $element['language']['value']);

if($moh_list !== false):
	echo	$form->select(array('desc'	=> $this->bbf('fm_mohinterpret'),
				    'name'		=> 'mohinterpret',
				    'labelid'	=> 'mohinterpret',
				    'key'		=> 'category',
					'help'		=> $this->bbf('hlp_fm_mohinterpret'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','mohinterpret','var_val'),
				    'default'	=> $element['mohinterpret']['default']),
			      $moh_list),

		$form->select(array('desc'	=> $this->bbf('fm_mohsuggest'),
				    'name'		=> 'mohsuggest',
				    'labelid'	=> 'mohsuggest',
				    'empty'		=> true,
				    'key'		=> 'category',
					'help'		=> $this->bbf('hlp_fm_mohsuggest'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','mohsuggest','var_val'),
				    'default'	=> $element['mohsuggest']['default']),
			      $moh_list);
endif;

	echo	$form->text(array('desc'	=> $this->bbf('fm_vmexten'),
				  'name'		=> 'vmexten',
				  'labelid'		=> 'vmexten',
				  'help'		=> $this->bbf('hlp_fm_vmexten'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','vmexten','var_val'),
				  'default'		=> $element['vmexten']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'vmexten')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_trustrpid'),
				      'name'		=> 'trustrpid',
				      'labelid'		=> 'trustrpid',
					  'help'		=> $this->bbf('hlp_fm_trustrpid'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','trustrpid','var_val'),
				      'default'		=> $element['trustrpid']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_sendrpid'),
				      'name'		=> 'sendrpid',
				      'labelid'		=> 'sendrpid',
					  'help'		=> $this->bbf('hlp_fm_sendrpid'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','sendrpid','var_val'),
				      'default'		=> $element['sendrpid']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_directmedia'),
				    'name'		=> 'directmedia',
				    'labelid'	=> 'directmedia',
				    'bbf'		=> 'fm_directmedia-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_directmedia'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','directmedia','var_val'),
				    'default'	=> $element['directmedia']['default']),
			      $element['directmedia']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_insecure'),
				    'name'		=> 'insecure',
				    'labelid'	=> 'insecure',
				    'bbf'		=> 'fm_insecure-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					'help'		=> $this->bbf('hlp_fm_insecure'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','insecure','var_val'),
				    'default'	=> $element['insecure']['default']),
			      $element['insecure']['value']),
	
		$form->text(array('desc'	=> $this->bbf('fm_parkinglot'),
				  'name'		=> 'parkinglot',
				  'labelid'		=> 'parkinglot',
				  'help'		=> $this->bbf('hlp_fm_parkinglot'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','parkinglot','var_val'),
				  'default'		=> $element['parkinglot']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'parkinglot')) ));

?>
</div>

<div id="sb-part-realtime" class="b-nodisplay">
<?php
	echo	$form->checkbox(array('desc'	=> $this->bbf('fm_rtcachefriends'),
				      'name'		=> 'rtcachefriends',
				      'labelid'		=> 'rtcachefriends',
					  'help'		=> $this->bbf('hlp_fm_rtcachefriends'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','rtcachefriends','var_val'),
				      'default'		=> $element['rtcachefriends']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_rtupdate'),
				      'name'		=> 'rtupdate',
				      'labelid'		=> 'rtupdate',
					  'help'		=> $this->bbf('hlp_fm_rtupdate'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','rtupdate','var_val'),
				      'default'		=> $element['rtupdate']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_ignoreregexpire'),
				      'name'		=> 'ignoreregexpire',
				      'labelid'		=> 'ignoreregexpire',
					  'help'		=> $this->bbf('hlp_fm_ignoreregexpire'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','ignoreregexpire','var_val'),
				      'default'		=> $element['ignoreregexpire']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_rtsavesysname'),
				      'name'		=> 'rtsavesysname',
				      'labelid'		=> 'rtsavesysname',
					  'help'		=> $this->bbf('hlp_fm_rtsavesysname'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','rtsavesysname','var_val'),
				      'default'		=> $element['rtsavesysname']['default'])),

		$form->select(array('desc'	=> $this->bbf('fm_rtautoclear'),
				    'name'		=> 'rtautoclear',
				    'labelid'	=> 'rtautoclear',
				    'key'		=> false,
				    'bbf'		=> 'fm_rtautoclear-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'second',
									'format'	=> '%M%s')),
					'help'		=> $this->bbf('hlp_fm_rtautoclear'),
					'required'	=> false,
				    'selected'	=> $this->get_var('info','rtautoclear','var_val'),
				    'default'	=> $element['rtautoclear']['default']),
			      $element['rtautoclear']['value']);
?>
</div>

<div id="sb-part-internals" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_hash_users'),
				  'name'		=> 'hash_users',
				  'labelid'		=> 'hash_users',
				  'help'		=> $this->bbf('hlp_fm_hash_users'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','hash_users','var_val'),
				  'default'		=> $element['hash_users']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'hash_users')) )),

	$form->text(array('desc'	=> $this->bbf('fm_hash_peers'),
				  'name'		=> 'hash_peers',
				  'labelid'		=> 'hash_peers',
				  'help'		=> $this->bbf('hlp_fm_hash_peers'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','hash_peers','var_val'),
				  'default'		=> $element['hash_peers']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'hash_peers')) )),

	$form->text(array('desc'	=> $this->bbf('fm_hash_dialogs'),
				  'name'		=> 'hash_dialogs',
				  'labelid'		=> 'hash_dialogs',
				  'help'		=> $this->bbf('hlp_fm_hash_dialogs'),
				  'required'	=> false,
				  'value'		=> $this->get_var('info','hash_dialogs','var_val'),
				  'default'		=> $element['hash_dialogs']['default'],
				  'error'		=> $this->bbf_args('error',
					   		$this->get_var('error', 'hash_dialogs')) ));

?>
</div>

	<?=$form->submit(array('name'	=> 'submit',
			       'id'	=> 'it-submit',
			       'value'	=> $this->bbf('fm_bt-save')));?>
</form>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
