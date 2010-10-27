<?php

#
# XiVO Web-Interface
# Copyright (C) 2006-2010  Proformatique <technique@proformatique.com>
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

$array['element']['bindport'] = array();
$array['element']['bindport']['default'] = 5060;
$array['element']['bindport']['setdef'] = true;

$array['element']['videosupport'] = array();
$array['element']['videosupport']['value'] = array('no','yes');
$array['element']['videosupport']['default'] = 'no';
$array['element']['videosupport']['set'] = true;

$array['element']['autocreatepeer'] = array();
$array['element']['autocreatepeer']['value'] = array('no','yes');
$array['element']['autocreatepeer']['default'] = 'no';
$array['element']['autocreatepeer']['set'] = true;

$array['element']['allowguest'] = array();
$array['element']['allowguest']['value'] = array('no','yes');
$array['element']['allowguest']['default'] = 'no';
$array['element']['allowguest']['set'] = true;

$array['element']['allowsubscribe'] = array();
$array['element']['allowsubscribe']['value'] = array('no','yes');
$array['element']['allowsubscribe']['default'] = 'yes';
$array['element']['allowsubscribe']['set'] = true;

$array['element']['allowoverlap'] = array();
$array['element']['allowoverlap']['value'] = array('no','yes');
$array['element']['allowoverlap']['default'] = 'yes';
$array['element']['allowoverlap']['set'] = true;

$array['element']['promiscredir'] = array();
$array['element']['promiscredir']['value'] = array('no','yes');
$array['element']['promiscredir']['default'] = 'no';
$array['element']['promiscredir']['set'] = true;

$array['element']['autodomain'] = array();
$array['element']['autodomain']['value'] = array('no','yes');
$array['element']['autodomain']['default'] = 'no';
$array['element']['autodomain']['set'] = true;

$array['element']['domain'] = array();
$array['element']['domain']['default'] = '';
$array['element']['domain']['null'] = true;

$array['element']['allowexternaldomains'] = array();
$array['element']['allowexternaldomains']['value'] = array('no','yes');
$array['element']['allowexternaldomains']['default'] = 'yes';
$array['element']['allowexternaldomains']['set'] = true;

$array['element']['usereqphone'] = array();
$array['element']['usereqphone']['value'] = array('no','yes');
$array['element']['usereqphone']['default'] = 'no';
$array['element']['usereqphone']['set'] = true;

$array['element']['realm'] = array();
$array['element']['realm']['default'] = 'xivo';

$array['element']['alwaysauthreject'] = array();
$array['element']['alwaysauthreject']['value'] = array('no','yes');
$array['element']['alwaysauthreject']['default'] = 'no';
$array['element']['alwaysauthreject']['set'] = true;

$array['element']['useragent'] = array();
$array['element']['useragent']['default'] = 'XIVO PBX';

$array['element']['buggymwi'] = array();
$array['element']['buggymwi']['value'] = array('no','yes');
$array['element']['buggymwi']['default'] = 'no';
$array['element']['buggymwi']['set'] = true;

$array['element']['regcontext'] = array();
$array['element']['regcontext']['default'] = '';
$array['element']['regcontext']['null'] = true;

$array['element']['callerid'] = array();
$array['element']['callerid']['default'] = 'xivo';

$array['element']['fromdomain'] = array();
$array['element']['fromdomain']['default'] = '';
$array['element']['fromdomain']['null'] = true;

$array['element']['sipdebug'] = array();
$array['element']['sipdebug']['value'] = array('no','yes');
$array['element']['sipdebug']['default'] = 'no';
$array['element']['sipdebug']['set'] = true;

$array['element']['dumphistory'] = array();
$array['element']['dumphistory']['value'] = array('no','yes');
$array['element']['dumphistory']['default'] = 'no';
$array['element']['dumphistory']['set'] = true;

$array['element']['recordhistory'] = array();
$array['element']['recordhistory']['value'] = array('no','yes');
$array['element']['recordhistory']['default'] = 'no';
$array['element']['recordhistory']['set'] = true;

$array['element']['callevents'] = array();
$array['element']['callevents']['value'] = array('no','yes');
$array['element']['callevents']['default'] = 'yes';
$array['element']['callevents']['set'] = true;
$array['element']['callevents']['forcedef'] = true;

$array['element']['tos_sip'] = array();
$array['element']['tos_sip']['value'] = array('CS0','CS1','CS2','CS3','CS4','CS5','CS6','CS7',
					      'AF11','AF12','AF13','AF21','AF22','AF23',
					      'AF31', 'AF32','AF33','AF41','AF42','AF43','EF');
$array['element']['tos_sip']['default'] = '';
$array['element']['tos_sip']['null'] = true;

$array['element']['tos_audio'] = array();
$array['element']['tos_audio']['value'] = array('CS0','CS1','CS2','CS3','CS4','CS5','CS6','CS7',
						'AF11','AF12','AF13','AF21','AF22','AF23',
						'AF31', 'AF32','AF33','AF41','AF42','AF43','EF');
$array['element']['tos_audio']['default'] = '';
$array['element']['tos_audio']['null'] = true;

$array['element']['tos_video'] = array();
$array['element']['tos_video']['value'] = array('CS0','CS1','CS2','CS3','CS4','CS5','CS6','CS7',
						'AF11','AF12','AF13','AF21','AF22','AF23',
						'AF31', 'AF32','AF33','AF41','AF42','AF43','EF');
$array['element']['tos_video']['default'] = '';
$array['element']['tos_video']['null'] = true;

$array['element']['t38pt_udptl'] = array();
$array['element']['t38pt_udptl']['value'] = array('no','yes', 'fec', 'redundancy', 'none');
$array['element']['t38pt_udptl']['default'] = 'no';
$array['element']['t38pt_udptl']['set'] = true;

