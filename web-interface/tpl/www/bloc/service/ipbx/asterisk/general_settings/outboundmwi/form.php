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
$url = $this->get_module('url');

$info = $this->get_var('info');
$element = $this->get_var('element');
$context_list = $this->get_var('context_list');

if($this->get_var('fm_save') === false):
	$dhtml = &$this->get_module('dhtml');
	$dhtml->write_js('xivo_form_result(false,\''.$dhtml->escape($this->bbf('fm_error-save')).'\');');
endif;

?>

<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_outboundmwi_username'),
				  'name'	=> 'outboundmwi[username]',
				  'labelid'	=> 'outboundmwi-username',
				  'size'	=> 15,
				  'default'	=> $element['outboundmwi']['username']['default'],
				  'value'	=> $info['username'],
				  'error'	=> $this->bbf_args('error',
						   $this->get_var('error', 'outboundmwi', 'username')) )),

			 $form->text(array('desc'	=> $this->bbf('fm_outboundmwi_password'),
				  'name'	=> 'outboundmwi[password]',
				  'labelid'	=> 'outboundmwi-password',
				  'size'	=> 15,
				  'default'	=> $element['outboundmwi']['password']['default'],
				  'value'	=> $info['password'],
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'outboundmwi', 'password')) )),

	     $form->text(array('desc'	=> $this->bbf('fm_outboundmwi_authuser'),
				  'name'	=> 'outboundmwi[authuser]',
				  'labelid'	=> 'outboundmwi-authuser',
				  'size'	=> 15,
				  'default'	=> $element['outboundmwi']['authuser']['default'],
				  'value'	=> $info['authuser'],
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'outboundmwi', 'authuser')) )),

       $form->text(array('desc'	=> $this->bbf('fm_outboundmwi_host'),
				  'name'	=> 'outboundmwi[host]',
				  'labelid'	=> 'outboundmwi-host',
				  'size'	=> 15,
				  'default'	=> $element['outboundmwi']['host']['default'],
				  'value'	=> $info['host'],
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'outboundmwi', 'host')) )),

	     $form->text(array('desc'	=> $this->bbf('fm_outboundmwi_port'),
				  'name'	=> 'outboundmwi[port]',
				  'labelid'	=> 'outboundmwi-port',
				  'size'	=> 15,
				  'default'	=> $element['outboundmwi']['port']['default'],
				  'value'	=> $info['port'],
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'outboundmwi', 'port')) )),

	     $form->text(array('desc'	=> $this->bbf('fm_outboundmwi_mailbox'),
				  'name'	=> 'outboundmwi[mailbox]',
				  'labelid'	=> 'outboundmwi-mailbox',
				  'size'	=> 15,
				  'default'	=> $element['outboundmwi']['mailbox']['default'],
				  'value'	=> $info['mailbox'],
				  'error'	=> $this->bbf_args('error',
					$this->get_var('error', 'outboundmwi', 'mailbox')) ));
?>

