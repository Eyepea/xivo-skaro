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

?>
<?php

$array = array();

$array['element'] = array();

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['mailbox'] = array();
$array['element']['mailbox']['default'] = '';

$array['element']['password'] = array();
$array['element']['password']['default'] = '';

$array['element']['fullname'] = array();
$array['element']['fullname']['default'] = '';

$array['element']['email'] = array();
$array['element']['email']['default'] = '';
$array['element']['email']['null'] = true;

$array['element']['pager'] = array();
$array['element']['pager']['default'] = '';
$array['element']['pager']['null'] = true;

$array['element']['dialout'] = array();
$array['element']['dialout']['default'] = '';
$array['element']['dialout']['null'] = true;

$array['element']['callback'] = array();
$array['element']['callback']['default'] = '';
$array['element']['callback']['null'] = true;

$array['element']['exitcontext'] = array();
$array['element']['exitcontext']['default'] = '';
$array['element']['exitcontext']['null'] = true;

$array['element']['tz'] = array();
$array['element']['tz']['default'] = '';
$array['element']['tz']['null'] = true;

$array['element']['language'] = array();
$array['element']['language']['value'] = array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA');
$array['element']['language']['default'] = '';
$array['element']['language']['null'] = true;

$array['element']['attach'] = array();
$array['element']['attach']['value'] = array(1,0);
$array['element']['attach']['default'] = '';
$array['element']['attach']['null'] = true;

$array['element']['saycid'] = array();
$array['element']['saycid']['value'] = array(1,0);
$array['element']['saycid']['default'] = '';
$array['element']['saycid']['null'] = true;

$array['element']['review'] = array();
$array['element']['review']['value'] = array(1,0);
$array['element']['review']['default'] = '';
$array['element']['review']['null'] = true;

$array['element']['operator'] = array();
$array['element']['operator']['value'] = array(1,0);
$array['element']['operator']['default'] = '';
$array['element']['operator']['null'] = true;

$array['element']['envelope'] = array();
$array['element']['envelope']['value'] = array(1,0);
$array['element']['envelope']['default'] = '';
$array['element']['envelope']['null'] = true;

$array['element']['sayduration'] = array();
$array['element']['sayduration']['value'] = array(1,0);
$array['element']['sayduration']['default'] = '';
$array['element']['sayduration']['null'] = true;