$array['element']['t38pt_usertpsource'] = array();
$array['element']['t38pt_usertpsource']['value'] = array('no','yes');
$array['element']['t38pt_usertpsource']['default'] = 'no';
$array['element']['t38pt_usertpsource']['set'] = true;

$array['element']['localnet'] = array();
$array['element']['localnet']['default'] = '';
$array['element']['localnet']['null'] = true;
$array['element']['localnet']['multi'] = true;

$array['element']['externip'] = array();
$array['element']['externip']['default'] = '';
$array['element']['externip']['null'] = true;

$array['element']['externhost'] = array();
$array['element']['externhost']['default'] = '';
$array['element']['externhost']['null'] = true;

$array['element']['externrefresh'] = array();
$array['element']['externrefresh']['value'] = array(1,10,20,30,40,50,60,70,80,90,
						    100,110,120,180,240,300,600,900,
						    1200,1800);
$array['element']['externrefresh']['default'] = 10;

$array['element']['matchexterniplocally'] = array();
$array['element']['matchexterniplocally']['value'] = array('no','yes');
$array['element']['matchexterniplocally']['default'] = 'no';
$array['element']['matchexterniplocally']['set'] = true;

$array['element']['outboundproxy'] = array();
$array['element']['outboundproxy']['default'] = '';
$array['element']['outboundproxy']['null'] = true;

$array['element']['g726nonstandard'] = array();
$array['element']['g726nonstandard']['value'] = array('no','yes');
$array['element']['g726nonstandard']['default'] = 'no';
$array['element']['g726nonstandard']['set'] = true;

$array['element']['disallow'] = array();
$array['element']['disallow']['value'] = array('all');
$array['element']['disallow']['default'] = 'all';
$array['element']['disallow']['unset'] = true;

$array['element']['allow'] = array();
$array['element']['allow']['value'] = array(
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_G723,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_GSM,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_ULAW,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_ALAW,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_ADPCM,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_SLIN,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_LPC10,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_G729,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_SPEEX,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_ILBC,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_G726,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_G722,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_G722_1,
					XIVO_SRE_IPBX_AST_CODEC_AUDIO_G722_1C,
					XIVO_SRE_IPBX_AST_CODEC_IMAGE_JPEG,
					XIVO_SRE_IPBX_AST_CODEC_IMAGE_PNG,
					XIVO_SRE_IPBX_AST_CODEC_VIDEO_H261,
					XIVO_SRE_IPBX_AST_CODEC_VIDEO_H263,
					XIVO_SRE_IPBX_AST_CODEC_VIDEO_H263P,
					XIVO_SRE_IPBX_AST_CODEC_VIDEO_H264);
$array['element']['allow']['default'] = '';
$array['element']['allow']['null'] = true;

$array['element']['t1min'] = array();
$array['element']['t1min']['value'] = array(0,10,20,30,40,50,60,70,80,90,100,
					    200,300,400,500,600,700,800,900,
					    1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,
					    2000,2500,3000,3500,4000);
$array['element']['t1min']['default'] = 100;

$array['element']['relaxdtmf'] = array();
$array['element']['relaxdtmf']['value'] = array('no','yes');
$array['element']['relaxdtmf']['default'] = 'no';
$array['element']['relaxdtmf']['set'] = true;

$array['element']['rfc2833compensate'] = array();
$array['element']['rfc2833compensate']['value'] = array('no','yes');
$array['element']['rfc2833compensate']['default'] = 'no';
$array['element']['rfc2833compensate']['set'] = true;

$array['element']['compactheaders'] = array();
$array['element']['compactheaders']['value'] = array('no','yes');
$array['element']['compactheaders']['default'] = 'no';
$array['element']['compactheaders']['set'] = true;

$array['element']['rtptimeout'] = array();
$array['element']['rtptimeout']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['rtptimeout']['default'] = 0;

$array['element']['rtpholdtimeout'] = array();
$array['element']['rtpholdtimeout']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['rtpholdtimeout']['default'] = 0;

$array['element']['rtpkeepalive'] = array();
$array['element']['rtpkeepalive']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['rtpkeepalive']['default'] = 0;

$array['element']['directrtpsetup'] = array();
$array['element']['directrtpsetup']['value'] = array('no','yes');
$array['element']['directrtpsetup']['default'] = 'no';
$array['element']['directrtpsetup']['set'] = true;

$array['element']['notifymimetype'] = array();
$array['element']['notifymimetype']['default'] = 'application/simple-message-summary';
$array['element']['notifymimetype']['setdef'] = true;

$array['element']['srvlookup'] = array();
$array['element']['srvlookup']['value'] = array('no','yes');
$array['element']['srvlookup']['default'] = 'no';
$array['element']['srvlookup']['set'] = true;

$array['element']['pedantic'] = array();
$array['element']['pedantic']['value'] = array('no','yes');
$array['element']['pedantic']['default'] = 'no';
$array['element']['pedantic']['set'] = true;

$array['element']['minexpiry'] = array();
$array['element']['minexpiry']['value'] = array(1,10,20,30,40,50,60,70,80,90,
						100,110,120,130,140,150,160,170,180,190,
						200,210,220,230,240,300,600,900,
						1200,1800,2400,2700,3000,3600,4500,
						5400,6300,7200);
$array['element']['minexpiry']['default'] = 60;

$array['element']['maxexpiry'] = array();
$array['element']['maxexpiry']['value'] = array(1,10,20,30,40,50,60,70,80,90,
						100,110,120,130,140,150,160,170,180,190,
						200,210,220,230,240,300,600,900,
						1200,1800,2400,2700,3000,3600,4500,
						5400,6300,7200);
$array['element']['maxexpiry']['default'] = 3600;

