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
$element = $this->get_var('element');


echo $form->hidden(array('name' => 'dbconfig[backend]', 'value' => 'postgresql'));
/*
echo	$form->select(array('desc'	=> $this->bbf('fm_dbconfig_backend'),
			    'name'	=> 'dbconfig[backend]',
			    'labelid'	=> 'dbconfig-backend',
			    'key'	=> 'label',
			    'help'	=> $this->bbf('hlp_fm_dbconfig_backend'),
			    'default'	=> $element['backend']['default'],
			    'selected'	=> $this->get_var('info','backend'),
			    'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('dbconfig','backend'))),
		      $this->get_var('dbbackend'));

echo	$form->checkbox(array('desc'		=> $this->bbf('fm_dbconfig_create_auto'),
			      'name'		=> 'dbconfig[create_auto]',
			      'labelid'		=> 'dbconfig-create_auto',
			  	  'default'		=> $element['create_auto']['default'],
			      'checked'		=> $this->get_var('dbconfig_is_autocreate')));
*/
?>
<div id="sb-part_dbconfig_postgresql">
<?php
	echo	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-host'),
			  'name'	=> 'dbconfig[postgresql][host]',
			  'labelid'	=> 'dbconfig-postgresql-host',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-host'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-host'),
			  'default'	=> $element['postgresql']['host']['default'],
			  'value'	=> $this->get_var('info','postgresql','host'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','host')))),

	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-port'),
			  'name'	=> 'dbconfig[postgresql][port]',
			  'labelid'	=> 'dbconfig-postgresql-port',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-port'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-port'),
			  'default'	=> $element['postgresql']['port']['default'],
			  'value'	=> $this->get_var('info','postgresql','port'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','port'))));

if(($error = (string) $this->get_var('error','dbconfig','postgresql','xivodb')) !== ''):
	echo	'<div id="error-dbconfig-postgresql-xivo" class="dwho-txt-error">','
			<span class="dwho-msg-error-icon">&nbsp;</span>',
			$this->bbf_args('error_dbconfig_xivo',$error),
		'</div>';
endif;

echo	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-xivodbname'),
			  'name'	=> 'dbconfig[postgresql][xivodbname]',
			  'labelid'	=> 'dbconfig-postgresql-xivodbname',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-xivodbname'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-xivodbname'),
			  'default'	=> $element['postgresql']['xivodbname']['default'],
			  'value'	=> $this->get_var('info','postgresql','xivodbname'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','xivodbname')))),

	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-xivouser'),
			  'name'	=> 'dbconfig[postgresql][xivouser]',
			  'labelid'	=> 'dbconfig-postgresql-xivouser',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-xivouser'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-xivouser'),
			  'default'	=> $element['postgresql']['xivouser']['default'],
			  'value'	=> $this->get_var('info','postgresql','xivouser'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','xivouser')))),

	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-xivopass'),
			  'name'	=> 'dbconfig[postgresql][xivopass]',
			  'labelid'	=> 'dbconfig-postgresql-xivopass',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-xivopass'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-xivopass'),
			  'default'	=> $element['postgresql']['xivopass']['default'],
			  'value'	=> $this->get_var('info','postgresql','xivopass'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','xivopass'))));

if(($error = (string) $this->get_var('error','dbconfig','postgresql','ipbxdb')) !== ''):
	echo	'<div id="error-dbconfig-postgresql-ipbx" class="dwho-txt-error">',
			'<span class="dwho-msg-error-icon">&nbsp;</span>',
			$this->bbf_args('error_dbconfig_ipbx',$error),
		'</div>';
endif;

echo	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-ipbxdbname'),
			  'name'	=> 'dbconfig[postgresql][ipbxdbname]',
			  'labelid'	=> 'dbconfig-postgresql-ipbxdbname',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-ipbxdbname'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-ipbxdbname'),
			  'default'	=> $element['postgresql']['ipbxdbname']['default'],
			  'value'	=> $this->get_var('info','postgresql','ipbxdbname'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','ipbxdbname')))),

	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-ipbxuser'),
			  'name'	=> 'dbconfig[postgresql][ipbxuser]',
			  'labelid'	=> 'dbconfig-postgresql-ipbxuser',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-ipbxuser'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-ipbxuser'),
			  'default'	=> $element['postgresql']['ipbxuser']['default'],
			  'value'	=> $this->get_var('info','postgresql','ipbxuser'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','ipbxuser')))),

	$form->text(array('desc'	=> $this->bbf('fm_dbconfig_postgresql-ipbxpass'),
			  'name'	=> 'dbconfig[postgresql][ipbxpass]',
			  'labelid'	=> 'dbconfig-postgresql-ipbxpass',
			  'size'	=> 20,
#			  'help'	=> $this->bbf('hlp_fm_dbconfig_postgresql-ipbxpass'),
			  'comment'	=> $this->bbf('cmt_fm_dbconfig_postgresql-ipbxpass'),
			  'default'	=> $element['postgresql']['ipbxpass']['default'],
			  'value'	=> $this->get_var('info','postgresql','ipbxpass'),
			  'error'	=> $this->bbf_args('error_generic',
							   $this->get_var('error','dbconfig','postgresql','ipbxpass'))));

?>
</div>
