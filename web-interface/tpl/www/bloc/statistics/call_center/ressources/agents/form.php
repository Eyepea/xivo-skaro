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

$element = $this->get_var('element');
$info = $this->get_var('info');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_agentfeatures_firstname'),
				  'name'	=> 'agentfeatures[firstname]',
				  'labelid'	=> 'agentfeatures-firstname',
				  'size'	=> 15,
				  'default'	=> $element['agentfeatures']['firstname']['default'],
				  'value'	=> $info['agentfeatures']['firstname'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','agentfeatures','firstname')))),

		$form->text(array('desc'	=> $this->bbf('fm_agentfeatures_lastname'),
				  'name'	=> 'agentfeatures[lastname]',
				  'labelid'	=> 'agentfeatures-lastname',
				  'size'	=> 15,
				  'default'	=> $element['agentfeatures']['lastname']['default'],
				  'value'	=> $info['agentfeatures']['lastname'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','agentfeatures','lastname')))),

		$form->text(array('desc'	=> $this->bbf('fm_agentfeatures_number'),
				  'name'	=> 'agentfeatures[number]',
				  'labelid'	=> 'agentfeatures-number',
				  'size'	=> 15,
				  'default'	=> $element['agentfeatures']['number']['default'],
				  'value'	=> $info['agentfeatures']['number'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','agentfeatures','number')))),

		$form->text(array('desc'	=> $this->bbf('fm_agentfeatures_passwd'),
				  'name'	=> 'agentfeatures[passwd]',
				  'labelid'	=> 'agentfeatures-passwd',
				  'size'	=> 15,
				  'default'	=> $element['agentfeatures']['passwd']['default'],
				  'value'	=> $info['agentfeatures']['passwd'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','agentfeatures','passwd'))));

	echo	$form->select(array('desc'	=> $this->bbf('fm_agentfeatures_language'),
				    'name'	=> 'agentfeatures[language]',
				    'labelid'	=> 'agentfeatures-language',
				    'key'	=> false,
				    'empty' => true,
				    'default'	=> $element['agentfeatures']['language']['default'],
				    'selected'	=> $info['agentfeatures']['language']),
			      $element['agentfeatures']['language']['value']);

?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-agentfeatures-description" for="it-agentfeatures-description"><?=$this->bbf('fm_agentfeatures_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'agentfeatures[description]',
					 'id'		=> 'it-agentfeatures-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['agentfeatures']['description']['default']),
				   $info['agentfeatures']['description']);?>
	</div>
</div>
