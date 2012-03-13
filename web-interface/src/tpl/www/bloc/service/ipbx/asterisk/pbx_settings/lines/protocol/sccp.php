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

$info = $this->get_var('info');
$error = $this->get_var('error');
$element = $this->get_var('element');

?>

<div id="sb-part-first">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_protocol_name'),
				  'name'	=> 'protocol[name]',
				  'labelid'	=> 'protocol-name',
				  'size'	=> 18,
				  'disabled'	=> true,
				  'readonly' => true,
				  'class'    => 'it-disabled',
				  'default'	=> $element['protocol']['sccp']['name']['default'],
				  'value'	=> $this->get_var('info','protocol','name'),
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'sccp', 'name')) )),

	$form->text(array('desc'	=> $this->bbf('fm_linefeatures_number'),
					  'name'	=> 'linefeatures[number]',
					  'labelid'	=> 'linefeatures-number',
					  'size'	=> 6,
					  'disabled'	=> true,
					  'readonly' => true,
					  'class'    => 'it-disabled',
					  'value'	=> $this->get_var('info','linefeatures','number'),
					  'error'	=> $this->bbf_args('error',$this->get_var('error', 'linefeatures', 'number')) ));

	if($context_list !== false):
		echo	$form->select(array('desc'	=> $this->bbf('fm_protocol_context'),
					    'name'		=> 'protocol[context]',
					    'labelid'	=> 'protocol-context',
					 	'disabled'	=> $hasnumber,
						'class'    	=> ($hasnumber ? 'it-disabled' : ''),
					    'key'		=> 'identity',
					    'altkey'	=> 'name',
					    'selected'	=> $context),
				      $context_list);
	else:
		echo	'<div id="fd-protocol-context" class="txt-center">',
			$url->href_htmln($this->bbf('create_context'),
					'service/ipbx/system_management/context',
					'act=add'),
			'</div>';
	endif;
?>
</div>
