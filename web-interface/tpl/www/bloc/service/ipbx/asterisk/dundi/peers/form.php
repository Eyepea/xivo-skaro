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

$form    = &$this->get_module('form');
$url     = $this->get_module('url');

$info    = $this->get_var('info');
$element = $this->get_var('element');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;
?>

<div id="sb-part-first">
<br/>
<?php
	echo $form->text(array('desc'	=> $this->bbf('fm_dundipeer_macaddr'),
			  'name'	=> 'dundipeer[macaddr]',
			  'labelid'	=> 'dundipeer-macaddr',
			  'size'	=> 15,
			  'default'	=> $element['dundipeer']['macaddr']['default'],
			  'value'	=> $info['dundipeer']['macaddr'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundipeer', 'macaddr')) )),

	$form->select(array('desc'	=> $this->bbf('fm_dundipeer_model'),
				    'name'	=> 'dundipeer[model]',
				    'labelid'	=> 'dundipeer-model',
						'empty' => false,
						'size' => 15,
						'key' => false,
				    'bbf'		=> 'fm_dundipeer_model-opt',
				    'help'	=> $this->bbf('hlp_fm_dundipeer-model'),
				    'selected'	=> $this->get_var('info','dundipeer','model'),
				    'default'	=> $element['dundipeer']['model']['default']),
			      $element['dundipeer']['model']['value']),

	$form->text(array('desc'	=> $this->bbf('fm_dundipeer_host'),
			  'name'	=> 'dundipeer[host]',
			  'labelid'	=> 'dundipeer-host',
			  'size'	=> 15,
			  'default'	=> $element['dundipeer']['host']['default'],
			  'value'	=> $info['dundipeer']['host'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundipeer', 'host')) )),

	$form->text(array('desc'	=> $this->bbf('fm_dundipeer_inkey'),
			  'name'	=> 'dundipeer[inkey]',
			  'labelid'	=> 'dundipeer-inkey',
			  'size'	=> 15,
		    'help'	=> $this->bbf('hlp_fm_dundipeer-inkey'),
			  'default'	=> $element['dundipeer']['inkey']['default'],
			  'value'	=> $info['dundipeer']['inkey'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundipeer', 'inkey')) )),

	$form->text(array('desc'	=> $this->bbf('fm_dundipeer_outkey'),
			  'name'	=> 'dundipeer[outkey]',
			  'labelid'	=> 'dundipeer-outkey',
			  'size'	=> 15,
		    'help'	=> $this->bbf('hlp_fm_dundipeer-outkey'),
			  'default'	=> $element['dundipeer']['outkey']['default'],
			  'value'	=> $info['dundipeer']['outkey'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundipeer', 'outkey')) )),

	$form->text(array('desc'	=> $this->bbf('fm_dundipeer_include'),
			  'name'	=> 'dundipeer[include]',
			  'labelid'	=> 'dundipeer-include',
			  'size'	=> 15,		
		    'help'	=> $this->bbf('hlp_fm_dundipeer-include'),
			  'default'	=> $element['dundipeer']['include']['default'],
			  'value'	=> $info['dundipeer']['include'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundipeer', 'include')) )),

	$form->text(array('desc'	=> $this->bbf('fm_dundipeer_permit'),
			  'name'	=> 'dundipeer[permit]',
			  'labelid'	=> 'dundipeer-permit',
			  'size'	=> 15,
		    'help'	=> $this->bbf('hlp_fm_dundipeer-permit'),
			  'default'	=> $element['dundipeer']['permit']['default'],
			  'value'	=> $info['dundipeer']['permit'],
			  'error'	=> $this->bbf_args('error',
				$this->get_var('error', 'dundipeer', 'permit')) )),

	$form->select(array('desc'	=> $this->bbf('fm_dundipeer_qualify'),
				    'name'	=> 'dundipeer[qualify]',
				    'labelid'	=> 'dundipeer-qualify',
						'empty' => false,
						'size' => 15,
						'key' => false,
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'help'	=> $this->bbf('hlp_fm_dundipeer-qualify'),
				    'selected'	=> $this->get_var('info','dundipeer','qualify'),
					  'error'	=> $this->bbf_args('error',
							$this->get_var('error', 'dundipeer', 'qualify')),
				    'default'	=> $element['dundipeer']['qualify']['default']),
			      $element['dundipeer']['qualify']['value']),

	$form->select(array('desc'	=> $this->bbf('fm_dundipeer_order'),
				    'name'	=> 'dundipeer[order]',
				    'labelid'	=> 'dundipeer-order',
						'empty' => true,
						'size' => 15,
						'key' => false,
				    'bbf'		=> 'fm_dundipeer_order-opt',
				    'help'	=> $this->bbf('hlp_fm_dundipeer-order'),
				    'selected'	=> $this->get_var('info','dundipeer','order'),
					  'error'	=> $this->bbf_args('error',
							$this->get_var('error', 'dundipeer', 'order')),
				    'default'	=> $element['dundipeer']['order']['default']),
			      $element['dundipeer']['order']['value']),

	$form->select(array('desc'	=> $this->bbf('fm_dundipeer_precache'),
				    'name'	=> 'dundipeer[precache]',
				    'labelid'	=> 'dundipeer-precache',
						'empty' => true,
						'size' => 15,
						'key' => false,
				    'bbf'		=> 'fm_dundipeer_precache-opt',
				    'help'	=> $this->bbf('hlp_fm_dundipeer-precache'),
				    'selected'	=> $this->get_var('info','dundipeer','precache'),
					  'error'	=> $this->bbf_args('error',
							$this->get_var('error', 'dundipeer', 'precache')),
				    'default'	=> $element['dundipeer']['precache']['default']),
			      $element['dundipeer']['precache']['value']);

?>

	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-dundipeer-description" for="it-dundipeer-description"><?=$this->bbf('fm_dundipeer_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'dundipeer[description]',
					 'id'		=> 'it-dundipeer-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['dundipeer']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'dundipeer', 'description')) ),
				   $info['dundipeer']['description']);?>
	</div>
</div>
