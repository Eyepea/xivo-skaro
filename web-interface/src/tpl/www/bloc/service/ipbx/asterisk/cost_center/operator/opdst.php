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
$type = $this->get_var('type');
$nb = $this->get_var('count');
$list = $this->get_var('list');
$err = $this->get_var('error',$type);

?>
<table>
	<thead>
	<tr class="sb-top">
		<th class="th-left"><?=$this->bbf('col_operator_destination-name');?></th>
		<th class="th-center"><?=$this->bbf('col_operator_destination-exten');?></th>
		<th class="th-center"><?=$this->bbf('col_operator_destination-price');?></th>
		<th class="th-center"><?=$this->bbf('col_operator_destination-price_is');?></th>
		<th class="th-right"><?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
								       $this->bbf('col_operator_destination-add'),
								       'border="0"'),
							'#',
							null,
							'onclick="xivo_operator_destination_enable_add(\''.$type.'\',this);
								  return(dwho.dom.free_focus());"',
							$this->bbf('col_operator_destination-add'));?></th>
	</tr>
	</thead>
	<tbody id="operator-<?=$type?>">
<?php
if($list !== false):
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
			<?=$form->text(array('paragraph'	=> false,
					     'name'		=> 'destination[name][]',
					     'id'		=> false,
					     'label'	=> false,
					     'size'		=> 25,
					     'value'	=> $ref['name'],
					     'default'	=> $element['destination']['name']['default']));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'		=> 'destination[exten][]',
					     'id'		=> false,
					     'label'	=> false,
					     'size'		=> 20,
					     'value'	=> $ref['exten'],
					     'default'	=> $element['destination']['exten']['default']));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'		=> 'destination[price][]',
					     'id'		=> false,
					     'label'	=> false,
					     'size'		=> 5,
					     'value'	=> $ref['price'],
					     'default'	=> $element['destination']['price']['default']));?>
		</td>
		<td>
			<?=$form->select(array('paragraph'	=> false,
				    'name'		=> 'destination[price_is][]',
				    'id'		=> false,
				    'label'		=> false,
				    'key'		=> false,
				    'bbf'		=> 'fm_price_is-opt',
				    'selected'	=> $ref['price_is'],
				    'default'	=> $element['destination']['price_is']['default']),
			      $element['destination']['price_is']['value']);?>
		</td>
		<td class="td-right"><?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
								       $this->bbf('opt_operator_destination-delete'),
								       'border="0"'),
							'#',
							null,
							'onclick="dwho.dom.make_table_list(\'operator-'.$type.'\',this,1);
								  return(dwho.dom.free_focus());"',
							$this->bbf('opt_operator_destination-delete'));?></td>
	</tr>
<?php
	endfor;
endif;
?>
	</tbody>
	<tfoot>
	<tr id="no-operator-<?=$type?>"<?=($list !== false ? ' class="b-nodisplay"' : '')?>>
		<td colspan="5" class="td-single"><?=$this->bbf('no_operator-'.$type);?></td>
	</tr>
	</tfoot>
</table>
<table class="b-nodisplay">
	<tbody id="ex-operator-<?=$type?>">
	<tr class="fm-paragraph">
		<td class="td-left txt-center">
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'destination[name][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 25,
					     'default'		=> $element['destination']['name']['default']));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'destination[exten][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 20,
					     'default'		=> $element['destination']['exten']['default']));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'destination[price][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 5,
					     'default'		=> $element['destination']['price']['default']));?>
		</td>
		<td>
			<?=$form->select(array('paragraph'	=> false,
				    'name'		=> 'destination[price_is][]',
				    'id'		=> 'price_is',
				    'key'		=> false,
				    'bbf'		=> 'fm_price_is-opt',
				    'default'	=> $element['destination']['price_is']['default']),
			      $element['destination']['price_is']['value']);?>
		</td>
		<td class="td-right"><?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
								       $this->bbf('opt_operator_destination-delete'),
								       'border="0"'),
							'#',
							null,
							'onclick="dwho.dom.make_table_list(\'operator-'.$type.'\',this,1);
								  return(dwho.dom.free_focus());"',
							$this->bbf('opt_operator_destination-delete'));?></td>
	</tr>
	</tbody>
</table>
