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

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_protocol_name'),
				  'name'	   => 'protocol[name]',
				  'labelid'	 => 'protocol-name',
					'size'	   => 15,
					'readonly' => $this->get_var('element','protocol','name','readonly'),
					'class'    => $this->get_var('element','protocol','name','class'),
					'default'  => $this->get_var('element','protocol','name','default'),
				  'value'	   => $info['protocol']['name'],
				  'error'	   => $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'name')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_secret'),
				  'name'	=> 'protocol[secret]',
				  'labelid'	=> 'protocol-secret',
				  'size'	=> 15,
					'readonly' => $this->get_var('element','protocol','secret','readonly'),
					'class'    => $this->get_var('element','protocol','secret','class'),
				  'default'	=> $this->get_var('element', 'protocol', 'secret', 'default'),
				  'value'	=> $this->get_var('info','protocol','secret'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'secret')) )),

		$form->text(array('desc'	=> $this->bbf('fm_linefeatures_number'),
				  'name'	=> 'linefeatures[number]',
				  'labelid'	=> 'linefeatures-number',
				  'size'	=> 6,
				  'disabled'	=> true,
				  'readonly' => true,
				  'class'    => 'it-disabled',
				  #'readonly' => $this->get_var('element','linefeatures','number','readonly'),
				  #'class'    => $this->get_var('element','linefeatures','number','class'),
				  'value'	=> $this->get_var('info','linefeatures','number'),
				  'error'	=> $this->bbf_args('error',$this->get_var('error', 'linefeatures', 'number')) ));

	if($context_list !== false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_protocol_context'),
					    'name'		=> 'protocol[context]',
					    'labelid'	=> 'protocol-context',
					 	'disabled'	=> $hasnumber,
						'class'    	=> ($hasnumber ? 'it-disabled' : ''),
					    'key'		=> 'identity',
					    'altkey'	=> 'name',
					    'selected'	=> $context),
				      $context_list);
	else:
		echo	'<div id="fd-protocol-context" class="txt-center">',
			$url->href_htmln($this->bbf('create_context'),
					'service/ipbx/system_management/context',
					'act=add'),
			'</div>';
	endif;

	echo	$form->select(array('desc'	=> $this->bbf('fm_protocol_nat'),
				    'name'	=> 'protocol[nat]',
				    'labelid'	=> 'sccp-protocol-nat',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['sccp']['nat']['default'],
				    'selected'	=> $this->get_var('info','protocol','nat')),
			      $element['protocol']['sccp']['nat']['value']);
?>
</div>

