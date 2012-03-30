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
$url = $this->get_module('url');

$info = $this->get_var('info');
$element = $this->get_var('element');

$context_list = $this->get_var('contexts');
$moh = $this->get_var('moh');

?>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_parkinglot_name'),
				  'name'	=> 'parkinglot[name]',
				  'labelid'	=> 'parkinglot-name',
				  'size'	=> 15,
				  'default'	=> $element['parkinglot']['name']['default'],
				  'value'	=> $info['name'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'parkinglot', 'name')) ));

	if($context_list !== false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_parkinglot_context'),
					    'name'	=> 'parkinglot[context]',
					    'labelid'	=> 'parkinglot-context',
					    'key'	=> 'identity',
					    'altkey'	=> 'name',
					    'selected'	=> $info['context']),
				      $context_list);
	else:
		echo	'<div id="fd-parkinglot-context" class="txt-center">',
			$url->href_htmln($this->bbf('create_context'),
					'service/ipbx/system_management/context',
					'act=add'),
			'</div>';
	endif;

		echo $form->text(array('desc'	=> $this->bbf('fm_parkinglot_extension'),
				  'name'	=> 'parkinglot[extension]',
				  'labelid'	=> 'parkinglot-extension',
				  'size'	=> 15,
				  'default'	=> $element['parkinglot']['extension']['default'],
				  'value'	=> $info['extension'],
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'parkinglot', 'extension')) )),

		$form->text(array('desc'	=> $this->bbf('fm_parkinglot_positions'),
				  'name'	=> 'parkinglot[positions]',
				  'labelid'	=> 'parkinglot-positions',
				  'size'	=> 15,
				  'default'	=> $element['parkinglot']['positions']['default'],
				  'value'	=> $info['positions'],
				  #'help'  => $this->bbf('hlp_fm_positions'),
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'parkinglot', 'positions')) )),

		$form->checkbox(array('desc'	=> $this->bbf('fm_parkinglot_next'),
				      'name'	=> 'parkinglot[next]',
				      'labelid'	=> 'parkinglot-next',
							'help'      => $this->bbf('hlp_fm_next'),
				      'default'	=> $element['parkinglot']['next']['default'],
							'checked'	=> $this->get_var('info','next')=='1')),

		$form->text(array('desc'	=> $this->bbf('fm_parkinglot_duration'),
				  'name'	=> 'parkinglot[duration]',
				  'labelid'	=> 'parkinglot-duration',
				  'size'	=> 15,
				  'default'	=> $element['parkinglot']['duration']['default'],
					'value'	=> $info['duration'],
				  'error'	=> $this->bbf_args('error',
						$this->get_var('error', 'parkinglot', 'duration')) )),

		$form->select(array('desc'	=> $this->bbf('fm_parkinglot_calltransfers'),
					    'name'	=> 'parkinglot[calltransfers]',
							'labelid'	=> 'parkinglot-calltransfers',
							'empty' => true,
					    'key'	=> false,
							'bbf'	=> 'parkinglot_call',
					    'selected'	=> $info['calltransfers']),
			      $element['parkinglot']['calltransfers']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_parkinglot_callreparking'),
					    'name'	=> 'parkinglot[callreparking]',
					    'labelid'	=> 'parkinglot-callreparking',
							'empty' => true,
					    'key'	=> false,
							'bbf'	=> 'parkinglot_call',
					    'selected'	=> $info['callreparking']),
			      $element['parkinglot']['callreparking']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_parkinglot_callhangup'),
					    'name'	=> 'parkinglot[callhangup]',
					    'labelid'	=> 'parkinglot-callhangup',
							'empty' => true,
					    'key'	=> false,
							'bbf'	=> 'parkinglot_call',
					    'selected'	=> $info['callhangup']),
			      $element['parkinglot']['callhangup']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_parkinglot_callrecording'),
					    'name'	=> 'parkinglot[callrecording]',
					    'labelid'	=> 'parkinglot-callrecording',
							'empty' => true,
					    'key'	=> false,
							'bbf'	=> 'parkinglot_call',
					    'selected'	=> $info['callrecording']),
			      $element['parkinglot']['callrecording']['value']),

		$form->select(array('desc'	=> $this->bbf('fm_parkinglot_musicclass'),
					    'name'	=> 'parkinglot[musicclass]',
					    'labelid'	=> 'parkinglot-musicclass',
							'empty' => true,
					    'key'	=> 'category',
					    'altkey'	=> 'category',
					    'selected'	=> $info['musicclass']),
					$moh),

		$form->checkbox(array('desc'	=> $this->bbf('fm_parkinglot_hints'),
				      'name'	=> 'parkinglot[hints]',
				      'labelid'	=> 'parkinglot-hints',
				      'default'	=> $element['parkinglot']['hints']['default'],
							'checked'	=> $this->get_var('info','hints')=='1'));

?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-parkinglot-description" for="it-parkinglot-description"><?=$this->bbf('fm_parkinglot_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'parkinglot[description]',
					 'id'		=> 'it-parkinglot-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['parkinglot']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'parkinglot', 'description')) ),
				   $info['description']);?>
	</div>