$array['element']['defaultexpiry'] = array();
$array['element']['defaultexpiry']['value'] = array(1,10,20,30,40,50,60,70,80,90,
						    100,110,120,130,140,150,160,170,180,190,
						    200,210,220,230,240,300,600,900,
						    1200,1800,2400,2700,3000,3600,4500,
						    5400,6300,7200);
$array['element']['defaultexpiry']['default'] = 120;

$array['element']['registertimeout'] = array();
$array['element']['registertimeout']['value'] = array(1,10,20,30,40,50,60,70,80,90,100,110,120);
$array['element']['registertimeout']['default'] = 20;

$array['element']['registerattempts'] = array();
$array['element']['registerattempts']['value'] = array(0,5,10,15,20,25,30,35,40,45,
						       50,55,60,65,70,75,80,85,90,95,
						       100,105,110,115,120,125,130,135,140,145,
						       150,155,160,165,170,175,180,185,190,195,200);
$array['element']['registerattempts']['default'] = 0;

$array['element']['notifyringing'] = array();
$array['element']['notifyringing']['value'] = array('no','yes');
$array['element']['notifyringing']['default'] = 'yes';
$array['element']['notifyringing']['set'] = true;

$array['element']['notifyhold'] = array();
$array['element']['notifyhold']['value'] = array('no','yes');
$array['element']['notifyhold']['default'] = 'no';
$array['element']['notifyhold']['set'] = true;

$array['element']['allowtransfer'] = array();
$array['element']['allowtransfer']['value'] = array('no','yes');
$array['element']['allowtransfer']['default'] = 'yes';
$array['element']['allowtransfer']['set'] = true;

$array['element']['maxcallbitrate'] = array();
$array['element']['maxcallbitrate']['default'] = 384;

$array['element']['autoframing'] = array();
$array['element']['autoframing']['value'] = array('no','yes');
$array['element']['autoframing']['default'] = 'yes';
$array['element']['autoframing']['set'] = true;

$array['element']['jbenable'] = array();
$array['element']['jbenable']['value'] = array('no','yes');
$array['element']['jbenable']['default'] = 'no';
$array['element']['jbenable']['set'] = true;

$array['element']['jbforce'] = array();
$array['element']['jbforce']['value'] = array('no','yes');
$array['element']['jbforce']['default'] = 'no';
$array['element']['jbforce']['set'] = true;

$array['element']['jbmaxsize'] = array();
$array['element']['jbmaxsize']['value'] = array(0,100,150,200,250,500,750,1000,1250,1500,1750,2000);
$array['element']['jbmaxsize']['default'] = 200;

$array['element']['jbresyncthreshold'] = array();
$array['element']['jbresyncthreshold']['value'] = array(-1,0,250,500,750,1000,1250,1500,1750,2000);
$array['element']['jbresyncthreshold']['default'] = 1000;

$array['element']['jbimpl'] = array();
$array['element']['jbimpl']['value'] = array('fixed','adaptative');
$array['element']['jbimpl']['default'] = 'fixed';

$array['element']['jblog'] = array();
$array['element']['jblog']['value'] = array('no','yes');
$array['element']['jblog']['default'] = 'no';
$array['element']['jblog']['set'] = true;

$array['element']['context'] = array();
$array['element']['context']['default'] = '';
$array['element']['context']['null'] = true;

$array['element']['nat'] = array();
$array['element']['nat']['value'] = array('no','yes','force_rport','comedia');
$array['element']['nat']['default'] = 'no';

$array['element']['dtmfmode'] = array();
$array['element']['dtmfmode']['value'] = array('rfc2833','inband','info','shortinfo', 'auto');
$array['element']['dtmfmode']['default'] = 'info';

$array['element']['qualify'] = array();
$array['element']['qualify']['value'] = array('no','yes',500,1000,1500,2000,2500,3000,3500,4000);
$array['element']['qualify']['default'] = 'no';

$array['element']['useclientcode'] = array();
$array['element']['useclientcode']['value'] = array('no','yes');
$array['element']['useclientcode']['default'] = 'no';
$array['element']['useclientcode']['set'] = true;

$array['element']['progressinband'] = array();
$array['element']['progressinband']['value'] = array('no','yes','never');
$array['element']['progressinband']['default'] = 'never';

$array['element']['language'] = array();
$array['element']['language']['value'] = array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA');
$array['element']['language']['default'] = 'fr_FR';

$array['element']['mohinterpret'] = array();
$array['element']['mohinterpret']['default'] = XIVO_SRE_IPBX_AST_MOH_DEFAULT;
$array['element']['mohinterpret']['setdef'] = true;

$array['element']['mohsuggest'] = array();
$array['element']['mohsuggest']['default'] = '';
$array['element']['mohsuggest']['null'] = true;

$array['element']['vmexten'] = array();
$array['element']['vmexten']['default'] = '*98';

$array['element']['trustrpid'] = array();
$array['element']['trustrpid']['value'] = array('no','yes');
$array['element']['trustrpid']['default'] = 'no';
$array['element']['trustrpid']['set'] = true;

$array['element']['sendrpid'] = array();
$array['element']['sendrpid']['value'] = array('no', 'yes','rpid','pai');
$array['element']['sendrpid']['default'] = 'no';

$array['element']['insecure'] = array();
$array['element']['insecure']['value'] = array('no'		=> 'no',
					       'port'		=> 'port',
					       'invite'		=> 'invite',
					       'port,invite'	=> 'all');
$array['element']['insecure']['default'] = 'no';

$array['element']['rtcachefriends'] = array();
$array['element']['rtcachefriends']['value'] = array('no','yes');
$array['element']['rtcachefriends']['default'] = 'yes';
$array['element']['rtcachefriends']['set'] = true;

