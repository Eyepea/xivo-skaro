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

$array['registered'] = 'SIP/Registry';

$array['element'] = array();

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['type'] = array();
$array['element']['type']['default'] = 'friend';
$array['element']['type']['forcedef'] = true;

$array['element']['username'] = array();
$array['element']['username']['unset'] = true;

$array['element']['secret'] = array();
$array['element']['secret']['default'] = '';

$array['element']['md5secret'] = array();
$array['element']['md5secret']['default'] = '';

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['language'] = array();
$array['element']['language']['value'] = array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA', 'nl_NL');
$array['element']['language']['default'] = '';
$array['element']['language']['null'] = true;

$array['element']['accountcode'] = array();
$array['element']['accountcode']['default'] = '';
$array['element']['accountcode']['null'] = true;

$array['element']['amaflags'] = array();
$array['element']['amaflags']['value'] = xivo_service_asterisk::get_amaflags_list();
$array['element']['amaflags']['default'] = XIVO_SRE_IPBX_AST_CDR_AMAFLAGS_META_DEFAULT;
$array['element']['amaflags']['setdef'] = true;

$array['element']['allowtransfer'] = array();
$array['element']['allowtransfer']['value'] = array(1,0);
$array['element']['allowtransfer']['default'] = '';
$array['element']['allowtransfer']['null'] = true;

$array['element']['fromuser'] = array();
$array['element']['fromuser']['default'] = '';
$array['element']['fromuser']['null'] = true;

$array['element']['fromdomain'] = array();
$array['element']['fromdomain']['default'] = '';
$array['element']['fromdomain']['null'] = true;

$array['element']['mailbox'] = array();
$array['element']['mailbox']['default'] = '';
$array['element']['mailbox']['null'] = true;

$array['element']['subscribemwi'] = array();
$array['element']['subscribemwi']['value'] = array(0,1);
$array['element']['subscribemwi']['default'] = 0;
$array['element']['subscribemwi']['set'] = true;

$array['element']['buggymwi'] = array();
$array['element']['buggymwi']['value'] = array(1,0);
$array['element']['buggymwi']['default'] = '';
$array['element']['buggymwi']['null'] = true;

$array['element']['call-limit'] = array();
$array['element']['call-limit']['value'] = range(0,40);
$array['element']['call-limit']['default'] = 0;
$array['element']['call-limit']['setdef'] = true;

$array['element']['callerid'] = array();
$array['element']['callerid']['default'] = '';
$array['element']['callerid']['null'] = true;

$array['element']['fullname'] = array();
$array['element']['fullname']['unset'] = true;

$array['element']['cid_number'] = array();
$array['element']['cid_number']['unset'] = true;

$array['element']['maxcallbitrate'] = array();
$array['element']['maxcallbitrate']['default'] = '';
$array['element']['maxcallbitrate']['null'] = true;

$array['element']['insecure'] = array();
$array['element']['insecure']['value'] = array('port'			=> 'port',
												'invite'		=> 'invite',
												'port,invite'	=> 'port,invite');
$array['element']['insecure']['default'] = '';
$array['element']['insecure']['null'] = true;

$array['element']['nat'] = array();
$array['element']['nat']['value'] = array('no','yes','force_rport','comedia');
$array['element']['nat']['default'] = '';
$array['element']['nat']['null'] = true;


$array['element']['promiscredir'] = array();
$array['element']['promiscredir']['value'] = array(1,0);
$array['element']['promiscredir']['default'] = '';
$array['element']['promiscredir']['null'] = true;

$array['element']['usereqphone'] = array();
$array['element']['usereqphone']['value'] = array(1,0);
$array['element']['usereqphone']['default'] = '';
$array['element']['usereqphone']['null'] = true;

$array['element']['trustrpid'] = array();
$array['element']['trustrpid']['value'] = array(1,0);
$array['element']['trustrpid']['default'] = '';
$array['element']['trustrpid']['null'] = true;

$array['element']['sendrpid'] = array();
$array['element']['sendrpid']['value'] = array(1,0);
$array['element']['sendrpid']['default'] = '';
$array['element']['sendrpid']['null'] = true;

$array['element']['allowsubscribe'] = array();
$array['element']['allowsubscribe']['value'] = array(1,0);
$array['element']['allowsubscribe']['default'] = '';
$array['element']['allowsubscribe']['null'] = true;

$array['element']['allowoverlap'] = array();
$array['element']['allowoverlap']['value'] = array(1,0);
$array['element']['allowoverlap']['default'] = '';
$array['element']['allowoverlap']['null'] = true;

