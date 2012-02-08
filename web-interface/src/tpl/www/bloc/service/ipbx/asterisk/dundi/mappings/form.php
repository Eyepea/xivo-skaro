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

$form    = &$this->get_module('form');
$url     = $this->get_module('url');

$info    = $this->get_var('info');
$element = $this->get_var('element');
$contexts = $this->get_var('contexts');
$trunks   = $this->get_var('trunks');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

	$penalties    = array();
	if (is_array($info) && array_key_exists('changes', $info))
		$penalties = $info['changes'];

	$signs        = array('+','-','=');
?>

<div id="sb-part-first" class="b-nodisplay">
<br/>
<?php
	echo $form->text(array('desc'	=> $this->bbf('fm_dundimapping_name'),
			  'name'	=> 'dundimapping[name]',
			  'labelid'	=> 'dundimapping-name',
			  'size'	=> 15,
			  'default'	=> $element['dundimapping']['name']['default'],
			  'value'	=> $info['dundimapping']['name'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundimapping', 'name')) )),

	$form->select(array('desc'	=> $this->bbf('fm_dundimapping_context'),
				    'name'	=> 'dundimapping[context]',
				    'labelid'	=> 'dundimapping-context',
						'empty' => false,
						'size' => 15,
						'key' => 'name',
						'altkey' => 'name',
				    'selected'	=> $this->get_var('info','dundimapping','context'),
				    'default'	=> $element['dundimapping']['context']['default']),
			      $contexts),

	$form->text(array('desc'	=> $this->bbf('fm_dundimapping_weight'),
			  'name'	=> 'dundimapping[weight]',
			  'labelid'	=> 'dundimapping-weight',
			  'size'	=> 15,
			  'default'	=> $element['dundimapping']['weight']['default'],
			  'value'	=> $info['dundimapping']['weight'],
		    'help'	=> $this->bbf('hlp_fm_dundimapping-weight'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundimapping', 'weight')) )),

	$form->select(array('desc'	=> $this->bbf('fm_dundimapping_trunk'),
				    'name'	=> 'dundimapping[trunk]',
				    'labelid'	=> 'dundimapping-trunk',
						'empty' => false,
						'size' => 15,
						'key' => 'identity',
						'altkey' => 'id',
				    'selected'	=> $this->get_var('info','dundimapping','trunk'),
				    'default'	=> $element['dundimapping']['trunk']['default']),
			      $trunks),

	$form->text(array('desc'	=> $this->bbf('fm_dundimapping_number'),
			  'name'	=> 'dundimapping[number]',
			  'labelid'	=> 'dundimapping-number',
			  'size'	=> 15,
			  'default'	=> $element['dundimapping']['number']['default'],
			  'value'	=> $info['dundimapping']['number'],
		    'help'	=> $this->bbf('hlp_fm_dundimapping-number'),
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundimapping', 'number')) ));
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-dundimapping-description" for="it-dundimapping-description"><?=$this->bbf('fm_dundimapping_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'dundimapping[description]',
					 'id'		=> 'it-dundimapping-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['dundimapping']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'dundimapping', 'description')) ),
				   $info['dundimapping']['description']);?>
	</div>
</div>

<div id="sb-part-options" class="b-nodisplay">
<br/>
<?php
		echo $form->checkbox(array('desc'	=> $this->bbf('fm_dundimapping_nounsolicited'),
				  	'name'		  => 'dundimapping[nounsolicited]',
						'labelid'	  => 'dundimapping-nounsolicited',
					  'help'	  	=> $this->bbf('hlp_fm_dundimapping-nounsolicited'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','dundimapping','nounsolicited'),
			      'default'		=> $element['dundimapping']['nounsolicited']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dundimapping_nocomunsolicit'),
				  	'name'		  => 'dundimapping[nocomunsolicit]',
						'labelid'	  => 'dundimapping-nocomunsolicit',
					  'help'	  	=> $this->bbf('hlp_fm_dundimapping-nocomunsolicit'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','dundimapping','nocomunsolicit'),
			      'default'		=> $element['dundimapping']['nocomunsolicit']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dundimapping_residential'),
				  	'name'		  => 'dundimapping[residential]',
						'labelid'	  => 'dundimapping-residential',
					  'help'	  	=> $this->bbf('hlp_fm_dundimapping-residential'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','dundimapping','residential'),
			      'default'		=> $element['dundimapping']['residential']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dundimapping_commercial'),
				  	'name'		  => 'dundimapping[commercial]',
						'labelid'	  => 'dundimapping-commercial',
					  'help'	  	=> $this->bbf('hlp_fm_dundimapping-commercial'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','dundimapping','commercial'),
			      'default'		=> $element['dundimapping']['commercial']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dundimapping_mobile'),
				  	'name'		  => 'dundimapping[mobile]',
						'labelid'	  => 'dundimapping-mobile',
					  'help'	  	=> $this->bbf('hlp_fm_dundimapping-mobile'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','dundimapping','mobile'),
			      'default'		=> $element['dundimapping']['mobile']['default'])),

		$form->checkbox(array('desc'	=> $this->bbf('fm_dundimapping_nopartial'),
				  	'name'		  => 'dundimapping[nopartial]',
						'labelid'	  => 'dundimapping-nopartial',
					  'help'	  	=> $this->bbf('hlp_fm_dundimapping-nopartial'),
					  'required'	=> false,
			      'checked'		=> $this->get_var('info','dundimapping','nopartial'),
			      'default'		=> $element['dundimapping']['nopartial']['default']));

?>

</div>
