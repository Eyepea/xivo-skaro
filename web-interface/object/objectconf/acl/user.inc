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
$array['tree'] = array();
$array['tree']['service'] = array();

$array['tree']['service']['ipbx'] = array();

$array['tree']['service']['ipbx']['general_settings'] = array();
$array['tree']['service']['ipbx']['general_settings']['sip'] = true;
$array['tree']['service']['ipbx']['general_settings']['iax'] = true;
$array['tree']['service']['ipbx']['general_settings']['voicemail'] = true;
$array['tree']['service']['ipbx']['general_settings']['phonebook'] = true;
$array['tree']['service']['ipbx']['general_settings']['advanced'] = true;

$array['tree']['service']['ipbx']['pbx_settings'] = array();
$array['tree']['service']['ipbx']['pbx_settings']['devices'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['lines'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['users'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['groups'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['voicemail'] = true;
$array['tree']['service']['ipbx']['pbx_settings']['meetme'] = true;


$array['tree']['service']['ipbx']['call_management'] = array();
$array['tree']['service']['ipbx']['call_management']['incall'] = true;
$array['tree']['service']['ipbx']['call_management']['outcall'] = true;
$array['tree']['service']['ipbx']['call_management']['rightcall'] = true;
$array['tree']['service']['ipbx']['call_management']['callfilter'] = true;
$array['tree']['service']['ipbx']['call_management']['pickup'] = true;
$array['tree']['service']['ipbx']['call_management']['schedule'] = true;

$array['tree']['service']['ipbx']['trunk_management'] = array();
$array['tree']['service']['ipbx']['trunk_management']['sip'] = true;
$array['tree']['service']['ipbx']['trunk_management']['iax'] = true;
$array['tree']['service']['ipbx']['trunk_management']['custom'] = true;

$array['tree']['service']['ipbx']['pbx_services'] = array();
$array['tree']['service']['ipbx']['pbx_services']['sounds'] = true;
$array['tree']['service']['ipbx']['pbx_services']['musiconhold'] = true;
$array['tree']['service']['ipbx']['pbx_services']['extenfeatures'] = true;
$array['tree']['service']['ipbx']['pbx_services']['paging'] = true;
$array['tree']['service']['ipbx']['pbx_services']['phonebook'] = true;

$array['tree']['service']['ipbx']['system_management'] = array();
$array['tree']['service']['ipbx']['system_management']['backupfiles'] = true;
$array['tree']['service']['ipbx']['system_management']['configfiles'] = true;
$array['tree']['service']['ipbx']['system_management']['context'] = true;

$array['tree']['service']['ipbx']['control_system'] = array();
$array['tree']['service']['ipbx']['control_system']['logfiles'] = true;
$array['tree']['service']['ipbx']['control_system']['reload'] = true;
$array['tree']['service']['ipbx']['control_system']['restart'] = true;

// cti
$array['tree']['service']['cti'] = array();
$array['tree']['service']['cti']['general_settings']                  = array();
$array['tree']['service']['cti']['general_settings']['general']       = true;
$array['tree']['service']['cti']['general_settings']['profiles']      = true;
$array['tree']['service']['cti']['general_settings']['presences']     = true;
$array['tree']['service']['cti']['general_settings']['phonehints']    = true;
$array['tree']['service']['cti']['general_settings']['agentstatus']   = true;
$array['tree']['service']['cti']['directories']                       = array();
$array['tree']['service']['cti']['directories']['directories']        = true;
$array['tree']['service']['cti']['directories']['reversedirectories'] = true;
$array['tree']['service']['cti']['directories']['displays']           = true;
$array['tree']['service']['cti']['directories']['contexts']           = true;
$array['tree']['service']['cti']['sheets']                            = array();
$array['tree']['service']['cti']['sheets']['sheetactions']            = true;
$array['tree']['service']['cti']['sheets']['sheetevents']             = true;
$array['tree']['service']['cti']['control_system']                    = array();
$array['tree']['service']['cti']['control_system']['restart']         = true;

// monitoring
$array['tree']['service']['monitoring'] = array();
$array['tree']['service']['monitoring']['control_system'] = array();
$array['tree']['service']['monitoring']['control_system']['start'] = true;
$array['tree']['service']['monitoring']['control_system']['stop'] = true;
$array['tree']['service']['monitoring']['control_system']['restart'] = true;
$array['tree']['service']['monitoring']['control_system']['monitor'] = true;
$array['tree']['service']['monitoring']['control_system']['unmonitor'] = true;

$array['tree']['service']['graphs'] = array();
$array['tree']['service']['graphs']['munin'] = true;

// statistics
$array['tree']['statistics'] = array();
$array['tree']['statistics']['call_center'] = array();
$array['tree']['statistics']['call_center']['settings'] = array();
$array['tree']['statistics']['call_center']['settings']['configuration'] = true;
$array['tree']['statistics']['call_center']['settings']['genercache'] = true;
$array['tree']['statistics']['call_center']['settings']['cache'] = true;
$array['tree']['statistics']['call_center']['data'] = array();
$array['tree']['statistics']['call_center']['data']['stats1'] = true;
$array['tree']['statistics']['call_center']['data']['stats2'] = true;
$array['tree']['statistics']['call_center']['data']['stats3'] = true;
$array['tree']['statistics']['call_center']['data']['stats4'] = true;

// callcenter
$array['tree']['service']['callcenter'] = array();
$array['tree']['service']['callcenter']['settings'] = array();
$array['tree']['service']['callcenter']['settings']['agents'] = true;
$array['tree']['service']['callcenter']['settings']['queues'] = true;
$array['tree']['service']['callcenter']['settings']['queuepenalty'] = true;
$array['tree']['service']['callcenter']['settings']['queueskills'] = true;
$array['tree']['service']['callcenter']['settings']['queueskillrules'] = true;

$array['tree']['xivo'] = array();

$array['tree']['xivo']['monit']  = true;

$array['tree']['xivo']['configuration'] = array();
$array['tree']['xivo']['configuration']['manage'] = array();
$array['tree']['xivo']['configuration']['manage']['user'] = true;
$array['tree']['xivo']['configuration']['manage']['entity'] = true;
$array['tree']['xivo']['configuration']['manage']['directories'] = true;
$array['tree']['xivo']['configuration']['manage']['accesswebservice'] = true;
$array['tree']['xivo']['configuration']['manage']['certificate'] = true;

$array['tree']['xivo']['configuration']['network'] = array();
$array['tree']['xivo']['configuration']['network']['interface'] = true;
$array['tree']['xivo']['configuration']['network']['iproute'] = true;
$array['tree']['xivo']['configuration']['network']['resolvconf'] = true;
$array['tree']['xivo']['configuration']['network']['mail'] = true;
$array['tree']['xivo']['configuration']['network']['dhcp'] = true;

$array['tree']['xivo']['configuration']['support'] = array();
$array['tree']['xivo']['configuration']['support']['xivo'] = true;
$array['tree']['xivo']['configuration']['support']['alerts'] = true;
$array['tree']['xivo']['configuration']['support']['limits'] = true;

$array['tree']['xivo']['configuration']['provisioning'] = array();
$array['tree']['xivo']['configuration']['provisioning']['general'] = true;
$array['tree']['xivo']['configuration']['provisioning']['configregistrar'] = true;
$array['tree']['xivo']['configuration']['provisioning']['configdevice'] = true;
$array['tree']['xivo']['configuration']['provisioning']['plugin'] = true;

$array['tree']['xivo']['configuration']['controlsystem'] = array();
$array['tree']['xivo']['configuration']['controlsystem']['network'] = true;
$array['tree']['xivo']['configuration']['controlsystem']['commonconf'] = true;

$array['group'] = array();
$array['group']['visitor'] = false;

$array['group']['user'] = array();
$array['group']['user']['service'] = false;

$array['group']['admin'] = array();
$array['group']['admin']['service'] = false;

$array['group']['root'] = true;

?>
