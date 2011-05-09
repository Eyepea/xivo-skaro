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

$array['provisioning_id'] = array();

$array['provisioning_id']['sip'] = array();
$array['provisioning_id']['sip']['prefix'] = 1;
$array['provisioning_id']['sip']['range'] = 100000;

$array['provisioning_id']['iax'] = array();
$array['provisioning_id']['iax']['prefix'] = 2;
$array['provisioning_id']['iax']['range'] = 100000;

$array['provisioning_id']['sccp'] = array();
$array['provisioning_id']['sccp']['prefix'] = 3;
$array['provisioning_id']['sccp']['range']  = 100000;

$array['element'] = array();

$array['element']['protocol'] = array();
$array['element']['protocol']['value'] = array(XIVO_SRE_IPBX_AST_PROTO_SIP,
					       XIVO_SRE_IPBX_AST_PROTO_IAX,
					       XIVO_SRE_IPBX_AST_PROTO_SCCP,
					       XIVO_SRE_IPBX_AST_PROTO_CUSTOM);
$array['element']['protocol']['default'] = XIVO_SRE_IPBX_AST_PROTO_SIP;

$array['element']['protocolid'] = array();
$array['element']['protocolid']['default'] = 0;

$array['element']['iduserfeatures'] = array();
$array['element']['iduserfeatures']['default'] = 0;

$array['element']['name'] = array();
$array['element']['name']['default'] = '';

$array['element']['context'] = array();
$array['element']['context']['default'] = 'default';

$array['element']['number'] = array();
$array['element']['number']['default'] = '';

$array['element']['config'] = array();
$array['element']['config']['default'] = '';

$array['element']['configregistrar'] = array();
$array['element']['configregistrar']['default'] = '';

$array['element']['device'] = array();
$array['element']['device']['default'] = '';

$array['element']['rules_type'] = array();
$array['element']['rules_type']['value'] = array('simul');
$array['element']['rules_type']['empty'] = true;
$array['element']['rules_type']['default'] = '';

$array['element']['rules_time'] = array();
$array['element']['rules_time']['default'] = '';

$array['element']['rules_order'] = array();
$array['element']['rules_order']['default'] = 0;

$array['element']['rules_group'] = array();
$array['element']['rules_group']['default'] = '';

$array['element']['num'] = array();
$array['element']['num']['value'] = array(1,2,3,4,5,6,7,8,9,10,11,12);
$array['element']['num']['default'] = 1;

$array['element']['line_num'] = array();
$array['element']['line_num']['default'] = 0;

$array['element']['internal'] = array();
$array['element']['internal']['value'] = array(0,1);
$array['element']['internal']['default'] = 0;
$array['element']['internal']['forcedef'] = true;

$array['element']['description'] = array();
$array['element']['description']['default'] = '';


$array['filter'] = array();
$array['filter']['protocol'] = array('key' => array(XIVO_SRE_IPBX_AST_PROTO_SIP,
						    XIVO_SRE_IPBX_AST_PROTO_IAX,
						    XIVO_SRE_IPBX_AST_PROTO_SCCP,
						    XIVO_SRE_IPBX_AST_PROTO_CUSTOM));
$array['filter']['protocolid'] = array('cast' => 'ulongint');
$array['filter']['iduserfeatures'] = array('set' => false,'cast' => 'ulongint');
$array['filter']['num'] = array('set' => false,'chk' => 2,'cast' => 'ulongint');
$array['filter']['line_num'] = array('set' => false,'chk' => 2,'cast' => 'ulongint');
$array['filter']['name'] = array('minlen' => 1,'maxlen' => 128,'regexp' => '/^[a-z0-9#\*\.\/_@:-]+$/i');
$array['filter']['config'] = array('set' => false,'chk' => 2,'maxlen' => 128,'regexp' => '/^[a-z0-9#\*\.\/_@:-]+$/i');
$array['filter']['configregistrar'] = array('set' => false,'chk' => 2,'maxlen' => 128,'regexp' => '/^[a-z0-9#\*\.\/_@:-]+$/i');
$array['filter']['device'] =  array('set' => false,'chk' => 2,'regexp' => '/^[a-z0-9]+$/','maxlen' => 32);
$array['filter']['context'] = array('callback' => 'xivo_service_asterisk::chk_context',
				    'callbackarg' => array(array(
							XIVO_SRE_IPBX_AST_CONTEXT_AUTHENTICATION,
							XIVO_SRE_IPBX_AST_CONTEXT_ZONEMESSAGES)));
$array['filter']['number'] = array('set' => false,'chk' => 2,'regexp' => '/^[0-9\*#]+$/','maxlen' => 40);
$array['filter']['rules_type'] = array('set' => false,'chk' => 2,'maxlen' => 40,'regexp' => '/^[a-z0-9_-]+$/i');
$array['filter']['rules_time'] = array('set' => false,'chk' => 2,'maxlen' => 8,'regexp' => '/^[0-9]+$/');
$array['filter']['rules_order'] = array('set' => false,'chk' => 2,'cast' => 'ulongint');
$array['filter']['rules_group'] =array('set' => false,'chk' => 2,'maxlen' => 16,'regexp' => '/^[a-z0-9_\.-]+$/i');
$array['filter']['internal'] = array('set' => false,'chk' => 0);
$array['filter']['description'] = array('set' => false,'chk' => 2,'maxlen' => 1000,'cast' => 'sgraph_crlf_tab','eol' => true);

?>
