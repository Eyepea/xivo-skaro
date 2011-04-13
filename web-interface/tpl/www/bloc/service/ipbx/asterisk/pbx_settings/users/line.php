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

$info = $this->get_var('info');
$element = $this->get_var('element');
$nb = $this->get_var('count');
$list = $this->get_var('list');
$err = $this->get_var('error','linefeatures');

?>
<!--
<fieldset>
	<legend><?=$this->bbf('linefeatures-description_legend');?></legend>
	<?=$this->bbf('linefeatures-description');?>
</fieldset>
-->
<span id="box-entityid"></span>

<p id="box-lines_free" class="fm-paragraph b-nodisplay">
	<span class="fm-desc clearboth">
		<label id="lb-lines_free" for="it-lines_free"><?=$this->bbf('fm_lines_free');?></label>
	</span>
	<span id="box-no_lines_free" class="b-nodisplay">
		<?=$this->bbf('no_line_free');?>
	</span>
	<span id="box-list_lines_free">
		<?=$form->select(array('paragraph'	=> false,
			    'name'		=> 'list_lines_free',
			    'id'		=> 'list_lines_free',
			    'key'		=> 'identity',
			    'altkey'	=> 'id'));?>
		<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
							       $this->bbf('col_line-add_free'),
							       'border="0"'),
						'#lines',
						null,
						'id="lnk-add-row-line_free"',
						$this->bbf('col_line-add'));?>
	</span>
</p>

<p class="fm-paragraph" id="box-rules_group">
	<span class="fm-desc clearboth">
		<label id="lb-rules_group" for="it-rules_group"><?=$this->bbf('fm_rules_group');?></label>
	</span>
	<?=$form->text(array('paragraph'	=> false,
			     'name'		=> false,
			     'id'		=> 'it-rules_group',
			     'label'	=> false,
			     'size'		=> 10));?>		     
	<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
									       $this->bbf('col_rules_group-add'),
									       'border="0"'),
								'#lines',
								null,
								'id="lnk-add-row-rules_group"',
								$this->bbf('col_rules_group-add'));?>
</p>

<table cellspacing="0" cellpadding="0" border="0" id="list_linefeatures">
	<thead>
	<tr class="sb-top">
		<th class="th-left"><?=$this->bbf('col_line-protocol');?></th>
		<th class="th-center"><?=$this->bbf('col_line-name');?></th>
		<th class="th-center"><?=$this->bbf('col_line-context');?></th>
		<th class="th-center"><?=$this->bbf('col_line-number');?></th>
<?php 
/*
		<th class="th-center"><?=$this->bbf('col_line-rules_type');?></th>
		<th class="th-center"><?=$this->bbf('col_line-rules_time');?></th>
		<th class="th-center"><?=$this->bbf('col_line-rules_order');?></th>
		<th class="th-center"><?=$this->bbf('col_line-rules_group');?></th>
*/ 
?>
		<th class="th-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
								       $this->bbf('col_line-add'),
								       'border="0"'),
							'#lines',
							null,
							'id="lnk-add-row"',
							$this->bbf('col_line-add'));?>
		</th>
	</tr>
	</thead>
	<tbody id="linefeatures">
<?php
if($list !== false):
	
	$rs = array();
	for($i = 0;$i < $nb;$i++):
		$ref = &$list[$i];

		if(isset($err[$i]) === true):
			$ref['errdisplay'] = ' l-infos-error';
		else:
			$ref['errdisplay'] = '';
		endif;
		
		$rulesgroup = $ref['rules_group'];
		if (($rulesorder = (int) $ref['rules_order']) === 0)
			$rulesgroup = 0;
		if ($rulesgroup === '')
			$rulesgroup = 0;
		
		if (isset($rs[$rulesgroup]) === false)
			$rs[$rulesgroup] = array();
			
		array_push($rs[$rulesgroup],$ref);
	endfor;
	
	foreach($rs as $rulesgroup => $list):

		if (empty($rulesgroup) === false
		|| $rulesgroup !== 0):
?>
	<tr class="fm-paragraph l-subth" id="tr-rules_group">
		<td colspan="4" class="td-left" id="td_rules_group_name">
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<?=$rulesgroup?>
		</td>
		<td class="td-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
							       $this->bbf('opt_row-delete'),
							       'border="0"'),
							'#lines',
							null,
							'onclick="lnkdroprow(this);"',
							$this->bbf('opt_row-delete'));?>
		</td>
	</tr>
<?php
		endif;
		if (($nblinegroup = count($list)) === 0)
			continue;
		for($i = 0;$i < $nblinegroup;$i++):
			$ref = &$list[$i];
			$secureclass = '';
			if(isset($ref['encryption']) === true
			&& $ref['encryption'] === true)
				$secureclass = 'xivo-icon xivo-icon-secure';
