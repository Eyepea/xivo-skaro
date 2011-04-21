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

$info 	 = $this->get_var('info');
$element = $this->get_var('element');
//var_dump($info, $element);
$ca_authorities = $this->get_var('ca_authorities');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;
?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo $form->text(array('desc'	=> $this->bbf('fm_name'),
			  'name'	=> 'name',
			  'labelid'	=> 'name',
			  'size'	=> 25,
			  'default'	=> $element['name']['default'],
			  'value'	=> $this->get_var('id'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'name')) )),

	$form->checkbox(array('desc'	=> $this->bbf('fm_CA'),
				      'name'		=> 'CA',
				      'labelid'		=> 'CA',
					  //'help'		=> $this->bbf('hlp_fm_CA'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','CA'),
							'default'		=> $element['CA']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_autosigned'),
				      'name'		=> 'autosigned',
				      'labelid'		=> 'autosigned',
					  //'help'		=> $this->bbf('hlp_fm_autosigned'),
					  'required'	=> false,
				      'checked'		=> $this->get_var('info','autosigned'),
							'default'		=> $element['autosigned']['default'])),

	$form->select(array('desc'	=> $this->bbf('fm_ca_authority'),
				    'name'	=> 'ca_authority',
				    'labelid'	=> 'ca_authority',
						'empty' => false,
						'size' => 15,
						'key' => 'name',
						'altkey' => 'name',
				    'selected'	=> $this->get_var('info','ca_authority'),
				    'default'	=> $element['ca_authority']['default']),
			      $ca_authorities),

	$form->text(array('desc'	=> $this->bbf('fm_ca_password'),
			  'name'	=> 'ca_password',
			  'labelid'	=> 'ca_password',
			  'size'	=> 40,
			  'default'	=> $element['ca_password']['default'],
			  'value'	=> $this->get_var('info','ca_password'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'ca_password')) )),

	$form->text(array('desc'	=> $this->bbf('fm_password'),
			  'name'	=> 'password',
			  'labelid'	=> 'password',
			  'size'	=> 40,
			  'default'	=> $element['password']['default'],
			  'value'	=> $this->get_var('info','password'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'password')) )),

	$form->select(array('desc'	=> $this->bbf('fm_cipher'),
				    'name'	=> 'cipher',
				    'labelid'	=> 'cipher',
						'empty' => true,
						'size' => 15,
						'key' => 'name',
						'altkey' => 'name',
				    'selected'	=> $this->get_var('info','cipher'),
				    'default'	=> $element['cipher']['default']),
							array('aes','des','des3','idea')),

	$form->text(array('desc'	=> $this->bbf('fm_fingerprint'),
			  'name'	=> 'fingerprint',
			  'labelid'	=> 'fingerprint',
			  'size'	=> 40,
			  'default'	=> $element['fingerprint']['default'],
			  'value'	=> $this->get_var('info','fingerprint'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'fingerprint')) )),

	$form->select(array('desc'	=> $this->bbf('fm_length'),
				    'name'	=> 'length',
				    'labelid'	=> 'length',
						'empty' => false,
						'size' => 15,
						'key' => false,
				    'selected'	=> $this->get_var('info','length'),
				    'default'	=> 1024),//$element['length']['default']),
			      array(128,256,512,1024,2048,4096,8192)),//$element['length']['value']),

	  $form->text(array('desc'	=> $this->bbf('fm_length'),
			  'name'	=> 'length_text',
			  'labelid'	=> 'length_text',
			  'size'	=> 25,
			  'default'	=> $element['length']['default'],
			  'value'	=> $this->get_var('info','length'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'length')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_validity-start'),
			  'name'	=> 'validity-start',
			  'labelid'	=> 'validity-start',
			  'size'	=> 25,
			  'default'	=> $element['validity-start']['default'],
			  'value'	=> $this->get_var('info','validity-start'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'validity-start')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_validity-end'),
			  'name'	=> 'validity-end',
			  'labelid'	=> 'validity-end',
			  'size'	=> 25,
			  'default'	=> $element['validity-end']['default'],
			  'value'	=> $this->get_var('info','validity-end'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'validity-end')) )),

		// hidden field
	  $form->text(array(
			  'name'	=> 'validity-end-format',
			  'labelid'	=> 'validity-end-format',
			  'size'	=> 25)),

		'<br/>',

	  $form->text(array('desc'	=> $this->bbf('fm_subject_CN'),
			  'name'	=> 'subject[CN]',
			  'labelid'	=> 'subject-CN',
				'help'		=> $this->bbf('hlp_fm_CN'),
			  'size'	=> 15,
			  'default'	=> $element['subject']['CN']['default'],
			  'value'	=> $this->get_var('info','subject','CN'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'CN')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_subject_emailAddress'),
			  'name'	=> 'subject[emailAddress]',
			  'labelid'	=> 'subject-emailAddress',
			  'size'	=> 40,
			  'default'	=> $element['subject']['emailAddress']['default'],
			  'value'	=> $this->get_var('info','subject','emailAddress'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'emailAddress')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_subject_OU'),
			  'name'	=> 'subject[OU]',
			  'labelid'	=> 'subject-OU',
			  'size'	=> 15,
			  'default'	=> $element['subject']['OU']['default'],
			  'value'	=> $this->get_var('info','subject','OU'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'OU')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_subject_O'),
			  'name'	=> 'subject[O]',
			  'labelid'	=> 'subject-O',
			  'size'	=> 15,
			  'default'	=> $element['subject']['O']['default'],
			  'value'	=> $this->get_var('info','subject','O'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'O')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_subject_L'),
			  'name'	=> 'subject[L]',
			  'labelid'	=> 'subject-L',
			  'size'	=> 15,
			  'default'	=> $element['subject']['L']['default'],
			  'value'	=> $this->get_var('info','subject','L'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'L')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_subject_ST'),
			  'name'	=> 'subject[ST]',
			  'labelid'	=> 'subject-ST',
			  'size'	=> 15,
			  'default'	=> $element['subject']['ST']['default'],
			  'value'	=> $this->get_var('info','subject','ST'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'ST')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_subject_C'),
			  'name'	=> 'subject[C]',
			  'labelid'	=> 'subject-C',
			  'size'	=> 15,
			  'default'	=> $element['subject']['C']['default'],
			  'value'	=> $this->get_var('info','subject','C'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'subject', 'C')) ));
