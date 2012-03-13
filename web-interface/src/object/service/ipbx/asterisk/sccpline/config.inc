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

$array = array();

$array['element'] = array();

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['context'] = array();
$array['element']['context']['default'] = 'default';

$array['element']['cid_name'] = array();
$array['element']['cid_name']['default'] = '';

$array['element']['cid_num'] = array();
$array['element']['cid_num']['default'] = '';

dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['name'] = array('minlen' => 1,'maxlen' => 80,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['context'] = array('callback' => 'xivo_service_asterisk::chk_context',
									'callbackarg' => array(array(
												XIVO_SRE_IPBX_AST_CONTEXT_AUTHENTICATION,
												XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['cid_name'] = array('minlen' => 1,'maxlen' => 80,'cast' => 'sgraph');
$array['filter']['cid_num'] = array('minlen' => 1,'maxlen' => 80,'regexp' => '/^[a-z0-9_-]+$/i');

?>
