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

	echo	$form->select(array('desc'	=> $this->bbf('fm_protocol-encryption'),
				    'name'	    => 'protocol[encryption]',
				    'labelid'	  => 'iax-protocol-encryption',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_protocol-encryption'),
            'selected'  => $info['protocol']['encryption'],
            'default'   => $element['protocol']['iax']['encryption']['default']),
         $element['protocol']['iax']['encryption']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol-forceencryption'),
				    'name'	    => 'protocol[forceencryption]',
				    'labelid'	  => 'iax-protocol-forceencryption',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_protocol-forceencryption'),
            'selected'  => $this->get_var('info', 'protocol','forceencryption'),
            'default'   => $element['protocol']['iax']['forceencryption']['default']),
         $element['protocol']['iax']['forceencryption']['value']);

/*
		$form->select(array('desc'	=> $this->bbf('fm_protocol_parkinglot'),
					'name'	=> 'protocol[parkinglot]',
					'labelid'   => 'procotol-parkinglot',
					'help'      => $this->bbf('hlp_fm_parkinglot'),
					'required'  => false,
					'key'       => 'name',
					'altkey'    => 'id',
					'empty'     => true,
					'selected'  => $this->get_var('info','protocol','parkinglot')),
					//'default'     => $element['protocol']['parkinglot']['default']),
		$this->get_var('parking_list'));
*/
?>
</div>

