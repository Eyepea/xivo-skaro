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
$info = $this->get_var('info');

?>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_queuefeatures_name'),
				  'name'	=> 'queuefeatures[name]',
				  'labelid' => 'queuefeatures-name',
				  'size'	=> 15,
				  'default'	=> $element['queuefeatures']['displayname']['default'],
				  'value'	=> $this->get_var('info','queuefeatures','name'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queuefeatures','name')))),

		$form->text(array('desc'	=> $this->bbf('fm_queuefeatures_number'),
				  'name'	=> 'queuefeatures[number]',
				  'labelid' => 'queuefeatures-number',
				  'size'	=> 15,
				  'default'	=> $element['queuefeatures']['number']['default'],
				  'value'	=> $this->get_var('info','queuefeatures','number'),
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','queuefeatures','number'))));
?>