$array['element']['rtupdate'] = array();
$array['element']['rtupdate']['value'] = array('no','yes');
$array['element']['rtupdate']['default'] = 'yes';
$array['element']['rtupdate']['set'] = true;

$array['element']['ignoreregexpire'] = array();
$array['element']['ignoreregexpire']['value'] = array('no','yes');
$array['element']['ignoreregexpire']['default'] = 'no';
$array['element']['ignoreregexpire']['set'] = true;

$array['element']['rtsavesysname'] = array();
$array['element']['rtsavesysname']['value'] = array('no','yes');
$array['element']['rtsavesysname']['default'] = 'no';
$array['element']['rtsavesysname']['set'] = true;

$array['element']['rtautoclear'] = array();
$array['element']['rtautoclear']['value'] = array('no','yes',1,10,20,30,40,50,60,70,80,90,
						  100,110,120,130,140,150,160,170,180,190,
						  200,210,220,230,240);
$array['element']['rtautoclear']['default'] = 'no';

$array['element']['subscribecontext'] = array();
$array['element']['subscribecontext']['default'] = '';
$array['element']['subscribecontext']['forcedef'] = true;
$array['element']['subscribecontext']['null'] = true;

// new asterisk 1.8 options
$array['element']['match_auth_username'] = array();
$array['element']['match_auth_username']['value'] = array('no', 'yes');
$array['element']['match_auth_username']['default'] = 'no';
$array['element']['match_auth_username']['set'] = true;

$array['element']['udpbindaddr'] = array();
$array['element']['udpbindaddr']['default'] = '0.0.0.0';
$array['element']['udpbindaddr']['null'] = true;

$array['element']['tcpenable'] = array();
$array['element']['tcpenable']['value'] = array('no','yes');
$array['element']['tcpenable']['default'] = 'no';
$array['element']['tcpenable']['set'] = true;

$array['element']['tcpbindaddr'] = array();
$array['element']['tcpbindaddr']['default'] = '';
$array['element']['tcpbindaddr']['null'] = true;

$array['element']['tlsenable'] = array();
$array['element']['tlsenable']['value'] = array('no','yes');
$array['element']['tlsenable']['default'] = 'no';
$array['element']['tlsenable']['set'] = true;

$array['element']['tlsbindaddr'] = array();
$array['element']['tlsbindaddr']['default'] = '';
$array['element']['tlsbindaddr']['null'] = true;

$array['element']['tlscertfile'] = array();
$array['element']['tlscertfile']['default'] = '';
$array['element']['tlscertfile']['null'] = true;

$array['element']['tlscafile'] = array();
$array['element']['tlscafile']['default'] = '';
$array['element']['tlscafile']['null'] = true;

$array['element']['tlscadir'] = array();
$array['element']['tlscadir']['default'] = '';
$array['element']['tlscadir']['null'] = true;

$array['element']['tlsdontverifyserver'] = array();
$array['element']['tlsdontverifyserver']['value'] = array('no','yes');
$array['element']['tlsdontverifyserver']['default'] = 'no';
$array['element']['tlsdontverifyserver']['set'] = true;

$array['element']['tlscipher'] = array();
$array['element']['tlscipher']['default'] = '';
$array['element']['tlscipher']['null'] = true;
//$array['element']['tlscipher']['value']    = array('default', 'complementofdefault', 'all', 'complementofall', 'high', 'medium', 'low', 'export', 'export40', 'export50', 'null', 'aNULL', 'RSA', 'kEDH', 'kDHd', 'aRSA', 'DSS', 'aDH', 'FZA', 'SSLv2', 'DH', 'ADH', 'AES', 'CAMELLIA', '3DES', 'DES', 'RC4', 'RC2', 'IDEA', 'SEED', 'MD5', 'SHA1', 'SHA', 'aGOST', 'aGOST01', 'aGOST94', 'kGOST', 'GOST94', 'GOST89MAC');

$array['element']['tos_text'] = array();
$array['element']['tos_text']['value'] = array('CS0','CS1','CS2','CS3','CS4','CS5','CS6','CS7',
					      'AF11','AF12','AF13','AF21','AF22','AF23',
					      'AF31', 'AF32','AF33','AF41','AF42','AF43','EF');
$array['element']['tos_text']['default'] = '';
$array['element']['tos_text']['null'] = true;

$array['element']['cos_sip'] = array();
$array['element']['cos_sip']['value']    = array(1, 2, 3, 4, 5, 6, 7);
$array['element']['cos_sip']['default']  = '';
$array['element']['cos_sip']['null']     = true;

$array['element']['cos_audio'] = array();
$array['element']['cos_audio']['value']    = array(1, 2, 3, 4, 5, 6, 7);
$array['element']['cos_audio']['default']  = '';
$array['element']['cos_audio']['null']     = true;

$array['element']['cos_video'] = array();
$array['element']['cos_video']['value']    = array(1, 2, 3, 4, 5, 6, 7);
$array['element']['cos_video']['default']  = '';
$array['element']['cos_video']['null']     = true;

$array['element']['cos_text'] = array();
$array['element']['cos_text']['value']    = array(1, 2, 3, 4, 5, 6, 7);
$array['element']['cos_text']['default']  = '';
$array['element']['cos_text']['null']     = true;

$array['element']['mwiexpiry'] = array();
$array['element']['mwiexpiry']['value'] = array(1,10,20,30,40,50,60,70,80,90,
						    100,110,120,130,140,150,160,170,180,190,
						    200,210,220,230,240,300,600,900,
						    1200,1800,2400,2700,3000,3600,4500,
						    5400,6300,7200);
$array['element']['mwiexpiry']['default']  = 3600;
$array['element']['mwiexpiry']['null']     = true;