<div id="sb-part-signalling" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_protocol_qualify'),
				    'name'		=> 'protocol[qualify]',
				    'labelid'	=> 'iax-protocol-qualify',
				    'key'		=> false,
				    'bbf'		=> 'fm_protocol_qualify-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['qualify']['default'],
				    'selected'	=> $qualify),
			      $element['protocol']['iax']['qualify']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_qualifysmoothing'),
				    'name'		=> 'protocol[qualifysmoothing]',
				    'labelid'	=> 'protocol-qualifysmoothing',
				    'key'		=> false,
				    'bbf'		=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['qualifysmoothing']['default'],
				    'selected'	=> $this->get_var('info','protocol','qualifysmoothing')),
			      $element['protocol']['iax']['qualifysmoothing']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_qualifyfreqok'),
				    'name'		=> 'protocol[qualifyfreqok]',
				    'labelid'	=> 'protocol-qualifyfreqok',
				    'key'		=> false,
				    'bbf'		=> 'fm_protocol_qualifyfreq-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'millisecond',
									'format'	=> '%M%s%ms')),
				    'default'	=> $element['protocol']['iax']['qualifyfreqok']['default'],
				    'selected'	=> $this->get_var('info','protocol','qualifyfreqok')),
			      $element['protocol']['iax']['qualifyfreqok']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_qualifyfreqnotok'),
				    'name'		=> 'protocol[qualifyfreqnotok]',
				    'labelid'	=> 'protocol-qualifyfreqnotok',
				    'key'		=> false,
				    'bbf'		=> 'fm_protocol_qualifyfreq-opt',
				    'bbfopt'	=> array('argmode'	=> 'paramvalue',
							 'time'		=> array(
									'from'		=> 'millisecond',
									'format'	=> '%M%s%ms')),
				    'default'	=> $element['protocol']['iax']['qualifyfreqnotok']['default'],
				    'selected'	=> $this->get_var('info','protocol','qualifyfreqnotok')),
			      $element['protocol']['iax']['qualifyfreqnotok']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_pickupcontext'),
					    'name'	=> 'protocol[pickupcontext]',
					    'labelid'	=> 'protocol-pickupcontext',
					    'key'	=> 'identity',
					    'altkey'	=> 'name',
					    'help'		=> $this->bbf('hlp_fm_pickupcontext'),
					    'selected'	=> $this->get_var('info', 'protocol', 'pickupcontext')),
				      $context_list),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_jitterbuffer'),
				    'name'	=> 'protocol[jitterbuffer]',
				    'labelid'	=> 'protocol-jitterbuffer',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['jitterbuffer']['default'],
				    'selected'	=> $this->get_var('info','protocol','jitterbuffer')),
			      $element['protocol']['iax']['jitterbuffer']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_forcejitterbuffer'),
				    'name'	=> 'protocol[forcejitterbuffer]',
				    'labelid'	=> 'protocol-forcejitterbuffer',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['forcejitterbuffer']['default'],
				    'selected'	=> $this->get_var('info','protocol','forcejitterbuffer')),
			      $element['protocol']['iax']['forcejitterbuffer']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_codecpriority'),
				    'name'	=> 'protocol[codecpriority]',
				    'labelid'	=> 'protocol-codecpriority',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_protocol_codecpriority-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['codecpriority']['default'],
				    'selected'	=> $this->get_var('info','protocol','codecpriority')),
			      $element['protocol']['iax']['codecpriority']['value']);
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

		$form->checkbox(array('desc'	=> $this->bbf('fm_protocol_sendani'),
				      'name'	=> 'protocol[sendani]',
				      'labelid'	=> 'protocol-sendani',
				      'default'	=> $element['protocol']['iax']['sendani']['default'],
				      'checked'	=> $this->get_var('info','protocol','sendani'))),

		$form->text(array('desc'	=> '&nbsp;',
				  'name'	=> 'protocol[host-static]',
				  'labelid'	=> 'protocol-host-static',
				  'size'	=> 15,
				  'value'	=> ($host_static === true ? $host : ''),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'host-static')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_mask'),
				  'name'	=> 'protocol[mask]',
				  'labelid'	=> 'protocol-mask',
				  'size'	=> 15,
				  'default'	=> $element['protocol']['iax']['mask']['default'],
				  'value'	=> $this->get_var('info','protocol','mask'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'mask')) )),

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

		$form->select(array('desc'	=> $this->bbf('fm_protocol_maxauthreq'),
				    'name'	=> 'protocol[maxauthreq]',
				    'labelid'	=> 'protocol-maxauthreq',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_protocol_maxauthreq-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['maxauthreq']['default'],
				    'selected'	=> $this->get_var('info','protocol','maxauthreq')),
			      $element['protocol']['iax']['maxauthreq']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_adsi'),
				    'name'	=> 'protocol[adsi]',
				    'labelid'	=> 'protocol-adsi',
				    'empty'	=> true,
				    'key'	=> false,
				    'bbf'	=> 'fm_bool-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['adsi']['default'],
				    'selected'	=> $this->get_var('info','protocol','adsi')),
			      $element['protocol']['iax']['adsi']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_protocol_requirecalltoken'),
				    'name'	=> 'protocol[requirecalltoken]',
				    'labelid'	=> 'protocol-requirecalltoken',
				    'key'	=> false,
				    'bbf'	=> 'fm_protocol_requirecalltoken-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['protocol']['iax']['requirecalltoken']['default'],
				    'selected'	=> $this->get_var('info', 'protocol', 'requirecalltoken')),
			      $element['protocol']['iax']['requirecalltoken']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_keepalive'),
				  'name'	=> 'protocol[keepalive]',
				  'labelid'	=> 'protocol-keepalive',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','keepalive'),
				  'help'		=> $this->bbf('hlp_fm_keepalive'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'keepalive')) )),

		$form->text(array('desc'	=> $this->bbf('fm_protocol_imageversion'),
				  'name'	=> 'protocol[imageversion]',
				  'labelid'	=> 'protocol-imageversion',
				  'size'	=> 15,
				  'value'	=> $this->get_var('info','protocol','imageversion'),
				  'help'		=> $this->bbf('hlp_fm_imageversion'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'imageversion')) )),

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
						   $this->get_var('error', 'protocol', 'adhocnumber')) )),

     $form->select(array('desc'  => $this->bbf('fm_protocol-immediate'),
            'name'      => 'protocol[immediate]',
            'labelid'   => 'protocol-immediate',
            'key'       => false,
            'empty'     => true,
            'bbf'       => 'fm_bool-opt',
            'bbfopt'    => array('argmode' => 'paramvalue'),
            'help'      => $this->bbf('hlp_fm_protocol-immediate'),
            'selected'  => isset($info['protocol']['immediate']) ? $info['protocol']['immediate'] : null,
            'default'   => $element['protocol']['iax']['immediate']['default']),
         $element['protocol']['iax']['immediate']['value']);

?>
</div>