$array['element']['dtmfmode'] = array();
$array['element']['dtmfmode']['value'] = array('rfc2833','inband','info','auto');
$array['element']['dtmfmode']['default'] = '';
$array['element']['dtmfmode']['null'] = true;

$array['element']['rfc2833compensate'] = array();
$array['element']['rfc2833compensate']['value'] = array(1,0);
$array['element']['rfc2833compensate']['default'] = '';
$array['element']['rfc2833compensate']['null'] = true;

$array['element']['qualify'] = array();
$array['element']['qualify']['value'] = array('no','yes',500,1000,1500,2000,2500,3000,3500,4000);
$array['element']['qualify']['default'] = '';
$array['element']['qualify']['null'] = true;

$array['element']['g726nonstandard'] = array();
$array['element']['g726nonstandard']['value'] = array(1,0);
$array['element']['g726nonstandard']['default'] = '';
$array['element']['g726nonstandard']['null'] = true;

$array['element']['disallow'] = array();
$array['element']['disallow']['value'] = array('all');
$array['element']['disallow']['default'] = 'all';
$array['element']['disallow']['null'] = true;

$array['element']['allow'] = array();
$array['element']['allow']['value'] = xivo_service_asterisk::get_codecs_list();
$array['element']['allow']['default'] = '';
$array['element']['allow']['null'] = true;

$array['element']['autoframing'] = array();
$array['element']['autoframing']['value'] = array(1,0);
$array['element']['autoframing']['default'] = '';
$array['element']['autoframing']['null'] = true;

$array['element']['mohinterpret'] = array();
$array['element']['mohinterpret']['unset'] = true;

$array['element']['mohsuggest'] = array();
$array['element']['mohsuggest']['default'] = '';
$array['element']['mohsuggest']['null'] = true;

$array['element']['useclientcode'] = array();
$array['element']['useclientcode']['value'] = array(1,0);
$array['element']['useclientcode']['default'] = '';
$array['element']['useclientcode']['null'] = true;

$array['element']['progressinband'] = array();
$array['element']['progressinband']['value'] = array('no','yes','never');
$array['element']['progressinband']['default'] = '';
$array['element']['progressinband']['null'] = true;

$array['element']['t38pt_udptl'] = array();
$array['element']['t38pt_udptl']['value'] = array(1,0);
$array['element']['t38pt_udptl']['default'] = '';
$array['element']['t38pt_udptl']['null'] = true;

$array['element']['t38pt_usertpsource'] = array();
$array['element']['t38pt_usertpsource']['value'] = array(1,0);
$array['element']['t38pt_usertpsource']['default'] = '';
$array['element']['t38pt_usertpsource']['null'] = true;

$array['element']['rtptimeout'] = array();
$array['element']['rtptimeout']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['rtptimeout']['default'] = '';
$array['element']['rtptimeout']['null'] = true;

$array['element']['rtpholdtimeout'] = array();
$array['element']['rtpholdtimeout']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['rtpholdtimeout']['default'] = '';
$array['element']['rtpholdtimeout']['null'] = true;

$array['element']['rtpkeepalive'] = array();
$array['element']['rtpkeepalive']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['rtpkeepalive']['default'] = '';
$array['element']['rtpkeepalive']['null'] = true;

$array['element']['deny'] = array();
$array['element']['deny']['default'] = '';
$array['element']['deny']['null'] = true;

$array['element']['permit'] = array();
$array['element']['permit']['default'] = '';
$array['element']['permit']['null'] = true;

$array['element']['defaultip'] = array();
$array['element']['defaultip']['unset'] = true;

$array['element']['callgroup'] = array();
$array['element']['callgroup']['default'] = '';
$array['element']['callgroup']['null'] = true;

$array['element']['pickupgroup'] = array();
$array['element']['pickupgroup']['default'] = '';
$array['element']['pickupgroup']['null'] = true;

$array['element']['setvar'] = array();
$array['element']['setvar']['default'] = '';

$array['element']['host'] = array();
$array['element']['host']['value'] = array('dynamic');
$array['element']['host']['default'] = 'dynamic';
$array['element']['host']['setdef'] = true;

$array['element']['host-static'] = array();
$array['element']['host-static']['default'] = '';
$array['element']['host-static']['unset'] = true;

$array['element']['host-type'] = array();
$array['element']['host-type']['value'] = array('dynamic','static');
$array['element']['host-type']['unset'] = true;

$array['element']['port'] = array();
$array['element']['port']['unset'] = true;

$array['element']['regexten'] = array();
$array['element']['regexten']['default'] = '';
$array['element']['regexten']['null'] = true;

