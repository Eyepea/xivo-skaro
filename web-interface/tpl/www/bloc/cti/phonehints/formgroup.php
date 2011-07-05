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

$presence = $this->get_var('phonehintsgroup');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_phonehintsgroup_name'),
				  'name'	=> 'phonehintsgroup[name]',
				  'labelid'	=> 'phonehintsgroup-name',
				  'size'	=> 15,
				  'default'	=> $element['phonehintsgroup']['name']['default'],
				  'value'	=> $info['phonehintsgroup']['name']));

?>
	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-phonehintsgroup-description" for="it-phonehintsgroup-description"><?=$this->bbf('fm_phonehintsgroup_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'phonehintsgroup[description]',
					 'id'		=> 'it-phonehintsgroup-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['phonehintsgroup']['description']['default']),
				   $info['phonehintsgroup']['description']);?>
	</div>
</div>