$array['element']['qualifyfreq'] = array();
$array['element']['qualifyfreq']['value'] = array(0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400,410,420,430,440,450,460,470,480,490,500,510,520,530,540,550,560,570,580,590,600);
$array['element']['qualifyfreq']['default'] = '60';
$array['element']['qualifyfreq']['null'] = true;

$array['element']['qualifygap'] = array();
$array['element']['qualifygap']['value'] = array(0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400,410,420,430,440,450,460,470,480,490,500,510,520,530,540,550,560,570,580,590,600,610,620,630,640,650,660,670,680,690,700,710,720,730,740,750,760,770,780,790,800,810,820,830,840,850,860,870,880,890,900,910,920,930,940,950,960,970,980,990,1000);
$array['element']['qualifygap']['default'] = '100';
$array['element']['qualifygap']['null'] = true;

$array['element']['qualifypeers'] = array();
$array['element']['qualifypeers']['value']    = array(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,35,40,45,50,60,70,80,90,100);
$array['element']['qualifypeers']['default']  = 1;
//$array['element']['qualifypeers']['null']     = true;

$array['element']['parkinglot'] = array();
$array['element']['parkinglot']['default']  = '';
$array['element']['parkinglot']['null']     = true;

$array['element']['prematuremedia'] = array();
$array['element']['prematuremedia']['value']    = array('no', 'yes');
$array['element']['prematuremedia']['default']  = 'no';
$array['element']['prematuremedia']['null']     = true;

$array['element']['sdpsession'] = array();
$array['element']['sdpsession']['default']  = '';
$array['element']['sdpsession']['null']     = true;

$array['element']['sdpowner'] = array();
$array['element']['sdpowner']['default']  = '';
$array['element']['sdpowner']['null']     = true;

$array['element']['authfailureevents'] = array();
$array['element']['authfailureevents']['value']    = array('no', 'yes');
$array['element']['authfailureevents']['default']  = 'no';
$array['element']['authfailureevents']['set']     = true;

$array['element']['dynamic_exclude_static'] = array();
$array['element']['dynamic_exclude_static']['value']    = array('no', 'yes');
$array['element']['dynamic_exclude_static']['default']  = 'no';
$array['element']['dynamic_exclude_static']['set']      = true;

$array['element']['contactdeny'] = array();
$array['element']['contactdeny']['default']  = '';
$array['element']['contactdeny']['null']     = true;

$array['element']['contactpermit'] = array();
$array['element']['contactpermit']['default']  = '';
$array['element']['contactpermit']['null']     = true;

$array['element']['shrinkcallerid'] = array();
$array['element']['shrinkcallerid']['value']    = array('no', 'yes');
$array['element']['shrinkcallerid']['default']  = 'yes';
$array['element']['shrinkcallerid']['set']      = true;

$array['element']['regextenonqualify'] = array();
$array['element']['regextenonqualify']['value']    = array('no', 'yes');
$array['element']['regextenonqualify']['default']  = 'no';
$array['element']['regextenonqualify']['set']      = true;

$array['element']['timert1'] = array();
$array['element']['timert1']['value'] = array(0,10,30,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000);
$array['element']['timert1']['default'] = '500';

$array['element']['timerb'] = array();
$array['element']['timerb']['value'] = array(0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,24000,25000,26000,27000,28000,29000,30000,31000,32000,33000,34000,35000,36000,37000,38000,39000,40000,41000,42000,43000,44000,45000,46000,47000,48000,49000,50000,51000,52000,53000,54000,55000,56000,57000,58000,59000,60000,61000,62000,63000,64000,65000,66000,67000,68000,69000,70000,71000,72000,73000,74000,75000,76000,77000,78000,79000,80000,81000,82000,83000,84000,85000,86000,87000,88000,89000,90000,91000,92000,93000,94000,95000,96000,97000,98000,99000,100000,101000,102000,103000,104000,105000,106000,107000,108000,109000,110000,111000,112000,113000,114000,115000,116000,117000,118000,119000,120000);
$array['element']['timerb']['default'] = '32000';
$array['element']['timerb']['null'] = true;

$array['element']['session-timers'] = array();
$array['element']['session-timers']['value']    = array('originate', 'accept', 'refuse');
$array['element']['session-timers']['default']  = null;
$array['element']['session-timers']['null']     = true;

$array['element']['session-expires'] = array();
$array['element']['session-expires']['value'] = array(0,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,960,1020,1080,1140,1200,1260,1320,1380,1440,1500,1560,1620,1680,1740,1800,1860,1920,1980,2040,2100,2160,2220,2280,2340,2400,2460,2520,2580,2640,2700,2760,2820,2880,2940,3000,3060,3120,3180,3240,3300,3360,3420,3480,3540,3600);
$array['element']['session-expires']['default'] = '1800';
$array['element']['session-expires']['null'] = true;

$array['element']['session-minse'] = array();
$array['element']['session-minse']['value'] = array(0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400,410,420,430,440,450,460,470,480,490,500,510,520,530,540,550,560,570,580,590,600);
$array['element']['session-minse']['default'] = '90';
$array['element']['session-minse']['null'] = true;

$array['element']['session-refresher'] = array();
$array['element']['session-refresher']['value']    = array('uas', 'uac');
$array['element']['session-refresher']['default']  = 'uas';
$array['element']['session-refresher']['null']     = false;

$array['element']['hash_users'] = array();
//$array['element']['hash_users']['default']  = '563';
$array['element']['hash_users']['default']  = null;
$array['element']['hash_users']['null']     = true;

$array['element']['hash_peers'] = array();
//$array['element']['hash_peers']['default']  = '563';
$array['element']['hash_peers']['default']  = null;
$array['element']['hash_peers']['null']     = true;

