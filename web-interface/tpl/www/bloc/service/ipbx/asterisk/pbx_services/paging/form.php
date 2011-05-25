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

$form         = &$this->get_module('form');
$url          = $this->get_module('url');

$info         = $this->get_var('info');
$element      = $this->get_var('element');
$paginguser   = $this->get_var('paginguser');
$pagingcaller   = $this->get_var('pagingcaller');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo $form->text(array('desc'	=> $this->bbf('fm_paging_number'),
				  'name'	=> 'paging[number]',
				  'labelid'	=> 'paging-number',
				  'size'	=> 15,
				  'default'	=> $element['paging']['number']['default'],
				  'value'	=> $this->get_var('info','paging','number'),
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'paging', 'number')) )),
					
		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_duplex'),
				      'name'		=> 'paging[duplex]',
				      'labelid'		=> 'paging-duplex',
				      'default'		=> $element['paging']['duplex']['default'],
					  'checked'		=> $this->get_var('info','paging','duplex'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_ignore'),
				      'name'		=> 'paging[ignore]',
				      'labelid'		=> 'paging-ignore',
				      'default'		=> $element['paging']['ignore']['default'],
					  'checked'		=> $this->get_var('info','paging','ignore'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_record'),
				      'name'		=> 'paging[record]',
				      'labelid'		=> 'paging-record',
				      'default'		=> $element['paging']['record']['default'],
					  'checked'		=> $this->get_var('info','paging','record'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_quiet'),
				      'name'		=> 'paging[quiet]',
				      'labelid'		=> 'paging-quiet',
				      'default'		=> $element['paging']['quiet']['default'],
					  'checked'		=> $this->get_var('info','paging','quiet'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_callnotbusy'),
				      'name'		=> 'paging[callnotbusy]',
				      'labelid'		=> 'paging-callnotbusy',
				      'default'		=> $element['paging']['callnotbusy']['default'],
					  'checked'		=> $this->get_var('info','paging','callnotbusy'))),
		
		$form->select(array('desc'	=> $this->bbf('fm_paging_timeout'),
					    'name'		=> 'paging[timeout]',
					    'labelid'	=> 'paging-timeout',
						'help'		=> $this->bbf('hlp_fm_paging_timetout'),
					    'key'		=> false,
					    'default'	=> $element['paging']['timeout']['default'],
					    'selected'	=> $this->get_var('info','paging','timeout')),
					$element['paging']['timeout']['value']),

		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_announcement_caller'),
				      'name'		=> 'paging[announcement_caller]',
				      'labelid'		=> 'paging-announcement_caller',
				      'default'		=> $element['paging']['announcement_caller']['default'],
					  'checked'		=> $this->get_var('info','paging','announcement_caller'))),

		$form->checkbox(array('desc'	=> $this->bbf('fm_paging_announcement_play'),
				      'name'		=> 'paging[announcement_play]',
				      'labelid'		=> 'paging-announcement_play',
				      'default'		=> $element['paging']['announcement_play']['default'],
					  'checked'		=> $this->get_var('info','paging','announcement_play'))),
		
		$form->select(array('desc'	=> $this->bbf('fm_paging_announcement_file'),
					    'name'		=> 'paging[announcement_file]',
					    'labelid'	=> 'paging-announcement_file',
						'empty' 	=> true,
					    'key'		=> 'filename',
					    'altkey'	=> 'filename',
					    'selected'	=> $this->get_var('info','paging','announcement_file')),
					$this->get_var('files'));
?>

	<div class="fm-paragraph fm-description">
		<p>
			<label id="lb-paging-description" for="it-paging-description"><?=$this->bbf('fm_paging_description');?></label>
		</p>
		<?=$form->textarea(array('paragraph'	=> false,
					 'label'	=> false,
					 'name'		=> 'paging[description]',
					 'id'		=> 'it-paging-description',
					 'cols'		=> 60,
					 'rows'		=> 5,
					 'default'	=> $element['paging']['description']['default'],
					 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'paging', 'description')) ),
				   $this->get_var('info','paging','description'));?>
	</div>
</div>
<div id="sb-part-last" class="b-nodisplay">
<?php
if($paginguser['list'] === false):
	echo	'<div class="txt-center">',
		$url->href_htmln($this->bbf('create_user'),
				'service/ipbx/pbx_settings/users',
				'act=add'),
		'</div>';
else:
?>
<div id="paginguserlist" class="fm-paragraph fm-description">
	<p>
		<label id="lb-paginguser" for="it-paginguser"><?=$this->bbf('fm_paginguser');?></label>
	</p>
		<?=$form->jq_select(array('paragraph'	=> false,
					 	'label'		=> false,
            			'name'    	=> 'paginguser[]',
						'id' 		=> 'paginguser',
						'key'		=> 'identity',
				       	'altkey'	=> 'id',
            			'selected'  => $paginguser['slt']),
					$paginguser['list']);?>
</div>
<div class="clearboth"></div>
<div id="pagingcallerlist" class="fm-paragraph fm-description">
	<p>
		<label id="lb-pagingcaller" for="it-pagingcaller"><?=$this->bbf('fm_pagingcaller');?></label>
	</p>
		<?=$form->jq_select(array('paragraph'	=> false,
					 	'label'		=> false,
            			'name'    	=> 'pagingcaller[]',
						'id' 		=> 'pagingcaller',
						'key'		=> 'identity',
				       	'altkey'	=> 'id',
            			'selected'  => $pagingcaller['slt']),
					$pagingcaller['list']);?>
</div>
<div class="clearboth"></div>
<?php
endif;
?>
</div>
