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
				<div id="userlist" class="fm-paragraph fm-multilist">
				<?=$form->input_for_ms('userlist',$this->bbf('ms_seek'))?>
					<div class="slt-outlist">
						<?=$form->select(array('name'	=> 'userlist',
								       'label'		=> false,
								       'id'			=> 'it-userlist',
								       'multiple'	=> true,
								       'paragraph'	=> false,
								       'key'		=> 'identity',
								       'altkey'		=> 'id'),
										$user['list']);?>
					</div>

					<div class="inout-list">
						<a href="#"
						   onclick="dwho.form.move_selected('it-userlist','it-user');
							    return(dwho.dom.free_focus());"
						   title="<?=$this->bbf('bt_inuser');?>">
							<?=$url->img_html('img/site/button/arrow-left.gif',
									  $this->bbf('bt_inuser'),
									  'class="bt-inlist" id="bt-inuser" border="0"');?></a><br />
						<a href="#"
						   onclick="dwho.form.move_selected('it-user','it-userlist');
							    return(dwho.dom.free_focus());"
						   title="<?=$this->bbf('bt_outuser');?>">
							<?=$url->img_html('img/site/button/arrow-right.gif',
									  $this->bbf('bt_outuser'),
									  'class="bt-outlist" id="bt-outuser" border="0"');?></a>
					</div>

					<div class="slt-inlist">
						<?=$form->select(array('name'	=> 'user[]',
								       'label'		=> false,
								       'id'			=> 'it-user',
								       'multiple'	=> true,
								       'paragraph'	=> false,
								       'key'		=> 'identity',
								       'altkey'		=> 'id'),
									   $user['slt']);?>
					</div>
				</div>
				<div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',$this->bbf('no_user'),'</div>';
	endif;
?>