$array['element']['hash_dialogs'] = array();
//$array['element']['hash_dialogs']['default']  = '563';
$array['element']['hash_dialogs']['default']  = null;
$array['element']['hash_dialogs']['null']     = true;


$array['element']['notifycid'] = array();
$array['element']['notifycid']['value']    = array('no', 'yes');
$array['element']['notifycid']['default']  = 'no';
$array['element']['notifycid']['set']      = true;

$array['element']['callcounter'] = array();
$array['element']['callcounter']['value']    = array('no', 'yes');
$array['element']['callcounter']['default']  = 'no';
$array['element']['callcounter']['set']      = true;

$array['element']['faxdetect'] = array();
$array['element']['faxdetect']['value']    = array('yes', 'no', 'cng', 't38', 'both');
$array['element']['faxdetect']['default']  = 'no';
$array['element']['faxdetect']['null']     = true;

$array['element']['stunaddr'] = array();
$array['element']['stunaddr']['default']  = '';
$array['element']['stunaddr']['null']     = true;

$array['element']['directmedia'] = array();
$array['element']['directmedia']['value']    = array(
	'yes'          => 'yes', 
	'no'           => 'no', 
	'nonat'        => 'nonat',
	'update'       => 'update', 
	'update,nonat' => 'update,nonat');
$array['element']['directmedia']['default']  = 'yes';
$array['element']['directmedia']['null']     = true;

$array['element']['ignoresdpversion'] = array();
$array['element']['ignoresdpversion']['value']    = array('no', 'yes');
$array['element']['ignoresdpversion']['default']  = 'no';
$array['element']['ignoresdpversion']['set']      = true;

$array['element']['jbtargetextra'] = array();
//$array['element']['jbtargetextra']['default']  = '40';
$array['element']['jbtargetextra']['default']  = null;
$array['element']['jbtargetextra']['null']     = true;

$array['element']['media_address'] = array();
$array['element']['media_address']['default'] = '';
$array['element']['media_address']['null'] = true;

$array['element']['externtcpport'] = array();
$array['element']['externtcpport']['default'] = '';
$array['element']['externtcpport']['null'] = true;

$array['element']['externtlsport'] = array();
$array['element']['externtlsport']['default'] = '';
$array['element']['externtlsport']['null'] = true;

$array['element']['use_q850_reason'] = array();
$array['element']['use_q850_reason']['value'] = array('no','yes');
$array['element']['use_q850_reason']['default'] = 'no';
$array['element']['use_q850_reason']['set'] = true;

$array['element']['snom_aoc_enabled'] = array();
$array['element']['snom_aoc_enabled']['value'] = array('no','yes');
$array['element']['snom_aoc_enabled']['default'] = 'no';
$array['element']['snom_aoc_enabled']['set'] = true;

$array['element']['subscribe_network_change_event'] = array();
$array['element']['subscribe_network_change_event']['value'] = array('no','yes');
$array['element']['subscribe_network_change_event']['default'] = 'yes';
$array['element']['subscribe_network_change_event']['set'] = true;

$array['element']['maxforwards'] = array();
$array['element']['maxforwards']['value'] = range(1,255,1);
$array['element']['maxforwards']['default'] = '';
$array['element']['maxforwards']['null'] = true;

$array['element']['disallow_methods'] = array();
$array['element']['disallow_methods']['default'] = '';
$array['element']['disallow_methods']['null'] = true;

$array['element']['domainsasrealm'] = array();
$array['element']['domainsasrealm']['value'] = array('no','yes');
$array['element']['domainsasrealm']['default'] = 'no';
$array['element']['domainsasrealm']['set']     = true;

$array['element']['textsupport'] = array();
$array['element']['textsupport']['value'] = array('no','yes');
$array['element']['textsupport']['default'] = '';
$array['element']['textsupport']['null']    = true;

$array['element']['videosupport'] = array();
$array['element']['videosupport']['value'] = array('no','yes','always');
$array['element']['videosupport']['default'] = '';
$array['element']['videosupport']['null'] = true;

$array['element']['auth_options_requests'] = array();
$array['element']['auth_options_requests']['value'] = array('no','yes');
$array['element']['auth_options_requests']['default'] = 'no';
$array['element']['auth_options_requests']['set'] = true;


// this is not a real sip option
$array['element']['srtp'] = array();
$array['element']['srtp']['value']    = array('no', 'yes');
$array['element']['srtp']['default']  = 'no';
$array['element']['srtp']['set']      = true;



dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['bindport'] = array('set' => false,'chk' => 2,'cast' => 'uint','between' => array(1,65535));
$array['filter']['udpbindaddr'] = array('set' => false,'chk' => 2,'callback' => 'dwho_network::valid_host',
				     'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC | DWHO_NETWORK_HOST_HOSTNAME)),
				     'maxlen'		=> 64);
$array['filter']['videosupport'] = array('bool' => true);
$array['filter']['autocreatepeer'] = array('bool' => true);
$array['filter']['allowguest'] = array('bool' => true);
$array['filter']['allowsubscribe'] = array('bool' => true);
$array['filter']['allowoverlap'] = array('bool' => true);
$array['filter']['promiscredir'] = array('bool' => true);
$array['filter']['autodomain'] = array('bool' => true);
$array['filter']['domain'] = array('set'		=> false,
				   'chk'		=> 2,
				   'callback'		=> 'dwho_network::valid_host',
				   'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
								  DWHO_NETWORK_HOST_HOSTNAME)),
				   'maxlen'		=> 64);
