DROP TABLE IF EXISTS "ctiprofiles";


CREATE TABLE "ctiprofiles" (
 "id" SERIAL,
 "xlets" text,
 "maxgui" integer,
 "appliname" varchar(255),
 "name" varchar(40) unique,
 "presence" varchar(255),
 "phonehints" varchar(255),
 "agents" varchar(255),
 "services" varchar(255),
 "preferences" varchar(2048),
 "deletable" INTEGER, -- BOOLEAN
 PRIMARY KEY("id")
);

INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "queues", "dock", "fms", "N/A" ],[ "queuedetails", "dock", "fms", "N/A" ],[ "queueentrydetails", "dock", "fcms", "N/A" ],[ "agents", "dock", "fcms", "N/A" ],[ "agentdetails", "dock", "fcms", "N/A" ],[ "identity", "grid", "fcms", "0" ],[ "conference", "dock", "fcm", "N/A" ]]',-1,'Superviseur','agentsup','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "queues", "dock", "ms", "N/A" ],[ "identity", "grid", "fcms", "0" ],[ "customerinfo", "dock", "cms", "N/A" ],[ "agentdetails", "dock", "cms", "N/A" ]]',-1,'Agent','agent','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "tabber", "grid", "fcms", "1" ],[ "dial", "grid", "fcms", "2" ],[ "search", "tab", "fcms", "0" ],[ "customerinfo", "tab", "fcms", "4" ],[ "identity", "grid", "fcms", "0" ],[ "fax", "tab", "fcms", "N/A" ],[ "history", "tab", "fcms", "N/A" ],[ "directory", "tab", "fcms", "N/A" ],[ "features", "tab", "fcms", "N/A" ],[ "mylocaldir", "tab", "fcms", "N/A" ],[ "conference", "tab", "fcms", "N/A" ]]',-1,'Client','client','xivo','xivo','xivo','enablednd,fwdunc,fwdbusy,fwdrna','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "tabber", "grid", "fcms", "1" ],[ "dial", "grid", "fcms", "2" ],[ "search", "tab", "fcms", "0" ],[ "customerinfo", "tab", "fcms", "4" ],[ "identity", "grid", "fcms", "0" ],[ "fax", "tab", "fcms", "N/A" ],[ "history", "tab", "fcms", "N/A" ],[ "directory", "tab", "fcms", "N/A" ],[ "features", "tab", "fcms", "N/A" ],[ "mylocaldir", "tab", "fcms", "N/A" ],[ "conference", "tab", "fcms", "N/A" ],[ "outlook", "tab", "fcms", "N/A" ]]',-1,'Client+Outlook','clientoutlook','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "datetime", "dock", "fm", "N/A" ]]',-1,'Horloge','clock','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "dial", "dock", "fm", "N/A" ],[ "operator", "dock", "fcm", "N/A" ],[ "datetime", "dock", "fcm", "N/A" ],[ "identity", "grid", "fcms", "0" ],[ "calls", "dock", "fcm", "N/A" ],[ "parking", "dock", "fcm", "N/A" ]]',-1,'Opérateur','oper','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "parking", "dock", "fcms", "N/A" ],[ "search", "dock", "fcms", "N/A" ],[ "calls", "dock", "fcms", "N/A" ],[ "switchboard", "dock", "fcms", "N/A" ],[ "customerinfo", "dock", "fcms", "N/A" ],[ "datetime", "dock", "fcms", "N/A" ],[ "dial", "dock", "fcms", "N/A" ],[ "identity", "grid", "fcms", "0" ],[ "operator", "dock", "fcms", "N/A" ]]',-1,'Switchboard','switchboard','xivo','xivo','xivo','','',1);

grant all on ctiprofiles to asterisk;