$array['element']['subscribecontext'] = array();
$array['element']['subscribecontext']['default'] = '';
$array['element']['subscribecontext']['null'] = true;
$array['element']['subscribecontext']['forcedef'] = true;

$array['element']['fullcontact'] = array();
$array['element']['fullcontact']['unset'] = true;

$array['element']['vmexten'] = array();
$array['element']['vmexten']['unset'] = true;

$array['element']['callingpres'] = array();
$array['element']['callingpres']['unset'] = true;

$array['element']['ipaddr'] = array();
$array['element']['ipaddr']['unset'] = true;

$array['element']['regseconds'] = array();
$array['element']['regseconds']['unset'] = true;

$array['element']['regserver'] = array();
$array['element']['regserver']['unset'] = true;

$array['element']['lastms'] = array();
$array['element']['lastms']['unset'] = true;

$array['element']['protocol'] = array();
$array['element']['protocol']['default'] = XIVO_SRE_IPBX_AST_PROTO_SIP;
$array['element']['protocol']['forcedef'] = true;

$array['element']['category'] = array();
$array['element']['category']['default'] = 'user';
$array['element']['category']['forcedef'] = true;

// asterisk 1.8 fields
$array['element']['transport'] = array();
$array['element']['transport']['value'] = array('udp','tcp','tls', 'udp,tcp', 'tcp,tls', 'udp,tcp,tls');
$array['element']['transport']['default'] = '';
$array['element']['transport']['null']    = true;

$array['element']['directmedia'] = array();
$array['element']['directmedia']['value'] = array('no','yes','nonat','update','update,nonat');
$array['element']['directmedia']['default'] = '';
$array['element']['directmedia']['null'] = true;

$array['element']['callcounter'] = array();
$array['element']['callcounter']['value'] = array(0, 1);
$array['element']['callcounter']['default'] = '';
$array['element']['callcounter']['null']    = true;

$array['element']['busylevel'] = array();
$array['element']['busylevel']['value'] = range(1,100,1);
$array['element']['busylevel']['default'] = '';
$array['element']['busylevel']['null'] = true;

$array['element']['ignoresdpversion'] = array();
$array['element']['ignoresdpversion']['value'] = array(0, 1);
$array['element']['ignoresdpversion']['default'] = '';
$array['element']['ignoresdpversion']['null']    = true;

$array['element']['session-timers'] = array();
$array['element']['session-timers']['value'] = array('originate','accept','refuse');
$array['element']['session-timers']['default'] = '';
$array['element']['session-timers']['null'] = true;

$array['element']['session-expires'] = array();
$array['element']['session-expires']['value'] = range(0,3600,60);
$array['element']['session-expires']['default'] = '';
$array['element']['session-expires']['null'] = true;

$array['element']['session-minse'] = array();
$array['element']['session-minse']['value'] = range(0,300,10);
$array['element']['session-minse']['default'] = '';
$array['element']['session-minse']['null'] = true;

$array['element']['session-refresher'] = array();
$array['element']['session-refresher']['value'] = array('uas','uac');
$array['element']['session-refresher']['default'] = '';
$array['element']['session-refresher']['null'] = true;

$array['element']['registertrying'] = array();
$array['element']['registertrying']['value'] = array(0, 1);
$array['element']['registertrying']['default'] = '';
$array['element']['registertrying']['null']    = true;

$array['element']['timert1'] = array();
$array['element']['timert1']['default'] = '';
$array['element']['timert1']['null'] = true;

$array['element']['timerb'] = array();
$array['element']['timerb']['default'] = '';
$array['element']['timerb']['null'] = true;

$array['element']['qualifyfreq'] = array();
$array['element']['qualifyfreq']['value'] = range(1,300,10);
$array['element']['qualifyfreq']['default'] = '';
$array['element']['qualifyfreq']['null'] = true;

$array['element']['contactpermit'] = array();
$array['element']['contactpermit']['default'] = '';
$array['element']['contactpermit']['null'] = true;

$array['element']['contactdeny'] = array();
$array['element']['contactdeny']['default'] = '';
$array['element']['contactdeny']['null'] = true;

$array['element']['unsolicited_mailbox'] = array();
$array['element']['unsolicited_mailbox']['default'] = '';
$array['element']['unsolicited_mailbox']['null'] = true;

$array['element']['use_q850_reason'] = array();
$array['element']['use_q850_reason']['value'] = array(1, 0);
$array['element']['use_q850_reason']['default'] = '';
$array['element']['use_q850_reason']['null']    = true;

