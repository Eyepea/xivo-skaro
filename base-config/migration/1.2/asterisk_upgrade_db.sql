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
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "datetime", "dock", "fm", "N/A" ]]',-1,'Horloge','clock','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "dial", "dock", "fm", "N/A" ],[ "operator", "dock", "fcm", "N/A" ],[ "datetime", "dock", "fcm", "N/A" ],[ "identity", "grid", "fcms", "0" ],[ "calls", "dock", "fcm", "N/A" ]]',-1,'Opérateur','oper','xivo','xivo','xivo','','',1);
INSERT INTO "ctiprofiles" VALUES(DEFAULT,'[[ "search", "dock", "fcms", "N/A" ],[ "calls", "dock", "fcms", "N/A" ],[ "switchboard", "dock", "fcms", "N/A" ],[ "customerinfo", "dock", "fcms", "N/A" ],[ "datetime", "dock", "fcms", "N/A" ],[ "dial", "dock", "fcms", "N/A" ],[ "identity", "grid", "fcms", "0" ],[ "operator", "dock", "fcms", "N/A" ]]',-1,'Switchboard','switchboard','xivo','xivo','xivo','','',1);

grant all on ctiprofiles to asterisk;
grant all on ctiprofiles_id_seq to asterisk;


DROP TABLE IF EXISTS "cdr";


DROP INDEX IF EXISTS "accessfeatures__idx__host";
DROP INDEX IF EXISTS "accessfeatures__idx__feature";
DROP INDEX IF EXISTS "accessfeatures__idx__commented";

DROP INDEX IF EXISTS "agentfeatures__idx__commented";

DROP INDEX IF EXISTS "agentqueueskill__idx__agentid";

DROP INDEX IF EXISTS "agentgroup__idx__groupid";
DROP INDEX IF EXISTS "agentgroup__idx__name";
DROP INDEX IF EXISTS "agentgroup__idx__commented";
DROP INDEX IF EXISTS "agentgroup__idx__deleted";

DROP INDEX IF EXISTS "callfilter__idx__context";
DROP INDEX IF EXISTS "callfilter__idx__type";
DROP INDEX IF EXISTS "callfilter__idx__bosssecretary";
DROP INDEX IF EXISTS "callfilter__idx__callfrom";
DROP INDEX IF EXISTS "callfilter__idx__commented";

DROP INDEX IF EXISTS "callfiltermember__idx__priority";
DROP INDEX IF EXISTS "callfiltermember__idx__bstype";
DROP INDEX IF EXISTS "callfiltermember__idx__active";

DROP INDEX IF EXISTS "context__idx__commented";
DROP INDEX IF EXISTS "context__idx__displayname";
DROP INDEX IF EXISTS "context__idx__contexttype";
DROP INDEX IF EXISTS "context__idx__entity";

DROP INDEX IF EXISTS "contextinclude__idx__context";
DROP INDEX IF EXISTS "contextinclude__idx__include";
DROP INDEX IF EXISTS "contextinclude__idx__priority";

DROP INDEX IF EXISTS "contextnumbers__idx__context_type";

DROP INDEX IF EXISTS "contexttype__idx__commented";
DROP INDEX IF EXISTS "contexttype__idx__deletable";

DROP INDEX IF EXISTS "dialaction__idx__actionarg2";
DROP INDEX IF EXISTS "dialaction__idx__linked";

DROP INDEX IF EXISTS "extensions__idx__commented";

DROP INDEX IF EXISTS "features__idx__filename";
DROP INDEX IF EXISTS "features__idx__commented";
DROP INDEX IF EXISTS "features__idx__var_name";

DROP INDEX IF EXISTS "paginguser__idx__userfeaturesid";
DROP INDEX IF EXISTS "paginguser__idx__caller";

DROP INDEX IF EXISTS "groupfeatures__idx__deleted";

DROP INDEX IF EXISTS "incall__idx__commented";

DROP INDEX IF EXISTS "linefeatures__idx__commented";

DROP INDEX IF EXISTS "ldapfilter__idx__ldapserverid";
DROP INDEX IF EXISTS "ldapfilter__idx__commented";

DROP INDEX IF EXISTS "meetmeguest__idx__meetmefeaturesid";
DROP INDEX IF EXISTS "meetmeguest__idx__fullname";
DROP INDEX IF EXISTS "meetmeguest__idx__email";

DROP INDEX IF EXISTS "musiconhold__idx__commented";

DROP INDEX IF EXISTS "operator__idx__disable";

DROP INDEX IF EXISTS "operator_destination__idx__disable";

DROP INDEX IF EXISTS "outcall__idx__commented";

