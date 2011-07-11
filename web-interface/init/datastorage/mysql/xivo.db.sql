/*
 * XiVO Web-Interface
 * Copyright (C) 2006-2011  Proformatique <technique@proformatique.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

START TRANSACTION;

GRANT ALL PRIVILEGES ON `xivo`.* TO `xivo`@`localhost` IDENTIFIED BY PASSWORD '*DBA86DFECE903EB25FE460A66BDCDA790A1CA4A4';
CREATE DATABASE IF NOT EXISTS `xivo` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

USE `xivo`;

DROP TABLE IF EXISTS `accesswebservice`;
CREATE TABLE `accesswebservice` (
 `id` int(10) unsigned auto_increment,
 `name` varchar(64) NOT NULL DEFAULT '',
 `login` varchar(64),
 `passwd` varchar(64),
 `host` varchar(255),
 `obj` longblob NOT NULL,
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `accesswebservice__idx__login` ON `accesswebservice`(`login`);
CREATE INDEX `accesswebservice__idx__passwd` ON `accesswebservice`(`passwd`);
CREATE INDEX `accesswebservice__idx__host` ON `accesswebservice`(`host`);
CREATE INDEX `accesswebservice__idx__disable` ON `accesswebservice`(`disable`);
CREATE UNIQUE INDEX `accesswebservice__uidx__name` ON `accesswebservice`(`name`);


DROP TABLE IF EXISTS `directories`;
CREATE TABLE `directories` (
 `id` int(10) unsigned auto_increment,
 `uri` varchar(255),
 `dirtype` varchar(20),
 `name` varchar(255),
 `tablename` varchar(255),
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `directories` VALUES (1,'internal' , NULL, 'internal' , '', 'XiVO internal users');
INSERT INTO `directories` VALUES (2,'phonebook', NULL, 'phonebook', '', 'XiVO phonebook');


DROP TABLE IF EXISTS `entity`;
CREATE TABLE `entity` (
 `id` int(10) unsigned auto_increment,
 `name` varchar(64) NOT NULL DEFAULT '',
 `displayname` varchar(128) NOT NULL DEFAULT '',
 `phonenumber` varchar(40) NOT NULL DEFAULT '',
 `faxnumber` varchar(40) NOT NULL DEFAULT '',
 `email` varchar(255) NOT NULL DEFAULT '',
 `url` varchar(255) NOT NULL DEFAULT '',
 `address1` varchar(30) NOT NULL DEFAULT '',
 `address2` varchar(30) NOT NULL DEFAULT '',
 `city` varchar(128) NOT NULL DEFAULT '',
 `state` varchar(128) NOT NULL DEFAULT '',
 `zipcode` varchar(16) NOT NULL DEFAULT '',
 `country` varchar(3) NOT NULL DEFAULT '',
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `entity__idx__displayname` ON `entity`(`displayname`);
CREATE INDEX `entity__idx__disable` ON `entity`(`disable`);
CREATE UNIQUE INDEX `entity__uidx__name` ON `entity`(`name`);


DROP TABLE IF EXISTS `i18ncache`;
CREATE TABLE `i18ncache` (
 `locale` varchar(7) NOT NULL DEFAULT '',
 `path` varchar(255) NOT NULL DEFAULT '',
 `language` varchar(3) NOT NULL DEFAULT '',
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `dupdate` int(10) unsigned NOT NULL DEFAULT 0,
 `obj` longblob NOT NULL,
 PRIMARY KEY(`locale`,`path`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `i18ncache__idx__language` ON `i18ncache`(`language`);
CREATE INDEX `i18ncache__idx__dupdate` ON `i18ncache`(`dupdate`);


DROP TABLE IF EXISTS `iproute`;
CREATE TABLE `iproute` (
 `id` int(10) unsigned auto_increment,
 `name` varchar(64) NOT NULL DEFAULT '',
 `iface` varchar(64) NOT NULL DEFAULT '',
 `destination` varchar(39) NOT NULL,
 `netmask` varchar(39) NOT NULL,
 `gateway` varchar(39) NOT NULL,
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `iproute__idx__iface` ON `iproute`(`iface`);
CREATE UNIQUE INDEX `iproute__uidx__name` ON `iproute`(`name`);
CREATE UNIQUE INDEX `iproute__uidx__destination_netmask_gateway` ON `iproute`(`destination`,`netmask`,`gateway`);


DROP TABLE IF EXISTS `ldapserver`;
CREATE TABLE `ldapserver` (
 `id` int(10) unsigned auto_increment,
 `name` varchar(64) NOT NULL DEFAULT '',
 `host` varchar(255) NOT NULL DEFAULT '',
 `port` smallint unsigned NOT NULL,
 `securitylayer` enum('tls','ssl'),
 `protocolversion` enum('2','3') NOT NULL DEFAULT '3',
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `ldapserver__idx__host` ON `ldapserver`(`host`);
CREATE INDEX `ldapserver__idx__port` ON `ldapserver`(`port`);
CREATE INDEX `ldapserver__idx__disable` ON `ldapserver`(`disable`);
CREATE UNIQUE INDEX `ldapserver__uidx__name` ON `ldapserver`(`name`);
CREATE UNIQUE INDEX `ldapserver__uidx__host_port` ON `ldapserver`(`host`,`port`);


DROP TABLE IF EXISTS `netiface`;
CREATE TABLE `netiface` (
 `name` varchar(64) NOT NULL DEFAULT '',
 `ifname` varchar(64) NOT NULL DEFAULT '',
 `hwtypeid` smallint unsigned NOT NULL DEFAULT 65534,
 `networktype` enum('data','voip') NOT NULL,
 `type` enum('iface') NOT NULL,
 `family` enum('inet','inet6') NOT NULL,
 `method` enum('static','dhcp') NOT NULL,
 `address` varchar(39),
 `netmask` varchar(39),
 `broadcast` varchar(15),
 `gateway` varchar(39),
 `mtu` smallint(4) unsigned,
 `vlanrawdevice` varchar(64),
 `vlanid` smallint(4) unsigned,
 `options` text NOT NULL,
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `netiface__idx__hwtypeid` ON `netiface`(`hwtypeid`);
CREATE INDEX `netiface__idx__networktype` ON `netiface`(`networktype`);
CREATE INDEX `netiface__idx__type` ON `netiface`(`type`);
CREATE INDEX `netiface__idx__family` ON `netiface`(`family`);
CREATE INDEX `netiface__idx__method` ON `netiface`(`method`);
CREATE INDEX `netiface__idx__address` ON `netiface`(`address`);
CREATE INDEX `netiface__idx__netmask` ON `netiface`(`netmask`);
CREATE INDEX `netiface__idx__broadcast` ON `netiface`(`broadcast`);
CREATE INDEX `netiface__idx__gateway` ON `netiface`(`gateway`);
CREATE INDEX `netiface__idx__mtu` ON `netiface`(`mtu`);
CREATE INDEX `netiface__idx__vlanrawdevice` ON `netiface`(`vlanrawdevice`);
CREATE INDEX `netiface__idx__vlanid` ON `netiface`(`vlanid`);
CREATE INDEX `netiface__idx__disable` ON `netiface`(`disable`);
CREATE UNIQUE INDEX `netiface__uidx__ifname` ON `netiface`(`ifname`);


DROP TABLE IF EXISTS `resolvconf`;
CREATE TABLE `resolvconf` (
 `id` tinyint(1) auto_increment,
 `hostname` varchar(63) NOT NULL DEFAULT 'xivo',
 `domain` varchar(255) NOT NULL DEFAULT '',
 `nameserver1` varchar(255),
 `nameserver2` varchar(255),
 `nameserver3` varchar(255),
 `search` varchar(255),
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `resolvconf__uidx__hostname` ON `resolvconf`(`hostname`);
INSERT INTO `resolvconf` VALUES(1, '', '', NULL, NULL, NULL, NULL, '');


DROP TABLE IF EXISTS `server`;
CREATE TABLE `server` (
 `id` int(10) unsigned auto_increment,
 `name` varchar(64) NOT NULL DEFAULT '',
 `host` varchar(255) NOT NULL DEFAULT '',
 `ws_login` varchar(64) NOT NULL DEFAULT '',
 `ws_pass` varchar(64) NOT NULL DEFAULT '',
 `ws_port` smallint unsigned NOT NULL,
 `ws_ssl` tinyint(1) NOT NULL DEFAULT 0,
 `cti_login` varchar(64) NOT NULL DEFAULT '',
 `cti_pass` varchar(64) NOT NULL DEFAULT '',
 `cti_port` smallint unsigned NOT NULL,
 `cti_ssl` tinyint(1) NOT NULL DEFAULT 0,
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `server__idx__host` ON `server`(`host`);
CREATE INDEX `server__idx__disable` ON `server`(`disable`);
CREATE UNIQUE INDEX `server__uidx__name` ON `server`(`name`);
CREATE UNIQUE INDEX `server__uidx__host_wsport` ON `server`(`host`,`ws_port`);
CREATE UNIQUE INDEX `server__uidx__host_ctiport` ON `server`(`host`,`cti_port`);


DROP TABLE IF EXISTS `session`;
CREATE TABLE `session` (
 `sessid` char(32) binary NOT NULL,
 `start` int(10) unsigned NOT NULL,
 `expire` int(10) unsigned NOT NULL,
 `identifier` varchar(255) NOT NULL,
 `data` longblob NOT NULL,
 PRIMARY KEY(`sessid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `session__idx__expire` ON `session`(`expire`);
CREATE INDEX `session__idx__identifier` ON `session`(`identifier`);


DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
 `id` int(10) unsigned auto_increment,
 `login` varchar(64) NOT NULL DEFAULT '',
 `passwd` varchar(64) NOT NULL DEFAULT '',
 `meta` enum('user','admin','root') NOT NULL DEFAULT 'user',
 `valid` tinyint(1) NOT NULL DEFAULT 1,
 `time` int(10) unsigned NOT NULL DEFAULT 0,
 `dcreate` int(10) unsigned NOT NULL DEFAULT 0,
 `dupdate` int(10) unsigned NOT NULL DEFAULT 0,
 `obj` longblob NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `user__idx__login` ON `user`(`login`);
CREATE INDEX `user__idx__passwd` ON `user`(`passwd`);
CREATE INDEX `user__idx__meta` ON `user`(`meta`);
CREATE INDEX `user__idx__valid` ON `user`(`valid`);
CREATE INDEX `user__idx__time` ON `user`(`time`);
CREATE UNIQUE INDEX `user__uidx__login_meta` ON `user`(`login`,`meta`);

INSERT INTO `user` VALUES (1,'root','proformatique','root',1,0,UNIX_TIMESTAMP(UTC_TIMESTAMP()),0,'');


DROP TABLE IF EXISTS `dhcp`;
CREATE TABLE `dhcp` (
 `id` int(10) unsigned auto_increment,
 `active` int(1) unsigned NOT NULL DEFAULT 0,
 `pool_start` varchar(64) NOT NULL DEFAULT '',
 `pool_end` varchar(64) NOT NULL DEFAULT '',
 `extra_ifaces` varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `dhcp` VALUES (1,0,'','','');


DROP TABLE IF EXISTS `mail`;
CREATE TABLE `mail` (
 `id` int(10) unsigned auto_increment,
 `mydomain` varchar(255) NOT NULL DEFAULT 0,
 `origin` varchar(255) NOT NULL DEFAULT 'xivo-clients.proformatique.com',
 `relayhost` varchar(255),
 `fallback_relayhost` varchar(255),
 `canonical` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `mail__uidx__origin` ON `mail`(`origin`);

INSERT INTO `mail` VALUES (1,'','xivo-clients.proformatique.com','','','');


DROP TABLE IF EXISTS `monitoring`;
CREATE TABLE `monitoring` (
 `id` int(10) unsigned auto_increment,
 `maintenance` int(1) unsigned NOT NULL DEFAULT 0,
 `alert_emails` varchar(4096) DEFAULT NULL,
 `dahdi_monitor_ports` varchar(255) DEFAULT NULL,
 `max_call_duration` int(5) DEFAULT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO monitoring VALUES (1,0,NULL,NULL,NULL);


-- HA
DROP TABLE IF EXISTS `ha`;
CREATE TABLE `ha` (
 `id`          INT(10) unsigned auto_increment,
 `netaddr`     VARCHAR(255) DEFAULT NULL,
 `netmask`     VARCHAR(255) DEFAULT NULL,
 `mcast`       VARCHAR(255) DEFAULT NULL,

 -- node 1
 `node1_ip`    VARCHAR(255) DEFAULT NULL,
 `node1_name`  VARCHAR(255) DEFAULT NULL,
 -- node 2
 `node2_ip`    VARCHAR(255) DEFAULT NULL,
 `node2_name`  VARCHAR(255) DEFAULT NULL,

 -- cluster
 `cluster_name`  VARCHAR(255) DEFAULT NULL,
 `cluster_group` INTEGER NOT NULL DEFAULT 1,
 `cluster_itf_data` VARCHAR(255) DEFAULT NULL,
 `cluster_monitor` INTEGER NOT NULL DEFAULT 20,
 `cluster_timeout` INTEGER NOT NULL DEFAULT 60,
 `cluster_mailto`  VARCHAR(255) DEFAULT NULL,
 `cluster_pingd`   VARCHAR(255) DEFAULT NULL,

 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `ha` VALUES (1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,20,60,NULL,NULL);


DROP TABLE IF EXISTS `ha_cluster_node`;
CREATE TABLE `ha_cluster_node` (
 -- primary key must not exceed 1000 butes
 -- 1 utf8 char == 3 bytes
 `device`  VARCHAR(128) NOT NULL DEFAULT '',
 `address` VARCHAR(128) NOT NULL DEFAULT '',
 PRIMARY KEY (`device`, `address`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `ha_service`;
CREATE TABLE `ha_service` (
 `name`      VARCHAR(128) NOT NULL,
 `active`    INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 `rsc_class` VARCHAR(8) DEFAULT NULL,  -- 'lsb' or 'ocf'
 `monitor`   INTEGER DEFAULT NULL,
 `timeout`   INTEGER DEFAULT NULL,
 PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `ha_service` VALUES ('asterisk'           , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('nginx'              , 0, 'ocf', NULL, NULL);
INSERT INTO `ha_service` VALUES ('isc-dhcp-server'    , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('ntp'                , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('csync2'             , 0, 'ocf', NULL, NULL);
INSERT INTO `ha_service` VALUES ('postgresql'         , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-agid'       , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-confgend'   , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-cti-server' , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-dxtora'     , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-provd'      , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-sysconfd'   , 0, 'lsb', NULL, NULL);
INSERT INTO `ha_service` VALUES ('pf-xivo-ha-scripts' , 0, 'lsb', NULL, NULL);


DROP TABLE IF EXISTS `provisioning`;
CREATE TABLE `provisioning` (
 `id` int(10) unsigned auto_increment,
 `net4_ip` varchar(39) NOT NULL,
 `net4_ip_rest` varchar(39) NOT NULL,
 `username` varchar(32) NOT NULL,
 `password` varchar(32) NOT NULL,
 `dhcp_integration` INTEGER NOT NULL DEFAULT 0,
 `rest_port` integer NOT NULL,
 `http_port` integer NOT NULL,
 `private` INTEGER NOT NULL DEFAULT 0,
 `secure` INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `provisioning` VALUES(1, '', '127.0.0.1', 'admin', 'admin', 0, 8666, 8667, 0, 0);


DROP TABLE IF EXISTS `stats_conf`;
CREATE TABLE `stats_conf` (
 `id` int(10) unsigned auto_increment,
 `name` varchar(64) NOT NULL DEFAULT '',
 `hour_start` time NOT NULL,
 `hour_end` time NOT NULL,
 `homepage` integer,
 `default_delta` varchar(16) NOT NULL DEFAULT 0,
 `monday` tinyint(1) NOT NULL DEFAULT 0,
 `tuesday` tinyint(1) NOT NULL DEFAULT 0,
 `wednesday` tinyint(1) NOT NULL DEFAULT 0,
 `thursday` tinyint(1) NOT NULL DEFAULT 0,
 `friday` tinyint(1) NOT NULL DEFAULT 0,
 `saturday` tinyint(1) NOT NULL DEFAULT 0,
 `sunday` tinyint(1) NOT NULL DEFAULT 0,
 `period1` varchar(16) NOT NULL DEFAULT 0,
 `period2` varchar(16) NOT NULL DEFAULT 0,
 `period3` varchar(16) NOT NULL DEFAULT 0,
 `period4` varchar(16) NOT NULL DEFAULT 0,
 `period5` varchar(16) NOT NULL DEFAULT 0,
 `dbegcache` int(10) unsigned, 
 `dendcache` int(10) unsigned, 
 `dgenercache` int(10) unsigned, 
 `dcreate` int(10) unsigned, 
 `dupdate` int(10) unsigned, 
 `disable` tinyint(1) NOT NULL DEFAULT 0,
 `description` text NOT NULL,
 PRIMARY KEY(`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE INDEX `stats_conf__idx__disable` ON `stats_conf`(`disable`);
CREATE UNIQUE INDEX `stats_conf__uidx__name` ON `stats_conf`(`name`);


DROP TABLE IF EXISTS `stats_conf_agent`;
CREATE TABLE `stats_conf_agent` (
    `stats_conf_id` int(10) NOT NULL,
    `agentfeatures_id` int(10) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `stats_conf_agent_index` ON `stats_conf_agent`(`stats_conf_id`,`agentfeatures_id`);


DROP TABLE IF EXISTS `stats_conf_user`;
CREATE TABLE `stats_conf_user` (
    `stats_conf_id` int(10) NOT NULL,
    `userfeatures_id` int(10) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `stats_conf_user_index` ON `stats_conf_user`(`stats_conf_id`,`userfeatures_id`);


DROP TABLE IF EXISTS `stats_conf_incall`;
CREATE TABLE `stats_conf_incall` (
    `stats_conf_id` int(10) NOT NULL,
    `incall_id` int(10) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `stats_conf_incall_index` ON `stats_conf_incall`(`stats_conf_id`,`incall_id`);


DROP TABLE IF EXISTS `stats_conf_queue`;
CREATE TABLE `stats_conf_queue` (
    `stats_conf_id` int(10) NOT NULL,
    `queuefeatures_id` int(10) NOT NULL,
    `qos` smallint(4) NOT NULL DEFAULT 0
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `stats_conf_queue_index` ON `stats_conf_queue`(`stats_conf_id`,`queuefeatures_id`);


DROP TABLE IF EXISTS `stats_conf_group`;
CREATE TABLE `stats_conf_group` (
    `stats_conf_id` int(10) NOT NULL,
    `groupfeatures_id` int(10) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE UNIQUE INDEX `stats_conf_group_index` ON `stats_conf_group`(`stats_conf_id`,`groupfeatures_id`);

COMMIT;
