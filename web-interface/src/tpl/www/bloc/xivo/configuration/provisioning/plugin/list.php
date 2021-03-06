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
		    'xivo/configuration/provisioning/plugin',
		    array('act' => $act));
?>
<div class="b-list">
<?php
	if($page !== ''):
		echo '<div class="b-page">',$page,'</div>';
	endif;
?>
<form action="#" name="fm-plugin-list" method="post" accept-charset="utf-8">
<?=$form->hidden(array('name' => DWHO_SESS_NAME,'value'	=> DWHO_SESS_ID));?>
<?=$form->hidden(array('name' => 'act','value'	=> $act));?>
<?=$form->hidden(array('name' => 'page','value' => $pager['page']));?>

<div id="box_installer" class="bi_bg">
	<div class="bi_message">
	<div class="bi_loading"><?=$url->img_html('img/site/loading.gif', $this->bbf('img_loading'), 'height="75" width="75" border="0"')?></div>
	</div>
</div>

<table id="table-main-listing">
	<tr class="sb-top">
		<th class="th-left xspan"><span class="span-left">&nbsp;</span></th>
		<th class="th-center"><?=$this->bbf('col_name');?></th>
		<th class="th-center"><?=$this->bbf('col_description');?></th>
		<th class="th-center"><?=$this->bbf('col_version');?></th>
		<th class="th-center"><?=$this->bbf('col_size');?></th>
		<th class="th-center col-action"><?=$this->bbf('col_action');?></th>
		<th class="th-right xspan"><span class="span-right">&nbsp;</span></th>
	</tr>
<?php
	if(($list = $this->get_var('list')) === false || ($nb = count($list)) === 0):
?>
	<tr class="sb-content">
		<td colspan="7" class="td-single"><?=$this->bbf('no_plugin');?></td>
	</tr>
<?php
	else:
		for($i = 0;$i < $nb;$i++):
			$ref = &$list[$i];

		$upgrade = false;
		if (isset($ref['version-installable']) === true):
			if($ref['version'] !== $ref['version-installable']):
				$upgrade = true;
			 	$version = '<b>'.$ref['version'].' / '.$ref['version-installable'].'</b>';
			else:
				$version = $ref['version'];
			endif;
		else:
			$version = $ref['version'];
		endif;
?>
	<tr onmouseover="this.tmp = this.className; this.className = 'sb-content l-infos-over';"
	    onmouseout="this.className = this.tmp;"
	    class="sb-content l-infos-<?=(($i % 2) + 1)?>on2">
		<td class="td-left">
			&nbsp;
		</td>
		<td class="txt-left" title="<?=dwho_alttitle($ref['name']);?>">
			<?=dwho_htmlen(dwho_trunc($ref['name'],25,'...',false));?>
		</td>
		<td class="txt-left" title="<?=dwho_alttitle($ref['description']);?>">
			<?=dwho_htmlen(dwho_trunc($ref['description'],65,'...',false));?>
		</td>
		<td>
			<?=$version?>
<?php
		if ($upgrade === true):
			echo	$url->href_html($url->img_html('img/site/utils/app-upgrade.png',
							       $this->bbf('opt_upgrade'),
							       'border="0"'),
						'xivo/configuration/provisioning/plugin',
						array('act'	=> 'upgrade',
						      'id'	=> $ref['name']),
						'style="margin-left:2px"',
						$this->bbf('opt_upgrade'));
		endif;
?>
		</td>
		<td><?=(isset($ref['dsize']) === true ? dwho_byte_to($ref['dsize']) : '-')?></td>
		<td class="td-right" colspan="2">
<?php
		if ($ref['type'] === 'installable'):
			echo	$url->href_html($url->img_html('img/site/utils/app-install.png',
							       $this->bbf('opt_install'),
							       'border="0"'),
						'#',
						null,
						'onclick="init_install_plugin(\''.$ref['name'].'\');return(false);"',
						$this->bbf('opt_install'));
		elseif ($ref['type'] === 'installed'):
			echo	$url->href_html($url->img_html('img/site/utils/edit-link.png',
							       $this->bbf('opt_modify'),
							       'border="0"'),
						'xivo/configuration/provisioning/plugin',
						array('act'	=> 'edit',
						      'id'	=> $ref['name']),
						'style="margin-left:2px"',
						$this->bbf('opt_modify'));
			echo	$url->href_html($url->img_html('img/site/utils/app-delete.png',
							       $this->bbf('opt_uninstall'),
							       'border="0"'),
						'xivo/configuration/provisioning/plugin',
						array('act'	=> 'uninstall',
						      'id'	=> $ref['name']),
						'onclick="return(confirm(\''.$dhtml->escape($this->bbf('opt_uninstall_confirm')).'\'));" style="margin-left:2px"',
						$this->bbf('opt_uninstall'));
		endif;
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
