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
$url = &$this->get_module('url');

$element = $this->get_var('element');
$info = $this->get_var('info');
$user = $this->get_var('user');

$dhtml = &$this->get_module('dhtml');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_servicesgroup_name'),
				  'name'	=> 'servicesgroup[name]',
				  'labelid'	=> 'servicesgroup-name',
				  'size'	=> 20,
				  'default'	=> $element['servicesgroup']['name']['default'],
				  'value'	=> $info['servicesgroup']['name'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','servicesgroup','name'))));
?>

<div class="fm-paragraph fm-description">
	<p>
		<label id="lb-servicesgroup-description" for="it-servicesgroup-description"><?=$this->bbf('fm_servicesgroup_description');?></label>
	</p>
	<?=$form->textarea(array('paragraph'	=> false,
				 'label'	=> false,
				 'name'		=> 'servicesgroup[description]',
				 'id'		=> 'it-servicesgroup-description',
				 'cols'		=> 60,
				 'rows'		=> 1,
				 'default'	=> $element['servicesgroup']['description']['default']),
			   $info['servicesgroup']['description']);?>
</div>
<?php
	if(isset($user['list']) === true
	&& $user['list'] !== false):
?>
    <div id="userlist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'user[]',
    						'id' 		=> 'it-user',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $user['slt']),
    					$user['list']);?>
    </div>
    <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',$this->bbf('no_user'),'</div>';
	endif;
?>

