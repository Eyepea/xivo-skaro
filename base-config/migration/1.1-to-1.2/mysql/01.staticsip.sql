
-- deletions
DELETE FROM `staticsip` WHERE `var_name` IN (
	'assertedidentity',
	'canreinvite',
	'checkmwi',
	'limitonpeer',
	'outboundproxyport',
	't38pt_rtp',
	't38pt_tcp'
);
-- changes
UPDATE `staticsip` SET `var_name` = 'udpbinaddr'  WHERE `var_name` = 'bindaddr';
UPDATE `staticsip` SET `var_name` = 'directmedia' WHERE `var_name` = 'canreinvite';

-- new fields
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','match_auth_username',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tcpenable','no');
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tcpbindaddr','0.0.0.0');
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlsenable','no');
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlsbindaddr',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlscertfile',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlscafile',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlscadir',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlsdontverifyserver',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tlscipher',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','tos_text',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','cos_sip',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','cos_audio',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','cos_video',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','cos_text',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','mwiexpiry',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','qualifyfreq',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','qualifygap',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','qualifypeers',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','parkinglot',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','permaturemedia',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','sdpsession',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','sdpowner',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','authfailureevents',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','dynamic_exclude_static',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','contactdeny',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','contactpermit',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','shrinkcallerid',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','regextenonqualify',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','timer1',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','timerb',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','session-timers',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','session-expires',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','session-minse',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','session-refresher',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','hash_users',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','hash_peers',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','notifycid',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','callcounter',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','faxdetect','no');
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','stunaddr',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','ignoresdpversion',NULL);
INSERT INTO `staticsip` VALUES (NULL,0,0,0,'sip.conf','general','jbtargetextra',NULL);


