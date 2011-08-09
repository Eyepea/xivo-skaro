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
$list = $this->get_var('info','dialpattern');
$err = $this->get_var('error','dialpattern');
$nb = 0;

?>

<table id="list_exten">
	<thead>
	<tr class="sb-top">
		<th class="th-left th-rule">&nbsp;</th>
		<th class="th-center"><?=$this->bbf('col_outcall-dialpattern_externprefix');?></th>
		<th class="th-center"><?=$this->bbf('col_outcall-dialpattern_prefix');?></th>
		<th class="th-center"><?=$this->bbf('col_outcall-dialpattern_exten');?></th>
		<th class="th-center"><?=$this->bbf('col_outcall-dialpattern_stripnum');?></th>
		<th class="th-center"><?=$this->bbf('col_outcall-dialpattern_callerid');?></th>
		<th class="th-center"><?=$this->bbf('col_outcall-dialpattern_emergency');?></th>
		<th class="th-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
								$this->bbf('col_row-add'),
								'border="0"'),
							'#exten',
							null,
							'id="lnk-add-row"',
							$this->bbf('col_row-add'));?>
		</th>
	</tr>
	</thead>
	<tbody>
<?php
if($list !== false
&& ((int) $nb = count($list)) > 0):
	for($i = 0;$i < $nb;$i++):
		$ref = &$list[$i];

		if(isset($err[$i]) === true):
			$errdisplay = ' l-infos-error';
		else:
			$errdisplay = '';
		endif;
?>
	<tr class="fm-paragraph<?=$errdisplay?>">
		<td class="td-left txt-center">
			<?=$form->hidden(array('name' => 'dialpattern[id][]',
						'value' 	=> $ref['id']));?>
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<span id="box-order" style="float:left;font-weight:bold;"></span>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					      'label'	=> false,
						  'name'	=> 'dialpattern[externprefix][]',
						  'labelid'	=> 'dialpattern-externprefix',
						  'size'	=> 8,
						  'default'	=> $element['dialpattern']['externprefix']['default'],
						  'value'	=> $ref['externprefix']))?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					      'label'	=> false,
						  'name'	=> 'dialpattern[prefix][]',
						  'labelid'	=> 'dialpattern-prefix',
						  'size'	=> 8,
						  'default'	=> $element['dialpattern']['prefix']['default'],
						  'value'	=> $ref['prefix']))?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'label'	=> false,
					     'name'		=> 'dialpattern[exten][]',
						 'labelid'	=> 'dialpattern-exten',
					     'size'		=> 25,
					     'value'	=> $ref['exten'],
					     'default'	=> $element['dialpattern']['exten']['default']));?>
		</td>
		<td>
			<?=$form->select(array('paragraph'	=> false,
					    'label'		=> false,
					    'name'		=> 'dialpattern[stripnum][]',
					    'labelid'	=> 'dialpattern-stripnum',
					    'key'		=> false,
					    'default'	=> $element['dialpattern']['stripnum']['default'],
					    'selected'	=> $ref['stripnum']),
			      $element['dialpattern']['stripnum']['value']);?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					      'label'	=> false,
						  'name'	=> 'dialpattern[callerid][]',
						  'labelid'	=> 'dialpattern-callerid',
						  'size'	=> 15,
						  'notag'	=> false,
						  'default'	=> $element['dialpattern']['callerid']['default'],
						  'value'	=> $ref['callerid']));?>
		</td>
		<td>
			<?=$form->hidden(array('name' => 'dialpattern[emergency][]',
					    'id'		=> 'dialpattern-emergency',
						'value' 	=> $ref['emergency']));?>
			<?=$form->checkbox(array('paragraph'	=> false,
					    'label'		=> false,
						'name'		=> 'enable-emergency',
					    'id'		=> 'enable-emergency',
					    'checked'	=> $ref['emergency'],
					    'default'	=> $element['dialpattern']['emergency']['default']))?>
		</td>
		<td class="td-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
						       $this->bbf('opt_row-delete'),
						       'border="0"'),
							'#exten',
							null,
							'id="lnk-del-row"',
							$this->bbf('opt_row-delete'));?>
		</td>
	</tr>
<?php
	endfor;
endif;
?>
	</tbody>
	<tfoot>
	<tr id="no-row"<?=(($nb === 0) ? '' : ' class="b-nodisplay"')?>>
		<td colspan="8" class="td-single"><?=$this->bbf('no_row');?></td>
	</tr>
	</tfoot>
</table>

<table class="b-nodisplay">
	<tbody id="ex-row">
	<tr class="fm-paragraph">
		<td class="td-left txt-center">
			<?=$form->hidden(array('name' => 'dialpattern[id][]',
						'value' 	=> 0));?>
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<span id="box-order" style="float:left;font-weight:bold;"></span>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'dialpattern[externprefix][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 8));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'dialpattern[prefix][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 8));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'dialpattern[exten][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 25));?>
		</td>
		<td>
			<?=$form->select(array('paragraph'	=> false,
					    'label'		=> false,
					     'id'		=> false,
					    'name'		=> 'dialpattern[stripnum][]',
					    'key'		=> false),
						$element['dialpattern']['stripnum']['value']);?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'dialpattern[callerid][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 15));?>
		</td>
		<td>
			<?=$form->checkbox(array('paragraph'	=> false,
					     'label'	=> false,
					     'id'		=> false,
					     'name'		=> 'dialpattern[emergency][]'))?>
		</td>
		<td class="td-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
						       $this->bbf('opt_row-delete'),
						       'border="0"'),
							'#exten',
							null,
							'id="lnk-del-row"',
							$this->bbf('opt_row-delete'));?>
		</td>
	</tr>
	</tbody>
</table>