$array['filter']['allowexternaldomains'] = array('bool' => true);
$array['filter']['usereqphone'] = array('bool' => true);
$array['filter']['realm'] = array('regexp' => '/[^"]/','maxlen' => 64);
$array['filter']['alwaysauthreject'] = array('bool' => true);
$array['filter']['useragent'] = array('cast' => 'sgraph','maxlen' => 80);
$array['filter']['buggymwi'] = array('bool' => true);
$array['filter']['regcontext'] = array('set' => false,'chk' => 2,
				       'callback' => 'xivo_service_asterisk::chk_context',
				       'callbackarg' => array(array(XIVO_SRE_IPBX_AST_CONTEXT_AUTHENTICATION)));
$array['filter']['callerid'] = array('maxlen'	=> 80,
				     'regexp'	=> '/^'.XIVO_SRE_IPBX_AST_REGEXP_CALLERID.'$/u',
				     'notag'	=> false);
$array['filter']['fromdomain'] = array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9_-\.]+$/i','maxlen' => 80);
$array['filter']['sipdebug'] = array('bool' => true);
$array['filter']['dumphistory'] = array('bool' => true);
$array['filter']['recordhistory'] = array('bool' => true);
$array['filter']['callevents'] = array('bool' => true);
$array['filter']['tos_sip'] = array('set' => false,'chk' => 2,'regexp' => '/^(CS[0-7]|AF[1-4][1-3]|EF)$/');
$array['filter']['tos_audio'] = array('set' => false,'chk' => 2,'regexp' => '/^(CS[0-7]|AF[1-4][1-3]|EF)$/');
$array['filter']['tos_video'] = array('set' => false,'chk' => 2,'regexp' => '/^(CS[0-7]|AF[1-4][1-3]|EF)$/');
$array['filter']['t38pt_udptl'] = array('bool' => true);
$array['filter']['t38pt_usertpsource'] = array('bool' => true);
$array['filter']['localnet'] = array('set'		=> false,
				     'chk'		=> 2,
				     'callback'		=> 'dwho_network::valid_host_subnet_ipv4',
				     'callbackarg'	=> array(null,null,DWHO_NETWORK_HOST_IPV4_DOTDEC),
				     'maxlen'		=> 128);
$array['filter']['externip'] = array('set'		=> false,
				     'chk'		=> 2,
				     'callback'		=> 'dwho_network::valid_host',
				     'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
								  DWHO_NETWORK_HOST_HOSTNAME)),
				     'maxlen'		=> 64);
$array['filter']['externhost'] = array('set'		=> false,
				       'chk'		=> 2,
				       'callback'	=> 'dwho_network::valid_host',
				       'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
								  DWHO_NETWORK_HOST_HOSTNAME)),
				       'maxlen'		=> 64);
$array['filter']['externrefresh'] = array('key' => array(1,10,20,30,40,50,60,70,80,90,100,110,120,180,240,300,600,900,1200,1800));
$array['filter']['matchexterniplocally'] = array('bool' => true);
$array['filter']['outboundproxy'] = array('set'		=> false,
					  'chk'		=> 2,
					  'callback'	=> 'dwho_network::valid_host',
					  'callbackarg'	=> array((DWHO_NETWORK_HOST_IPV4_DOTDEC |
								  DWHO_NETWORK_HOST_HOSTNAME)),
					  'maxlen'	=> 64);
$array['filter']['g726nonstandard'] = array('bool' => true);
$array['filter']['disallow'] = array('set' => false,'chk' => 2,'key' => array('all'));
$array['filter']['allow'] = array('set' => false,'chk' => 2,'uvalue' => array(
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_G723,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_GSM,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_ULAW,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_ALAW,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_ADPCM,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_SLIN,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_LPC10,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_G729,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_SPEEX,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_ILBC,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_G726,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_G722,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_G722_1,
						XIVO_SRE_IPBX_AST_CODEC_AUDIO_G722_1C,
						XIVO_SRE_IPBX_AST_CODEC_IMAGE_JPEG,
						XIVO_SRE_IPBX_AST_CODEC_IMAGE_PNG,
						XIVO_SRE_IPBX_AST_CODEC_VIDEO_H261,
						XIVO_SRE_IPBX_AST_CODEC_VIDEO_H263,
						XIVO_SRE_IPBX_AST_CODEC_VIDEO_H263P,
						XIVO_SRE_IPBX_AST_CODEC_VIDEO_H264));
$array['filter']['t1min'] = array('key' => array(0,10,20,30,40,50,60,70,80,90,100,
						 200,300,400,500,600,700,800,900,
						 1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,
						 2000,2500,3000,3500,4000));
$array['filter']['relaxdtmf'] = array('bool' => true);
$array['filter']['rfc2833compensate'] = array('bool' => true);
$array['filter']['compactheaders'] = array('bool' => true);
$array['filter']['rtptimeout'] = array('cast' => 'uint','between' => array(0,60,5));
$array['filter']['rtpholdtimeout'] = array('cast' => 'uint','between' => array(0,60,5));
$array['filter']['rtpkeepalive'] = array('cast' => 'uint','between' => array(0,60,5));
$array['filter']['directrtpsetup'] = array('bool' => true);
$array['filter']['notifymimetype'] = array('set' => false,'chk' => 2,'maxlen' => 80,
					   'regexp' => '#^(?:text|application)/[a-zA-Z][a-zA-Z0-9][a-zA-Z0-9\+][a-zA-Z0-9\-\+\.]*$#');
$array['filter']['srvlookup'] = array('bool' => true);
$array['filter']['pedantic'] = array('bool' => true);
$array['filter']['minexpiry'] = array('key' => array(1,10,20,30,40,50,60,
						     70,80,90,100,110,120,
						     130,140,150,160,170,
						     180,190,200,210,220,230,
						     240,300,600,900,1200,1800,
						     2400,2700,3000,3600,4500,
						     5400,6300,7200));
