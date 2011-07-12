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
$array['tree'] = array();
$array['tree']['xivo'] = array();
$array['tree']['xivo']['configuration'] = array();
$array['tree']['xivo']['configuration']['check'] = true;

$array['tree']['xivo']['configuration']['manage'] = array();
$array['tree']['xivo']['configuration']['manage']['entity'] = true;

$array['tree']['xivo']['configuration']['network'] = array();
$array['tree']['xivo']['configuration']['network']['interface'] = true;
$array['tree']['xivo']['configuration']['network']['iproute'] = true;
$array['tree']['xivo']['configuration']['network']['resolvconf'] = true;
$array['tree']['xivo']['configuration']['network']['mail'] = true;
$array['tree']['xivo']['configuration']['network']['dhcp'] = true;
$array['tree']['xivo']['configuration']['network']['ha'] = true;

$array['tree']['xivo']['configuration']['support']['monitoring'] = true;

$array['tree']['xivo']['configuration']['provisioning']['general'] = true;
$array['tree']['xivo']['configuration']['provisioning']['autoprov'] = true;

$array['tree']['xivo']['configuration']['cti'] = array();
$array['tree']['xivo']['configuration']['cti']['configuration'] = true;
$array['tree']['xivo']['configuration']['cti']['accounts'] = true;

$array['tree']['service'] = array();
$array['tree']['service']['ipbx'] = array();
$array['tree']['service']['ipbx']['ctiserver'] = array();
$array['tree']['service']['ipbx']['ctiserver']['configuration']   = true;
$array['tree']['service']['ipbx']['queuelogger']['configuration'] = true;

$array['tree']['service']['ipbx']['general_settings'] = array();
$array['tree']['service']['ipbx']['general_settings']['sip']         = true;
$array['tree']['service']['ipbx']['general_settings']['iax']         = true;
$array['tree']['service']['ipbx']['general_settings']['sccp']        = true;
$array['tree']['service']['ipbx']['general_settings']['voicemail']   = true;
$array['tree']['service']['ipbx']['general_settings']['phonebook']   = true;
$array['tree']['service']['ipbx']['general_settings']['advanced']    = true;
$array['tree']['service']['ipbx']['general_settings']['outboundmwi'] = true;

$array['tree']['service']['ipbx']['pbx_settings'] = array();
$array['tree']['service']['ipbx']['pbx_settings']['users'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['lines'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['devices'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['groups'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['meetme'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['voicemail'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['extension'] = true;

$array['tree']['service']['ipbx']['call_management'] = array();
$array['tree']['service']['ipbx']['call_management']['incall'] = true;
$array['tree']['service']['ipbx']['call_management']['outcall'] = true;
$array['tree']['service']['ipbx']['call_management']['pickup']  = true;

$array['tree']['service']['ipbx']['trunk_management'] = array();
$array['tree']['service']['ipbx']['trunk_management']['sip'] = true;
$array['tree']['service']['ipbx']['trunk_management']['iax'] = true;
$array['tree']['service']['ipbx']['trunk_management']['custom'] = true;

$array['tree']['service']['ipbx']['pbx_services'] = array();
$array['tree']['service']['ipbx']['pbx_services']['phonebook'] = true;
$array['tree']['service']['ipbx']['pbx_services']['extenfeatures'] = true;
$array['tree']['service']['ipbx']['pbx_services']['parkinglot'] = true;

$array['tree']['service']['ipbx']['system_management'] = array();
$array['tree']['service']['ipbx']['system_management']['context'] = true;

$array['tree']['service']['ipbx']['dundi'] = array();
$array['tree']['service']['ipbx']['dundi']['peers'] = true;
$array['tree']['service']['ipbx']['dundi']['mappings'] = true;

$array['tree']['service']['ipbx']['control_system'] = array();
$array['tree']['service']['ipbx']['control_system']['reload'] = true;
$array['tree']['service']['ipbx']['control_system']['restart'] = true;

$array['tree']['statistics'] = array();
$array['tree']['statistics']['statistics'] = array();
$array['tree']['statistics']['statistics']['call_center'] = true;
$array['tree']['statistics']['statistics']['cel'] = true;

$array['tree']['service']['callcenter'] = array();
$array['tree']['service']['callcenter']['settings']['agents'] = true;
$array['tree']['service']['callcenter']['settings']['queues'] = true;
$array['tree']['service']['callcenter']['settings']['queuepenalties'] = true;
$array['tree']['service']['callcenter']['settings']['queueskills'] = true;
$array['tree']['service']['callcenter']['settings']['queueskillrules'] = true;
$array['tree']['service']['callcenter']['registrationcampaign']['campaigns'] = true;

?>