?>
</div>


<div id="sb-part-issuer" class="b-nodisplay">
<?php
/*
	echo $form->text(array('desc'	=> $this->bbf('fm_issuer_fingerprint'),
			  'name'	=> 'issuer[fingerprint]',
			  'labelid'	=> 'issuer-fingerprint',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['fingerprint']['default'],
			  'value'	=> $info['issuer']['fingerprint'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'fingerprint')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_validity-start'),
			  'name'	=> 'issuer[validity-start]',
			  'labelid'	=> 'issuer-validity-start',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['validity-start']['default'],
			  'value'	=> $info['issuer']['validity-start'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'validity-start')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_validity-end'),
			  'name'	=> 'issuer[validity-end]',
			  'labelid'	=> 'issuer-validity-end',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['validity-end']['default'],
			  'value'	=> $info['issuer']['validity-end'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'validity-end')) )),
 */

	  echo $form->text(array('desc'	=> $this->bbf('fm_issuer_CN'),
			  'name'	=> 'issuer[CN]',
			  'labelid'	=> 'issuer-CN',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['CN']['default'],
			  'value'	=> $this->get_var('info','issuer','CN'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'CN')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_emailAddress'),
			  'name'	=> 'issuer[emailAddress]',
			  'labelid'	=> 'issuer-emailAddress',
			  'size'	=> 40,
			  'default'	=> $element['issuer']['emailAddress']['default'],
			  'value'	=> $this->get_var('info','issuer','emailAddress'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'emailAddress')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_OU'),
			  'name'	=> 'issuer[OU]',
			  'labelid'	=> 'issuer-OU',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['OU']['default'],
			  'value'	=> $this->get_var('info','issuer','OU'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'OU')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_O'),
			  'name'	=> 'issuer[O]',
			  'labelid'	=> 'issuer-O',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['O']['default'],
			  'value'	=> $this->get_var('info','issuer','O'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'O')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_L'),
			  'name'	=> 'issuer[L]',
			  'labelid'	=> 'issuer-L',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['L']['default'],
			  'value'	=> $this->get_var('info','issuer','L'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'L')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_ST'),
			  'name'	=> 'issuer[ST]',
			  'labelid'	=> 'issuer-ST',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['ST']['default'],
			  'value'	=> $this->get_var('info','issuer','ST'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'ST')) )),

	  $form->text(array('desc'	=> $this->bbf('fm_issuer_C'),
			  'name'	=> 'issuer[C]',
			  'labelid'	=> 'issuer-C',
			  'size'	=> 15,
			  'default'	=> $element['issuer']['C']['default'],
			  'value'	=> $this->get_var('info','issuer','C'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'issuer', 'C')) ));
?>
</div>
