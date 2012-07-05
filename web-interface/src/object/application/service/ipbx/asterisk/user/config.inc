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

$array['picture'] = array();
$array['picture']['file'] = array();
$array['picture']['file']['mime'] = array('image/jpeg','image/png');

$array['import'] = array();
$array['import']['file'] = array();
$array['import']['file']['mime'] = array('text/plain','text/csv');

$array['import']['field'] = array();
$array['import']['field']['entityid'] = array('userfeatures','entityid');
$array['import']['field']['firstname'] = array('userfeatures','firstname');
$array['import']['field']['lastname'] = array('userfeatures','lastname');
$array['import']['field']['language'] = array('userfeatures','language');
$array['import']['field']['outcallerid'] = array('userfeatures','outcallerid');
$array['import']['field']['enableclient'] = array('userfeatures','enableclient');
$array['import']['field']['username'] = array('userfeatures','loginclient');
$array['import']['field']['password'] = array('userfeatures','passwdclient');
$array['import']['field']['profileclient'] = array('userfeatures','profileclient');
$array['import']['field']['enablehint'] = array('userfeatures','enablehint');
$array['import']['field']['agentnumber'] = array('userfeatures','agentnumber');
$array['import']['field']['mobilephonenumber'] = array('userfeatures','mobilephonenumber');
$array['import']['field']['bosssecretary'] = array('userfeatures','bsfilter');

$array['import']['field']['phonenumber'] = array('linefeatures','number',0);
$array['import']['field']['context'] = array('linefeatures','context',0);
$array['import']['field']['callerid'] = array('linefeatures','callerid',0);
$array['import']['field']['protocol'] = array('linefeatures','protocol',0);
$array['import']['field']['linename'] = array('linefeatures','name',0);
$array['import']['field']['linesecret'] = array('linefeatures','secret',0);

$array['import']['field']['voicemailname'] = array('voicemail','fullname');
$array['import']['field']['voicemailmailbox'] = array('voicemail','mailbox');
$array['import']['field']['voicemailpassword'] = array('voicemail','password');
$array['import']['field']['voicemailemail'] = array('voicemail','email');
$array['import']['field']['voicemailattach'] = array('voicemail','attach');
$array['import']['field']['voicemaildelete'] = array('voicemail','deletevoicemail');
$array['import']['field']['voicemailskippass'] = array('voicemailfeatures','skipcheckpass');

$array['import']['field']['incallexten'] = array('incall','exten');
$array['import']['field']['incallcontext'] = array('incall','context');
$array['import']['field']['incallringseconds'] = array('incall','ringseconds');

?>
