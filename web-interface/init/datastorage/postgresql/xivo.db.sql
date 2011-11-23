/*
 * XiVO Web-Interface
 * Copyright (C) 2006-2011  Avencall
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

-- execute with *psql -f xivo.db.sql template1*

CREATE USER xivo WITH PASSWORD 'proformatique';
CREATE DATABASE xivo WITH OWNER xivo ENCODING 'UTF8';

\connect xivo;
CREATE LANGUAGE plpgsql;

BEGIN;

DROP TABLE IF EXISTS "accesswebservice";
CREATE TABLE "accesswebservice" (
 "id" SERIAL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "login" varchar(64),
 "passwd" varchar(64),
 "host" varchar(255),
 "obj" TEXT NOT NULL, -- BYTEA
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "accesswebservice__idx__login" ON "accesswebservice"("login");
CREATE INDEX "accesswebservice__idx__passwd" ON "accesswebservice"("passwd");
CREATE INDEX "accesswebservice__idx__host" ON "accesswebservice"("host");
CREATE INDEX "accesswebservice__idx__disable" ON "accesswebservice"("disable");
CREATE UNIQUE INDEX "accesswebservice__uidx__name" ON "accesswebservice"("name");


DROP TABLE IF EXISTS "directories";
CREATE TABLE "directories" (
 "id" SERIAL,
 "uri" varchar(255),
 "dirtype" varchar(20),
 "name" varchar(255),
 "tablename" varchar(255),
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

INSERT INTO "directories" VALUES (1,'internal' , NULL, 'internal' , '', 'XiVO internal users');
INSERT INTO "directories" VALUES (2,'phonebook', NULL, 'phonebook', '', 'XiVO phonebook');
SELECT setval('directories_id_seq', 3);


DROP TABLE IF EXISTS "entity";
CREATE TABLE "entity" (
 "id" SERIAL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "displayname" varchar(128) NOT NULL DEFAULT '',
 "phonenumber" varchar(40) NOT NULL DEFAULT '',
 "faxnumber" varchar(40) NOT NULL DEFAULT '',
 "email" varchar(255) NOT NULL DEFAULT '',
 "url" varchar(255) NOT NULL DEFAULT '',
 "address1" varchar(30) NOT NULL DEFAULT '',
 "address2" varchar(30) NOT NULL DEFAULT '',
 "city" varchar(128) NOT NULL DEFAULT '',
 "state" varchar(128) NOT NULL DEFAULT '',
 "zipcode" varchar(16) NOT NULL DEFAULT '',
 "country" varchar(3) NOT NULL DEFAULT '',
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "entity__idx__displayname" ON "entity"("displayname");
CREATE INDEX "entity__idx__disable" ON "entity"("disable");
CREATE UNIQUE INDEX "entity__uidx__name" ON "entity"("name");


DROP TABLE IF EXISTS "iproute";
CREATE TABLE "iproute" (
 "id" SERIAL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "iface" varchar(64) NOT NULL DEFAULT '',
 "destination" varchar(39) NOT NULL,
 "netmask" varchar(39) NOT NULL,
 "gateway" varchar(39) NOT NULL,
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "iproute__idx__iface" ON "iproute"("iface");
CREATE UNIQUE INDEX "iproute__uidx__name" ON "iproute"("name");
CREATE UNIQUE INDEX "iproute__uidx__destination_netmask_gateway" ON "iproute"("destination","netmask","gateway");


DROP TABLE IF EXISTS "ldapserver";
DROP TYPE  IF EXISTS "ldapserver_securitylayer";
DROP TYPE  IF EXISTS "ldapserver_protocolversion";

CREATE TYPE "ldapserver_securitylayer" AS ENUM ('tls', 'ssl');
CREATE TYPE "ldapserver_protocolversion" AS ENUM ('2', '3');

CREATE TABLE "ldapserver" (
 "id" SERIAL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "host" varchar(255) NOT NULL DEFAULT '',
 "port" INTEGER NOT NULL,
 "securitylayer" ldapserver_securitylayer,
 "protocolversion" ldapserver_protocolversion NOT NULL DEFAULT '3',
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "ldapserver__idx__host" ON "ldapserver"("host");
CREATE INDEX "ldapserver__idx__port" ON "ldapserver"("port");
CREATE INDEX "ldapserver__idx__disable" ON "ldapserver"("disable");
CREATE UNIQUE INDEX "ldapserver__uidx__name" ON "ldapserver"("name");
CREATE UNIQUE INDEX "ldapserver__uidx__host_port" ON "ldapserver"("host","port");


DROP TABLE IF EXISTS "netiface";
DROP TYPE  IF EXISTS "netiface_networktype";
DROP TYPE  IF EXISTS "netiface_type";
DROP TYPE  IF EXISTS "netiface_family";
DROP TYPE  IF EXISTS "netiface_method";

CREATE TYPE "netiface_networktype" AS ENUM ('data','voip');
CREATE TYPE "netiface_type" AS ENUM ('iface');
CREATE TYPE "netiface_family" AS ENUM ('inet','inet6');
CREATE TYPE "netiface_method" AS ENUM ('static','dhcp');
CREATE TABLE "netiface" ( 
 "id" SERIAL,
 "uuid" varchar(64) NOT NULL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "ifname" varchar(64) NOT NULL DEFAULT '',
 "hwtypeid" INTEGER NOT NULL DEFAULT 65534,
 "networktype" netiface_networktype NOT NULL,
 "type" netiface_type NOT NULL,
 "family" netiface_family NOT NULL,
 "method" netiface_method NOT NULL,
 "address" varchar(39),
 "netmask" varchar(39),
 "broadcast" varchar(15),
 "gateway" varchar(39),
 "mtu" INTEGER,
 "vlanrawdevice" varchar(64),
 "vlanid" INTEGER,
 "options" text NOT NULL,
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "netiface__idx__hwtypeid" ON "netiface"("hwtypeid");
CREATE INDEX "netiface__idx__networktype" ON "netiface"("networktype");
CREATE INDEX "netiface__idx__type" ON "netiface"("type");
CREATE INDEX "netiface__idx__family" ON "netiface"("family");
CREATE INDEX "netiface__idx__method" ON "netiface"("method");
CREATE INDEX "netiface__idx__address" ON "netiface"("address");
CREATE INDEX "netiface__idx__netmask" ON "netiface"("netmask");
CREATE INDEX "netiface__idx__broadcast" ON "netiface"("broadcast");
CREATE INDEX "netiface__idx__gateway" ON "netiface"("gateway");
CREATE INDEX "netiface__idx__mtu" ON "netiface"("mtu");
CREATE INDEX "netiface__idx__vlanrawdevice" ON "netiface"("vlanrawdevice");
CREATE INDEX "netiface__idx__vlanid" ON "netiface"("vlanid");
CREATE INDEX "netiface__idx__disable" ON "netiface"("disable");
CREATE UNIQUE INDEX "netiface__uidx__ifname" ON "netiface"("uuid","ifname");


DROP TABLE IF EXISTS "resolvconf";
CREATE TABLE "resolvconf" (
 "id" SERIAL,
 "hostname" varchar(63) NOT NULL DEFAULT 'xivo',
 "domain" varchar(255) NOT NULL DEFAULT '',
 "nameserver1" varchar(255),
 "nameserver2" varchar(255),
 "nameserver3" varchar(255),
 "search" varchar(255),
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE UNIQUE INDEX "resolvconf__uidx__hostname" ON "resolvconf"("hostname");

INSERT INTO "resolvconf" VALUES(1, '', '', NULL, NULL, NULL, NULL, '');
SELECT setval('resolvconf_id_seq', 2);

DROP TABLE IF EXISTS "server";
CREATE TABLE "server" (
 "id" SERIAL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "host" varchar(255) NOT NULL DEFAULT '',
 "ws_login" varchar(64) NOT NULL DEFAULT '',
 "ws_pass" varchar(64) NOT NULL DEFAULT '',
 "ws_port" INTEGER NOT NULL,
 "ws_ssl" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "cti_port" INTEGER NOT NULL,
 "cti_login" varchar(64) NOT NULL DEFAULT '',
 "cti_pass" varchar(64) NOT NULL DEFAULT '',
 "cti_ssl" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "description" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "server__idx__host" ON "server"("host");
CREATE INDEX "server__idx__disable" ON "server"("disable");
CREATE UNIQUE INDEX "server__uidx__name" ON "server"("name");
CREATE UNIQUE INDEX "server__uidx__host_wsport" ON "server"("host","ws_port");
CREATE UNIQUE INDEX "server__uidx__host_ctiport" ON "server"("host","cti_port");


DROP TABLE IF EXISTS "session";
CREATE TABLE "session" (
 "sessid" char(32) NOT NULL,
 "start" INTEGER NOT NULL,
 "expire" INTEGER NOT NULL,
 "identifier" varchar(255) NOT NULL,
 "data" TEXT NOT NULL, -- BYTEA
 PRIMARY KEY("sessid")
);

CREATE INDEX "session__idx__expire" ON "session"("expire");
CREATE INDEX "session__idx__identifier" ON "session"("identifier");


DROP TABLE IF EXISTS "user";
DROP TYPE  IF EXISTS "user_meta";

CREATE TYPE "user_meta" AS ENUM ('user','admin','root');
CREATE TABLE "user" (
 "id" SERIAL,
 "login" varchar(64) NOT NULL DEFAULT '',
 "passwd" varchar(64) NOT NULL DEFAULT '',
 "meta" user_meta NOT NULL DEFAULT 'user',
 "valid" INTEGER NOT NULL DEFAULT 1, -- BOOLEAN
 "time" INTEGER NOT NULL DEFAULT 0,
 "dcreate" INTEGER NOT NULL DEFAULT 0, -- TIMESTAMP
 "dupdate" INTEGER NOT NULL DEFAULT 0, -- TIMESTAMP
 "obj" TEXT NOT NULL, -- BYTEA
 PRIMARY KEY("id")
);

CREATE INDEX "user__idx__login" ON "user"("login");
CREATE INDEX "user__idx__passwd" ON "user"("passwd");
CREATE INDEX "user__idx__meta" ON "user"("meta");
CREATE INDEX "user__idx__valid" ON "user"("valid");
CREATE INDEX "user__idx__time" ON "user"("time");
CREATE UNIQUE INDEX "user__uidx__login_meta" ON "user"("login","meta");

INSERT INTO "user" VALUES (1,'root','proformatique','root',1,0,EXTRACT(EPOCH from now()),0,'');
SELECT setval('user_id_seq', 2);


DROP TABLE IF EXISTS "dhcp";
CREATE TABLE "dhcp" (
 "id" SERIAL,
 "active" INTEGER NOT NULL DEFAULT 0,
 "pool_start" varchar(64) NOT NULL DEFAULT '',
 "pool_end" varchar(64) NOT NULL DEFAULT '',
 "extra_ifaces" varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY("id")
);

INSERT INTO "dhcp" VALUES (1,0,'','','');
SELECT setval('dhcp_id_seq', 2);


DROP TABLE IF EXISTS "mail";
CREATE TABLE "mail" (
 "id" SERIAL,
 "mydomain" varchar(255) NOT NULL DEFAULT 0,
 "origin" varchar(255) NOT NULL DEFAULT 'xivo-clients.proformatique.com',
 "relayhost" varchar(255),
 "fallback_relayhost" varchar(255),
 "canonical" text NOT NULL,
 PRIMARY KEY("id")
);

CREATE UNIQUE INDEX "mail__uidx__origin" ON "mail"("origin");

INSERT INTO "mail" VALUES (1,'','xivo-clients.proformatique.com','','','');
SELECT setval('mail_id_seq', 2);


DROP TABLE IF EXISTS "monitoring";
CREATE TABLE "monitoring" (
 "id" SERIAL,
 "maintenance" INTEGER NOT NULL DEFAULT 0,
 "alert_emails" varchar(4096) DEFAULT NULL,
 "dahdi_monitor_ports" varchar(255) DEFAULT NULL,
 "max_call_duration" INTEGER DEFAULT NULL,
 PRIMARY KEY("id")
);

INSERT INTO monitoring VALUES (1,0,NULL,NULL,NULL);
SELECT setval('monitoring_id_seq', 2);


-- HA
DROP TABLE IF EXISTS "ha";
CREATE TABLE "ha" (
 "id" SERIAL,
 "active"      INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "netaddr"     VARCHAR(255) DEFAULT NULL,
 "netmask"     VARCHAR(255) DEFAULT NULL,
 "mcast"       VARCHAR(255) DEFAULT NULL,

 -- node 1
 "node1_ip"    VARCHAR(255) DEFAULT NULL,
 "node1_name"  VARCHAR(255) DEFAULT NULL,
 -- node 2
 "node2_ip"    VARCHAR(255) DEFAULT NULL,
 "node2_name"  VARCHAR(255) DEFAULT NULL,

 -- cluster
 "cluster_name"  VARCHAR(255) DEFAULT NULL,
 "cluster_group" INTEGER NOT NULL DEFAULT 1,
 "cluster_itf_data" VARCHAR(255) DEFAULT NULL,
 "cluster_itf_master_ip" VARCHAR(255) DEFAULT NULL,
 "cluster_itf_slave_ip"  VARCHAR(255) DEFAULT NULL,

 "cluster_monitor" INTEGER NOT NULL DEFAULT 20,
 "cluster_timeout" INTEGER NOT NULL DEFAULT 60,
 "cluster_mailto"  VARCHAR(255) DEFAULT NULL,
 "cluster_pingd"   VARCHAR(255) DEFAULT NULL,

 PRIMARY KEY("id")
);

INSERT INTO "ha" VALUES (1,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,20,60,NULL,NULL);
SELECT setval('ha_id_seq', 2);


DROP TABLE IF EXISTS "ha_cluster_node";
CREATE TABLE "ha_cluster_node" (
 "device"  VARCHAR(128) NOT NULL DEFAULT '',
 "address" VARCHAR(128) NOT NULL DEFAULT '',
 PRIMARY KEY ("device", "address")
);


DROP TABLE IF EXISTS "ha_service";
CREATE TABLE "ha_service" (
 "name"      VARCHAR(128) NOT NULL,
 "active"    INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "rsc_class" VARCHAR(8) DEFAULT NULL,  -- 'lsb' or 'ocf'
 "monitor"   INTEGER DEFAULT NULL,
 "timeout"   INTEGER DEFAULT NULL,
 PRIMARY KEY ("name")
);

INSERT INTO "ha_service" VALUES ('asterisk'           , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('nginx'              , 0, 'ocf', NULL, NULL);
INSERT INTO "ha_service" VALUES ('spawn-fcgi'         , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('isc-dhcp-server'    , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('ntp'                , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('csync2'             , 0, 'ocf', NULL, NULL);
INSERT INTO "ha_service" VALUES ('postgresql'         , 0, 'ocf', 30, NULL);
INSERT INTO "ha_service" VALUES ('pf-xivo-agid'       , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('xivo-confgend'      , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('pf-xivo-cti-server' , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('pf-xivo-dxtora'     , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('pf-xivo-provd'      , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('pf-xivo-sysconfd'   , 0, 'lsb', NULL, NULL);
INSERT INTO "ha_service" VALUES ('pf-xivo-ha-scripts' , 0, 'lsb', NULL, NULL);


DROP TABLE IF EXISTS "provisioning";
CREATE TABLE "provisioning" (
 "id" SERIAL,
 "net4_ip" varchar(39) NOT NULL,
 "net4_ip_rest" varchar(39) NOT NULL,
 "username" varchar(32) NOT NULL,
 "password" varchar(32) NOT NULL,
 "dhcp_integration" INTEGER NOT NULL DEFAULT 0,
 "rest_port" integer NOT NULL,
 "http_port" integer NOT NULL,
 "private" INTEGER NOT NULL DEFAULT 0,
 "secure" INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY ("id")
);

INSERT INTO "provisioning" VALUES(1, '', '127.0.0.1', 'admin', 'admin', 0, 8666, 8667, 0, 0);
SELECT setval('provisioning_id_seq', 2);


--- STATS ---
DROP TABLE IF EXISTS "stats_conf";
CREATE TABLE "stats_conf" (
 "id" SERIAL,
 "name" varchar(64) NOT NULL DEFAULT '',
 "hour_start" time NOT NULL,
 "hour_end" time NOT NULL,
 "homepage" integer,
 "timezone" varchar(128) NOT NULL DEFAULT '',
 "default_delta" varchar(16) NOT NULL DEFAULT 0,
 "monday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "tuesday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "wednesday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "thursday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "friday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "saturday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "sunday" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "period1" varchar(16) NOT NULL DEFAULT 0,
 "period2" varchar(16) NOT NULL DEFAULT 0,
 "period3" varchar(16) NOT NULL DEFAULT 0,
 "period4" varchar(16) NOT NULL DEFAULT 0,
 "period5" varchar(16) NOT NULL DEFAULT 0,
 "dbegcache" integer DEFAULT 0, 
 "dendcache" integer DEFAULT 0, 
 "dgenercache" integer DEFAULT 0, 
 "dcreate" integer DEFAULT 0, 
 "dupdate" integer DEFAULT 0, 
 "disable" smallint NOT NULL DEFAULT 0, -- BOOLEAN
 "description" text NOT NULL,
 PRIMARY KEY("id")
);
CREATE INDEX "stats_conf__idx__disable" ON "stats_conf"("disable");
CREATE UNIQUE INDEX "stats_conf__uidx__name" ON "stats_conf"("name");


DROP TABLE IF EXISTS "stats_conf_agent";
CREATE TABLE "stats_conf_agent" (
    "stats_conf_id" integer NOT NULL,
    "agentfeatures_id" integer NOT NULL
);
CREATE UNIQUE INDEX "stats_conf_agent_index" ON "stats_conf_agent" USING btree ("stats_conf_id","agentfeatures_id");


DROP TABLE IF EXISTS "stats_conf_user";
CREATE TABLE "stats_conf_user" (
    "stats_conf_id" integer NOT NULL,
    "userfeatures_id" integer NOT NULL
);
CREATE UNIQUE INDEX "stats_conf_user_index" ON "stats_conf_user" USING btree ("stats_conf_id","userfeatures_id");


DROP TABLE IF EXISTS "stats_conf_incall";
CREATE TABLE "stats_conf_incall" (
    "stats_conf_id" integer NOT NULL,
    "incall_id" integer NOT NULL
);
CREATE UNIQUE INDEX "stats_conf_incall_index" ON "stats_conf_incall" USING btree ("stats_conf_id","incall_id");


DROP TABLE IF EXISTS "stats_conf_queue";
CREATE TABLE "stats_conf_queue" (
    "stats_conf_id" integer NOT NULL,
    "queuefeatures_id" integer NOT NULL,
    "qos" smallint NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX "stats_conf_queue_index" ON "stats_conf_queue" USING btree ("stats_conf_id","queuefeatures_id");


DROP TABLE IF EXISTS "stats_conf_group";
CREATE TABLE "stats_conf_group" (
    "stats_conf_id" integer NOT NULL,
    "groupfeatures_id" integer NOT NULL
);
CREATE UNIQUE INDEX "stats_conf_group_index" ON "stats_conf_group" USING btree ("stats_conf_id","groupfeatures_id");

-- grant all rights to xivo.* for xivo user
CREATE OR REPLACE FUNCTION execute(text) 
RETURNS VOID AS '
BEGIN
	execute $1;
END;
' LANGUAGE plpgsql;
SELECT execute('GRANT ALL ON '||schemaname||'.'||tablename||' TO xivo;') FROM pg_tables WHERE schemaname = 'public';
SELECT execute('GRANT ALL ON SEQUENCE '||relname||' TO xivo;') FROM pg_class WHERE relkind = 'S';

COMMIT;

