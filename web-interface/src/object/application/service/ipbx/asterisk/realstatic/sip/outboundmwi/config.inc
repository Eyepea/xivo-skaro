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

$array['element']['username'] = array();
$array['element']['username']['default'] = '';
$array['element']['username']['null'] = true;

$array['element']['password'] = array();
$array['element']['password']['default'] = '';
$array['element']['password']['null'] = true;

$array['element']['authuser'] = array();
$array['element']['authuser']['default'] = '';
$array['element']['authuser']['null'] = true;

$array['element']['host'] = array();
$array['element']['host']['default'] = '';
$array['element']['host']['null'] = true;

$array['element']['port'] = array();
$array['element']['port']['default'] = '';
$array['element']['host']['null'] = true;

$array['element']['mailbox'] = array();
$array['element']['mailbox']['default'] = '';
$array['element']['mailbox']['null'] = true;

dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['username'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['password'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['authuser'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['host'] = array('set'		=> false,
				 'callback'	    => 'dwho_network::valid_host',
				 'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC | DWHO_NETWORK_HOST_HOSTNAME)),
				 'maxlen'	=> 64);
$array['filter']['port'] = array('set' => false, 'chk' => 2, 'cast' => 'uint');
$array['filter']['mailbox'] = array('set' => false,'chk' => 2,'maxlen' => 25);

?>
