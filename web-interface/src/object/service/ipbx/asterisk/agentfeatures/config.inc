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

$array['element']['agentid'] = array();
$array['element']['agentid']['default'] = '';

$array['element']['numgroup'] = array();
$array['element']['numgroup']['default'] = '';

$array['element']['firstname'] = array();
$array['element']['firstname']['default'] = '';

$array['element']['lastname'] = array();
$array['element']['lastname']['default'] = '';

$array['element']['number'] = array();
$array['element']['number']['default'] = '';

$array['element']['passwd'] = array();
$array['element']['passwd']['default'] = '';

$array['element']['context'] = array();
$array['element']['context']['default'] = '';

$array['element']['language'] = array();
$array['element']['language']['value'] = array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA');
$array['element']['language']['default'] = '';

$array['element']['silent'] = array();
$array['element']['silent']['value'] = array(0,1);
$array['element']['silent']['default'] = 0;
$array['element']['silent']['set'] = true;

$array['element']['autologoff'] = array();
$array['element']['autologoff']['value'] = array(0,5,10,15,20,25,30,35,40,45,50,55,60);
$array['element']['autologoff']['default'] = 0;
$array['element']['autologoff']['setdef'] = true;

$array['element']['ackcall'] = array();
$array['element']['ackcall']['value'] = array('no','yes','always');
$array['element']['ackcall']['default'] = 'no';

$array['element']['acceptdtmf'] = array();
$array['element']['acceptdtmf']['value'] = array('0','1','2','3','4','5','6','7','8','9','*','#');
$array['element']['acceptdtmf']['default'] = '#';
$array['element']['acceptdtmf']['null'] = true;

$array['element']['enddtmf'] = array();
$array['element']['enddtmf']['value'] = array('0','1','2','3','4','5','6','7','8','9','*','#');
$array['element']['enddtmf']['default'] = '*';
$array['element']['enddtmf']['null'] = true;

$array['element']['wrapuptime'] = array();
$array['element']['wrapuptime']['value'] = array(0,5000,10000,15000,20000,
						 25000,30000,35000,40000,
						 45000,50000,55000,60000);
$array['element']['wrapuptime']['default'] = 0;
$array['element']['wrapuptime']['setdef'] = true;

$array['element']['musiconhold'] = array();
$array['element']['musiconhold']['default'] = XIVO_SRE_IPBX_AST_MOH_DEFAULT;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';

$array['filter'] = array();
$array['filter']['agentid'] = array('cast' => 'ulongint');
$array['filter']['numgroup'] = array('cast' => 'uint','between' => array(1,63));
$array['filter']['number'] = array('regexp' => '/^[0-9\*#]+$/','minlen' => 1,'maxlen' => 40);
$array['filter']['passwd'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9\*#]+$/','minlen' => 1,'maxlen' => 40);
$array['filter']['firstname'] = array('set' => false,'chk' => 2,'maxlen' => 128,'cast' => 'sgraph');
$array['filter']['lastname'] = array('set' => false,'chk' => 2,'maxlen' => 128,'cast' => 'sgraph');
$array['filter']['context'] = array('callback' => 'xivo_service_asterisk::chk_context');
$array['filter']['language'] = array('set' => false,'chk' => 2,'maxlen' => 5,'key' => array('de_DE', 'en_US', 'es_ES', 'fr_FR', 'fr_CA'));
$array['filter']['silent'] = array('bool' => true);
$array['filter']['autologoff'] = array('cast' => 'uint','between' => array(0,60,5));
$array['filter']['ackcall'] = array('key' => array('no','yes','always'));
$array['filter']['acceptdtmf'] = array('set' => false,
					'chk'    => 2,
					'key'    => array('0','1','2','3','4','5','6','7','8','9','*','#'));
$array['filter']['enddtmf'] = array('set' => false,
					'chk'    => 2,
					'key'    => array('0','1','2','3','4','5','6','7','8','9','*','#'));
$array['filter']['wrapuptime'] = array('key' => array(0,5000,10000,15000,20000,
						      25000,30000,35000,40000,
						      45000,50000,55000,60000));
$array['filter']['musiconhold'] = array('set' => false,'chk' => 2,'maxlen' => 20);
$array['filter']['description'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);

?>
