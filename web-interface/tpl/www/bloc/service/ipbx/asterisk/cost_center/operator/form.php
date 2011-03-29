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
$trunk = $this->get_var('trunk');

$dhtml = &$this->get_module('dhtml');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

$destination_nb = 0;
$destination_list = false;

if(dwho_issa('destination',$info) === true):

	$context_js = array();

	if(($destination_nb = count($info['destination'])) > 0):
		$destination_list = $info['destination'];
		$context_js[] = 'dwho.dom.set_table_list(\'operator_destination\','.$destination_nb.');';
	endif;

	if(isset($context_js[0]) === true):
		$dhtml = &$this->get_module('dhtml');
		$dhtml->write_js($context_js);
	endif;

endif;

?>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_operator_name'),
				  'name'	=> 'operator[name]',
				  'labelid'	=> 'operator-name',
				  'size'	=> 20,
				  'default'	=> $element['operator']['name']['default'],
				  'value'	=> $info['operator']['name'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','operator','name')))),


			$form->text(array('desc'	=> $this->bbf('fm_operator_default_price'),
				  'name'	=> 'operator[default_price]',
				  'labelid'	=> 'operator-default_price',
				  'size'	=> 5,
				  'help'	=> $this->bbf('hlp_fm_operator_default_price'),
				  'default'	=> $element['operator']['default_price']['default'],
				  'value'	=> $info['operator']['default_price'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','operator','default_price')))),

			$form->select(array('desc'	=> $this->bbf('fm_operator_default_price_is'),
				    'name'		=> 'operator[default_price_is]',
				    'labelid'	=> 'operator-default_price_is',
				    'key'		=> false,
				    'bbf'		=> 'fm_default_price_is-opt',
				    'selected'	=> $info['operator']['default_price_is'],
				    'default'	=> $element['operator']['default_price_is']['default']),
			      $element['operator']['default_price_is']['value']),

		$form->text(array('desc'	=> $this->bbf('fm_operator_currency'),
				  'name'	=> 'operator[currency]',
				  'labelid'	=> 'operator-currency',
				  'size'	=> 10,
				  'default'	=> $element['operator']['currency']['default'],
				  'value' 	=> $info['operator']['currency'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','operator','currency'))));

?>

<div class="fm-paragraph fm-description">
	<p>
		<label id="lb-operator-description" for="it-operator-description"><?=$this->bbf('fm_operator_description');?></label>
	</p>
	<?=$form->textarea(array('paragraph'	=> false,
				 'label'	=> false,
				 'name'		=> 'operator[description]',
				 'id'		=> 'it-operator-description',
				 'cols'		=> 60,
				 'rows'		=> 1,
				 'default'	=> $element['operator']['description']['default']),
			   $info['operator']['description']);?>
</div>
<?php
	if(isset($trunk['list']) === true
	&& $trunk['list'] !== false):
?>
				<div id="trunklist" class="fm-paragraph fm-multilist">
				<?=$form->input_for_ms('trunklist',$this->bbf('ms_seek'))?>
					<div class="slt-outlist">
						<?=$form->select(array('name'	=> 'trunklist',
								       'label'		=> false,
								       'id'			=> 'it-trunklist',
								       'multiple'	=> true,
								       'paragraph'	=> false,
								       'key'		=> 'identity',
								       'altkey'		=> 'id'),
										$trunk['list']);?>
					</div>

					<div class="inout-list">
						<a href="#"
						   onclick="dwho.form.move_selected('it-trunklist','it-trunk');
							    return(dwho.dom.free_focus());"
						   title="<?=$this->bbf('bt_intrunk');?>">
							<?=$url->img_html('img/site/button/arrow-left.gif',
									  $this->bbf('bt_intrunk'),
									  'class="bt-inlist" id="bt-intrunk" border="0"');?></a><br />
						<a href="#"
						   onclick="dwho.form.move_selected('it-trunk','it-trunklist');
							    return(dwho.dom.free_focus());"
						   title="<?=$this->bbf('bt_outtrunk');?>">
							<?=$url->img_html('img/site/button/arrow-right.gif',
									  $this->bbf('bt_outtrunk'),
									  'class="bt-outlist" id="bt-outtrunk" border="0"');?></a>
					</div>

					<div class="slt-inlist">
						<?=$form->select(array('name'	=> 'trunk[]',
								       'label'		=> false,
								       'id'			=> 'it-trunk',
								       'multiple'	=> true,
								       'paragraph'	=> false,
								       'key'		=> 'identity',
								       'altkey'		=> 'id'),
									   $trunk['slt']);?>
					</div>
				</div>
				<div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',$this->bbf('no_trunk'),'</div>';
	endif;
?>

	<div class="sb-list">
<?php
	$this->file_include('bloc/service/ipbx/asterisk/cost_center/operator/opdst',
			    array('type'	=> 'destination',
				  'count'	=> $destination_nb,
				  'list'	=> $destination_list));
?>
	</div>

