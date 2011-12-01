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

$act	 = $this->get_var('act');
$info    = $this->get_var('info');
$error   = $this->get_var('error');
$element = $this->get_var('element');
$context_list = $this->get_var('context_list');
$ipbxinfos = $this->get_var('info','ipbx');

if(isset($info['protocol']) === true):
	$allow = explode(',', $info['protocol']['allow']);
	$protocol = (string) dwho_ak('protocol',$info['protocol'],true);
	$context = (string) dwho_ak('context',$info['protocol'],true);
	$amaflags = (string) dwho_ak('amaflags',$info['protocol'],true);
	$qualify = (string) dwho_ak('qualify',$info['protocol'],true);
	$host = (string) dwho_ak('host',$info['protocol'],true);
	$number = (string) dwho_ak('number',$info['linefeatures'],true);
else:
	$allow = array();
	$protocol = $this->get_var('proto');
	$context = $amaflags = $qualify = $host = $number = '';
endif;

$codec_active = empty($allow) === false;
$host_static = ($host !== '' && $host !== 'dynamic');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

echo $form->hidden(array('name' => 'proto','value' => $protocol));

$hasnumber = false;
if (empty($number) === false):
	echo $form->hidden(array('name' => 'protocol[context]','value' => $context));
	$hasnumber = true;
endif;

$filename = dirname(__FILE__).'/protocol/'.$protocol.'.php';
if (is_readable($filename) === true)
	include($filename);
?>

<div id="sb-part-ipbxinfos" class="b-nodisplay">
<div class="sb-list">
<table>
	<thead>
	<tr class="sb-top">
		<th class="th-left"><?=$this->bbf('col_line-key');?></th>
		<th class="th-right"><?=$this->bbf('col_line-value');?></th>
	</tr>
	</thead>
<?php
$i = 0;
if($ipbxinfos !== false
&& ($nb = count($ipbxinfos)) !== 0):
	foreach($ipbxinfos as $k => $v):
?>
	<tbody>
	<tr onmouseover="this.tmp = this.className; this.className = 'sb-content l-infos-over';"
	    onmouseout="this.className = this.tmp;"
	    class="fm-paragraph l-infos-<?=(($i++ % 2) + 1)?>on2">
		<td class="td-left"><?=$k?></td>
		<td class="td-right"><?=$v?></td>
	</tr>
<?php
	endforeach;
else:
?>
	<tfoot>
	<tr<?=($ipbxinfos !== false ? ' class="b-nodisplay"' : '')?>>
		<td colspan="2" class="td-single"><?=$this->bbf('no_ipbxinfos_found');?></td>
	</tr>
	</tfoot>
<?php
endif;
?>
	</tbody>
</table>
</div>
</div>
