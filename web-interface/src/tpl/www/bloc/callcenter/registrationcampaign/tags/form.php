<?php

#
# XiVO Web-Interface
# Copyright (C) 2010  Avencall
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
$url  = &$this->get_module('url');

$info 		= $this->get_var('info');
$element 	= $this->get_var('element');

?>

<div id="sb-part-first">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_tag_name'),
				  'name'	=> 'tag[name]',
				  'labelid'	=> 'tag-name',
					'size'	=> 32,
				  'default'	=> $element['name']['default'],
				  'value'	=> $this->get_var('info','tag','name'),
			    'error'	=> $this->bbf($this->get_var('error', 'name')) )),

			$form->text(array('desc'	=> $this->bbf('fm_tag_label'),
				  'name'	=> 'tag[label]',
				  'labelid'	=> 'tag-label',
				  'size'	=> 32,
				  'default'	=> $element['label']['default'],
				  'value'	=> $this->get_var('info','tag','label'),
					'error'	=> $this->bbf($this->get_var('error', 'label')) )),

			$form->select(array('desc'	=> $this->bbf('fm_tag_action'),
				    'name'	    => 'tag[action]',
				    'labelid'	  => 'tag-action',
				    'key'	      => false,
				    'bbf'      	=> 'fm_tag_action-opt',
				    'bbfopt'	  => array('argmode' => 'paramvalue'),
				    'default'	  => $element['action']['default'],
				    'selected'	=> $this->get_var('info','tag','action')),
			      $element['action']['value']);
?>

</div>

