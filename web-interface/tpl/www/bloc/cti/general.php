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

$url = &$this->get_module('url');
$form = &$this->get_module('form');
$dhtml = &$this->get_module('dhtml');

$info = $this->get_var('info');
$element = $this->get_var('element');
$error = $this->get_var('error');
$listaccount = $this->get_var('listaccount');

if(($fm_save = $this->get_var('fm_save')) === true):
	$dhtml->write_js('xivo_form_result(true,\''.$dhtml->escape($this->bbf('fm_success-save')).'\');');
elseif($fm_save === false):
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

$error_js = array();
$error_nb = count($error['ctimain']);

for($i = 0;$i < $error_nb;$i++):
	$error_js[] = 'dwho.form.error[\'it-ctimain-'.$error['ctimain'][$i].'\'] = true;';
endfor;

if(isset($error_js[0]) === true)
	$dhtml->write_js($error_js);

?>
<div class="b-infos b-form">
<h3 class="sb-top xspan">
	<span class="span-left">&nbsp;</span>
	<span class="span-center"><?=$this->bbf('title_content_name');?></span>
	<span class="span-right">&nbsp;</span>
</h3>
<div class="sb-content">
<form action="#" method="post" accept-charset="utf-8">
<?php
	echo
		$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),
		$form->hidden(array('name'	=> 'fm_send',
				    'value'	=> 1));
?>

<div id="sb-part-first">
	<?=$form->select(array('desc'	=> $this->bbf('fm_cti_commandset'),
				    'name'	=> 'cti[commandset]',
				    'labelid'	=> 'cti_commandset',
				    'key'	=> false,
				    'default'	=> $element['ctimain']['commandset']['default'],
#				    'help'	=> $this->bbf('hlp_fm_cti_commandset'),
				    'selected'	=> $this->get_var('ctimain','commandset','var_val')),
			      $element['ctimain']['commandset']['value']);
	?>
<fieldset id="cti-ami">
	<legend><?=$this->bbf('cti-ami');?></legend>
			<?=$form->text(array('desc'	=> $this->bbf('fm_cti_ami_login'),
						  'name'	=> 'cti[ami_login]',
						  'labelid'	=> 'cti-ami_login',
						  'required'	=> 1,
						  'size'	=> 15,
						  'default'	=> $element['ctimain']['ami_login']['default'],
						  'value'	=> $info['ctimain']['ami_login']))?>
			<?=$form->text(array('desc'	=> $this->bbf('fm_cti_ami_password'),
						  'name'	=> 'cti[ami_password]',
						  'labelid'	=> 'cti-ami_password',
						  'required'	=> 1,
						  'size'	=> 15,
						  'default'	=> $element['ctimain']['ami_password']['default'],
						  'value'	=> $info['ctimain']['ami_password']))?>
			<?=$form->text(array('desc'	=> $this->bbf('fm_cti_ami_ip'),
						  'name'	=> 'cti[ami_ip]',
						  'labelid'	=> 'cti-ami_ip',
						  'required'	=> 1,
						  'regexp'	=> '[[:ipv4:]]',
						  'size'	=> 15,
						  'default'	=> $element['ctimain']['ami_ip']['default'],
						  'value'	=> $info['ctimain']['ami_ip']))?>
			<?=$form->text(array('desc'	=> $this->bbf('fm_cti_ami_port'),
						  'name'	=> 'cti[ami_port]',
						  'labelid'	=> 'cti-ami_port',
						  'required'	=> 1,
						  'regexp'	=> '[[:port:]]',
						  'size'	=> 4,
						  'default'	=> $element['ctimain']['ami_port']['default'],
						  'value'	=> $info['ctimain']['ami_port']))?>
</fieldset>
<fieldset id="cti-accounts">
	<legend><?=$this->bbf('cti-accounts');?></legend>
