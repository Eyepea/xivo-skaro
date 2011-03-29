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

$act	 = $this->get_var('act');
$info    = $this->get_var('info');
$error   = $this->get_var('error');
$element = $this->get_var('element');
$context_list = $this->get_var('context_list');

if(isset($info['protocol']) === true):
	if(dwho_issa('allow',$info['protocol']) === true):
		$allow = $info['protocol']['allow'];
	else:
		$allow = array();
	endif;

	$protocol = (string) dwho_ak('protocol',$info['protocol'],true);
	$context = (string) dwho_ak('context',$info['protocol'],true);
	$amaflags = (string) dwho_ak('amaflags',$info['protocol'],true);
	$qualify = (string) dwho_ak('qualify',$info['protocol'],true);
	$host = (string) dwho_ak('host',$info['protocol'],true);
else:
	$allow = array();
	$protocol = $this->get_var('proto');
	$context = $amaflags = $qualify = $host = '';
endif;

$codec_active = empty($allow) === false;
$host_static = ($host !== '' && $host !== 'dynamic');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>
<?=$form->hidden(array('name' => 'proto','value' => $protocol))?>
<?php
	$filename = dirname(__FILE__).'/protocol/'.$protocol.'.php';
	if (is_readable($filename) === true)
		include($filename);
?>