DROP INDEX IF EXISTS "outcalldundipeer__idx__priority";

DROP INDEX IF EXISTS "phonebook__idx__title";
DROP INDEX IF EXISTS "phonebook__idx__firstname";
DROP INDEX IF EXISTS "phonebook__idx__lastname";
DROP INDEX IF EXISTS "phonebook__idx__displayname";
DROP INDEX IF EXISTS "phonebook__idx__society";
DROP INDEX IF EXISTS "phonebook__idx__email";

DROP INDEX IF EXISTS "phonebookaddress__idx__address1";
DROP INDEX IF EXISTS "phonebookaddress__idx__address2";
DROP INDEX IF EXISTS "phonebookaddress__idx__city";
DROP INDEX IF EXISTS "phonebookaddress__idx__state";
DROP INDEX IF EXISTS "phonebookaddress__idx__zipcode";
DROP INDEX IF EXISTS "phonebookaddress__idx__country";
DROP INDEX IF EXISTS "phonebookaddress__idx__type";

DROP INDEX IF EXISTS "phonebooknumber__idx__number";
DROP INDEX IF EXISTS "phonebooknumber__idx__type";

DROP INDEX IF EXISTS "queue__idx__commented";

DROP INDEX IF EXISTS "queuemember__idx__commented";

DROP INDEX IF EXISTS "rightcall__idx__context";
DROP INDEX IF EXISTS "rightcall__idx__passwd";
DROP INDEX IF EXISTS "rightcall__idx__authorization";
DROP INDEX IF EXISTS "rightcall__idx__commented";

DROP INDEX IF EXISTS "schedule__idx__commented";

DROP INDEX IF EXISTS "serverfeatures__idx__serverid";
DROP INDEX IF EXISTS "serverfeatures__idx__feature";
DROP INDEX IF EXISTS "serverfeatures__idx__type";
DROP INDEX IF EXISTS "serverfeatures__idx__commented";

DROP INDEX IF EXISTS "servicesgroup__idx__disable";

DROP INDEX IF EXISTS "staticagent__idx__commented";
DROP INDEX IF EXISTS "staticagent__idx__filename";
DROP INDEX IF EXISTS "staticagent__idx__var_name";
DROP INDEX IF EXISTS "staticagent__idx__var_val";

DROP INDEX IF EXISTS "staticiax__idx__filename";
DROP INDEX IF EXISTS "staticiax__idx__commented";
DROP INDEX IF EXISTS "staticiax__idx__var_name";

DROP INDEX IF EXISTS "staticmeetme__idx__commented";
DROP INDEX IF EXISTS "staticmeetme__idx__filename";
DROP INDEX IF EXISTS "staticmeetme__idx__var_name";

DROP INDEX IF EXISTS "staticqueue__idx__commented";
DROP INDEX IF EXISTS "staticqueue__idx__filename";
DROP INDEX IF EXISTS "staticqueue__idx__var_name";

DROP INDEX IF EXISTS "staticsip__idx__commented";
DROP INDEX IF EXISTS "staticsip__idx__filename";
DROP INDEX IF EXISTS "staticsip__idx__var_name";

DROP INDEX IF EXISTS "staticvoicemail__idx__commented";
DROP INDEX IF EXISTS "staticvoicemail__idx__filename";
DROP INDEX IF EXISTS "staticvoicemail__idx__var_name";

DROP INDEX IF EXISTS "staticsccp__idx__commented";
DROP INDEX IF EXISTS "staticsccp__idx__filename";
DROP INDEX IF EXISTS "staticsccp__idx__var_name";

DROP INDEX IF EXISTS "usercustom__idx__protocol";
DROP INDEX IF EXISTS "usercustom__idx__commented";

DROP INDEX IF EXISTS "userfeatures__idx__commented";

DROP INDEX IF EXISTS "useriax__idx__name_host";
DROP INDEX IF EXISTS "useriax__idx__name_ipaddr_port";
DROP INDEX IF EXISTS "useriax__idx__ipaddr_port";
DROP INDEX IF EXISTS "useriax__idx__host_port";
DROP INDEX IF EXISTS "useriax__idx__protocol";
DROP INDEX IF EXISTS "useriax__idx__commented";

DROP INDEX IF EXISTS "usersip__idx__host_port";
DROP INDEX IF EXISTS "usersip__idx__ipaddr_port";
DROP INDEX IF EXISTS "usersip__idx__lastms";
DROP INDEX IF EXISTS "usersip__idx__protocol";
DROP INDEX IF EXISTS "usersip__idx__commented";

DROP INDEX IF EXISTS "voicemail__idx__commented";

DROP INDEX IF EXISTS "voicemenu__idx__commented";
