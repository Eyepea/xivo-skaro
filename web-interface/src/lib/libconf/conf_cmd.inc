<?php 


$array = array();
$array['userfeatures'] = array();

$array['userfeatures']['ctibus'] = array('xivo[user,%s,%s]',
		'xivo[phone,%s,%s]');
$array['userfeatures']['ipbx'] = array('dialplan reload',
		'module reload app_queue.so',
		'sip reload');


$array['groupfeatures']['ctibus'] = array('xivo[group,%s,%s]');
$array['groupfeatures']['ipbx'] = array('dialplan reload',
		'module reload app_queue.so',
		'sip reload');

$array['linefeatures']['ctibus'] = array('xivo[phone,%s,%s]');
$array['linefeatures']['ipbx'] = array('dialplan reload',
		'sip reload');

$array['meetmefeatures']['ctibus'] = array('xivo[meetme,%s,%s]');
$array['meetmefeatures']['ipbx'] = array('dialplan reload',
		'module reload app_queue.so');

$array['voicemailfeatures']['ctibus'] = array('xivo[voicemail,%s,%s]');
$array['voicemailfeatures']['ipbx'] = array('voicemail reload');

$array['agentfeatures']['ctibus'] = array('xivo[agent,%s,%s]',
		'xivo[user,%s,%s]',
		'xivo[queuemember,update]');
$array['agentfeatures']['ipbx'] = array('module reload app_queue.so',
		'module reload chan_agent.so');

$array['queuefeatures']['ctibus'] = array('xivo[queue,%s,%s]',
		'xivo[queuemember,update]');
$array['queuefeatures']['ipbx'] = array('module reload app_queue.so',
		'dialplan reload',
		'sip reload');

$array['queueskill']['ctibus'] = array();
$array['queueskill']['ipbx'] = array('module reload app_queue.so');

$array['queueskillrule']['ctibus'] = array();
$array['queueskillrule']['ipbx'] = array('module reload app_queue.so');

$array['cti*']['ctibus'] = array('xivo[cticonfig,update]');
$array['cti*']['ipbx'] = array();

$array['ctidirectories']['dird'] = array('update-config');

$array['ctireversedirectories']['dird'] = array('update-config');

$array['incall']['ctibus'] = array();
$array['incall']['ipbx'] = array('dialplan reload');

$array['outcall']['ctibus'] = array();
$array['outcall']['ipbx'] = array('dialplan reload');

$array['voicemenu']['ctibus'] = array();
$array['voicemenu']['ipbx'] = array('dialplan reload');

$array['context']['ctibus'] = array();
$array['context']['ipbx'] = array('dialplan reload');

$array['pickup']['ctibus'] = array();
$array['pickup']['ipbx'] = array('sip reload');

$array['staticsip']['ctibus'] = array();
$array['staticsip']['ipbx'] = array('sip reload');

$array['trunksip']['ctibus'] = array();
$array['trunksip']['ipbx'] = array('dialplan reload',
		'sip reload');

$array['staticiax']['ctibus'] = array();
$array['staticiax']['ipbx'] = array('iax2 reload');

$array['trunkiax']['ctibus'] = array();
$array['trunkiax']['ipbx'] = array('dialplan reload',
		'iax2 reload');

$array['trunkiax']['ctibus'] = array();
$array['trunkiax']['ipbx'] = array('dialplan reload',
		'iax2 reload');

$array['extensions']['ctibus'] = array();
$array['extensions']['ipbx'] = array('dialplan reload',
		'features reload');

$array['extenumbers']['ctibus'] = array();
$array['extenumbers']['ipbx'] = array('dialplan reload',
		'features reload');

$array['musiconhold']['ctibus'] = array();
$array['musiconhold']['ipbx'] = array('moh reload');

$array['parkinglot']['ctibus'] = array();
$array['parkinglot']['ipbx'] = array('features reload');

$array['phonebook']['dird'] = array('update-phonebook');
$array['phonebook']['ctibus'] = array('xivo[phonebook,%s,%s]');
$array['phonebook']['ipbx'] = array();

$array['sccp*']['ctibus'] = array();
$array['sccp*']['ipbx'] = array('sccp update config');

?>