$array['element']['encryption'] = array();
$array['element']['encryption']['value'] = array(1, 0);
$array['element']['encryption']['default'] = '';
$array['element']['encryption']['null']    = true;

$array['element']['snom_aoc_enabled'] = array();
$array['element']['snom_aoc_enabled']['value'] = array(1, 0);
$array['element']['snom_aoc_enabled']['default'] = '';
$array['element']['snom_aoc_enabled']['null']    = true;

$array['element']['disallowed_methods'] = array();
$array['element']['disallowed_methods']['default'] = '';
$array['element']['disallowed_methods']['null'] = true;

$array['element']['maxforwards'] = array();
$array['element']['maxforwards']['value'] = range(1,255,1);
$array['element']['maxforwards']['default'] = '';
$array['element']['maxforwards']['null'] = true;

$array['element']['textsupport'] = array();
$array['element']['textsupport']['value'] = array(1, 0);
$array['element']['textsupport']['default'] = '';
$array['element']['textsupport']['null']    = true;

$array['element']['videosupport'] = array();
$array['element']['videosupport']['value'] = array('no','yes','always');
$array['element']['videosupport']['default'] = '';
$array['element']['videosupport']['null'] = true;

$array['element']['parkinglot'] = array();
$array['element']['parkinglot']['default'] = '';
$array['element']['parkinglot']['null'] = true;



dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['name'] = array('minlen' => 1,'maxlen' => 40,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['type'] = array('set' => false);
$array['filter']['username'] = array('set' => false,'chk' => 0);
$array['filter']['secret'] = array('set'	=> false,
				   'chk'	=> 2,
				   'cast'	=> 'sgraph',
				   'minlen'	=> 1,
				   'maxlen'	=> 80);
$array['filter']['md5secret'] = array('set'	=> false,
				      'chk'	=> 2,
				      'minlen'	=> 1,
				      'maxlen'	=> 32,
				      'cast'	=> 'xdigit');
$array['filter']['context'] = array('callback'		=> 'xivo_service_asterisk::chk_context',
				    'callbackarg'	=> array(array(XIVO_SRE_IPBX_AST_CONTEXT_AUTHENTICATION,
								       XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['language'] = array('set' => false,'chk' => 2,'minlen' =>5,'maxlen' => 5,'key' => array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA', 'nl_NL'));
$array['filter']['accountcode'] = array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9_-]+$/i','maxlen' => 20);
$array['filter']['amaflags'] = array('set'	=> false,
				     'chk'	=> 2,
				     'key'	=> xivo_service_asterisk::get_amaflags_list());
$array['filter']['allowtransfer'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['fromuser'] = array('set' => false,'chk' => 2,'maxlen' => 80,'cast' => 'sgraph');
$array['filter']['fromdomain'] = array('set' => false,
					'chk'		=> 2,
					'callback'	=> 'dwho_network::valid_host',
					'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
						DWHO_NETWORK_HOST_HOSTNAME)));
$array['filter']['mailbox'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9#\*]{1,40}(?:@[a-z0-9@_\-]{1,39})?$/','maxlen' => 80);
$array['filter']['subscribemwi'] = array('bool' => true);
$array['filter']['buggymwi'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['call-limit'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(0,40));
$array['filter']['callerid'] = array('set'	=> false,
				     'chk'	=> 2,
				     'maxlen'	=> 80,
				     'regexp'	=> '/^'.XIVO_SRE_IPBX_AST_REGEXP_CALLERID.'$/u',
				     'notag'	=> false);
$array['filter']['fullname'] = array('set' => false,'chk' => 0);
$array['filter']['cid_number'] = array('set' => false,'chk' => 0);
$array['filter']['maxcallbitrate'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,1860));
$array['filter']['insecure'] = array('set' => false,'chk' => 2,'key' => $array['element']['insecure']['value']);
$array['filter']['nat'] = array('set' => false,'chk' => 2,'key' => array('no','yes','force_rport','comedia'));
$array['filter']['promiscredir'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['usereqphone'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['trustrpid'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['sendrpid'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['allowsubscribe'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['allowoverlap'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['dtmfmode'] = array('set' => false,'chk' => 2,'key' => array('rfc2833','inband','info','auto'));
$array['filter']['rfc2833compensate'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['qualify'] = array('set' => false,'chk' => 2,'key' => array('no','yes',500,1000,1500,2000,2500,3000,3500,4000));
$array['filter']['g726nonstandard'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['disallow'] = array('set' => false,'chk' => 2,'key' => array('all'));
$array['filter']['allow'] = array('set' => false,'chk' => 2,'uvalue' => xivo_service_asterisk::get_codecs_list());
$array['filter']['autoframing'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['mohinterpret'] = array('set' => false,'chk' => 0);
$array['filter']['mohsuggest'] = array('set' => false,'chk' => 2,'cast' => 'sgraph','maxlen' => 20);
$array['filter']['useclientcode'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['progressinband'] = array('set' => false,'chk' => 2,'key' => array('no','yes','never'));
$array['filter']['t38pt_udptl'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['t38pt_usertpsource'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['rtptimeout'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(0,60,5));
$array['filter']['rtpholdtimeout'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(0,60,5));
$array['filter']['rtpkeepalive'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(0,60,5));
$array['filter']['deny'] = array('set'			=> false,
				 'chk'			=> 2,
				 'callback'	=> 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['permit'] = array('set'		=> false,
				   'chk'		=> 2,
				 'callback'	=> 'dwho_network::valid_host_subnet_ipv4');
$array['filter']['defaultip'] = array('set' => false,'chk' => 0);
$array['filter']['callgroup'] = array('set' => false,'chk' => 2,'regexp' => '/^(?:[0-9]+[,]?)*$/','maxlen' => 180);
$array['filter']['pickupgroup'] = array('set' => false,'chk' => 2,'regexp' => '/^(?:[0-9]+[,]?)*$/','maxlen' => 180);
$array['filter']['setvar'] = array('set'	=> false,
				   'chk'	=> 2,
				   'minlen'	=> 2,
				   'maxlen'	=> 100,
				   'regexp'	=> '/^[a-zA-Z0-9_\(\)]+=[^\|,]*(?:\|[a-zA-Z0-9_\(\)]+=[^\|,]*)*$/');
$array['filter']['host'] = array('set'		=> false,
				 'chk'		=> 2,
				 'key'		=> array('dynamic','static'),
				 'strict'	=> false,
				 'callback'	=> 'dwho_network::valid_host',
				 'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
							  DWHO_NETWORK_HOST_HOSTNAME)));
$array['filter']['port'] = array('set' => false,'chk' => 0);
$array['filter']['regexten'] = array('set' => false,'chk' => 0);
$array['filter']['subscribecontext'] = array('set' => false,'chk' => 0);
$array['filter']['fullcontact'] = array('set' => false,'chk' => 0);
$array['filter']['vmexten'] = array('set' => false,'chk' => 0);
$array['filter']['callingpres'] = array('set' => false,'chk' => 0);
$array['filter']['ipaddr'] = array('set' => false,'chk' => 0);
$array['filter']['regseconds'] = array('set' => false);
$array['filter']['regserver'] = array('set' => false,'chk' => 0);
$array['filter']['lastms'] = array('set' => false,'chk' => 0);
$array['filter']['protocol'] = array('set' => false);
$array['filter']['category'] = array('set' => false);
$array['filter']['transport'] = array('set' => false, 'chk' => 2, 'key' => array('udp','tcp','tls', 'udp,tcp', 'tcp,tls', 'udp,tcp,tls'));
$array['filter']['directmedia'] = array('set' => false, 'chk' => 2, 'key' => array('no','yes','nonat','update','update,nonat'));
$array['filter']['callcounter'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['busylevel'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(1,100,1));
$array['filter']['ignoresdpversion'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['session-timers'] = array('set' => false, 'chk' => 2, 'key' => array('originate','accept','refuse'));
$array['filter']['session-expires'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,3600,60));
$array['filter']['session-minse'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,300,10));
$array['filter']['session-refresher'] = array('set' => false, 'chk' => 2, 'key' => array('uas','uac'));
$array['filter']['registertrying'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['timert1'] = array('set' => false,'chk' => 2,'maxlen' => 5);
$array['filter']['timerb'] = array('set' => false,'chk' => 2,'maxlen' => 5);
$array['filter']['qualifyfreq'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(1,300,10));
$array['filter']['contactpermit'] = array('set' => false,'chk' => 2,'maxlen' => 35);
$array['filter']['contactdeny'] = array('set' => false,'chk' => 2,'maxlen' => 35);
$array['filter']['unsolicited_mailbox'] = array('set' => false,'chk' => 2,'maxlen' => 1024);
$array['filter']['use_q850_reason'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['encryption'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['snom_aoc_enabled'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['disallowed_methods'] = array('set' => false,'chk' => 2,'maxlen' => 1024);
$array['filter']['maxforwards'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(1,255,1));
$array['filter']['textsupport'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['videosupport'] = array('set' => false, 'chk' => 2, 'key' => array('no','yes','always'));
$array['filter']['parkinglot'] = array('set' => false,'chk' => 2,'cast' => 'uint');

?>
