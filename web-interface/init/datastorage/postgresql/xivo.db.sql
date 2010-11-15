/*
 * XiVO Web-Interface
 * Copyright (C) 2010  Proformatique <technique@proformatique.com>
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
 "obj" bytea NOT NULL,
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


DROP TABLE IF EXISTS "i18ncache";
CREATE TABLE "i18ncache" (
 "locale" varchar(7) NOT NULL DEFAULT '',
 "path" varchar(255) NOT NULL DEFAULT '',
 "language" varchar(3) NOT NULL DEFAULT '',
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "dupdate" INTEGER NOT NULL DEFAULT 0,
 "obj" bytea NOT NULL,
 PRIMARY KEY("locale","path")
);

CREATE INDEX "i18ncache__idx__language" ON "i18ncache"("language");
CREATE INDEX "i18ncache__idx__dupdate" ON "i18ncache"("dupdate");


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

CREATE TYPE	"netiface_networktype" AS ENUM ('data','voip');
CREATE TYPE "netiface_type" AS ENUM ('iface');
CREATE TYPE "netiface_family" AS ENUM ('inet','inet6');
CREATE TYPE "netiface_method" AS ENUM ('static','dhcp');
CREATE TABLE "netiface" (
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
 PRIMARY KEY("name")
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
CREATE UNIQUE INDEX "netiface__uidx__ifname" ON "netiface"("ifname");


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
 "port" INTEGER NOT NULL,
 "ssl" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "disable" INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 "dcreate" INTEGER NOT NULL DEFAULT 0,
 "description" text NOT NULL,
 "webi" varchar(255) NOT NULL DEFAULT '',
 "ami_port" INTEGER NOT NULL,
 "ami_login" varchar(64) NOT NULL DEFAULT '',
 "ami_pass" varchar(64) NOT NULL DEFAULT '',
 PRIMARY KEY("id")
);

CREATE INDEX "server__idx__host" ON "server"("host");
CREATE INDEX "server__idx__port" ON "server"("port");
CREATE INDEX "server__idx__disable" ON "server"("disable");
CREATE UNIQUE INDEX "server__uidx__name" ON "server"("name");
CREATE UNIQUE INDEX "server__uidx__host_port" ON "server"("host","port");

INSERT INTO "server" VALUES(1,'xivo','localhost',443,1,0,1271070538,'','127.0.0.1',5038,'xivouser','xivouser');
SELECT setval('server_id_seq', 2);


DROP TABLE IF EXISTS "session";
CREATE TABLE "session" (
 "sessid" char(32) NOT NULL,
 "start" INTEGER NOT NULL,
 "expire" INTEGER NOT NULL,
 "identifier" varchar(255) NOT NULL,
 "data" bytea NOT NULL,
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
 "dcreate" TIMESTAMP NOT NULL DEFAULT TIMESTAMP '-infinity',
 "dupdate" TIMESTAMP NOT NULL DEFAULT TIMESTAMP '-infinity',
 "obj" bytea NOT NULL,
 PRIMARY KEY("id")
);

CREATE INDEX "user__idx__login" ON "user"("login");
CREATE INDEX "user__idx__passwd" ON "user"("passwd");
CREATE INDEX "user__idx__meta" ON "user"("meta");
CREATE INDEX "user__idx__valid" ON "user"("valid");
CREATE INDEX "user__idx__time" ON "user"("time");
CREATE UNIQUE INDEX "user__uidx__login_meta" ON "user"("login","meta");

INSERT INTO "user" VALUES (1,'root','proformatique','root',1,0,TIMESTAMP 'now',TIMESTAMP '-infinity','');
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


DROP TABLE IF EXISTS "queue_info";
CREATE TABLE "queue_info" (
 "id" SERIAL,
 "call_time_t" INTEGER,
 "queue_name" varchar(255) NOT NULL,
 "caller" varchar(255) NOT NULL,
 "caller_uniqueid" varchar(255) NOT NULL,
 "call_picker" varchar(255),
 "hold_time" INTEGER,
 "talk_time" INTEGER,
 PRIMARY KEY("id")
);

CREATE INDEX "queue_info_call_time_t_index" ON "queue_info"("call_time_t");
CREATE INDEX "queue_info_queue_name_index" ON "queue_info"("queue_name");


-- HA
DROP TABLE IF EXISTS "ha";
CREATE TABLE "ha" (
 "id" SERIAL,
 "apache2" INTEGER NOT NULL DEFAULT 0,
 "asterisk" INTEGER NOT NULL DEFAULT 0,
 "dhcp" INTEGER NOT NULL DEFAULT 0,
 "monit" INTEGER NOT NULL DEFAULT 0,
 "mysql" INTEGER NOT NULL DEFAULT 0,
 "ntp" INTEGER NOT NULL DEFAULT 0,
 "rsync" INTEGER NOT NULL DEFAULT 0,
 "smokeping" INTEGER NOT NULL DEFAULT 0,
 "mailto" INTEGER NOT NULL DEFAULT 0,
 "alert_emails" varchar(1024) DEFAULT NULL,
 "serial" varchar(16) NOT NULL DEFAULT '',
 "authkeys" varchar(128) NOT NULL DEFAULT '',
 "com_mode" varchar(8) NOT NULL DEFAULT 'ucast',
 "user" varchar(16) NOT NULL DEFAULT 'pf-replication',
 "password" varchar(16) NOT NULL DEFAULT 'proformatique',
 "dest_user" varchar(16) NOT NULL DEFAULT 'pf-replication',
 "dest_password" varchar(16) NOT NULL DEFAULT 'proformatique',
 PRIMARY KEY("id")
);

INSERT INTO "ha" VALUES (1,0,0,0,0,0,0,0,0,0,NULL,'','','ucast','pf-replication','proformatique','pf-replication','proformatique');
SELECT setval('ha_id_seq', 2);

DROP TABLE IF EXISTS "ha_uname_node";
CREATE TABLE "ha_uname_node" (
 "uname_node" varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY ("uname_node")
);

DROP TABLE IF EXISTS "ha_ping_ipaddr";
CREATE TABLE "ha_ping_ipaddr" (
 "ping_ipaddr" varchar(39) NOT NULL DEFAULT '',
 PRIMARY KEY ("ping_ipaddr")
);

DROP TABLE IF EXISTS "ha_virtual_network";
CREATE TABLE "ha_virtual_network" (
 "ipaddr" varchar(39) NOT NULL DEFAULT '',
 "netmask" varchar(39) NOT NULL DEFAULT '',
 "broadcast" varchar(39) NOT NULL DEFAULT '',
 PRIMARY KEY ("ipaddr")
);

DROP TABLE IF EXISTS "ha_peer";
CREATE TABLE "ha_peer" (
 "iface" varchar(64) NOT NULL DEFAULT '',
 "host" varchar(128) NOT NULL DEFAULT '',
 "transfer" INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY ("iface", "host")
);


-- provisioning
DROP TABLE IF EXISTS "provisioning";
CREATE TABLE "provisioning" (
 "id" SERIAL,
 "registrar_main"   varchar(255) NOT NULL DEFAULT '',
 "registrar_backup" varchar(255) NOT NULL DEFAULT '',
 "proxy_main"       varchar(255) NOT NULL DEFAULT '',
 "proxy_backup"     varchar(255) NOT NULL DEFAULT '',
 "vlan_id"					integer,
 PRIMARY KEY("id")
);

INSERT INTO "provisioning" VALUES(1, '', '', '', '', NULL);
SELECT setval('provisioning_id_seq', 2);

-- grant all rights to xivo.* for xivo user
CREATE FUNCTION execute(text) 
RETURNS VOID AS '
BEGIN
	execute $1;
END;
' LANGUAGE plpgsql;
SELECT execute('GRANT ALL ON '||schemaname||'.'||tablename||' TO xivo;') FROM pg_tables WHERE schemaname = 'public';

COMMIT;

