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

<div id="sb-part-first" class="b-nodisplay">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_config_ip'),
				  'name'	=> 'config[ip]',
				  'labelid'	=> 'config-ip',
				  'size'	=> 15,
				  'default'	=> $element['config']['ip']['default'],
				  'value'	=> $info['config']['ip'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','config','ip')))),
					   
			$form->text(array('desc'	=> $this->bbf('fm_config_http_port'),
				  'name'	=> 'config[http_port]',
				  'labelid'	=> 'config-http_port',
				  'size'	=> 5,
				  'default'	=> $element['config']['http_port']['default'],
				  'value'	=> $info['config']['http_port'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','config','http_port')))),
					   
			$form->text(array('desc'	=> $this->bbf('fm_config_tftp_port'),
				  'name'	=> 'config[tftp_port]',
				  'labelid'	=> 'config-tftp_port',
				  'size'	=> 5,
				  'default'	=> $element['config']['tftp_port']['default'],
				  'value'	=> $info['config']['tftp_port'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','config','tftp_port'))));
/*
	echo	$form->select(array('desc'	=> $this->bbf('fm_config_http_port'),
				    'name'	=> 'queue[http_port]',
				    'labelid'	=> 'queue-http_port',
				    'key'	=> false,
				    'bbf'	=> 'fm_queue_strategy-opt',
				    'bbfopt'	=> array('argmode' => 'paramvalue'),
				    'default'	=> $element['queue']['strategy']['default'],
				    'selected'	=> $info['queue']['strategy']),
			      $element['queue']['strategy']['value']);
*/
?>
</div>

<div id="sb-part-lines" class="b-nodisplay">
<?php
	if(isset($info['config']['sip']) === true):
		
		if(isset($info['config']['sip']['lines']) === true):
			foreach ($info['config']['sip']['lines'] as $k => $v):
				
			endforeach;
		endif;
		
	endif;
	if(isset($info['config']['sccp']) === true
	&& isset($info['config']['sccp']['call_managers']) === true):
		echo	$form->text(array('desc'	=> $this->bbf('fm_config_sccp_call_managers_ip'),
				  'name'	=> 'config[sccp][call_managers][ip]',
				  'labelid'	=> 'config-sccp_call_managers_ip',
				  'size'	=> 15,
				  'default'	=> $element['config']['sccp']['call_managers']['default'],
				  'value'	=> $info['config']['sccp']['call_managers'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','config','ip')) )),
					   
			$form->text(array('desc'	=> $this->bbf('fm_config_sccp_call_managers_port'),
				  'name'	=> 'config[sccp][call_managers][port]',
				  'labelid'	=> 'config-sccp_call_managers_port',
				  'size'	=> 5,
				  'default'	=> $element['config']['sccp']['call_managers']['port']['default'],
				  'value'	=> $info['config']['sccp']['call_managers']['port'],
				  'error'	=> $this->bbf_args('error',
					   $this->get_var('error','config','http_port'))));
	
	endif;
?>
</div>

<div id="sb-part-advanced" class="b-nodisplay">
	advanced
</div>
