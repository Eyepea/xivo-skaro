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

$info = $this->get_var('info');
$element = $this->get_var('element');

?>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_name'),
				'name'	=> 'name',
				'labelid'	=> 'name',
				'size'	=> 15,
				'default'	=> $element['name']['default'],
				'value' => $info['name'],
				'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'name')) )),

		$form->select(array('desc'	=> $this->bbf('fm_type'),
				'name'	=> 'type',
				'labelid'	=> 'type',
				'key' => 'name',
				'altkey' => false,
				'default'	=> $element['type']['default'],
				'selected'	=> $info['type']),
				$this->get_var('types'),
				'onchange="javascript:hidediv();"'),

		$form->text(array('desc'	=> $this->bbf('fm_uri'),
				  'name'	=> 'uri',
				  'labelid'	=> 'uri',
				  'size'	=> 30,
				  'default'	=> $element['uri']['default'],
				  'value'	=> $info['uri'],
		          'error'	=> $this->bbf_args('error',
					   $this->get_var('error', 'uri')) ));
?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-description" for="it-description"><?=$this->bbf('fm_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'description',
					 'id'		=> 'it-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['description']['default'],
		          'error'	=> $this->bbf_args('description',
					   $this->get_var('error', 'description')) ),
				   $info['description']);?>
	</div>
