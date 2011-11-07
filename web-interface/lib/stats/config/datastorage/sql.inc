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

$array = array();

$array['accesswebservice'] = array();
$array['accesswebservice']['table'] = 'accesswebservice';
$array['accesswebservice']['primary'] = array('id' => '');

$array['agentfeatures'] = array();
$array['agentfeatures']['table'] = 'agentfeatures';
$array['agentfeatures']['primary'] = array('id' => '');

$array['cdr'] = array();
$array['cdr']['table'] = 'cdr';
$array['cdr']['primary'] = array('id' => '');

$array['cel'] = array();
$array['cel']['table'] = 'cel';
$array['cel']['primary'] = array('id' => '');

$array['entity'] = array();
$array['entity']['table'] = 'entity';
$array['entity']['primary'] = array('id' => '');

$array['ldapserver'] = array();
$array['ldapserver']['table'] = 'ldapserver';
$array['ldapserver']['primary'] = array('id' => '');

$array['queuefeatures'] = array();
$array['queuefeatures']['table'] = 'queuefeatures';
$array['queuefeatures']['primary'] = array('id' => '');

$array['queue_log'] = array();
$array['queue_log']['table'] = 'queue_log';
$array['queue_log']['primary'] = array('time' => '');

$array['server'] = array();
$array['server']['table'] = 'server';
$array['server']['primary'] = array('id' => '');

$array['stats_conf'] = array();
$array['stats_conf']['table'] = 'stats_conf';
$array['stats_conf']['primary'] = array('id' => '');

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

$array['stats_conf_xivouser'] = array();
$array['stats_conf_xivouser']['table'] = 'stats_conf_xivouser';
$array['stats_conf_xivouser']['primary'] = array('stats_conf_id' => '');


?>
