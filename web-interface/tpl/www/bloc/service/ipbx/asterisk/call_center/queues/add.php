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

?>
<div id="sr-queues" class="b-infos b-form">
	<h3 class="sb-top xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center"><?=$this->bbf('title_content_name');?></span>
		<span class="span-right">&nbsp;</span>
	</h3>
<?php
	$this->file_include('bloc/service/ipbx/asterisk/call_center/queues/submenu');
?>

	<div class="sb-content">
		<form action="#" method="post" accept-charset="utf-8" onsubmit="dwho.form.select('it-queue-periodic-announce');
										dwho.form.select('it-user');
										dwho.form.select('it-agentgroup');
										dwho.form.select('it-agent');
										dwho.form.select('it-rightcall');
										dwho.form.select('it-ctipresence');
										dwho.form.select('it-nonctipresence');">
<?php
		echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
					    'value'	=> DWHO_SESS_ID)),

			$form->hidden(array('name'	=> 'act',
					    'value'	=> 'add')),

			$form->hidden(array('name'	=> 'fm_send',
					    'value'	=> 1));

		$this->file_include('bloc/service/ipbx/asterisk/call_center/queues/form');

		echo	$form->submit(array('name'	=> 'submit',
					    'id'	=> 'it-submit',
					    'value'	=> $this->bbf('fm_bt-save')));
?>

		</form>
	</div>
	<div class="sb-foot xspan">
		<span class="span-left">&nbsp;</span>
		<span class="span-center">&nbsp;</span>
		<span class="span-right">&nbsp;</span>
	</div>
</div>
