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

$access_category = 'cti';
$access_subcategory = 'configuration';

$_XOBJ = &dwho_gct::get('xivo_object');

include(dwho_file::joinpath(dirname(__FILE__),'_common.php'));

$starttime = microtime(true);

$act = $_QRY->get('act');

switch($act)
{
    case 'view':
    default:
        $act = 'view';

        $app = &$ipbx->get_application('serverfeatures', array('feature' => 'phonebook', 'type' => 'xivo'));
        $cticontexts = &$ipbx->get_module('cticontexts');
        $ctidirectories = &$ipbx->get_module('ctidirectories');
        $ctidirectoryfld = &$ipbx->get_module('ctidirectoryfields');
        $ctidisplays = &$ipbx->get_module('ctidisplays');
        $ctisheetactions = &$ipbx->get_module('ctisheetactions');
        $ctisheetevents = &$ipbx->get_module('ctisheetevents');
        $ctimain = &$ipbx->get_module('ctimain');
        $ctiprofiles = &$ipbx->get_module('ctiprofiles');
        $ctistatus = &$ipbx->get_module('ctistatus');
        $ctipresences = &$ipbx->get_module('ctipresences');
        $ctiphonehints = &$ipbx->get_module('ctiphonehints');
        $ctiphonehintsgroup = &$ipbx->get_module('ctiphonehintsgroup');
        $ctirdid = &$ipbx->get_module('ctireversedirectories');

        $modresolvconf = &$_XOBJ->get_module('resolvconf');
        $infolocalserver = $modresolvconf->get(1);

        $ldapfilter = &$ipbx->get_module('ldapfilter');
        xivo::load_class('xivo_ldapserver',XIVO_PATH_OBJECT,null,false);
        $ldapserver = new xivo_ldapserver();

        // load database settings
        // 1. xivo
        $config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'cti.ini');
        $db_cti = $config['general']['datastorage'];
        $db_queuelogger = $config['queuelogger']['datastorage'];
        $db_ctilog = $config['queuelogger']['datastorage'];

        // 2. asterisk
        $config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');
        $db_ast  = $config['general']['datastorage'];

        // Timezone
        $general = &$ipbx->get_module('general');
        $info_general = $general->get(1);

        $load_ctimain = $ctimain->get(1);

        $load_contexts = $cticontexts->get_all();
        $load_directories = $ctidirectories->get_all();
        $load_displays = $ctidisplays->get_all();
        $load_sheetactions = $ctisheetactions->get_all();
        $load_sheetevents = $ctisheetevents->get_all();
        $load_profiles = $ctiprofiles->get_all();
        $load_presences = $ctipresences->get_all();
        $load_phonehintsgroups = $ctiphonehintsgroup->get_all();
        $load_rdid = $ctirdid->get_all();
        $list = $app->get_server_list();

        $out = array(
            'main'             => array(),
            'contexts'         => array(),
            'directories'      => array(),
            'displays'         => array(),
            'sheets'           => array(),
            'profiles'         => array(),
            # capabilities referred to by the profiles
            'regcommands'      => array(),
            'ipbxcommands'     => array(),
            'services'         => array(),
            'preferences'      => array(),
            # object display options referred to by the profiles
            'userstatus'       => array(),
            'phonestatus'      => array(),
        );

        # CONTEXTS
        if(isset($load_contexts) === true && is_array($load_contexts) === true)
        {
            $ctxout = array();
            foreach($load_contexts as $context)
            {
                $ctxid = $context['name'];
                $ctxout[$ctxid] = array();
                $ctxdirs = explode(',', $context['directories']);
                $ctxout[$ctxid]['directories'] = $ctxdirs;
                $ctxout[$ctxid]['display'] = $context['display'];
            }
            $out['contexts'] = $ctxout;
        }

        # DISPLAYS
        if(isset($load_displays) === true && is_array($load_displays) === true)
        {
            $dspout = array();

            foreach($load_displays as $display)
            {
                $dspid = $display['name'];
                $dspout[$dspid] = dwho_json::decode($display['data'], true);

            }
            $out['displays'] = $dspout;
        }

        # DIRECTORIES
        if(isset($load_directories) === true && is_array($load_directories) === true)
        {
            $dirout = array();

            foreach($load_directories as $dir)
            {
                $uri = $dir['uri'];
                if(strpos($uri, 'ldapfilter://') === 0)
                {
                    if(is_null($filterid = $ldapfilter->get_primary(array('name'=> substr($uri, 13)))))
                        continue;

                    $filter   = $ldapfilter->get($filterid);
                    $server   = $ldapserver->get($filter['ldapserverid']);

                    // formatting ldap uri
                    $uri  = sprintf("%s://%s:%s@%s:%s/%s???%s",
                        ($server['securitylayer'] == 'ssl' ? 'ldaps' : 'ldap'),
                        $filter['user'],
                        $filter['passwd'],
                        $server['host'],
                        $server['port'],
                        $filter['basedn'],
                        rawurlencode($filter['filter']));
                }

                $dirid = $dir['name'];
                $dirout[$dirid]['uri'] = $uri;
                $dirout[$dirid]['delimiter'] = $dir['delimiter'];
                $dirout[$dirid]['name'] = $dir['description'];
                $dirout[$dirid]['match_direct'] = dwho_json::decode($dir['match_direct'], true) == false ? array() : dwho_json::decode($dir['match_direct'], true);
                $dirout[$dirid]['match_reverse'] = dwho_json::decode($dir['match_reverse'], true) == false ? array() : dwho_json::decode($dir['match_reverse'], true);

                $fields = $ctidirectoryfld->get_all_where(array('dir_id' => $dir['id']));
                foreach($fields as $field)
                    $dirout[$dirid]['field_' . $field['fieldname']] = array($field['value']);
            }
            $out['directories'] = $dirout;
        }

        # REVERSEDID
        if(isset($load_rdid) === true && is_array($load_rdid) === true)
        {
            foreach($load_rdid as $rdid)
            {
                $curctx  = $rdid['context'];
                if(! array_key_exists($curctx, $out['contexts']))
                    $out['contexts'][$curctx] = array();

                $curblok = array();
                $dirblok = dwho_json::decode($rdid['directories'], true);
                foreach(explode(',', $rdid['extensions']) as $exten)
                    $curblok[$exten] = $dirblok;

                $out['contexts'][$curctx]['didextens'] = $curblok;
            }
        }

        # SHEETS
        $sheetsout = array();
        if(isset($load_sheetevents,$load_sheetevents[0]))
        {
            $evtout = array();
            foreach(array_keys($load_sheetevents[0]) as $k)
            {
                if($k == 'id')
                    continue;
                if($load_sheetevents[0][$k] == "")
                    continue;
                $eventdef = array();
                $eventdef["display"] = $load_sheetevents[0][$k];
                $eventdef["option"] = $load_sheetevents[0][$k];
                $eventdef["condition"] = $load_sheetevents[0][$k];
                $evtout[$k][] = $eventdef;
            }
            if (isset($evtout['custom']) === true)
                $evtout['custom'] = dwho_json::decode($evtout['custom'], true) == false ? array() : dwho_json::decode($evtout['custom'], true);
            $out['sheets']['events'] = $evtout;
        }
        if(isset($load_sheetactions) === true
        && is_array($load_sheetactions) === true)
        {
            $optout = array();
            $dispout = array();
            $condout = array();

            foreach($load_sheetactions as $action)
            {
                $actid = $action['name'];

                $optout[$actid]['focus'] = $action['focus'] == 1 ? "yes" : "no";
                $optout[$actid]['zip'] = 1;

                $condout[$actid]['whom'] = $action['whom'];
                $condout[$actid]['contexts'] = dwho_json::decode($action['context'], true) == false ? array() : dwho_json::decode($action['context'], true);
                $condout[$actid]['profileids'] = dwho_json::decode($action['capaids'], true) == false ? array() : dwho_json::decode($action['capaids'], true);

                $arr = array();
                $arr = dwho_json::decode($action['sheet_info'], true);
                $qtui = "null";

                if(is_array($arr) === true)
                {
                    foreach($arr as $k=>$v)
                    {
                        $a1 = $arr[$k];
                        if($a1[1] == 'form')
                            $qtui = $a1[3];
                    }
                }
                $dispout[$actid]['systray_info'] = dwho_json::decode($action['systray_info'], true) == false ? array() : dwho_json::decode($action['systray_info'], true);
                $dispout[$actid]['sheet_info'] = dwho_json::decode($action['sheet_info'], true) == false ? array() : dwho_json::decode($action['sheet_info'], true);
                $dispout[$actid]['action_info'] = dwho_json::decode($action['action_info'], true) == false ? array() : dwho_json::decode($action['action_info'], true);
                $dispout[$actid]['sheet_qtui'][$qtui] = $action['sheet_qtui'];
            }
            $out['sheets']['options'] = $optout;
            $out['sheets']['displays'] = $dispout;
            $out['sheets']['conditions'] = $condout;
        }

        # MAIN
		$tcpdefs = array();
		foreach(array('fagi','cti','ctis','webi','info') as $k)
			$tcpdefs[strtoupper($k)] = array(
				$load_ctimain[$k.'_ip'],
				$load_ctimain[$k.'_port'],
				$load_ctimain[$k.'_active'] != 0
			);

		$udpdefs = array(
			'ANNOUNCE' => array(
				$load_ctimain['announce_ip'],
				$load_ctimain['announce_port'],
				$load_ctimain['announce_active'] != 0
			)
		);

        $out['certfile'] = $load_ctimain['tlscertfile'];
        $out['keyfile']  = $load_ctimain['tlsprivkeyfile'];

        $out['main']['incoming_tcp'] = $tcpdefs;
        $out['main']['incoming_udp'] = $udpdefs;
        $out['main']['sockettimeout'] = $load_ctimain['socket_timeout'];
        $out['main']['updates_period'] = $load_ctimain['updates_period'];
        $out['main']['logintimeout'] = $load_ctimain['login_timeout'];
        $out['main']['asterisk_queuestat_db'] = $db_queuelogger;
        $out['main']['ctilog_db_uri'] = $db_ctilog;
        $out['main']['parting_astid_context'] = array();

        if($load_ctimain['parting_astid_context'] != "")
            $out['main']['parting_astid_context'] = explode(",", $load_ctimain['parting_astid_context']);

        # PRESENCES (USER STATUSES)
        if(isset($load_presences) === true
        && is_array($load_presences) === true)
        {
            $presout = array();
            foreach($load_presences as $pres)
            {
                $presid = $pres['name'];
                $id = $pres['id'];
                $where = array();
                $where['presence_id'] = $id;
                if(($load_status = $ctistatus->get_all_where($where)) === false)
                    continue;

                $statref = array();
                foreach($load_status as $stat)
                    $statref[$stat['id']] = $stat['name'];

                foreach($load_status as $stat)
                {
                    $name = $stat['name'];
                    $presout[$presid][$name]['longname'] = $stat['display_name'];
                    $presout[$presid][$name]['color'] = $stat['color'];
                    $accessids = $stat['access_status'];

                    $accessstatus = array();
                    foreach(explode(',', $accessids) as $i)
                        if (isset($statref[$i]))
                            $accessstatus[] = $statref[$i];
                    if(!empty($accessstatus)) {
                        $presout[$presid][$name]['allowed'] = $accessstatus;
                    }

                    $actions = explode(',', $stat['actions']);
                    $pattern = '/^(.*)\((.*)\)/';
                    $actionsout = array();
                    foreach($actions as $a)
                    {
                        if (preg_match($pattern, $a, $match) > 0)
                        	$actionsout[$match[1]] = $match[2];
                    }
                    if(!empty($actionsout)) {
                        $presout[$presid][$name]['actions'] = $actionsout;
                    }
                }
            }
            $out['userstatus'] = $presout;
        }

        # PHONEHINTS (LINE STATUSES)
        if(isset($load_phonehintsgroups) === true
        && is_array($load_phonehintsgroups) === true)
        {
            $hintsout = array();
            foreach($load_phonehintsgroups as $phonehintsgroup)
            {
                $where = array('idgroup' => $phonehintsgroup['id']);
                if(($load_phonehints = $ctiphonehints->get_all_where($where)) === false)
                    continue;

                $phonehintsgroup_id = $phonehintsgroup['name'];
                $hintsout[$phonehintsgroup_id] = array();

                foreach($load_phonehints as $phonehint)
                {
                    $phonehint_id = $phonehint['number'];
                    $hintsout[$phonehintsgroup_id][$phonehint_id] = array();
                    $hintsout[$phonehintsgroup_id][$phonehint_id]['longname'] = $phonehint['name'];
                    $hintsout[$phonehintsgroup_id][$phonehint_id]['color'] = $phonehint['color'];
                }
            }
            $out['phonestatus'] = $hintsout;
        }

        $out['regcommands']['itm_regcommands'] = array("login_id", "login_pass", "login_capas",
                                                       "getipbxlist",
                                                       "getlist", "ipbxcommand", "chitchat",
                                                       "actionfiche",
                                                       "availstate", "keepalive", "filetransfer",
                                                       "getqueuesstats", "logfromclient",
                                                       "featuresput", "featuresget", "faxsend",
                                                       "logfromclient", "getqueuesstats", "directory",
                                                       "records_campaign",
                                                       "history");

        $out['ipbxcommands']['itm_ipbxcommands'] = array("originate",
                                                         "sipnotify",
                                                         "agentlogin", "agentlogout",
                                                         "queueadd",
                                                         "queueremove", "queuepause", "queueunpause",
                                                         "queueremove_all", "queuepause_all", "queueunpause_all",
                                                         "listen", "record",
                                                         "parking", "meetme",
                                                         "mailboxcount",
                                                         "intercept",
                                                         "cancel", "refuse", "answer",
                                                         "transfercancel", "hangup", "hangupme",
                                                         "atxfer", "transfer", "dial");

        # PROFILES
        if(isset($load_profiles) === true
        && is_array($load_profiles) === true)
        {
            foreach($load_profiles as $pf)
            {
                $pfid = $pf['name'];
                $out['profiles'][$pfid] = array(
                    'name' => $pf['appliname'],

                    'xlets' => dwho_json::decode($pf['xlets'], true),
                    'services' => "itm_services_".$pfid,
                    'preferences' => "itm_preferences_".$pfid,
                    'regcommands' => "itm_regcommands",
                    'ipbxcommands' => "itm_ipbxcommands",
                    'userstatus' => $pf['presence'],
                    'phonestatus' => $pf['phonehints'],
                    #'callcenter_type' => $pf['callcenter_type']
                );
                $out['services']["itm_services_".$pfid] = explode(',', $pf['services']);
                $out['preferences']["itm_preferences_".$pfid] = 0?null:dwho_json::decode($pf['preferences']);
            }
        }

        $hostname = $infolocalserver['hostname'];

        # XiVO LOCAL SERVER
        $out['ipbxes'][$hostname] = array();
        $outlocalserver = &$out['ipbxes'][$hostname];

        # ASTERISK AMI
        $ami_infos = array(
            'ipaddress' => $load_ctimain['ami_ip'],
            'ipport'    => $load_ctimain['ami_port'],
            'username'  => $load_ctimain['ami_login'],
            'password'  => $load_ctimain['ami_password']
        );

        $outlocalserver['ipbx_connection'] = $ami_infos;

        if(isset($_SERVER['REMOTE_ADDR']) === false
        || ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1'
            && $_SERVER['REMOTE_ADDR'] !== '::1'))
        {
            $ipbxuri = 'https://'.$_SERVER['SERVER_ADDR'].'/service/ipbx/json.php/restricted/';
            $callcenteruri = 'https://'.$_SERVER['SERVER_ADDR'].'/callcenter/json.php/restricted/';
        }
        else
        {
            $ipbxuri = 'http://127.0.0.1/service/ipbx/json.php/private/';
            $callcenteruri = 'http://127.0.0.1/callcenter/json.php/private/';
        }

        $urllists = array(
            'urllist_users' => array($ipbxuri.'pbx_settings/users'),
            'urllist_lines' => array($ipbxuri.'pbx_settings/lines'),
            'urllist_devices' => array($ipbxuri.'pbx_settings/devices'),
            'urllist_groups' => array($ipbxuri.'pbx_settings/groups'),
            'urllist_meetmes' => array($ipbxuri.'pbx_settings/meetme'),
            'urllist_voicemails' => array($ipbxuri.'pbx_settings/voicemail'),
            'urllist_incalls' => array($ipbxuri.'call_management/incall'),
            'urllist_outcalls' => array($ipbxuri.'call_management/outcall'),
            'urllist_contexts' => array($ipbxuri.'system_management/context'),
            'urllist_trunks' => array($ipbxuri.'trunk_management/sip',$ipbxuri.'trunk_management/iax'),
            'urllist_phonebook' => array($ipbxuri.'pbx_services/phonebook'),
            'urllist_extenfeatures' => array($ipbxuri.'pbx_services/extenfeatures'),
            'urllist_parkinglot' => array($ipbxuri.'pbx_services/parkinglot'),

            'urllist_agents' => array($callcenteruri.'settings/agents'),
            'urllist_queues' => array($callcenteruri.'settings/queues')
        );
        $outlocalserver['urllists'] = $urllists;
        $outlocalserver['cdr_db_uri'] = $db_ast;
        $outlocalserver['userfeatures_db_uri'] = $db_ast;
		$outlocalserver['timezone'] = $info_general['timezone'];

        $out['bench'] = (microtime(true) - $starttime);

        $_TPL->set_var('info',$out);
        break;
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/genericjson');

?>