$array['filter']['maxexpiry'] = array('key' => array(1,10,20,30,40,50,60,
						     70,80,90,100,110,120,
						     130,140,150,160,170,
						     180,190,200,210,220,230,
						     240,300,600,900,1200,1800,
						     2400,2700,3000,3600,4500,
						     5400,6300,7200));
$array['filter']['defaultexpiry'] = array('key' => array(1,10,20,30,40,50,60,
							 70,80,90,100,110,120,
							 130,140,150,160,170,
							 180,190,200,210,220,230,
							 240,300,600,900,1200,1800,
							 2400,2700,3000,3600,4500,
							 5400,6300,7200));
$array['filter']['registertimeout'] = array('cast' => 'uint','between' => array(1,120,10));
$array['filter']['registerattempts'] = array('cast' => 'uint','between' => array(0,200,5));
$array['filter']['notifyringing'] = array('bool' => true);
$array['filter']['notifyhold'] = array('bool' => true);
$array['filter']['allowtransfer'] = array('bool' => true);
$array['filter']['maxcallbitrate'] = array('cast' => 'uint','between' => array(1,1860));
$array['filter']['autoframing'] = array('bool' => true);
$array['filter']['jbenable'] = array('bool' => true);
$array['filter']['jbforce'] = array('bool' => true);
$array['filter']['jbmaxsize'] = array('key' => array(0,100,150,200,250,500,750,1000,1250,1500,1750,2000));
$array['filter']['jbresyncthreshold'] = array('key' => array(-1,0,250,500,750,1000,1250,1500,1750,2000));
$array['filter']['jbimpl'] = array('key' => array('fixed','adaptative'));
$array['filter']['jblog'] = array('bool' => true);
$array['filter']['context'] = array('set' => false,'chk' => 2,
				    'callback' => 'xivo_service_asterisk::chk_context',
				    'callbackarg' => array(array(XIVO_SRE_IPBX_AST_CONTEXT_AUTHENTICATION)));
$array['filter']['nat'] = array('key' => array('no','yes','force_rport','comedia'));
$array['filter']['dtmfmode'] = array('key' => array('rfc2833','inband','info','shortinfo','auto'));
$array['filter']['qualify'] = array('key' => array('no','yes',500,1000,1500,2000,2500,3000,3500,4000));
$array['filter']['useclientcode'] = array('bool' => true);
$array['filter']['progressinband'] = array('key' => array('no','yes','never'));
$array['filter']['language'] = array('key' => array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA'));
$array['filter']['mohinterpret'] = array('set' => false,'chk' => 2,'maxlen' => 20);
$array['filter']['mohsuggest'] = array('set' => false,'chk' => 2,'maxlen' => 20);
$array['filter']['vmexten'] = array('regexp' => '/^[0-9\*]+$/','maxlen' => 40);
$array['filter']['trustrpid'] = array('bool' => true);
$array['filter']['sendrpid'] = array('key' => array('yes','no','rpid','pai'));
$array['filter']['directmedia'] = array('key' => array('no','yes','update','nonat','update,nonat'));
$array['filter']['insecure'] = array('key' => array('no','port','invite','port,invite'));
$array['filter']['rtcachefriends'] = array('bool' => true);
$array['filter']['rtupdate'] = array('bool' => true);
$array['filter']['ignoreregexpire'] = array('bool' => true);
$array['filter']['rtsavesysname'] = array('bool' => true);
$array['filter']['rtautoclear'] = array('key' => array('yes','no',1,10,20,30,40,50,60,70,80,90,
						       100,110,120,130,140,150,160,170,180,
						       190,200,210,220,230,240));
$array['filter']['subscribecontext'] = array('set' => false,'chk' => 0);

$array['filter']['match_auth_username'] = array('bool' => true);
$array['filter']['udpbindaddr'] = array('set' => false,'chk' => 2);
$array['filter']['tcpenable'] = array('bool' => true);
$array['filter']['tcpbindaddr'] = array('set' => false,'chk' => 2);
$array['filter']['tlscertfile'] = array('set' => false,'chk' => 2);
$array['filter']['tlscafile'] = array('set' => false,'chk' => 2);
$array['filter']['tlscadir'] = array('set' => false,'chk' => 2);
$array['filter']['tlsdontverifyserver'] = array('bool' => true);
$array['filter']['tlscipher'] = array('set' => false,'chk' => 2);
$array['filter']['qualifyfreq'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,600,10));
$array['filter']['qualifygap'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,1000,10));
$array['filter']['dynamic_exclude_static'] = array('bool' => true);
$array['filter']['timert1'] = array('cast' => 'uint','between' => array(0,2000,100));
$array['filter']['timerb'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,120000,1000));
$array['filter']['session-expires'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,3600,60));
$array['filter']['session-minse'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,600,10));
$array['filter']['shrinkcallerid'] = array('bool' => true);
$array['filter']['media_address'] = array('set' => false,'chk' => 2,'maxlen' => 20);
$array['filter']['externtcpport'] = array('set' => false,'chk' => 2,'maxlen' => 10);
$array['filter']['externtlsport'] = array('set' => false,'chk' => 2,'maxlen' => 10);
$array['filter']['use_q850_reason'] = array('bool' => true);
$array['filter']['snom_aoc_enabled'] = array('bool' => true);
$array['filter']['subscribe_network_change_event'] = array('bool' => true);
$array['filter']['maxforwards'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(1,255,1));
$array['filter']['disallow_methods'] = array('set' => false,'chk' => 2,'maxlen' => 255);
$array['filter']['domainsasrealm'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['textsupport'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['videosupport'] = array('set' => false, 'chk' => 2, 'key' => array('no','yes','always'));
$array['filter']['auth_options_requests'] = array('bool' => true);


$array['filter']['srtp'] = array('bool' => true);

?>