<div class="sb-list">
<table id="list_exten">
	<thead>
	<tr class="sb-top">
		<th class="th-left th-rule">&nbsp;</th>
		<th class="th-center"><?=$this->bbf('col_ctiaccounts_label');?></th>
		<th class="th-center"><?=$this->bbf('col_ctiaccounts_login');?></th>
		<th class="th-center"><?=$this->bbf('col_ctiaccounts_password');?></th>
		<th class="th-right">
			<?=$url->href_html($url->img_html('img/site/button/mini/orange/bo-add.gif',
								$this->bbf('col_row-add'),
								'border="0"'),
							'#',
							null,
							'id="lnk-add-row"',
							$this->bbf('col_row-add'));?>
		</th>
	</tr>
	</thead>
	<tbody>
<?php
$nbla = 0;
if($listaccount !== false
&& ((int) $nbla = count($listaccount)) > 0):
    	for($i = 0;$i < $nbla;$i++):
    		$ref = &$listaccount[$i];

    		if(isset($err[$i]) === true):
    			$errdisplay = ' l-infos-error';
    		else:
    			$errdisplay = '';
    		endif;
?>
	<tr class="fm-paragraph<?=$errdisplay?>">
		<td class="td-left txt-center">
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<span id="box-order" style="float:left;font-weight:bold;"></span>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					      'label'	=> false,
						  'name'	=> 'ctiaccounts[label][]',
						  'labelid'	=> 'ctiaccounts-label',
						  'size'	=> 15,
						  'default'	=> $element['ctiaccounts']['label']['default'],
						  'value'	=> $ref['label']))?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					      'label'	=> false,
						  'name'	=> 'ctiaccounts[login][]',
						  'labelid'	=> 'ctiaccounts-login',
						  'size'	=> 15,
						  'default'	=> $element['ctiaccounts']['login']['default'],
						  'value'	=> $ref['login']))?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					      'label'	=> false,
						  'name'	=> 'ctiaccounts[password][]',
						  'labelid'	=> 'ctiaccounts-password',
						  'size'	=> 15,
						  'default'	=> $element['ctiaccounts']['password']['default'],
						  'value'	=> $ref['password']))?>
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
	<tr id="no-row"<?=(($nbla === 0) ? '' : ' class="b-nodisplay"')?>>
		<td colspan="8" class="td-single"><?=$this->bbf('no_row');?></td>
	</tr>
	</tfoot>
</table>
</div>

