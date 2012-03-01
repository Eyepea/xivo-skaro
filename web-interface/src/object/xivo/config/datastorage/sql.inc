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

$array['accesswebservice'] = array();
$array['accesswebservice']['table'] = 'accesswebservice';
$array['accesswebservice']['primary'] = array('id' => '');

$array['entity'] = array();
$array['entity']['table'] = 'entity';
$array['entity']['primary'] = array('id' => '');

$array['iproute'] = array();
$array['iproute']['table'] = 'iproute';
$array['iproute']['primary'] = array('id' => '');

$array['ldapserver'] = array();
$array['ldapserver']['table'] = 'ldapserver';
$array['ldapserver']['primary'] = array('id' => '');

$array['mail'] = array();
$array['mail']['table'] = 'mail';
$array['mail']['primary'] = array('id' => '');

$array['monitoring'] = array();
$array['monitoring']['table'] = 'monitoring';
$array['monitoring']['primary'] = array('id' => '');

$array['netiface'] = array();
$array['netiface']['table'] = 'netiface';
$array['netiface']['primary'] = array('id' => '');

$array['resolvconf'] = array();
$array['resolvconf']['table'] = 'resolvconf';
$array['resolvconf']['primary'] = array('id' => '');

$array['server'] = array();
$array['server']['table'] = 'server';
$array['server']['primary'] = array('id' => '');

$array['dhcp'] = array();
$array['dhcp']['table'] = 'dhcp';
$array['dhcp']['primary'] = array('id' => '');

$array['stats_conf'] = array();
$array['stats_conf']['table'] = 'stats_conf';
$array['stats_conf']['primary'] = array('id' => '');

$array['provisioning'] = array();
$array['provisioning']['table'] = 'provisioning';
$array['provisioning']['primary'] = array('id' => '');

$array['stats_conf_queue'] = array();
$array['stats_conf_queue']['table'] = 'stats_conf_queue';
$array['stats_conf_queue']['primary'] = array('stats_conf_id' => '');

$array['stats_conf_group'] = array();
$array['stats_conf_group']['table'] = 'stats_conf_group';
$array['stats_conf_group']['primary'] = array('stats_conf_id' => '');

$array['stats_conf_agent'] = array();
$array['stats_conf_agent']['table'] = 'stats_conf_agent';
$array['stats_conf_agent']['primary'] = array('stats_conf_id' => '');

$array['stats_conf_user'] = array();
$array['stats_conf_user']['table'] = 'stats_conf_user';
$array['stats_conf_user']['primary'] = array('stats_conf_id' => '');

$array['stats_conf_incall'] = array();
$array['stats_conf_incall']['table'] = 'stats_conf_incall';
$array['stats_conf_incall']['primary'] = array('stats_conf_id' => '');


?>
