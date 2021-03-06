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

echo	nl2br($this->bbf('welcome_description')),

	$form->select(array('desc'	=> $this->bbf('fm_language'),
			    'name' 	=> 'hl',
			    'id'	=> 'it-language',
			    'selected' 	=> DWHO_I18N_BABELFISH_LANGUAGE,
			    'error'	=> $this->bbf_args('error_fm_language',$this->get_var('error','welcome','language'))),
		      $this->get_var('language'));

?>