$array['element']['saydurationm'] = array();
$array['element']['saydurationm']['value'] = array(1,2,3,4,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['saydurationm']['default'] = '';
$array['element']['saydurationm']['null'] = true;

$array['element']['sendvoicemail'] = array();
$array['element']['sendvoicemail']['value'] = array(1,0);
$array['element']['sendvoicemail']['default'] = '';
$array['element']['sendvoicemail']['null'] = true;

$array['element']['deletevoicemail'] = array();
$array['element']['deletevoicemail']['value'] = array(0,1);
$array['element']['deletevoicemail']['default'] = 0;
$array['element']['deletevoicemail']['set'] = true;

$array['element']['forcename'] = array();
$array['element']['forcename']['value'] = array(1,0);
$array['element']['forcename']['default'] = '';
$array['element']['forcename']['null'] = true;

$array['element']['forcegreetings'] = array();
$array['element']['forcegreetings']['value'] = array(1,0);
$array['element']['forcegreetings']['default'] = '';
$array['element']['forcegreetings']['null'] = true;

$array['element']['hidefromdir'] = array();
$array['element']['hidefromdir']['value'] = array('no','yes');
$array['element']['hidefromdir']['default'] = 'no';
$array['element']['hidefromdir']['set'] = true;

$array['element']['maxmsg'] = array();
$array['element']['maxmsg']['value'] = array(1,10,15,20,25,50,75,100,
					     125,150,175,200,300,400,500,600,700,800,900,
					     1000,2000,3000,4000,5000,6000,7000,8000,9000,9999);
$array['element']['maxmsg']['default'] = '';
$array['element']['maxmsg']['null'] = true;

$array['element']['commented'] = array();
$array['element']['commented']['value'] = array(0,1);
$array['element']['commented']['default'] = 0;
$array['element']['commented']['set'] = true;

$array['element']['option'] = array();
$array['element']['option']['value'] = array('add','search');
$array['element']['option']['default'] = '';
$array['element']['option']['unset'] = true;

// asterisk 1.8 fields
$array['element']['emailsubject'] = array();
$array['element']['emailsubject']['default'] = '';
$array['element']['emailsubject']['null'] = true;

$array['element']['emailbody'] = array();
$array['element']['emailbody']['default'] = '';
$array['element']['emailbody']['null'] = true;

$array['element']['imapuser'] = array();
$array['element']['imapuser']['default'] = '';
$array['element']['imapuser']['null'] = true;

$array['element']['imappassword'] = array();
$array['element']['imappassword']['default'] = '';
$array['element']['imappassword']['null'] = true;

$array['element']['imapfolder'] = array();
$array['element']['imapfolder']['default'] = '';
$array['element']['imapfolder']['null'] = true;

$array['element']['imapvmsharedid'] = array();
$array['element']['imapvmsharedid']['default'] = '';
$array['element']['imapvmsharedid']['null'] = true;

$array['element']['attachfmt'] = array();
$array['element']['attachfmt']['value'] = array(
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_WAV49,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_GSM,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_OGG,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_ULAW,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_ALAW,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_AU,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_VOX,
					XIVO_SRE_IPBX_AST_FORMAT_AUDIO_SLIN);
$array['element']['attachfmt']['default'] = '';
$array['element']['attachfmt']['null'] = true;

$array['element']['serveremail'] = array();
$array['element']['serveremail']['default'] = '';
$array['element']['serveremail']['null'] = true;

$array['element']['locale'] = array();
$array['element']['locale']['value'] = array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA');
$array['element']['locale']['default'] = '';
$array['element']['locale']['null'] = true;

$array['element']['tempgreetwarn'] = array();
$array['element']['tempgreetwarn']['value'] = array(0,1);
$array['element']['tempgreetwarn']['default'] = '';
$array['element']['tempgreetwarn']['null']    = true;

$array['element']['messagewrap'] = array();
$array['element']['messagewrap']['value'] = array(0,1);
$array['element']['messagewrap']['default'] = 'false';
$array['element']['messagewrap']['null'] = true;

$array['element']['moveheard'] = array();
$array['element']['moveheard']['value'] = array(0,1);
$array['element']['moveheard']['default'] = 'false';
$array['element']['moveheard']['null'] = true;

$array['element']['minsecs'] = array();
$array['element']['minsecs']['value'] = array(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60);
$array['element']['minsecs']['default'] = '';
$array['element']['minsecs']['null'] = true;

$array['element']['maxsecs'] = array();
$array['element']['maxsecs']['value'] = array(30,60,90,120,150,180,210,240,270,300,330,360,390,420,450,480,510,540,570,600);
$array['element']['maxsecs']['default'] = '';
$array['element']['maxsecs']['null'] = true;

$array['element']['nextaftercmd'] = array();
$array['element']['nextaftercmd']['value'] = array(0,1);
$array['element']['nextaftercmd']['default'] = 'false';
$array['element']['nextaftercmd']['null'] = true;

$array['element']['backupdeleted'] = array();
$array['element']['backupdeleted']['value'] = range(0,100,1);
$array['element']['backupdeleted']['default'] = '';
$array['element']['backupdeleted']['null'] = true;

$array['element']['volgain'] = array();
$array['element']['volgain']['value'] = array(-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5);
$array['element']['volgain']['default'] = '';
$array['element']['volgain']['null'] = true;


$array['element']['passwordlocation'] = array();
$array['element']['passwordlocation']['value'] = array('spooldir','voicemail');
$array['element']['passwordlocation']['default'] = '';
$array['element']['passwordlocation']['null'] = true;

dwho::load_class('dwho_network');

$array['filter'] = array();
$array['filter']['context'] = array('callback' => 'xivo_service_asterisk::chk_context',
				    'callbackarg' => array(array(XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['mailbox'] = array('minlen' => 1,'maxlen' => 40,'regexp' => '/^[0-9#\*]+$/');
$array['filter']['password'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9#\*]+$/','maxlen' => 80);
$array['filter']['fullname'] = array('cast' => 'sgraph','maxlen' => 80);
$array['filter']['email'] = array('set' => false,'chk' => 2,'maxlen' => 80,'callback' => 'dwho_network::valid_email');
$array['filter']['pager'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9#\*]+$/','maxlen' => 80);
$array['filter']['dialout'] = array('set' => false,
				    'chk' => 2,
				    'callback' => 'xivo_service_asterisk::chk_context',
				    'callbackarg' => array(array(XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['callback'] = array('set' => false,
				     'chk' => 2,
				     'callback' => 'xivo_service_asterisk::chk_context',
				     'callbackarg' => array(array(XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['exitcontext'] = array('set' => false,
				     'chk' => 2,
				     'callback' => 'xivo_service_asterisk::chk_context',
				     'callbackarg' => array(array(XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['tz'] = array('set' => false,'chk' => 2,'minlen' => 1,'maxlen' => 80,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['language'] = array('set' => false,'chk' => 2,'minlen' => 5,'maxlen' => 5,'key' => array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA'));
$array['filter']['attach'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['saycid'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['review'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['operator'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['envelope'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['sayduration'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['saydurationm'] = array('set' => false,'chk' => 2,'key' => array(1,2,3,4,5,10,15,20,25,30,35,40,45,50,55,60));
$array['filter']['sendvoicemail'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['deletevoicemail'] = array('bool' => true);
$array['filter']['forcename'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['forcegreetings'] = array('set' => false,'chk' => 2,'bool' => true);
$array['filter']['hidefromdir'] = array('bool' => true);
$array['filter']['maxmsg'] = array('set' => false,'chk' => 2,
				   'key' => array(1,10,15,20,25,50,75,100,
						  125,150,175,200,300,400,500,600,700,800,900,
						  1000,2000,3000,4000,5000,6000,7000,8000,9000,9999));
$array['filter']['commented'] = array('bool' => true);
$array['filter']['emailsubject'] = array('set' => false,'chk' => 2,'maxlen' => 4096);
$array['filter']['emailbody'] = array('set' => false,'chk' => 2);
$array['filter']['imapuser'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['imappassword'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['imapfolder'] = array('set' => false,'chk' => 2,'maxlen' => 64);
$array['filter']['imapvmsharedid'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['attachfmt'] = array('set' => false,'chk' => 2,'maxlen' => 20);
$array['filter']['serveremail'] = array('set' => false,'chk' => 2,'maxlen' => 80);
$array['filter']['locale'] = array('chk' => 2,
  'key' => array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA'));
$array['filter']['tempgreetwarn'] = array('set' => false, 'chk' => 2, 'bool' => true);

$array['filter']['messagewrap'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['moveheard'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['minsecs'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(1,60,1));
$array['filter']['maxsecs'] = array('set' => false, 'chk' => 2, 'between' => array(1,600,30));
$array['filter']['nextaftercmd'] = array('set' => false, 'chk' => 2, 'bool' => true);
$array['filter']['backupdeleted'] = array('set' => false, 'chk' => 2, 'cast' => 'uint','between' => array(0,100,1));
$array['filter']['volgain'] = array('set' => false, 'chk' => 2, 'cast' => 'float', 'key' => array(-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5));
$array['filter']['passwordlocation'] = array('set' => false, 'chk' => 2, 'key' => array('spooldir','voicemail'));

?>
