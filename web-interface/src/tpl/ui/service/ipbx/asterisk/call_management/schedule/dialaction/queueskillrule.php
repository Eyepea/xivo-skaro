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

$form 	 = &$this->get_module('form');
$url 	 = &$this->get_module('url');
$dhtml 	 = &$this->get_module('dhtml');

$element = $this->get_var('element');
$event 	 = $this->get_var('event');
$skillrules = $this->get_var('skillrules');

echo '<div id="fd-dialaction-',$event,'-queueskillrule-actiontype" class="b-nodisplay">',
     $form->select(array('desc'	=> $this->bbf('fm_dialaction_queueskillrule-name'),
			    'name'	=> 'dialaction['.$event.'][name]',
			    'labelid'	=> 'dialaction-'.$event.'-queueskillrule-name',
			    'key'	=> 'name',
			    'altkey'	=> 'name',
			    ),
		      $skillrules),

     $form->button(array('name'		=> 'add-defapplication-queueskillrule',
			 'id'		=> 'it-add-defapplication-queueskillrule',
			 'value'	=> $this->bbf('fm_bt-add')),
		         'onclick="xivo_ast_defapplication_queueskillrule(\''.$dhtml->escape($event).'\',\'it-voicemenu-flow\');"'),

     '</div>';

?>
