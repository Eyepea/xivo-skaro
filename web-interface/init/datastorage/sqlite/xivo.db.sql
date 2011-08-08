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

BEGIN TRANSACTION;

DROP TABLE accesswebservice;
CREATE TABLE accesswebservice (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 login varchar(64),
 passwd varchar(64),
 host varchar(255),
 obj longblob NOT NULL,
 disable tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX accesswebservice__idx__login ON accesswebservice(login);
CREATE INDEX accesswebservice__idx__passwd ON accesswebservice(passwd);
CREATE INDEX accesswebservice__idx__host ON accesswebservice(host);
CREATE INDEX accesswebservice__idx__disable ON accesswebservice(disable);
CREATE UNIQUE INDEX accesswebservice__uidx__name ON accesswebservice(name);


DROP TABLE directories;
CREATE TABLE directories (
 id integer unsigned,
 uri varchar(255),
 dirtype varchar(20),
 name varchar(255),
 tablename varchar(255),
 description text NOT NULL,
 PRIMARY KEY(id)
);

INSERT INTO directories VALUES (1,'internal' , NULL, 'internal' , '', 'XiVO internal users');
INSERT INTO directories VALUES (2,'phonebook', NULL, 'phonebook', '', 'XiBO phonebook');


DROP TABLE entity;
CREATE TABLE entity (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 displayname varchar(128) NOT NULL DEFAULT '',
 phonenumber varchar(40) NOT NULL DEFAULT '',
 faxnumber varchar(40) NOT NULL DEFAULT '',
 email varchar(255) NOT NULL DEFAULT '',
 url varchar(255) NOT NULL DEFAULT '',
 address1 varchar(30) NOT NULL DEFAULT '',
 address2 varchar(30) NOT NULL DEFAULT '',
 city varchar(128) NOT NULL DEFAULT '',
 state varchar(128) NOT NULL DEFAULT '',
 zipcode varchar(16) NOT NULL DEFAULT '',
 country varchar(3) NOT NULL DEFAULT '',
 disable tinyint(1) NOT NULL DEFAULT 0,
 dcreate integer unsigned NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX entity__idx__displayname ON entity(displayname);
CREATE INDEX entity__idx__disable ON entity(disable);
CREATE UNIQUE INDEX entity__uidx__name ON entity(name);


DROP TABLE i18ncache;
CREATE TABLE i18ncache (
 locale varchar(7) NOT NULL DEFAULT '',
 path varchar(255) NOT NULL DEFAULT '',
 language varchar(3) NOT NULL DEFAULT '',
 dcreate integer unsigned NOT NULL DEFAULT 0,
 dupdate integer unsigned NOT NULL DEFAULT 0,
 obj longblob NOT NULL,
 PRIMARY KEY(locale,path)
);

CREATE INDEX i18ncache__idx__language ON i18ncache(language);
CREATE INDEX i18ncache__idx__dupdate ON i18ncache(dupdate);


DROP TABLE iproute;
CREATE TABLE iproute (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 iface varchar(64) NOT NULL DEFAULT '',
 destination varchar(39),
 netmask varchar(39),
 gateway varchar(39),
 disable tinyint(1) NOT NULL DEFAULT 0,
 dcreate integer unsigned NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX iproute__idx__iface ON iproute(iface);
CREATE UNIQUE INDEX iproute__uidx__name ON iproute(name);
CREATE UNIQUE INDEX iproute__uidx__destination_netmask_gateway ON iproute(destination,netmask,gateway);


DROP TABLE ldapserver;
CREATE TABLE ldapserver (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 host varchar(255) NOT NULL DEFAULT '',
 port smallint unsigned NOT NULL,
 securitylayer char(3),
 protocolversion char(1) NOT NULL DEFAULT '3',
 disable tinyint(1) NOT NULL DEFAULT 0,
 dcreate integer unsigned NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX ldapserver__idx__host ON ldapserver(host);
CREATE INDEX ldapserver__idx__port ON ldapserver(port);
CREATE INDEX ldapserver__idx__disable ON ldapserver(disable);
CREATE UNIQUE INDEX ldapserver__uidx__name ON ldapserver(name);
CREATE UNIQUE INDEX ldapserver__uidx__host_port ON ldapserver(host,port);


DROP TABLE netiface;
CREATE TABLE netiface (
 id integer unsigned,
 uuid varchar(64) NOT NULL,
 name varchar(64) NOT NULL DEFAULT '',
 ifname varchar(64) NOT NULL DEFAULT '',
 networktype char(4) NOT NULL,
 hwtypeid smallint unsigned NOT NULL DEFAULT 65534,
 type char(5) NOT NULL,
 family varchar(5) NOT NULL,
 method varchar(6) NOT NULL,
 address varchar(39),
 netmask varchar(39),
 broadcast varchar(39),
 gateway varchar(39),
 mtu smallint unsigned,
 vlanrawdevice varchar(64),
 vlanid smallint unsigned,
 options text NOT NULL,
 disable tinyint(1) NOT NULL DEFAULT 0,
 dcreate integer unsigned NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX netiface__idx__hwtypeid ON netiface(hwtypeid);
CREATE INDEX netiface__idx__networktype ON netiface(networktype);
CREATE INDEX netiface__idx__type ON netiface(type);
CREATE INDEX netiface__idx__family ON netiface(family);
CREATE INDEX netiface__idx__method ON netiface(method);
CREATE INDEX netiface__idx__address ON netiface(address);
CREATE INDEX netiface__idx__netmask ON netiface(netmask);
CREATE INDEX netiface__idx__broadcast ON netiface(broadcast);
CREATE INDEX netiface__idx__gateway ON netiface(gateway);
CREATE INDEX netiface__idx__mtu ON netiface(mtu);
CREATE INDEX netiface__idx__vlanrawdevice ON netiface(vlanrawdevice);
CREATE INDEX netiface__idx__vlanid ON netiface(vlanid);
CREATE INDEX netiface__idx__disable ON netiface(disable);
CREATE UNIQUE INDEX netiface__uidx__ifname ON netiface(uuid,ifname);


DROP TABLE resolvconf;
CREATE TABLE resolvconf (
 id tinyint(1),
 hostname varchar(63) NOT NULL DEFAULT 'xivo',
 domain varchar(255) NOT NULL DEFAULT '',
 nameserver1 varchar(255),
 nameserver2 varchar(255),
 nameserver3 varchar(255),
 search varchar(255),
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX resolvconf__uidx__hostname ON resolvconf(hostname);
INSERT INTO resolvconf VALUES(1, '', '', NULL, NULL, NULL, NULL, '');

DROP TABLE server;
CREATE TABLE server (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 host varchar(255) NOT NULL DEFAULT '',
 ws_login varchar(64) NOT NULL DEFAULT '',
 ws_pass varchar(64) NOT NULL DEFAULT '',
 ws_port INTEGER NOT NULL,
 ws_ssl INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 cti_port INTEGER NOT NULL,
 cti_login varchar(64) NOT NULL DEFAULT '',
 cti_pass varchar(64) NOT NULL DEFAULT '',
 cti_ssl INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 dcreate integer unsigned NOT NULL DEFAULT 0,
 disable tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);


CREATE INDEX server__idx__host ON server(host);
CREATE INDEX server__idx__disable ON server(disable);
CREATE UNIQUE INDEX server__uidx__name ON server(name);
CREATE UNIQUE INDEX server__uidx__host_wsport ON server(host,ws_port);
CREATE UNIQUE INDEX server__uidx__host_ctiport ON server(host,cti_port);


DROP TABLE session;
CREATE TABLE session (
 sessid char(32) NOT NULL,
 start integer unsigned NOT NULL,
 expire integer unsigned NOT NULL,
 identifier varchar(255) NOT NULL,
 data longblob NOT NULL,
 PRIMARY KEY(sessid)
);

CREATE INDEX session__idx__expire ON session(expire);
CREATE INDEX session__idx__identifier ON session(identifier);


DROP TABLE user;
CREATE TABLE user (
 id integer unsigned,
 login varchar(64) NOT NULL DEFAULT '',
 passwd varchar(64) NOT NULL DEFAULT '',
 meta varchar(5) NOT NULL DEFAULT 'user',
 valid tinyint(1) NOT NULL DEFAULT 1,
 time integer unsigned NOT NULL DEFAULT 0,
 dcreate integer unsigned NOT NULL DEFAULT 0,
 dupdate integer unsigned NOT NULL DEFAULT 0,
 obj longblob NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX user__idx__login ON user(login);
CREATE INDEX user__idx__passwd ON user(passwd);
CREATE INDEX user__idx__meta ON user(meta);
CREATE INDEX user__idx__valid ON user(valid);
CREATE INDEX user__idx__time ON user(time);
CREATE UNIQUE INDEX user__uidx__login_meta ON user(login,meta);

INSERT INTO user VALUES (1,'root','proformatique','root',1,0,strftime('%s',datetime('now','utc')),0,'');
--INSERT INTO user VALUES (2,'admin','proformatique','admin',1,0,strftime('%s',datetime('now','utc')),0,'');


DROP TABLE dhcp;
CREATE TABLE dhcp (
 id integer unsigned,
 active tinyint(1) NOT NULL DEFAULT 0,
 pool_start varchar(64) NOT NULL DEFAULT '',
 pool_end varchar(64) NOT NULL DEFAULT '',
 extra_ifaces varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

INSERT INTO dhcp VALUES (1,0,'','','');


DROP TABLE mail;
CREATE TABLE mail (
 id integer unsigned,
 mydomain varchar(255) NOT NULL DEFAULT 0,
 origin varchar(255) NOT NULL DEFAULT 'xivo-clients.proformatique.com',
 relayhost varchar(255) NOT NULL DEFAULT '',
 fallback_relayhost varchar(255) NOT NULL DEFAULT '',
 canonical varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

INSERT INTO mail VALUES (1,'', 'xivo-clients.proformatique.com', '', '', '');


DROP TABLE monitoring;
CREATE TABLE monitoring (
 id integer unsigned,
 maintenance tinyint(1) NOT NULL DEFAULT 0,
 alert_emails varchar(4096) DEFAULT NULL,
 dahdi_monitor_ports varchar(255) DEFAULT NULL,
 max_call_duration integer DEFAULT NULL,
 PRIMARY KEY(id)
);

INSERT INTO monitoring VALUES (1,0,NULL,NULL,NULL);


-- HA
DROP TABLE ha;
CREATE TABLE ha (
 id integer unsigned,
 netaddr     VARCHAR(255) DEFAULT NULL,
 netmask     VARCHAR(255) DEFAULT NULL,
 mcast       VARCHAR(255) DEFAULT NULL,

 -- node 1
 node1_ip    VARCHAR(255) DEFAULT NULL,
 node1_name  VARCHAR(255) DEFAULT NULL,
 -- node 2
 node2_ip    VARCHAR(255) DEFAULT NULL,
 node2_name  VARCHAR(255) DEFAULT NULL,

 -- cluster
 cluster_name  VARCHAR(255) DEFAULT NULL,
 cluster_group INTEGER NOT NULL DEFAULT 1,
 cluster_itf_data VARCHAR(255) DEFAULT NULL,
 cluster_monitor INTEGER NOT NULL DEFAULT 20,
 cluster_timeout INTEGER NOT NULL DEFAULT 60,
 cluster_mailto  VARCHAR(255) DEFAULT NULL,
 cluster_pingd   VARCHAR(255) DEFAULT NULL,
 PRIMARY KEY(id)
);

INSERT INTO ha VALUES (1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,20,60,NULL,NULL);


DROP TABLE ha_cluster_node;
CREATE TABLE ha_cluster_node (
 device  VARCHAR(128) NOT NULL DEFAULT '',
 address VARCHAR(128) NOT NULL DEFAULT '',
 PRIMARY KEY (device, address)
);


DROP TABLE ha_service;
CREATE TABLE ha_service (
 name      VARCHAR(128) NOT NULL,
 active    INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 rsc_class VARCHAR(8) DEFAULT NULL,  -- 'lsb' or 'ocf'
 monitor   INTEGER DEFAULT NULL,
 timeout   INTEGER DEFAULT NULL,
 PRIMARY KEY (name)
);

INSERT INTO ha_service VALUES ('asterisk'           , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('nginx'              , 0, 'ocf', NULL, NULL);
INSERT INTO ha_service VALUES ('isc-dhcp-server'    , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('ntp'                , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('csync2'             , 0, 'ocf', NULL, NULL);
INSERT INTO ha_service VALUES ('postgresql'         , 0, 'ocf', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-agid'       , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-confgend'   , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-cti-server' , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-dxtora'     , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-provd'      , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-sysconfd'   , 0, 'lsb', NULL, NULL);
INSERT INTO ha_service VALUES ('pf-xivo-ha-scripts' , 0, 'lsb', NULL, NULL);


DROP TABLE provisioning;
CREATE TABLE provisioning (
 id INTEGER UNSIGNED,
 net4_ip varchar(39) NOT NULL,
 net4_ip_rest varchar(39) NOT NULL,
 username varchar(32) NOT NULL,
 password varchar(32) NOT NULL,
 dhcp_integration INTEGER NOT NULL DEFAULT 0,
 rest_port integer NOT NULL,
 http_port integer NOT NULL,
 private INTEGER NOT NULL DEFAULT 0,
 secure INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY (id)
);

INSERT INTO provisioning VALUES(1, '', '127.0.0.1', 'admin', 'admin', 0, 8666, 8667, 0, 0);


--- STATS ---
DROP TABLE stats_conf;
CREATE TABLE stats_conf (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 hour_start time NOT NULL,
 hour_end time NOT NULL,
 default_delta varchar(16) NOT NULL DEFAULT 0,
 monday tinyint(1) NOT NULL DEFAULT 0,
 tuesday tinyint(1) NOT NULL DEFAULT 0,
 wednesday tinyint(1) NOT NULL DEFAULT 0,
 thursday tinyint(1) NOT NULL DEFAULT 0,
 friday tinyint(1) NOT NULL DEFAULT 0,
 saturday tinyint(1) NOT NULL DEFAULT 0,
 sunday tinyint(1) NOT NULL DEFAULT 0,
 period1 varchar(16) NOT NULL DEFAULT 0,
 period2 varchar(16) NOT NULL DEFAULT 0,
 period3 varchar(16) NOT NULL DEFAULT 0,
 period4 varchar(16) NOT NULL DEFAULT 0,
 period5 varchar(16) NOT NULL DEFAULT 0,
 dbegcache int(10) NOT NULL DEFAULT 0, 
 dendcache int(10) NOT NULL DEFAULT 0, 
 dgenercache integer unsigned, 
 dcreate integer unsigned, 
 dupdate integer unsigned, 
 disable tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX stats_conf__idx__disable ON stats_conf(disable);
CREATE UNIQUE INDEX stats_conf__uidx__name ON stats_conf(name);


DROP TABLE stats_conf_agent;
CREATE TABLE stats_conf_agent (
    stats_conf_id int(10) NOT NULL,
    agentfeatures_id int(10) NOT NULL
);
CREATE UNIQUE INDEX stats_conf_agent_index ON stats_conf_agent(stats_conf_id,agentfeatures_id);


DROP TABLE stats_conf_user;
CREATE TABLE stats_conf_user (
    stats_conf_id int(10) NOT NULL,
    userfeatures_id int(10) NOT NULL
);
CREATE UNIQUE INDEX stats_conf_user_index ON stats_conf_user(stats_conf_id,userfeatures_id);


DROP TABLE stats_conf_incall;
CREATE TABLE stats_conf_incall (
    stats_conf_id int(10) NOT NULL,
    incall_id int(10) NOT NULL
);
CREATE UNIQUE INDEX stats_conf_incall_index ON stats_conf_incall(stats_conf_id,incall_id);


DROP TABLE stats_conf_queue;
CREATE TABLE stats_conf_queue (
    stats_conf_id int(10) NOT NULL,
    queuefeatures_id int(10) NOT NULL,
    "qos" integer NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX stats_conf_queue_index ON stats_conf_queue(stats_conf_id,queuefeatures_id);


DROP TABLE stats_conf_group;
CREATE TABLE stats_conf_group (
    stats_conf_id int(10) NOT NULL,
    groupfeatures_id int(10) NOT NULL
);
CREATE UNIQUE INDEX stats_conf_group_index ON stats_conf_group(stats_conf_id,groupfeatures_id);

COMMIT;
