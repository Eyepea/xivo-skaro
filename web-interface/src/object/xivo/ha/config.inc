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

$array['element']['active'] = array();
$array['element']['active']['value'] = array(0,1);
$array['element']['active']['default'] = 0;
$array['element']['active']['set'] = true;

$array['element']['type'] = array();
$array['element']['type']['value'] = array('slave','master');
$array['element']['type']['default'] = '';

$array['element']['remote_address'] = array();
$array['element']['remote_address']['default'] = '';


$array['filter'] = array();
$array['filter']['type'] = array('key' => $array['element']['type']['value']);
$array['filter']['remote_address'] = array(
					'callback'		=> 'dwho_network::valid_host',
					'callbackarg'	=> array(DWHO_NETWORK_HOST_IPV4_DOTDEC));

?>