?>
	<tr class="fm-paragraph<?=$ref['errdisplay']?>" style="cursor: move;">
		<td class="td-left txt-center">
			<?=$form->hidden(array('name' => 'linefeatures[id][]','value' => $ref['id']));?>
			<?=$form->hidden(array('name' => 'linefeatures[protocol][]','value' => $ref['protocol']));?>
			<?=$form->hidden(array('name' => '','id' => 'context-selected','value' => $ref['context']));?>		 	
			<?=$form->hidden(array('name' => 'linefeatures[rules_group][]',
						'value' 	=> null,
					    'id'		=> 'linefeatures-rules_group',
					    'value'	=> $ref['rules_group'],));?>
			<?=$form->hidden(array('name' => 'linefeatures[rules_order][]',
						'value' 	=> null,
					    'id'		=> 'linefeatures-rules_order',
					    'value'	=> $ref['rules_order']));?>
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<span>
				<span class="<?=$secureclass?>">&nbsp;</span>
				<?=$this->bbf('line_protocol-'.$ref['protocol'])?>
			</span>
		</td>
		<td>
			<?=$form->hidden(array('name' => 'linefeatures[name][]','value' => $ref['name']));?>
			<?=$url->href_html($ref['name'],
				'service/ipbx/pbx_settings/lines',
				array('act' => 'edit', 'id' => $ref['id']));?>
		</td>
		<td>
			<?=$form->select(array('paragraph'	=> false,
					    'name'		=> 'linefeatures[context][]',
					    'id'		=> 'linefeatures-context',
					    'label'		=> false));?>
		</td>
		<td>			
			<?=$form->text(array('paragraph'	=> false,
					     'name'		=> 'linefeatures[number][]',
				   		 'id'		=> 'linefeatures-number',
					     'label'	=> false,
					     'size'		=> 5,
					     'value'	=> $ref['number'],
					     'default'	=> $element['linefeatures']['number']['default']));?>
			<div class="dialog-helper" id="numberpool_helper"></div>
		</td>
		<td class="td-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
						       $this->bbf('opt_line-delete'),
						       'border="0"'),
							'#lines',
							null,
							'onclick="lnkdroprow(this);"',
							$this->bbf('opt_line-delete'));?>
		</td>
	</tr>
<?php
		endfor;
	endforeach;
endif;
?>
	</tbody>
	<tfoot>
	<tr id="no-linefeatures"<?=($list !== false ? ' class="b-nodisplay"' : '')?>>
		<td colspan="5" class="td-single"><?=$this->bbf('no_linefeatures');?></td>
	</tr>
	</tfoot>
</table>

<table class="b-nodisplay">
	<tbody id="ex-rules_group">
	<tr class="fm-paragraph l-subth" id="tr-rules_group">
		<td colspan="4" class="td-left" id="td_rules_group_name">
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
		</td>
		<td class="td-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
							       $this->bbf('opt_row-delete'),
							       'border="0"'),
							'#lines',
							null,
							'onclick="lnkdroprow(this);"',
							$this->bbf('opt_row-delete'));?>
		</td>
	</tr>
	</tbody>
</table>

<table class="b-nodisplay">
	<tbody id="ex-linefeatures">
	<tr class="fm-paragraph" style="cursor: move;">
		<td class="td-left txt-center" id="td_ex-linefeatures-protocol">
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<?=$form->hidden(array('name' => 'linefeatures[id][]',
					'value' 	=> 0,
				    'id'		=> 'linefeatures-id'));?>
			<?=$form->select(array('paragraph'	=> false,
				    'name'		=> 'linefeatures[protocol][]',
				    'id'		=> 'linefeatures-protocol',
				    'label'		=> false,
				    'key'		=> false,
					'bbf'		=> 'line_protocol-opt',
				    'default'	=> $element['linefeatures']['protocol']['default']),
			      $element['linefeatures']['protocol']['value']);?>
		</td>
		<td id="td_ex-linefeatures-name">
			<?=$form->hidden(array('name' => 'linefeatures[name][]',
					'value' 	=> null,
				    'id'		=> 'linefeatures-name'));?>
		</td>
		<td id="td_ex-linefeatures-context">
			<?=$form->select(array('paragraph'	=> false,
				    'name'		=> 'linefeatures[context][]',
				    'id'		=> 'linefeatures-context',
				    'label'		=> false,
				    'key'		=> 'displayname',
				    'altkey'	=> 'name',
				    'default'	=> $element['linefeatures']['context']['default']));?>
		</td>
		<td id="td_ex-linefeatures-number">
			<?=$form->text(array('paragraph'	=> false,
					     'name'		=> 'linefeatures[number][]',
					     'id'		=> 'linefeatures-number',
					     'label'	=> false,
					     'size'		=> 5,
					     'default'	=> $element['linefeatures']['number']['default']));?>
			<div class="dialog-helper" id="numberpool_helper"></div>
		</td>
		<td class="td-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/blue/delete.gif',
							       $this->bbf('opt_row-delete'),
							       'border="0"'),
							'#lines',
							null,
							'onclick="lnkdroprow(this);"',
							$this->bbf('opt_row-delete'));?>
		</td>
	</tr>
	</tbody>
</table>