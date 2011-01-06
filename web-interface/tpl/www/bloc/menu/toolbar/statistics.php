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
$dhtml = &$this->get_module('dhtml');

$listconf = $this->get_var('listconf');

?>
<script type="text/javascript" src="<?=$this->file_time($this->url('js/xivo_toolbar.js'));?>"></script>

<form action="#" method="post" accept-charset="utf-8">
<?php
	echo	$form->hidden(array('name'	=> DWHO_SESS_NAME,
				    'value'	=> DWHO_SESS_ID));
?>
	<div class="fm-paragraph">
<?php
		echo	$form->select(array('name'	=> 'confid',
					    'id'		=> 'it-toolbar-conf',
					    'paragraph'	=> false,
					    'browse'	=> 'conf',
					    'empty'		=> $this->bbf('toolbar_fm_conf'),
					    'key'		=> 'name',
					    'altkey'	=> 'id',
					    'selected'	=> $this->get_var('confid')),
				      	$listconf);
?>
	</div>
</form>

<script type="text/javascript">
dwho.dom.set_onload(function()
{
	dwho.dom.add_event('change',
			   dwho_eid('it-toolbar-conf'),
			   function()
			   {
				this.form.submit();
			   });
});
</script>
