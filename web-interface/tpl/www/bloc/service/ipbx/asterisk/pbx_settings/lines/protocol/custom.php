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
	echo	$form->text(array('desc'	=> $this->bbf('fm_protocol_interface'),
				  'name'	=> 'protocol[interface]',
				  'labelid'	=> 'protocol-interface',
				  'size'	=> 15,
				  'default'	=> $element['protocol']['custom']['interface']['default'],
				  'value'	=> $this->get_var('info','protocol','interface'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'protocol', 'interface')) ));

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
?>
</div>

<div id="sb-part-signalling" class="b-nodisplay">
<?php
	echo	$form->select(array('desc'	=> $this->bbf('fm_protocol_pickupcontext'),
					    'name'	=> 'protocol[pickupcontext]',
					    'labelid'	=> 'protocol-pickupcontext',
					    'key'	=> 'identity',
					    'altkey'	=> 'name',
					    'help'		=> $this->bbf('hlp_fm_pickupcontext'),
					    'selected'	=> $this->get_var('info', 'protocol', 'pickupcontext')),
				      $context_list);
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
						   $this->get_var('error', 'protocol', 'adhocnumber')) ));

?>
</div>
