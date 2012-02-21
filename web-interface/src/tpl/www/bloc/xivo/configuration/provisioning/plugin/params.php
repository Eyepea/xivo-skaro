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

if (($params = $info['params']) !== false
&& is_array($params) === true
&& ($nb = count($params)) > 0):

	$uri = '/xivo/configuration/ui.php/provisioning/plugin';

	for($i=0;$i<$nb;$i++):
		$ref = &$params[$i];
		if (isset($ref['links'][0]) === false
		|| isset($ref['links'][0]['href']) === false
		|| ($href = $ref['links'][0]['href']) === '')
			continue;
?>
<div id="res-<?=$ref['id']?>"></div>
<?php
	echo	$form->hidden(array('name'	=> 'href',
			  'id'	    => 'href-'.$ref['id'],
			  'value'	=> $href));
	echo	$form->hidden(array('name'	=> 'uri',
			  'id'	    => 'uri-'.$ref['id'],
			  'value'	=> $uri));
	echo	$form->hidden(array('name'	=> 'act',
			  'id'	    => 'act-'.$ref['id'],
			  'value'	=> 'editparams'));
	echo	$form->text(array('desc' => $this->bbf('fm_configure_'.$ref['id']),
			  'name'	=> $ref['id'],
			  'id'		=> 'configure-ajax',
			  'size'	=> strlen($ref['value']),
			  'value'	=> $ref['value'],
			  'help'	=> $ref['description']));
?>
<?php
	endfor;
endif;
?>