<div id="sb-part-signalling" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_protocol_dtmfmode'),
				    'name'		=> 'protocol[dtmfmode]',
				    'labelid'	=> 'sccp-protocol-dtmfmode',
				    'empty'		=> true,
				    'key'		=> false,
				    'bbf'		=> 'fm_protocol_dtmfmode-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['sccp']['dtmfmode']['default'],
				    'selected'	=> $this->get_var('info','protocol','dtmfmode')),
			      $element['protocol']['sccp']['dtmfmode']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_park'),
				    'name'	=> 'protocol[park]',
				    'labelid'	=> 'protocol-park',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_park'),
				    'default'	=> $element['protocol']['sccp']['park']['default'],
				    'selected'	=> $this->get_var('info','protocol','park')),
			      $element['protocol']['sccp']['park']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_cfwdall'),
				    'name'	=> 'protocol[cfwdall]',
				    'labelid'	=> 'protocol-cfwdall',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_cfwdall'),
				    'default'	=> $element['protocol']['sccp']['cfwdall']['default'],
				    'selected'	=> $this->get_var('info','protocol','cfwdall')),
			      $element['protocol']['sccp']['cfwdall']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_cfwdbusy'),
				    'name'	=> 'protocol[cfwdbusy]',
				    'labelid'	=> 'protocol-cfwdbusy',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_cfwdbusy'),
				    'default'	=> $element['protocol']['sccp']['cfwdbusy']['default'],
				    'selected'	=> $this->get_var('info','protocol','cfwdbusy')),
			      $element['protocol']['sccp']['cfwdbusy']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_cfwdnoanswer'),
				    'name'	=> 'protocol[cfwdnoanswer]',
				    'labelid'	=> 'protocol-cfwdnoanswer',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_cfwdnoanswer'),
				    'default'	=> $element['protocol']['sccp']['cfwdnoanswer']['default'],
				    'selected'	=> $this->get_var('info','protocol','cfwdnoanswer')),
			      $element['protocol']['sccp']['cfwdnoanswer']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_pickupexten'),
				    'name'	=> 'protocol[pickupexten]',
				    'labelid'	=> 'protocol-pickupexten',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_pickupexten'),
				    'default'	=> $element['protocol']['sccp']['pickupexten']['default'],
				    'selected'	=> $this->get_var('info','protocol','pickupexten')),
			      $element['protocol']['sccp']['pickupexten']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_pickupcontext'),
					    'name'	=> 'protocol[pickupcontext]',
					    'labelid'	=> 'protocol-pickupcontext',
					    'key'	=> 'identity',
					    'altkey'	=> 'name',
					    'help'		=> $this->bbf('hlp_fm_pickupcontext'),
					    'selected'	=> $this->get_var('info', 'protocol', 'pickupcontext')),
				      $context_list),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_pickupmodeanswer'),
				    'name'	=> 'protocol[pickupmodeanswer]',
				    'labelid'	=> 'protocol-pickupmodeanswer',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_pickupmodeanswer-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_pickupmodeanswer'),
				    'default'	=> $element['protocol']['sccp']['pickupmodeanswer']['default'],
				    'selected'	=> $this->get_var('info','protocol','pickupmodeanswer')),
			      $element['protocol']['sccp']['pickupmodeanswer']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_dnd'),
				    'name'	=> 'protocol[dnd]',
				    'labelid'	=> 'protocol-dnd',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_dnd'),
				    'default'	=> $element['protocol']['sccp']['dnd']['default'],
				    'selected'	=> $this->get_var('info','protocol','dnd')),
			      $element['protocol']['sccp']['dnd']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_directrtp'),
				    'name'	=> 'protocol[directrtp]',
				    'labelid'	=> 'protocol-directrtp',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_directrtp'),
				    'default'	=> $element['protocol']['sccp']['directrtp']['default'],
				    'selected'	=> $this->get_var('info','protocol','directrtp')),
			      $element['protocol']['sccp']['directrtp']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_earlyrtp'),
				    'name'	=> 'protocol[earlyrtp]',
				    'labelid'	=> 'protocol-earlyrtp',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_earlyrtp',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_earlyrtp'),
				    'default'	=> $element['protocol']['sccp']['earlyrtp']['default'],
				    'selected'	=> $this->get_var('info','protocol','earlyrtp')),
			      $element['protocol']['sccp']['earlyrtp']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_private'),
				    'name'	=> 'protocol[private]',
				    'labelid'	=> 'protocol-private',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_private'),
				    'default'	=> $element['protocol']['sccp']['private']['default'],
				    'selected'	=> $this->get_var('info','protocol','private')),
			      $element['protocol']['sccp']['private']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_privacy'),
				    'name'	=> 'protocol[privacy]',
				    'labelid'	=> 'protocol-privacy',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_privacy',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_privacy'),
				    'default'	=> $element['protocol']['sccp']['privacy']['default'],
				    'selected'	=> $this->get_var('info','protocol','privacy')),
			      $element['protocol']['sccp']['privacy']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_mwilamp'),
				    'name'	=> 'protocol[mwilamp]',
				    'labelid'	=> 'protocol-mwilamp',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_mwilamp',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_mwilamp'),
				    'default'	=> $element['protocol']['sccp']['mwilamp']['default'],
				    'selected'	=> $this->get_var('info','protocol','mwilamp')),
			      $element['protocol']['sccp']['mwilamp']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_mwioncall'),
				    'name'	=> 'protocol[mwioncall]',
				    'labelid'	=> 'protocol-mwioncall',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_mwioncall'),
				    'default'	=> $element['protocol']['sccp']['mwioncall']['default'],
				    'selected'	=> $this->get_var('info','protocol','mwioncall')),
			      $element['protocol']['sccp']['mwioncall']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_echocancel'),
				    'name'	=> 'protocol[echocancel]',
				    'labelid'	=> 'protocol-echocancel',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_echocancel'),
				    'default'	=> $element['protocol']['sccp']['echocancel']['default'],
				    'selected'	=> $this->get_var('info','protocol','echocancel')),
			      $element['protocol']['sccp']['echocancel']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_silencesuppression'),
				    'name'	=> 'protocol[silencesuppression]',
				    'labelid'	=> 'protocol-silencesuppression',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_silencesuppression'),
				    'default'	=> $element['protocol']['sccp']['silencesuppression']['default'],
				    'selected'	=> $this->get_var('info','protocol','silencesuppression')),
			      $element['protocol']['sccp']['silencesuppression']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_incominglimit'),
				    'name'	=> 'protocol[incominglimit]',
				    'labelid'	=> 'protocol-incominglimit',
				    'empty'	=> true,
				    'key'	=> false,
					  'help'		=> $this->bbf('hlp_fm_incominglimit'),
				    'default'	=> $element['protocol']['sccp']['incominglimit']['default'],
				    'selected'	=> $this->get_var('info','protocol','incominglimit')),
			      $element['protocol']['sccp']['incominglimit']['value']);
