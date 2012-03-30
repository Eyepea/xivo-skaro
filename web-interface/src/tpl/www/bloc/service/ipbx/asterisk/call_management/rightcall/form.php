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
$dhtml = &$this->get_module('dhtml');

$info = $this->get_var('info');
$element = $this->get_var('element');

$rcalluser = $this->get_var('rcalluser');
$rcallgroup = $this->get_var('rcallgroup');
$rcallincall = $this->get_var('rcallincall');
$rcalloutcall = $this->get_var('rcalloutcall');
$rcallexten = $this->get_var('rcallexten');

?>

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_rightcall_name'),
				  'name'	=> 'rightcall[name]',
				  'labelid'	=> 'rightcall-name',
				  'size'	=> 15,
				  'default'	=> $element['rightcall']['name']['default'],
				  'value'	=> $info['rightcall']['name'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'rightcall', 'name')) ));

	echo	$form->text(array('desc'	=> $this->bbf('fm_rightcall_passwd'),
				  'name'	=> 'rightcall[passwd]',
				  'labelid'	=> 'rightcall-passwd',
				  'size'	=> 15,
				  'default'	=> $element['rightcall']['passwd']['default'],
				  'value'	=> $info['rightcall']['passwd'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'rightcall', 'passwd')) )),

		$form->select(array('desc'	=> $this->bbf('fm_rightcall_authorization'),
				    'name'	=> 'rightcall[authorization]',
				    'bbf'	=> 'fm_rightcall_authorization-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'labelid'	=> 'authorization',
				    'selected'	=> $info['rightcall']['authorization'],
				    'default'	=> $element['rightcall']['authorization']['default']),
			      $element['rightcall']['authorization']['value']);
?>
<div id="extenlist" class="fm-paragraph fm-multilist">
	<p>
		<label id="lb-exten" for="it-exten"><?=$this->bbf('fm_rightcallexten_exten');?></label>
	</p>
				<?=$form->input_for_ms('rightcallexten',$this->bbf('ms_seek'))?>
	<div class="slt-list">
		<?=$form->select(array('name'		=> 'rightcallexten[]',
				       'label'		=> false,
				       'id'		=> 'it-exten',
				       'key'		=> true,
				       'altkey'		=> 'exten',
				       'multiple'	=> true,
				       'size'		=> 5,
				       'paragraph'	=> false),
				 $rcallexten);?>
		<div class="bt-adddelete">
			<a href="#"
			   onclick="xivo_fm_select_add_exten('it-exten',
							     prompt('<?=$dhtml->escape($this->bbf('rightcallexten_add-extension'));?>'));
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_addexten');?>">
				<?=$url->img_html('img/site/button/mini/blue/add.gif',
						  $this->bbf('bt_addexten'),
						  'class="bt-addlist" id="bt-addexten" border="0"');?></a><br />
			<a href="#"
			   onclick="dwho.form.select_delete_entry('it-exten');
				    return(dwho.dom.free_focus());"
			   title="<?=$this->bbf('bt_deleteexten');?>">
				<?=$url->img_html('img/site/button/mini/orange/delete.gif',
						  $this->bbf('bt_deleteexten'),
						  'class="bt-deletelist" id="bt-deleteexten" border="0"');?></a>
		</div>
	</div>
</div>
<div class="clearboth"></div>

<div class="fm-paragraph fm-description">
	<p>
		<label id="lb-rightcall-description" for="it-rightcall-description"><?=$this->bbf('fm_rightcall_description');?></label>
	</p>
	<?=$form->textarea(array('paragraph'	=> false,
				 'label'	=> false,
				 'name'		=> 'rightcall[description]',
				 'id'		=> 'it-rightcall-description',
				 'cols'		=> 60,
				 'rows'		=> 5,
				 'default'	=> $element['rightcall']['description']['default'],
				 'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'rightcall', 'description')) ),
			   $info['rightcall']['description']);?>
</div>
</div>

<div id="sb-part-rightcalluser" class="b-nodisplay">
<?php
	if($rcalluser['list'] !== false):
?>
    <div id="rightcalllist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'rightcalluser[]',
    						'id' 		=> 'it-rightcalluser',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $rcalluser['slt']),
    					$rcalluser['list']);?>
    </div>
    <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_user'),
					'service/ipbx/pbx_settings/users',
					'act=add'),
			'</div>';
	endif;
?>
</div>

<div id="sb-part-rightcallgroup" class="b-nodisplay">
<?php
	if($rcallgroup['list'] !== false):
?>
    <div id="grouplist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'rightcallgroup[]',
    						'id' 		=> 'it-rightcallgroup',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $rcallgroup['slt']),
    					$rcallgroup['list']);?>
    </div>
	<div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_group'),
					'service/ipbx/pbx_settings/groups',
					'act=add'),
			'</div>';
	endif;
?>
</div>
<div id="sb-part-rightcallincall" class="b-nodisplay">
<?php
	if($rcallincall['list'] !== false):
?>
    <div id="incalllist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'rightcallincall[]',
    						'id' 		=> 'it-rightcallincall',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $rcallincall['slt']),
    					$rcallincall['list']);?>
    </div>
    <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_incall'),
					'service/ipbx/call_management/incall',
					'act=add'),
			'</div>';
	endif;
?>
</div>

<div id="sb-part-last" class="b-nodisplay">
<?php
	if($rcalloutcall['list'] !== false):
?>
    <div id="incalllist" class="fm-paragraph fm-description">
    		<?=$form->jq_select(array('paragraph'	=> false,
    					 	'label'		=> false,
                			'name'    	=> 'rightcalloutcall[]',
    						'id' 		=> 'it-rightcalloutcall',
    						'key'		=> 'identity',
    				       	'altkey'	=> 'id',
                			'selected'  => $rcalloutcall['slt']),
    					$rcalloutcall['list']);?>
    </div>
    <div class="clearboth"></div>
<?php
	else:
		echo	'<div class="txt-center">',
			$url->href_htmln($this->bbf('create_outcall'),
					'service/ipbx/call_management/outcall',
					'act=add'),
			'</div>';
	endif;
?>
</div>
