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

$access_category = 'cti';
$access_subcategory = 'configuration';

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
        $ctirdid = &$ipbx->get_module('ctireversedirectories');

        $ldapfilter = &$ipbx->get_module('ldapfilter');
        xivo::load_class('xivo_ldapserver',XIVO_PATH_OBJECT,null,false);
        $ldapserver = new xivo_ldapserver();

        // load database settings
        // 1. xivo
        $config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'cti.ini');
        $db_cti = $config['general']['datastorage'];
        $db_queuelogger = $config['queuelogger']['datastorage'];

        // 2. asterisk
        $config  = dwho::load_init(XIVO_PATH_CONF.DWHO_SEP_DIR.'ipbx.ini');
        $db_ast  = $config['general']['datastorage'];

        $load_ctimain = $ctimain->get(1);

        $load_contexts = $cticontexts->get_all();
        $load_directories = $ctidirectories->get_all();
        $load_displays = $ctidisplays->get_all();
        $load_sheetactions = $ctisheetactions->get_all();
        $load_sheetevents = $ctisheetevents->get_all();
        $load_profiles = $ctiprofiles->get_all();
        $load_status = $ctistatus->get_all();
        $load_presences = $ctipresences->get_all();
        $load_phonehints = $ctiphonehints->get_all();
        $load_rdid = $ctirdid->get_all();
        $list = $app->get_server_list();

        $ctxlist = array();

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
            'functions'        => array(),
            'preferences'      => array(),
            # object display options referred to by the profiles
            'userstatus'       => array(),
            'phonestatus'      => array(),
            'agentstatus'      => array(),
            'channelstatus'    => array()
        );

        # CONTEXTS
        if(isset($load_contexts))
        {
            $ctxout = array();
            foreach($load_contexts as $context)
            {
                $ctxid = $context['name'];
                $ctxlist[] = "contexts.".$ctxid;
                $ctxdirs = explode(',', $context['directories']);
                $ctxout[$ctxid] = array();
                $arr = array();
                foreach($ctxdirs as $cd)
                {
                    $arr[] = "directories.".$cd;
                }
                $ctxout[$ctxid]['directories'] = $arr;

                $ctxout[$ctxid]['display'] = $context['display'];
            }
            $out['contexts'] = $ctxout;
        }

        # DISPLAYS
        if(isset($load_displays))
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
        if(isset($load_directories))
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
                        $filter['filter']);
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

                $dirout[$dirid]['display_reverse'] = dwho_json::decode($dir['display_reverse'], true) == false ? array() : dwho_json::decode($dir['display_reverse'], true);
            }
            $out['directories'] = $dirout;
        }

        # REVERSEDID
        if(isset($load_rdid))
        {
            $rdidout = array();
            $curctx  = null;
            $curblok = null;

            foreach($load_rdid as $rdid)
            {
                if($rdid['context'] != $curctx)
                {
                    if(!is_null($curctx))
                        $out['contexts'][$curctx]['didextens'] = $curblok;

                    $curctx  = $rdid['context'];
                    if(is_array($curctx) === true
                    && array_key_exists($out['contexts'], $curctx))
                        $curblok = $out['contexts'][$curctx];
                    else
                        $curblok = array();
                }

                $dirblok = dwho_json::decode($rdid['directories'], true);
                for($i = 0; $i < count($dirblok); $i++)
                    $dirblok[$i] = "directories." . $dirblok[$i];

                foreach(explode(',', $rdid['extensions']) as $exten)
                    $curblok['didextens'][$exten] = $dirblok;
            }

            if(!is_null($curctx))
                $out['contexts'][$curctx] = $curblok;
        }

        # SHEETS
        $sheetsout = array();
        if(isset($load_sheetevents))
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
            $evtout['custom'] = dwho_json::decode($evtout['custom'], true) == false ? array() : dwho_json::decode($evtout['custom'], true);
            $out['sheets']['events'] = $evtout;
        }
        if(isset($load_sheetactions))
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
                foreach($arr as $k=>$v)
                {
                    $a1 = $arr[$k];
                    if($a1[1] == 'form')
                        $qtui = $a1[3];
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
        $tcpdefs['FAGI'] = array($load_ctimain['fagi_ip'], $load_ctimain['fagi_port']);
        $tcpdefs['CTI'] = array($load_ctimain['cti_ip'], $load_ctimain['cti_port']);
        $tcpdefs['CTIS'] = array($load_ctimain['ctis_ip'], $load_ctimain['ctis_port']);
        $tcpdefs['WEBI'] = array($load_ctimain['webi_ip'], $load_ctimain['webi_port']);
        $tcpdefs['INFO'] = array($load_ctimain['info_ip'], $load_ctimain['info_port']);
        $udpdefs = array();
        $udpdefs['ANNOUNCE'] = array($load_ctimain['announce_ip'], $load_ctimain['announce_port']);
        $out['main']['incoming_tcp'] = $tcpdefs;
        $out['main']['incoming_udp'] = $udpdefs;

        $out['main']['sockettimeout'] = $load_ctimain['socket_timeout'];
        $out['main']['updates_period'] = $load_ctimain['updates_period'];
        $out['main']['logintimeout'] = $load_ctimain['login_timeout'];
        $out['main']['asterisk_queuestat_db'] = $db_queuelogger;
        $out['main']['parting_astid_context'] = array();
        if($load_ctimain['parting_astid_context'] != "")
            $out['main']['parting_astid_context'] = explode(",", $load_ctimain['parting_astid_context']);

        # PRESENCES (USER STATUSES)
        if(isset($load_presences))
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
                        $accessstatus[] = $statref[$i];
                    $presout[$presid][$name]['allowed'] = $accessstatus;

                    $actions = explode(',', $stat['actions']);
                    $pattern = '/^(.*)\((.*)\)/';
                    $actionsout = array();
                    foreach($actions as $a)
                    {
                        $match = array();
                        preg_match($pattern, $a, $match);
                        $actionsout[$match[1]] = $match[2];
                    }
                    $presout[$presid][$name]['actions'] = $actionsout;
                }
            }
            $out['userstatus'] = $presout;
        }

        # PHONEHINTS (LINE STATUSES)
        if(isset($load_phonehints))
        {
            $hintsout = array();
            foreach($load_phonehints as $ph)
            {
                $phid = $ph['number'];
                $hintsout[$phid] = array();
                $hintsout[$phid]['longname'] = $ph['name'];
                $hintsout[$phid]['color'] = $ph['color'];
            }
            $out['phonestatus']['itm_phonestatus'] = $hintsout;
        }

        $out['regcommands']['itm_regcommands'] = array("login_id", "login_pass", "login_capas",
                                                       "getipbxlist",
                                                       "getlist", "ipbxcommand", "chitchat",
                                                       "availstate", "keepalive", "filetransfer",
                                                       "getqueuesstats", "logfromclient",
                                                       "featuresput", "featuresget", "faxsend",
                                                       "logfromclient", "getqueuesstats", "directory",
                                                       "history");

        $out['ipbxcommands']['itm_ipbxcommands'] = array("originate",
                                                         "sipnotify",
                                                         "agentlogin", "agentlogout",
                                                         "queueadd",
                                                         "queueremove", "queuepause", "queueunpause",
                                                         "queueremove_all", "queuepause_all", "queueunpause_all",
                                                         "listen", "record",
                                                         "parking", "meetme",
                                                         "intercept",
                                                         "cancel", "refuse", "answer",
                                                         "transfercancel", "hangup", "hangupme",
                                                         "atxfer", "transfer", "dial");

        # PROFILES
        if(isset($load_profiles))
        {
            foreach($load_profiles as $pf)
            {
                $pfid = $pf['name'];
                $prefs = array();
                $prefout = array();

                $prefs = explode(',', $pf['preferences']);
                $pattern = '/^(.*)\((.*)\)/';
                foreach($prefs as $p)
                {
                    $match = array();
                    if (preg_match($pattern, $p, $match) === 1)
                        $prefout[$match[1]] = $match[2];
                }
                $out['profiles'][$pfid] = array(
                    'name' => $pf['appliname'],

                    'xlets' => dwho_json::decode($pf['xlets'], true),
                    'functions' => "itm_functions_".$pfid,
                    'services' => "itm_services_".$pfid,
                    'preferences' => "itm_preferences_".$pfid,
                    'regcommands' => "itm_regcommands",
                    'ipbxcommands' => "itm_ipbxcommands",

                    'userstatus' => $pf['presence'],
                    'phonestatus' => "itm_phonestatus",
                    'agentstatus' => "itm_agentstatus",
                    'channelstatus' => "itm_channelstatus",
                    #'callcenter_type' => $pf['callcenter_type']
                );
                $out['functions']["itm_functions_".$pfid] = explode(',', $pf['funcs']);
                $out['services']["itm_services_".$pfid] = explode(',', $pf['services']);
                $out['preferences']["itm_preferences_".$pfid] = $prefout;
            }
        }

        # XiVO SERVERS
        if(isset($load_ctimain['asterisklist'])
        && dwho_has_len($load_ctimain['asterisklist']))
        {
            $ipbxlist = explode(',', $load_ctimain['asterisklist']);
            foreach($ipbxlist as $k => $v)
            {
                $hostname = $list[$v]['name'];
                $url_scheme = $list[$v]['url']['scheme'];
                $url_auth_host = $list[$v]['url']['authority']['host'];

                if((preg_match('/^127\./', $url_auth_host) > 0)
                || (preg_match('/^localhost/', $url_auth_host) > 0))
                {
                    $type = 'private';
                    $json = $url_scheme . '://' . $url_auth_host . '/service/ipbx/json.php/private/';
                }
                else
                {
                    $type = 'restricted';
                    $json = $url_scheme . '://' . $url_auth_host . '/service/ipbx/json.php/restricted/';
                }

                $out['main']['ctilog_db_uri'] = $db_cti;
                $out['ipbxes'][$hostname] = array();
                $urllists = array(
                    'urllist_users' => array($json . 'pbx_settings/users',
                                             $url_scheme.'://'.$url_auth_host.'/cti/json.php/'.$type.'/accounts'),
                    'urllist_lines' => array($json . 'pbx_settings/lines'),
                    'urllist_devices' => array($json . 'pbx_settings/devices'),
                    'urllist_agents' => array($json . 'call_center/agents'),
                    'urllist_queues' => array($json . 'call_center/queues'),
                    'urllist_groups' => array($json . 'pbx_settings/groups'),
                    'urllist_meetmes' => array($json . 'pbx_settings/meetme'),
                    'urllist_voicemails' => array($json . 'pbx_settings/voicemail'),
                    'urllist_incalls' => array($json . 'call_management/incall'),
                    'urllist_outcalls' => array($json . 'call_management/outcall'),
                    'urllist_contexts' => array($json . 'system_management/context'),
                    'urllist_trunks' => array($json . 'trunk_management/sip',$json . 'trunk_management/iax'),
                    'urllist_phonebook' => array($json . 'pbx_services/phonebook'),
                    'urllist_extenfeatures' => array($json . 'pbx_services/extenfeatures')
                );
                $out['ipbxes'][$hostname]['urllists'] = $urllists;
                $out['ipbxes'][$hostname]['cdr_db_uri'] = $db_ast;
                $out['ipbxes'][$hostname]['userfeatures_db_uri'] = $db_ast;
            }
        }

        # ASTERISK AMI
        $ami_infos = array(
            'ipaddress' => $load_ctimain['ami_ip'],
            'ipport'    => $load_ctimain['ami_port'],
            'username'  => $load_ctimain['ami_login'],
            'password'  => $load_ctimain['ami_password']
        );

        $out['ipbx_connection'] = $ami_infos;

        $out['bench'] = (microtime(true) - $starttime);

        $_TPL->set_var('info',$out);
        break;
}

$_TPL->set_var('act',$act);
$_TPL->set_var('sum',$_QRY->get('sum'));
$_TPL->display('/genericjson');

?>