?>
</div>

<div id="sb-part-advanced" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_protocol_callerid'),
				  'name'	=> 'protocol[callerid]',
				  'labelid'	=> 'protocol-callerid',
				  'value'	=> $this->get_var('info','protocol','callerid'),
				  'size'	=> 15,
				  'notag'	=> false,
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'callerid')) )),

		$form->text(array('desc'	=> '&nbsp;',
				  'name'	=> 'protocol[host-static]',
				  'labelid'	=> 'protocol-host-static',
				  'size'	=> 15,
				  'value'	=> ($host_static === true ? $host : ''),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'host-static')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_permit'),
				  'name'	=> 'protocol[permit]',
				  'labelid'	=> 'protocol-permit',
				  'size'	=> 20,
				  'value'	=> $this->get_var('info','protocol','permit'),
				  'error'   => $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'permit')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_deny'),
				  'name'	=> 'protocol[deny]',
				  'labelid'	=> 'protocol-deny',
				  'size'	=> 20,
				  'value'	=> $this->get_var('info','protocol','deny'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'deny')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_keepalive'),
				  'name'	=> 'protocol[keepalive]',
				  'labelid'	=> 'protocol-keepalive',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','keepalive'),
				  'help'		=> $this->bbf('hlp_fm_keepalive'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'keepalive')) )),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_tzoffset'),
				    'name'	=> 'protocol[tzoffset]',
				    'labelid'	=> 'protocol-tzoffset',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_tzoffset',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_tzoffset'),
				    'default'	=> $element['protocol']['sccp']['tzoffset']['default'],
				    'selected'	=> $this->get_var('info','protocol','tzoffset')),
			      $element['protocol']['sccp']['tzoffset']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_imageversion'),
				  'name'	=> 'protocol[imageversion]',
				  'labelid'	=> 'protocol-imageversion',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','imageversion'),
				  'help'		=> $this->bbf('hlp_fm_imageversion'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'imageversion')) )),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_trustphoneip'),
				    'name'	=> 'protocol[trustphoneip]',
				    'labelid'	=> 'protocol-trustphoneip',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_trustphoneip'),
				    'default'	=> $element['protocol']['sccp']['trustphoneip']['default'],
				    'selected'	=> $this->get_var('info','protocol','trustphoneip')),
			      $element['protocol']['sccp']['trustphoneip']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_secondary_dialtone_digits'),
				    'name'	=> 'protocol[secondary_dialtone_digits]',
				    'labelid'	=> 'protocol-secondary_dialtone_digits',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_digit',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
					  'help'		=> $this->bbf('hlp_fm_dialtone_digits'),
				    'default'	=> $element['protocol']['sccp']['secondary_dialtone_digits']['default'],
				    'selected'	=> $this->get_var('info','protocol','secondary_dialtone_digits')),
			      $element['protocol']['sccp']['secondary_dialtone_digits']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_secondary_dialtone_tone'),
				  'name'	=> 'protocol[secondary_dialtone_tone]',
				  'labelid'	=> 'protocol-secondary_dialtone_tone',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','secondary_dialtone_tone'),
				  'help'		=> $this->bbf('hlp_fm_dialtone_tone'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'secondary_dialtone_tone')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_audio_tos'),
				  'name'	=> 'protocol[audio_tos]',
				  'labelid'	=> 'protocol-audio_tos',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','audio_tos'),
				  'help'		=> $this->bbf('hlp_fm_audio_tos'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'audio_tos')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_audio_cos'),
				  'name'	=> 'protocol[audio_cos]',
				  'labelid'	=> 'protocol-audio_cos',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','audio_cos'),
				  'help'		=> $this->bbf('hlp_fm_audio_cos'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'audio_cos')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_video_tos'),
				  'name'	=> 'protocol[video_tos]',
				  'labelid'	=> 'protocol-video_tos',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','video_tos'),
				  'help'		=> $this->bbf('hlp_fm_video_tos'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'video_tos')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_video_cos'),
				  'name'	=> 'protocol[video_cos]',
				  'labelid'	=> 'protocol-video_cos',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','video_cos'),
				  'help'		=> $this->bbf('hlp_fm_video_cos'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'video_cos')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_adhocnumber'),
				  'name'	=> 'protocol[adhocnumber]',
				  'labelid'	=> 'protocol-adhocnumber',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','adhocnumber'),
				  'help'		=> $this->bbf('hlp_fm_adhocnumber'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'adhocnumber')) ));

?>
</div>