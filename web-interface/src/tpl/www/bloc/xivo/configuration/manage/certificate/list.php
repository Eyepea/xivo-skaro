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

$url = &$this->get_module('url');
$form = &$this->get_module('form');
$dhtml = &$this->get_module('dhtml');

$pager = $this->get_var('pager');
$act = $this->get_var('act');

$page = $url->pager($pager['pages'],
		    $pager['page'],
		    $pager['prev'],
		    $pager['next'],
		    'xivo/configuration/manage/certificate',
		    array('act' => $act));

?>
<div class="b-list">
<?php
	if($page !== ''):
		echo '<div class="b-page">',$page,'</div>';
	endif;
?>
<form action="#" name="fm-certificate-list" method="post" accept-charset="utf-8">
<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID)),

		$form->hidden(array('name'	=> 'act',
				    'value'	=> $act)),

		$form->hidden(array('name'	=> 'page',
				    'value'	=> $pager['page']));
?>
<table id="table-main-listing">
	<tr class="sb-top">
		<th class="th-left xspan"><span class="span-left">&nbsp;</span></th>
		<th class="th-center"><?=$this->bbf('col_type');?></th>
		<th class="th-center"><?=$this->bbf('col_name');?></th>
		<th class="th-center"><?=$this->bbf('col_length');?></th>
		<th class="th-center"><?=$this->bbf('col_validity');?></th>
		<th class="th-center col-action"><?=$this->bbf('col_action');?></th>
		<th class="th-right xspan"><span class="span-right">&nbsp;</span></th>
	</tr>
<?php
	if(($list = $this->get_var('list')) === false || ($nb = count($list)) === 0):
?>
	<tr class="sb-content">
		<td colspan="8" class="td-single"><?=$this->bbf('no_certificate');?></td>
	</tr>
<?php
	else:
		for($i = 0;$i < $nb;$i++):
			$ref  = &$list[$i];
?>
	<tr onmouseover="this.tmp = this.className; this.className = 'sb-content l-infos-over';"
	    onmouseout="this.className = this.tmp;"
	    class="sb-content l-infos-<?=(($i % 2) + 1)?>on2">
		<td class="td-left">
			<?=$form->checkbox(array('name'		=> 'certificates[]',
						 'value'	=> $ref['filename'],
						 'label'	=> false,
						 'id'		=> 'it-certificate-'.$i,
						 'checked'	=> false,
						 'paragraph'	=> false));?>
		</td>
		<td class="txt-left">
			<label for="it-certificate-<?=$i?>" id="lb-certificate-<?=$i?>">
<?php
			// keys
			// certificates
			if(in_array('certificate', $ref['types'])) {
				if(array_key_exists('CA', $ref) && $ref['CA'] == 1)
					echo '<img title="'.$this->bbf('ca_authority').'" src="/img/site/utils/cacert.png" />';
				else if(array_key_exists('autosigned',$ref) && $ref['autosigned'])
					echo '<img title="'.$this->bbf('autosigned').'" src="/img/site/utils/autosigned.png" />';
				else
					echo '<img title="'.$this->bbf('certificate').'" src="/img/site/utils/stock_lock.png" />';
			}
			if(in_array('privkey', $ref['types']))
				echo '<img title="'.$this->bbf('private_key').'" src="/img/site/utils/privkey.png" />';
			if(in_array('pubkey', $ref['types']))
				echo '<img title="'.$this->bbf('public_key').'" src="/img/site/utils/pubkey.png" />';
?>
			</label>
		</td>

		<td><?=$ref['name'];?></td>
		<td><?=in_array('certificate', $ref['types'])?$ref['length']:'&nbsp;'?></td>
		<td><?=in_array('certificate', $ref['types'])?$ref['validity-end']:'&nbsp;'?></td>
		<td class="td-right" colspan="2">
<?
		if(in_array('certificate', $ref['types']))
			echo	$url->href_html($url->img_html('img/site/button/monitor.gif',
							       $this->bbf('opt_modify'),
							       'border="0"'),
						'xivo/configuration/manage/certificate',
						array('act'	=> 'edit',
						      'id'	=> $ref['filename']),
						null,
						$this->bbf('opt_view'));

		echo $url->href_html($url->img_html('img/site/button/key.gif',
								       $this->bbf('opt_acl'),
								       'border="0"'),
						'xivo/configuration/manage/certificate',
						array('act'	=> 'export',
						      'id'	=> $ref['filename']),
						null,
						$this->bbf('opt_export'));

		echo $url->href_html($url->img_html('img/site/button/delete.gif',
							       $this->bbf('opt_delete'),
						       'border="0"'),
						'xivo/configuration/manage/certificate',
						array('act'	=> 'delete',
									'id'	=> $ref['filename'],
						      'page'	=> $pager['page']),
						'onclick="return(confirm(\''.$dhtml->escape($this->bbf('opt_delete_confirm')).'\'));"',
						$this->bbf('opt_delete'));
?>
		</td>
	</tr>
<?php
		endfor;
	endif;
?>
	<tr class="sb-foot">
		<td class="td-left xspan b-nosize"><span class="span-left b-nosize">&nbsp;</span></td>
		<td class="td-center" colspan="5"><span class="b-nosize">&nbsp;</span></td>
		<td class="td-right xspan b-nosize"><span class="span-right b-nosize">&nbsp;</span></td>
	</tr>
</table>
</form>
<?php
	if($page !== ''):
		echo '<div class="b-page">',$page,'</div>';
	endif;
?>
</div>