<table class="b-nodisplay">
	<tbody id="ex-row">
	<tr class="fm-paragraph">
		<td class="td-left txt-center">
			<span class="ui-icon ui-icon-arrowthick-2-n-s" style="float:left;"></span>
			<span id="box-order" style="float:left;font-weight:bold;"></span>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'ctiaccounts[label][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 15));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'ctiaccounts[login][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 15));?>
		</td>
		<td>
			<?=$form->text(array('paragraph'	=> false,
					     'name'			=> 'ctiaccounts[password][]',
					     'id'			=> false,
					     'label'		=> false,
					     'size'			=> 15));?>
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
</fieldset>
	<fieldset id="cti-servers">
		<legend><?=$this->bbf('cti-servers');?></legend>
		<div class="sb-list">
			<table>
			<tr class="sb-top">
				<th width="70%"><?=$this->bbf('fm_cti_list_ip')?></th>
				<th class="th-right"><?=$this->bbf('fm_cti_list_port')?></th>
			</tr>
			<tr>
				<td>
				<?=$form->text(array('desc'	=> $this->bbf('fm_cti_fagi_ip'),
					'name'	    => 'cti[fagi_ip]',
					'labelid'	=> 'cti_fagi_ip',
					'required'	=> 1,
					'regexp'	=> '[[:ipv4:]]',
					'value'		=> $info['ctimain']['fagi_ip'],
					'default'	=> $element['ctimain']['fagi_ip']['default'] //,
					/* 'help'		=> $this->bbf('hlp_fm_cti_fagi_ip') */ ))
				?>
				</td>
				<td class="td-right">
				<?=$form->text(array(#'desc'	=> $this->bbf('fm_cti_fagi_port'),
					'name'		=> 'cti[fagi_port]',
					'labelid'	=> 'cti_fagi_port',
					'value'		=> $info['ctimain']['fagi_port'],
					'required'	=> 1,
					'regexp'	=> '[[:port:]]',
					'default'	=> $element['ctimain']['fagi_port']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_fagi_port')
					))
				?>
				</td>
			</tr>
			<tr>
				<td>
				<?=$form->text(array('desc'	=> $this->bbf('fm_cti_cti_ip'),
					'name'		=> 'cti[cti_ip]',
					'labelid'	=> 'cti_cti_ip',
					'value'		=> $info['ctimain']['cti_ip'],
					'required'	=> 1,
					'regexp'	=> '[[:ipv4:]]',
					'default'	=> $element['ctimain']['cti_ip']['default'] //,
					/* 'help'		=> $this->bbf('hlp_fm_cti_cti_ip') */ ))
				?>
				</td>
				<td class="td-right">
				<?=$form->text(array(#'desc'	=> $this->bbf('fm_cti_cti_port'),
					'name'		=> 'cti[cti_port]',
					'labelid'	=> 'cti_cti_port',
					'value'		=> $info['ctimain']['cti_port'],
					'required'	=> 1,
					'regexp'	=> '[[:port:]]',
					'default'	=> $element['ctimain']['cti_port']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_cti_port')
					))
				?>
				</td>
			</tr>
			<tr>
				<td>
				<?=$form->text(array('desc'	=> $this->bbf('fm_cti_ctis_ip'),
					'name'		=> 'cti[ctis_ip]',
					'labelid'	=> 'cti_ctis_ip',
					'value'		=> $info['ctimain']['ctis_ip'],
					'required'	=> 1,
					'regexp'	=> '[[:ipv4:]]',
					'default'	=> $element['ctimain']['ctis_ip']['default'] //,
					/* 'help'		=> $this->bbf('hlp_fm_ctis_cti_ip') */ ))
				?>
				</td>
				<td class="td-right">
				<?=$form->text(array(#'desc'	=> $this->bbf('fm_cti_ctis_port'),
					'name'		=> 'cti[ctis_port]',
					'labelid'	=> 'cti_ctis_port',
					'value'		=> $info['ctimain']['ctis_port'],
					'required'	=> 1,
					'regexp'	=> '[[:port:]]',
					'default'	=> $element['ctimain']['ctis_port']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_ctis_port')
					))
				?>
				</td>
			</tr>
			<tr class="sb-content">
				<td>
				<?=$form->text(array('desc'	=> $this->bbf('fm_cti_webi_ip'),
					'name'		=> 'cti[webi_ip]',
					'labelid'	=> 'cti_webi_ip',
					'value'		=> $info['ctimain']['webi_ip'],
					'required'	=> 1,
					'regexp'	=> '[[:ipv4:]]',
					'default'	=> $element['ctimain']['webi_ip']['default'] //,
					/* 'help'		=> $this->bbf('hlp_fm_cti_webi_ip') */ ))
				?>
				</td>
				<td class="td-right">
				<?=$form->text(array(#'desc'	=> $this->bbf('fm_cti_webi_port'),
					'name'		=> 'cti[webi_port]',
					'labelid'	=> 'cti_webi_port',
					'value'		=> $info['ctimain']['webi_port'],
					'required'	=> 1,
					'regexp'	=> '[[:port:]]',
					'default'	=> $element['ctimain']['webi_port']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_webi_port')
					))
				?>
				</td>
			</tr>

			<tr class="sb-content">
				<td>
				<?=$form->text(array('desc'	=> $this->bbf('fm_cti_info_ip'),
					'name'		=> 'cti[info_ip]',
					'labelid'	=> 'cti_info_ip',
					'value'		=> $info['ctimain']['info_ip'],
					'required'	=> 1,
					'regexp'	=> '[[:ipv4:]]',
					'default'	=> $element['ctimain']['info_ip']['default'] //,
					/* 'help'		=> $this->bbf('hlp_fm_cti_info_ip') */ ))
				?>
				</td>
				<td class="td-right">
				<?=$form->text(array(#'desc'	=> $this->bbf('fm_cti_info_port'),
					'name'		=> 'cti[info_port]',
					'labelid'	=> 'cti_info_port',
					'value'		=> $info['ctimain']['info_port'],
					'required'	=> 1,
					'regexp'	=> '[[:port:]]',
					'default'	=> $element['ctimain']['info_port']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_info_port')
					))
				?>
				</td>
			</tr>

			<tr class="sb-content">
				<td>
				<?=$form->text(array('desc'	=> $this->bbf('fm_cti_announce_ip'),
					'name'		=> 'cti[announce_ip]',
					'labelid'	=> 'cti_announce_ip',
					'value'		=> $info['ctimain']['announce_ip'],
					'required'	=> 1,
					'regexp'	=> '[[:ipv4:]]',
					'default'	=> $element['ctimain']['announce_ip']['default'] //,
					/* 'help'		=> $this->bbf('hlp_fm_cti_announce_ip') */ ))
				?>
				</td>
				<td class="td-right">
				<?=$form->text(array(#'desc'	=> $this->bbf('fm_cti_annouce_port'),
					'name'		=> 'cti[announce_port]',
					'labelid'	=> 'cti_announce_port',
					'value'		=> $info['ctimain']['announce_port'],
					'required'	=> 1,
					'regexp'	=> '[[:port:]]',
					'default'	=> $element['ctimain']['announce_port']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_announce_port')
					))
				?>
				</td>
			</tr>
			</table>
		</div>
	</fieldset>
	<fieldset id="cti-intervals">
		<legend><?=$this->bbf('cti-intervals');?></legend>
<?php

	echo	$form->text(array('desc'	=> $this->bbf('fm_cti_updates_period'),
					'name'		=> 'cti[updates_period]',
					'labelid'	=> 'cti_updates_period',
					'value'		=> $info['ctimain']['updates_period'],
					'regexp'	=> '[[:int:]]',
					'default'	=> $element['ctimain']['updates_period']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_updates_period')
					)),

			$form->text(array('desc'	=> $this->bbf('fm_cti_socket_timeout'),
					'name'		=> 'cti[socket_timeout]',
					'labelid'	=> 'cti_socket_timeout',
					'value'		=> $info['ctimain']['socket_timeout'],
					'regexp'	=> '[[:int:]]',
					'default'	=> $element['ctimain']['socket_timeout']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_socket_timeout')
					)),

			$form->text(array('desc'	=> $this->bbf('fm_cti_login_timeout'),
					'name'		=> 'cti[login_timeout]',
					'labelid'	=> 'cti_login_timeout',
					'value'		=> $info['ctimain']['login_timeout'],
					'regexp'	=> '[[:int:]]',
					'default'	=> $element['ctimain']['login_timeout']['default'],
#					'help'		=> $this->bbf('hlp_fm_cti_login_timeout')
					));
?>
	</fieldset>
<?php
	$parting = array();
	if(isset($info['ctimain']['parting_astid_context']) && dwho_has_len($info['ctimain']['parting_astid_context']))
	{
		$parting = explode(',', $info['ctimain']['parting_astid_context']);
	}
	echo	$form->checkbox(array('desc' => $this->bbf('fm_cti_parting_astid_context'),
							'name' => 'cti[parting_astid_context]',
							'labelid' => 'cti_parting_astid_context',
							'checked' => in_array('context', $parting))),

			$form->checkbox(array('desc' => $this->bbf('fm_cti_parting_astid_ipbx'),
							'name' => 'cti[parting_astid_ipbx]',
							'labelid' => 'cti_parting_astid_ipbx',
							'checked' => in_array('astid', $parting)));
?>
	<br />
	<fieldset id="cti-xivo_servers">
		<legend><?=$this->bbf('cti-xivo_servers');?></legend>
		<div id="xivoserver" class="fm-paragraph">
		    <?=$form->jq_select(array('paragraph'	=> false,
					 	'label'		=> false,
            			'name'    	=> 'xivoserver[]',
						'id' 		=> 'it-xivoserver',
						'key'		=> 'identity',
				       	'altkey'	=> 'id',
            			'selected'  => $info['xivoserver']['slt']),
					$info['xivoserver']['list']);?>
		</div>
		<div class="clearboth"></div>
	</fieldset>
</div>

<?php
	echo	$form->submit(array('name'	=> 'submit',
				    'id'	=> 'it-submit',
				    'value'	=> $this->bbf('fm_bt-save')));
?>
</form>

	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
