/*
 * XiVO Base-Config
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

DROP TABLE accessfeatures;
CREATE TABLE accessfeatures (
 id integer unsigned,
 host varchar(255) NOT NULL DEFAULT '',
 feature varchar(9) NOT NULL,
 commented tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE INDEX accessfeatures__idx__host ON accessfeatures(host);
CREATE INDEX accessfeatures__idx__feature ON accessfeatures(feature);
CREATE INDEX accessfeatures__idx__commented ON accessfeatures(commented);
CREATE UNIQUE INDEX accessfeatures__uidx__host_type ON accessfeatures(host,feature);


DROP TABLE agentfeatures;
CREATE TABLE agentfeatures (
 id integer unsigned,
 agentid integer unsigned NOT NULL,
 numgroup tinyint unsigned NOT NULL,
 firstname varchar(128) NOT NULL DEFAULT '',
 lastname varchar(128) NOT NULL DEFAULT '',
 'number' varchar(40) NOT NULL,
 passwd varchar(128) NOT NULL,
 context varchar(39) NOT NULL,
 language varchar(20) NOT NULL,
 silent tinyint(1) NOT NULL DEFAULT 0,
 -- features
 autologoff INTEGER DEFAULT NULL,
 ackcall    VARCHAR(6) NOT NULL DEFAULT 'no',
 acceptdtmf VARCHAR(1) NOT NULL DEFAULT '#',
 enddtmf    VARCHAR(1) NOT NULL DEFAULT '*',
 wrapuptime INTEGER DEFAULT NULL,
 musiconhold VARCHAR(80) DEFAULT NULL,
 'group'      VARCHAR(255) DEFAULT NULL,
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX agentfeatures__idx__commented ON agentfeatures(commented);
CREATE UNIQUE INDEX agentfeatures__uidx__number ON agentfeatures(number);
CREATE UNIQUE INDEX agentfeatures__uidx__agentid ON agentfeatures(agentid);


DROP TABLE agentgroup;
CREATE TABLE agentgroup (
 id tinyint unsigned,
 groupid integer unsigned NOT NULL,
 name varchar(128) NOT NULL DEFAULT '',
 groups varchar(255) NOT NULL DEFAULT '',
 commented tinyint(1) NOT NULL DEFAULT 0,
 deleted tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX agentgroup__idx__groupid ON agentgroup(groupid);
CREATE INDEX agentgroup__idx__name ON agentgroup(name);
CREATE INDEX agentgroup__idx__commented ON agentgroup(commented);
CREATE INDEX agentgroup__idx__deleted ON agentgroup(deleted);

INSERT INTO agentgroup VALUES (1,3,'default','',0,0,'');


-- agent queueskills
DROP TABLE agentqueueskill;
CREATE TABLE agentqueueskill
(
 agentid integer unsigned,
 skillid integer unsigned,
 weight integer unsigned NOT NULL DEFAULT 0,
 PRIMARY KEY(agentid, skillid)
);

CREATE INDEX agentqueueskill__idx__agentid ON agentqueueskill(agentid);


DROP TABLE attachment;
CREATE TABLE attachment (
 id INTEGER UNSIGNED,
 name varchar(64) NOT NULL,
 object_type varchar(16) NOT NULL,
 object_id INTEGER NOT NULL,
 file BINARY,
 size INTEGER NOT NULL,
 mime varchar(64) NOT NULL,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX attachment__uidx__object_type__object_id ON attachment(object_type,object_id);


DROP TABLE callerid;
CREATE TABLE callerid (
 mode varchar(9),
 callerdisplay varchar(80) NOT NULL DEFAULT '',
 type varchar(32) NOT NULL,
 typeval integer unsigned NOT NULL,
 PRIMARY KEY(type,typeval)
);


DROP TABLE callfilter;
CREATE TABLE callfilter (
 id integer unsigned,
 name varchar(128) NOT NULL DEFAULT '',
 context varchar(39) NOT NULL,
 type varchar(14) NOT NULL DEFAULT 'bosssecretary',
 bosssecretary varchar(16),
 callfrom varchar(8) NOT NULL DEFAULT 'all',
 ringseconds tinyint unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX callfilter__idx__context ON callfilter(context);
CREATE INDEX callfilter__idx__type ON callfilter(type);
CREATE INDEX callfilter__idx__bosssecretary ON callfilter(bosssecretary);
CREATE INDEX callfilter__idx__callfrom ON callfilter(callfrom);
CREATE INDEX callfilter__idx__commented ON callfilter(commented);
CREATE UNIQUE INDEX callfilter__uidx__name ON callfilter(name);


DROP TABLE callfiltermember;
CREATE TABLE callfiltermember (
 id integer unsigned,
 callfilterid integer unsigned NOT NULL DEFAULT 0,
 type char(4) NOT NULL DEFAULT 'user',
 typeval varchar(128) NOT NULL DEFAULT 0,
 ringseconds tinyint unsigned NOT NULL DEFAULT 0,
 priority tinyint unsigned NOT NULL DEFAULT 0,
 bstype varchar(9),
 active tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE INDEX callfiltermember__idx__priority ON callfiltermember(priority);
CREATE INDEX callfiltermember__idx__bstype ON callfiltermember(bstype);
CREATE INDEX callfiltermember__idx__active ON callfiltermember(active);
CREATE UNIQUE INDEX callfiltermember__uidx__callfilterid_type_typeval ON callfiltermember(callfilterid,type,typeval);


DROP TABLE cdr;
CREATE TABLE cdr (
 id integer unsigned,
 calldate char(19) DEFAULT '0000-00-00 00:00:00',
 clid varchar(80) NOT NULL DEFAULT '',
 src varchar(80) NOT NULL DEFAULT '',
 dst varchar(80) NOT NULL DEFAULT '',
 dcontext varchar(39) NOT NULL DEFAULT '',
 channel varchar(80) NOT NULL DEFAULT '',
 dstchannel varchar(80) NOT NULL DEFAULT '',
 lastapp varchar(80) NOT NULL DEFAULT '',
 lastdata varchar(80) NOT NULL DEFAULT '',
 answer char(19) DEFAULT '0000-00-00 00:00:00',
 end char(19) DEFAULT '0000-00-00 00:00:00',
 duration integer unsigned NOT NULL DEFAULT 0,
 billsec integer unsigned NOT NULL DEFAULT 0,
 disposition varchar(9) NOT NULL DEFAULT '',
 amaflags tinyint unsigned NOT NULL DEFAULT 0,
 accountcode varchar(20) NOT NULL DEFAULT '',
 uniqueid varchar(32) NOT NULL DEFAULT '',
 userfield varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

CREATE INDEX cdr__idx__calldate ON cdr(calldate);
CREATE INDEX cdr__idx__clid ON cdr(clid);
CREATE INDEX cdr__idx__src ON cdr(src);
CREATE INDEX cdr__idx__dst ON cdr(dst);
CREATE INDEX cdr__idx__channel ON cdr(channel);
CREATE INDEX cdr__idx__dstchannel ON cdr(dstchannel);
CREATE INDEX cdr__idx__duration ON cdr(duration);
CREATE INDEX cdr__idx__disposition ON cdr(disposition);
CREATE INDEX cdr__idx__amaflags ON cdr(amaflags);
CREATE INDEX cdr__idx__accountcode ON cdr(accountcode);
CREATE INDEX cdr__idx__userfield ON cdr(userfield);


DROP TABLE cel;
CREATE TABLE cel (
 id integer unsigned,
 eventtype varchar (30) NOT NULL,
 eventtime char(19) NOT NULL DEFAULT '0000-00-00 00:00:00',
 userdeftype varchar(255) NOT NULL,
 cid_name varchar (80) NOT NULL,
 cid_num varchar (80) NOT NULL,
 cid_ani varchar (80) NOT NULL,
 cid_rdnis varchar (80) NOT NULL,
 cid_dnid varchar (80) NOT NULL,
 exten varchar (80) NOT NULL,
 context varchar (80) NOT NULL,
 channame varchar (80) NOT NULL,
 appname varchar (80) NOT NULL,
 appdata varchar (80) NOT NULL,
 amaflags integer (10) NOT NULL,
 accountcode varchar (20) NOT NULL,
 peeraccount varchar (20) NOT NULL,
 uniqueid varchar (150) NOT NULL,
 linkedid varchar (150) NOT NULL,
 userfield varchar (255) NOT NULL,
 peer varchar (80) NOT NULL,
 PRIMARY KEY(id)
);


DROP TABLE context;
CREATE TABLE context (
 name varchar(39) NOT NULL,
 displayname varchar(128) NOT NULL DEFAULT '',
 entity varchar(64),
 contexttype varchar(40) NOT NULL DEFAULT 'internal',
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(name)
);

CREATE INDEX context__idx__displayname ON context(displayname);
CREATE INDEX context__idx__contexttype ON context(contexttype);
CREATE INDEX context__idx__entity ON context(entity);
CREATE INDEX context__idx__commented ON context(commented);


DROP TABLE contextinclude;
CREATE TABLE contextinclude (
 context varchar(39) NOT NULL,
 include varchar(39) NOT NULL,
 priority tinyint unsigned NOT NULL DEFAULT 0,
 PRIMARY KEY(context,include)
);

CREATE INDEX contextinclude__idx__context ON contextinclude(context);
CREATE INDEX contextinclude__idx__include ON contextinclude(include);
CREATE INDEX contextinclude__idx__priority ON contextinclude(priority);


DROP TABLE contextmember;
CREATE TABLE contextmember (
 context varchar(39) NOT NULL,
 type varchar(32) NOT NULL,
 typeval varchar(128) NOT NULL DEFAULT '',
 varname varchar(128) NOT NULL DEFAULT '',
 PRIMARY KEY(context,type,typeval,varname)
);

CREATE INDEX contextmember__idx__context ON contextmember(context);
CREATE INDEX contextmember__idx__context_type ON contextmember(context,type);


DROP TABLE contextnumbers;
CREATE TABLE contextnumbers (
 context varchar(39) NOT NULL,
 type varchar(6) NOT NULL,
 numberbeg varchar(16) NOT NULL DEFAULT '',
 numberend varchar(16) NOT NULL DEFAULT '',
 didlength tinyint unsigned NOT NULL DEFAULT 0,
 PRIMARY KEY(context,type,numberbeg,numberend)
);

CREATE INDEX contextnumbers__idx__context_type ON contextnumbers(context,type);


DROP TABLE contextnummember;
CREATE TABLE contextnummember (
 context varchar(39) NOT NULL,
 type varchar(6) NOT NULL,
 typeval varchar(128) NOT NULL DEFAULT 0,
 number varchar(40) NOT NULL DEFAULT '',
 PRIMARY KEY(context,type,typeval)
);

CREATE INDEX contextnummember__idx__context ON contextnummember(context);
CREATE INDEX contextnummember__idx__context_type ON contextnummember(context,type);
CREATE INDEX contextnummember__idx__number ON contextnummember(number);


DROP TABLE contexttype;
CREATE TABLE contexttype (
 id integer unsigned,
 name varchar(40) NOT NULL,
 displayname varchar(40) NOT NULL,
 commented integer,
 deletable integer,
 description text,
 PRIMARY KEY(id)
);

CREATE INDEX contexttype__idx__commented ON contexttype(commented);
CREATE INDEX contexttype__idx__deletable ON contexttype(deletable);
CREATE UNIQUE INDEX contexttype__uidx__name ON contexttype(name);

INSERT INTO contexttype VALUES(1, 'internal', 'Interne', 0, 0, '');
INSERT INTO contexttype VALUES(2, 'incall', 'Entrant', 0, 0, '');
INSERT INTO contexttype VALUES(3, 'outcall', 'Sortant', 0, 0, '');
INSERT INTO contexttype VALUES(4, 'services', 'Services', 0, 0, '');
INSERT INTO contexttype VALUES(5, 'others', 'Autres', 0, 0, '');


DROP TABLE ctiaccounts;
CREATE TABLE ctiaccounts (
 login varchar(64) NOT NULL,
 password varchar(64) NOT NULL,
 label varchar(128) NOT NULL,
 PRIMARY KEY(login)
);


DROP TABLE ctilog;
CREATE TABLE ctilog (
 id integer unsigned,
 eventdate char(19) DEFAULT '0000-00-00 00:00:00',
 loginclient varchar(64),
 company varchar(64),
 status varchar(64),
 action varchar(64),
 arguments varchar(255),
 callduration integer unsigned,
 PRIMARY KEY(id)
);


DROP TABLE cticontexts;
CREATE TABLE cticontexts (
 id integer unsigned,
 name varchar(50),
 directories text NOT NULL,
 display text NOT NULL,
 description text NOT NULL,
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO cticontexts VALUES(3,'default','xivodir,internal','Display','Contexte par défaut',1);


DROP TABLE ctidirectories;
CREATE TABLE ctidirectories (
 id integer unsigned,
 name varchar(255),
 uri varchar(255),
 delimiter varchar(20),
 match_direct text NOT NULL,
 match_reverse text NOT NULL,
 description varchar(255),
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO ctidirectories VALUES(1,'xivodir', 'phonebook', '', '[phonebook.firstname,phonebook.lastname,phonebook.displayname,phonebook.society,phonebooknumber.office.number]','[phonebooknumber.office.number,phonebooknumber.mobile.number]','Répertoire XiVO Externe',1);
INSERT INTO ctidirectories VALUES(2,'internal','internal','','[userfeatures.firstname,userfeatures.lastname]','','Répertoire XiVO Interne',1);


DROP TABLE ctidirectoryfields;
CREATE TABLE ctidirectoryfields (
 dir_id INTEGER,
 fieldname varchar(255),
 value varchar(255),
 PRIMARY KEY(dir_id, fieldname)
);

INSERT INTO ctidirectoryfields VALUES(1, 'phone', 'phonebooknumber.office.number');
INSERT INTO ctidirectoryfields VALUES(1, 'firstname', 'phonebook.firstname');
INSERT INTO ctidirectoryfields VALUES(1, 'lastname', 'phonebook.lastname');
INSERT INTO ctidirectoryfields VALUES(1, 'fullname', 'phonebook.fullname');
INSERT INTO ctidirectoryfields VALUES(1, 'company', 'phonebook.society');
INSERT INTO ctidirectoryfields VALUES(1, 'mail', 'phonebook.email');
INSERT INTO ctidirectoryfields VALUES(1, 'reverse', 'phonebook.fullname');
INSERT INTO ctidirectoryfields VALUES(2, 'firstname', 'userfeatures.firstname');
INSERT INTO ctidirectoryfields VALUES(2, 'lastname', 'userfeatures.lastname');
INSERT INTO ctidirectoryfields VALUES(2, 'phone', 'userfeatures.number');


DROP TABLE ctidisplays;
CREATE TABLE ctidisplays (
 id integer unsigned,
 name varchar(50),
 data text NOT NULL,
 deletable tinyint(1),
 description text NOT NULL,
 PRIMARY KEY(id)
);

INSERT INTO ctidisplays VALUES(4,'Display','{10: [ Nom,,,{db-firstname} {db-lastname} ],20: [ Numéro,phone,,{db-phone} ],30: [ Entreprise,,Inconnue,{db-company} ],40: [ E-mail,,,{db-mail} ],50: [ Source,,,{xivo-directory} ]}',1,'Affichage par défaut');


DROP TABLE ctimain;
CREATE TABLE ctimain (
 id integer unsigned,
 commandset varchar(20),
 ami_ip varchar(16),
 ami_port INTEGER,
 ami_login varchar(64),
 ami_password varchar(64),
 fagi_ip varchar(255),
 fagi_port integer unsigned,
 cti_ip varchar(255),
 cti_port integer unsigned,
 ctis_ip varchar(16),
 ctis_port INTEGER,
 webi_ip varchar(255),
 webi_port integer unsigned,
 info_ip varchar(255),
 info_port integer unsigned,
 announce_ip varchar(255),
 announce_port integer unsigned,
 asterisklist varchar(255),
 updates_period integer unsigned,
 socket_timeout integer unsigned,
 login_timeout integer unsigned,
 parting_astid_context varchar(255),
 PRIMARY KEY(id)
);

INSERT INTO ctimain VALUES(1, 'xivocti', '127.0.0.1', 5038, 'xivo_cti_user', 'phaickbebs9', '0.0.0.0', 5002, '0.0.0.0', 5003, '0.0.0.0', 5013, '127.0.0.1', 5004, '127.0.0.1', 5005, '127.0.0.1', 5006, 1, 3600, 10, 5, 'context');


DROP TABLE ctiphonehints;
CREATE TABLE ctiphonehints (
 id integer unsigned,
 idgroup integer,
 number integer,
 name varchar(255),
 color varchar(128),
 PRIMARY KEY(id)
);

INSERT INTO ctiphonehints VALUES(1,1,-2,'Inexistant','#030303');
INSERT INTO ctiphonehints VALUES(2,1,-1,'Désactivé','#000000');
INSERT INTO ctiphonehints VALUES(3,1,0,'Disponible','#0DFF25');
INSERT INTO ctiphonehints VALUES(4,1,1,'En ligne OU appelle','#FF032D');
INSERT INTO ctiphonehints VALUES(5,1,2,'Occupé','#FF0008');
INSERT INTO ctiphonehints VALUES(6,1,4,'Indisponible','#FFFFFF');
INSERT INTO ctiphonehints VALUES(7,1,8,'Sonne','#1B0AFF');
INSERT INTO ctiphonehints VALUES(8,1,9,'(En Ligne OU Appelle) ET Sonne','#FF0526');
INSERT INTO ctiphonehints VALUES(9,1,16,'En Attente','#F7FF05');


DROP TABLE ctiphonehintsgroup;
CREATE TABLE ctiphonehintsgroup (
 id INTEGER UNSIGNED,
 name varchar(255),
 description varchar(255),
 deletable INTEGER, -- BOOLEAN
 PRIMARY KEY(id)
);

INSERT INTO ctiphonehintsgroup VALUES(1,'xivo','De base non supprimable',0);


DROP TABLE ctipresences;
CREATE TABLE ctipresences (
 id integer unsigned,
 name varchar(255),
 description varchar(255),
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO ctipresences VALUES(1,'xivo','De base non supprimable',0);


DROP TABLE ctiprofiles;
CREATE TABLE ctiprofiles (
 id integer unsigned,
 xlets text,
 funcs varchar(255),
 maxgui integer,
 appliname varchar(255),
 name varchar(40) unique,
 presence varchar(255),
 services varchar(255),
 preferences varchar(2048),
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO ctiprofiles VALUES(9,'[[ queues, dock, fms, N/A ],[ queuedetails, dock, fms, N/A ],[ queueentrydetails, dock, fcms, N/A ],[ agents, dock, fcms, N/A ],[ agentdetails, dock, fcms, N/A ],[ identity, grid, fcms, 0 ],[ conference, dock, fcm, N/A ]]','agents,presence,switchboard',-1,'Superviseur','agentsup','xivo','','',1);
INSERT INTO ctiprofiles VALUES(10,'[[ queues, dock, ms, N/A ],[ identity, grid, fcms, 0 ],[ customerinfo, dock, cms, N/A ],[ agentdetails, dock, cms, N/A ]]','presence',-1,'Agent','agent','xivo','','',1);
INSERT INTO ctiprofiles VALUES(11,'[[ tabber, grid, fcms, 1 ],[ dial, grid, fcms, 2 ],[ search, tab, fcms, 0 ],[ customerinfo, tab, fcms, 4 ],[ identity, grid, fcms, 0 ],[ fax, tab, fcms, N/A ],[ history, tab, fcms, N/A ],[ directory, tab, fcms, N/A ],[ features, tab, fcms, N/A ],[ mylocaldir, tab, fcms, N/A ],[ conference, tab, fcms, N/A ]]','presence,customerinfo',-1,'Client','client','xivo','','',1);
INSERT INTO ctiprofiles VALUES(12,'[[ tabber, grid, fcms, 1 ],[ dial, grid, fcms, 2 ],[ search, tab, fcms, 0 ],[ customerinfo, tab, fcms, 4 ],[ identity, grid, fcms, 0 ],[ fax, tab, fcms, N/A ],[ history, tab, fcms, N/A ],[ directory, tab, fcms, N/A ],[ features, tab, fcms, N/A ],[ mylocaldir, tab, fcms, N/A ],[ conference, tab, fcms, N/A ],[ outlook, tab, fcms, N/A ]]','presence,customerinfo',-1,'Client+Outlook','clientoutlook','xivo','','',1);
INSERT INTO ctiprofiles VALUES(13,'[[ datetime, dock, fm, N/A ]]','',-1,'Horloge','clock','xivo','','',1);
INSERT INTO ctiprofiles VALUES(14,'[[ dial, dock, fm, N/A ],[ operator, dock, fcm, N/A ],[ datetime, dock, fcm, N/A ],[ identity, grid, fcms, 0 ],[ calls, dock, fcm, N/A ],[ parking, dock, fcm, N/A ]]','presence,switchboard,search,dial',-1,'Opérateur','oper','xivo','','',1);
INSERT INTO ctiprofiles VALUES(15,'[[ parking, dock, fcms, N/A ],[ search, dock, fcms, N/A ],[ calls, dock, fcms, N/A ],[ switchboard, dock, fcms, N/A ],[ customerinfo, dock, fcms, N/A ],[ datetime, dock, fcms, N/A ],[ dial, dock, fcms, N/A ],[ identity, grid, fcms, 0 ],[ operator, dock, fcms, N/A ]]','switchboard,dial,presence,customerinfo,search,agents,conference,directory,features,history,fax,chitchat,database','','Switchboard','switchboard','xivo','','',1);



DROP TABLE ctireversedirectories;
CREATE TABLE ctireversedirectories (
 id integer unsigned,
 context varchar(50),
 extensions  text NOT NULL,
 directories text NOT NULL,
 description text NOT NULL,
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO ctireversedirectories VALUES(1,'*', '*', '[xivodir]','Répertoires XiVO',1);


DROP TABLE ctisheetactions;
CREATE TABLE ctisheetactions (
 id integer unsigned,
 name varchar(50),
 description text NOT NULL,
 context varchar(50),
 whom varchar(50),
 capaids text NOT NULL,
 sheet_info text,
 systray_info text,
 sheet_qtui text,
 action_info text,
 focus tinyint(1),
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO ctisheetactions VALUES(6,'dial','','[default]','dest','[agentsup,agent,client]','{10: [ ,text,Inconnu,Appel {xivo-direction} de {xivo-calleridnum} ],20: [ Numéro entrant,phone,Inconnu,{xivo-calleridnum} ],30: [ Nom,text,Inconnu,{db-fullname} ],40: [ Numéro appelé,phone,Inconnu,{xivo-calledidnum} ]}','{10: [ ,title,,Appel {xivo-direction} ],20: [ ,body,Inconnu,appel de {xivo-calleridnum} pour {xivo-calledidnum} ],30: [ ,body,Inconnu,{db-fullname} (selon {xivo-directory}) ],40: [ ,body,,le {xivo-date}, il est {xivo-time} ]}','','{}',0,1);
INSERT INTO ctisheetactions VALUES(7,'queue','','[default]','dest','[agentsup,agent,client]','{10: [ ,text,Inconnu,Appel {xivo-direction} de la File {xivo-queuename} ],20: [ Numéro entrant,phone,Inconnu,{xivo-calleridnum} ],30: [ Nom,text,Inconnu,{db-fullname} ]}','{10: [ ,title,,Appel {xivo-direction} de la File {xivo-queuename} ],20: [ ,body,Inconnu,appel de {xivo-calleridnum} pour {xivo-calledidnum} ],30: [ ,body,Inconnu,{db-fullname} (selon {xivo-directory}) ],40: [ ,body,,le {xivo-date}, il est {xivo-time} ]}','file:///etc/pf-xivo/ctiservers/form.ui','{}',0,1);
INSERT INTO ctisheetactions VALUES(8,'custom1','','[default]','all','[agentsup,agent,client]','{10: [ ,text,Inconnu,Appel {xivo-direction} (Custom) ],20: [ Numéro entrant,phone,Inconnu,{xivo-calleridnum} ],30: [ Nom,text,Inconnu,{db-fullname} ]}','{10: [ ,title,,Appel {xivo-direction} (Custom) ],20: [ ,body,Inconnu,appel de {xivo-calleridnum} pour {xivo-calledidnum} ],30: [ ,body,Inconnu,{db-fullname} (selon {xivo-directory}) ],40: [ ,body,,le {xivo-date}, il est {xivo-time} ]}','','{}',0,1);


DROP TABLE ctisheetevents;
CREATE TABLE ctisheetevents (
 id integer unsigned,
 agentlinked varchar(50),
 agentunlinked varchar(50),
 faxreceived varchar(50),
 incomingqueue varchar(50),
 incominggroup varchar(50),
 incomingdid varchar(50),
 dial varchar(50),
 link varchar(50),
 unlink varchar(50),
 custom text NOT NULL,
 PRIMARY KEY(id)
);

INSERT INTO ctisheetevents VALUES(1,'','','','','','','dial','','','{custom-example1: custom1}');


DROP TABLE ctistatus;
CREATE TABLE ctistatus (
 id integer unsigned,
 presence_id integer unsigned,
 name varchar(255),
 display_name varchar(255),
 actions varchar(255),
 color varchar(20),
 access_status varchar(255),
 deletable tinyint(1),
 PRIMARY KEY(id)
);

INSERT INTO ctistatus VALUES(1,1,'available','Disponible','enablednd(false)','#08FD20','1,2,3,4,5',1);
INSERT INTO ctistatus VALUES(2,1,'away','Sorti','enablednd(true)','#FDE50A','1,2,3,4,5',1);
INSERT INTO ctistatus VALUES(3,1,'outtolunch','Parti Manger','enablednd(true)','#001AFF','1,2,3,4,5',1);
INSERT INTO ctistatus VALUES(4,1,'donotdisturb','Ne pas déranger','enablednd(true)','#FF032D','1,2,3,4,5',1);
INSERT INTO ctistatus VALUES(5,1,'berightback','Bientôt de retour','enablednd(true)','#FFB545','1,2,3,4,5',1);


DROP TABLE devicefeatures;
CREATE TABLE devicefeatures (
 id integer unsigned,
 mac varchar(17) NOT NULL,
 vendor varchar(16) NOT NULL,
 model varchar(16) NOT NULL,
 proto varchar(50) NOT NULL,
 sn varchar(128),
 ip varchar(39),
 version varchar(128),
 plugin varchar(128),
 config varchar(64),
 deviceid varchar(32) NOT NULL,
 internal integer DEFAULT 0 NOT NULL,
 configured integer DEFAULT 0 NOT NULL,
 commented integer DEFAULT 0 NOT NULL,
 description text,
 PRIMARY KEY(id)
);

CREATE INDEX devicefeatures__idx__mac ON devicefeatures(mac);
CREATE INDEX devicefeatures__idx__ip ON devicefeatures(ip);
CREATE INDEX devicefeatures__idx__plugin ON devicefeatures(plugin);
CREATE INDEX devicefeatures__idx__config ON devicefeatures(config);
CREATE INDEX devicefeatures__idx__deviceid ON devicefeatures(deviceid);


DROP TABLE dialaction;
CREATE TABLE dialaction (
 event varchar(11) NOT NULL,
 category varchar(10) NOT NULL,
 categoryval varchar(128) NOT NULL DEFAULT '',
 action varchar(64) NOT NULL DEFAULT 'none',
 actionarg1 varchar(255) DEFAULT NULL,
 actionarg2 varchar(255) DEFAULT NULL,
 linked tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(event,category,categoryval)
);

CREATE INDEX dialaction__idx__action_actionarg1 ON dialaction(action,actionarg1);
CREATE INDEX dialaction__idx__actionarg2 ON dialaction(actionarg2);
CREATE INDEX dialaction__idx__linked ON dialaction(linked);


DROP TABLE dialpattern;
CREATE TABLE dialpattern (
 id INTEGER UNSIGNED,
 type varchar(32) NOT NULL,
 typeid integer NOT NULL,
 externprefix varchar(64),
 prefix varchar(32),
 exten varchar(40) NOT NULL,
 stripnum integer,
 emergency integer,
 setcallerid integer NOT NULL DEFAULT 0,
 callerid varchar(80),
 PRIMARY KEY(id)
);

CREATE INDEX dialpattern__idx__type_typeid ON dialpattern(type,typeid);


DROP TABLE extensions;
CREATE TABLE extensions (
 id integer unsigned,
 commented tinyint(1) NOT NULL DEFAULT 0,
 context varchar(39) NOT NULL DEFAULT '',
 exten varchar(40) NOT NULL DEFAULT '',
 priority tinyint unsigned NOT NULL DEFAULT 0,
 app varchar(128) NOT NULL DEFAULT '',
 appdata varchar(128) NOT NULL DEFAULT '',
 name varchar(128) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

CREATE INDEX extensions__idx__commented ON extensions(commented);
CREATE INDEX extensions__idx__context_exten_priority ON extensions(context,exten,priority);
CREATE INDEX extensions__idx__name ON extensions(name);

INSERT INTO extensions VALUES (NULL,1,'xivo-features','_*33.',1,'GoSub','agentdynamiclogin,s,1(${EXTEN:3})','agentdynamiclogin');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','_*31.',1,'GoSub','agentstaticlogin,s,1(${EXTEN:3})','agentstaticlogin');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','_*32.',1,'GoSub','agentstaticlogoff,s,1(${EXTEN:3})','agentstaticlogoff');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','_*30.',1,'GoSub','agentstaticlogtoggle,s,1(${EXTEN:3})','agentstaticlogtoggle');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*37.',1,'GoSub','bsfilter,s,1(${EXTEN:3})','bsfilter');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*664.',1,'GoSub','group,s,1(${EXTEN:4})','callgroup');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','*34',1,'GoSub','calllistening,s,1','calllistening');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*667.',1,'GoSub','meetme,s,1(${EXTEN:4})','callmeetme');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*665.',1,'GoSub','queue,s,1(${EXTEN:4})','callqueue');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','*26',1,'GoSub','callrecord,s,1','callrecord');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*666.',1,'GoSub','user,s,1(${EXTEN:4})','calluser');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*36',1,'Directory','${CONTEXT}','directoryaccess');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*25',1,'GoSub','enablednd,s,1','enablednd');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*90',1,'GoSub','enablevm,s,1','enablevm');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*91',1,'GoSub','enablevmbox,s,1','enablevmbox');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*91.',1,'GoSub','enablevmbox,s,1(${EXTEN:3})','enablevmboxslt');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*90.',1,'GoSub','enablevm,s,1(${EXTEN:3})','enablevmslt');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*23.',1,'GoSub','feature_forward,s,1(busy,${EXTEN:3})','fwdbusy');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*22.',1,'GoSub','feature_forward,s,1(rna,${EXTEN:3})','fwdrna');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*21.',1,'GoSub','feature_forward,s,1(unc,${EXTEN:3})','fwdunc');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*20',1,'GoSub','fwdundoall,s,1','fwdundoall');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*51.',1,'GoSub','groupmember,s,1(group,add,${EXTEN:3})','groupaddmember');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*52.',1,'GoSub','groupmember,s,1(group,remove,${EXTEN:3})','groupremovemember');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*50.',1,'GoSub','groupmember,s,1(group,toggle,${EXTEN:3})','grouptogglemember');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*48378',1,'GoSub','autoprovprov,s,1','autoprovprov');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*27',1,'GoSub','incallfilter,s,1','incallfilter');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*10',1,'GoSub','phonestatus,s,1','phonestatus');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*735.',1,'GoSub','phoneprogfunckey,s,1(${EXTEN:0:4},${EXTEN:4})','phoneprogfunckey');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*8.',1,'Pickup','${EXTEN:2}%${CONTEXT}@PICKUPMARK','pickup');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*56.',1,'GoSub','groupmember,s,1(queue,add,${EXTEN:3})','queueaddmember');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*57.',1,'GoSub','groupmember,s,1(queue,remove,${EXTEN:3})','queueremovemember');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*55.',1,'GoSub','groupmember,s,1(queue,toggle,${EXTEN:3})','queuetogglemember');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*9',1,'GoSub','recsnd,s,1(wav)','recsnd');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*99.',1,'GoSub','vmboxmsg,s,1(${EXTEN:3})','vmboxmsgslt');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','_*93.',1,'GoSub','vmboxpurge,s,1(${EXTEN:3})','vmboxpurgeslt');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*97.',1,'GoSub','vmbox,s,1(${EXTEN:3})','vmboxslt');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*98',1,'GoSub','vmusermsg,s,1','vmusermsg');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','*92',1,'GoSub','vmuserpurge,s,1','vmuserpurge');
INSERT INTO extensions VALUES (NULL,1,'xivo-features','_*92.',1,'GoSub','vmuserpurge,s,1(${EXTEN:3})','vmuserpurgeslt');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*96.',1,'GoSub','vmuser,s,1(${EXTEN:3})','vmuserslt');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','_*11.',1,'GoSub','paging,s,1(${EXTEN:3})','paging');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*14',1,'GoSub','alarmclk-set,s,1','alarmclk-set');
INSERT INTO extensions VALUES (NULL,0,'xivo-features','*15',1,'GoSub','alarmclk-clear,s,1','alarmclk-clear');


DROP TABLE extenumbers;
CREATE TABLE extenumbers (
 id integer unsigned,
 exten varchar(40) NOT NULL DEFAULT '',
 extenhash char(40) NOT NULL DEFAULT '',
 context varchar(39) NOT NULL,
 type varchar(64) NOT NULL DEFAULT '',
 typeval varchar(255) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

CREATE INDEX extenumbers__idx__exten ON extenumbers(exten);
CREATE INDEX extenumbers__idx__extenhash ON extenumbers(extenhash);
CREATE INDEX extenumbers__idx__context ON extenumbers(context);
CREATE INDEX extenumbers__idx__type ON extenumbers(type);
CREATE INDEX extenumbers__idx__typeval ON extenumbers(typeval);

INSERT INTO extenumbers VALUES (NULL,'*8','aa5820277564fac26df0e3dc72f796407597721d','','generalfeatures','pickupexten');
INSERT INTO extenumbers VALUES (NULL,'700','d8e4bbea3af2e4861ad5a445aaec573e02f9aca2','','generalfeatures','parkext');
INSERT INTO extenumbers VALUES (NULL,'*0','e914c907ff6d7a8ffefae72fe47363726b39d112','','featuremap','disconnect');
INSERT INTO extenumbers VALUES (NULL,'*1','8e04e82b8798d3979eded4ca2afdda3bebcb963d','','featuremap','blindxfer');
INSERT INTO extenumbers VALUES (NULL,'*2','6951109c8ca021277336cc2c8f6ac7f47d3b30e9','','featuremap','atxfer');
INSERT INTO extenumbers VALUES (NULL,'*3','68631b4b53ba2a27a969ca63bdcdc00805c2c258','','featuremap','automon');
INSERT INTO extenumbers VALUES (NULL,'_*33.','269371911e5bac9176919fa42e66814882c496e1','','extenfeatures','agentdynamiclogin');
INSERT INTO extenumbers VALUES (NULL,'_*31.','678fe23ee0d6aa64460584bebbed210e270d662f','','extenfeatures','agentstaticlogin');
INSERT INTO extenumbers VALUES (NULL,'_*32.','3ae0f1ff0ef4907faa2dad5da7bb891c9dbf45ad','','extenfeatures','agentstaticlogoff');
INSERT INTO extenumbers VALUES (NULL,'_*30.','7758898081b262cc0e42aed23cf601fba8969b08','','extenfeatures','agentstaticlogtoggle');
INSERT INTO extenumbers VALUES (NULL,'_*37.','249b00b17a5983bbb2af8ed0af2ab1a74abab342','','extenfeatures','bsfilter');
INSERT INTO extenumbers VALUES (NULL,'_*664.','9dfe780f1dc7fccbfc841b41a38933d4dab56369','','extenfeatures','callgroup');
INSERT INTO extenumbers VALUES (NULL,'*34','668a8d2d8fe980b663e2cdcecb977860e1b272f3','','extenfeatures','calllistening');
INSERT INTO extenumbers VALUES (NULL,'_*667.','666f6f18439eb7f205b5932d7f9aef6d2e5ba9a3','','extenfeatures','callmeetme');
INSERT INTO extenumbers VALUES (NULL,'_*665.','7e2df45aedebded219eaa5fb84d6db7e8e24fc66','','extenfeatures','callqueue');
INSERT INTO extenumbers VALUES (NULL,'*26','f8aeb70618cc87f1143c7dff23cdc0d3d0a48a0c','','extenfeatures','callrecord');
INSERT INTO extenumbers VALUES (NULL,'_*666.','d7b68f456ddb50215670c5bfca921176a21c4270','','extenfeatures','calluser');
INSERT INTO extenumbers VALUES (NULL,'*36','f9b69fe3c361ddfc2ae49e048460ea197ea850c8','','extenfeatures','directoryaccess');
INSERT INTO extenumbers VALUES (NULL,'*25','c0d236c38bf8d5d84a2e154203cd2a18b86c6b2a','','extenfeatures','enablednd');
INSERT INTO extenumbers VALUES (NULL,'*90','2fc9fcda52bd8293da1bfa68cbdb8974fafd409e','','extenfeatures','enablevm');
INSERT INTO extenumbers VALUES (NULL,'*91','880d3330b465056ede825e1fbc8ceb50fd816e1d','','extenfeatures','enablevmbox');
INSERT INTO extenumbers VALUES (NULL,'_*91.','936ec7abe6019d9d47d8be047ef6fc0ebc334c00','','extenfeatures','enablevmboxslt');
INSERT INTO extenumbers VALUES (NULL,'_*90.','9fdaa61ea338dcccf1450949cbf6f7f99f1ccc54','','extenfeatures','enablevmslt');
INSERT INTO extenumbers VALUES (NULL,'_*23.','a1968a70f1d265b8aa263e73c79259961c4f7bbb','','extenfeatures','fwdbusy');
INSERT INTO extenumbers VALUES (NULL,'_*22.','00638af9e028d4cd454c00f43caf5626baa7d84c','','extenfeatures','fwdrna');
INSERT INTO extenumbers VALUES (NULL,'_*21.','52c97d56ebcca524ccf882590e94c52f6db24649','','extenfeatures','fwdunc');
INSERT INTO extenumbers VALUES (NULL,'*20','934aca632679075488681be0e9904cf9102f8766','','extenfeatures','fwdundoall');
INSERT INTO extenumbers VALUES (NULL,'_*51.','fd3d50358d246ab2fbc32e14056e2f559d054792','','extenfeatures','groupaddmember');
INSERT INTO extenumbers VALUES (NULL,'_*52.','069a278d266d0cf2aa7abf42a732fc5ad109a3e6','','extenfeatures','groupremovemember');
INSERT INTO extenumbers VALUES (NULL,'_*50.','53f7e7fa7fbbabb1245ed8dedba78da442a8659f','','extenfeatures','grouptogglemember');
INSERT INTO extenumbers VALUES (NULL,'*48378','e27276ceefcc71a5d2def28c9b59a6410959eb43','','extenfeatures','autoprovprov');
INSERT INTO extenumbers VALUES (NULL,'*27','663b9615ba92c21f80acac52d60b28a8d1fb1c58','','extenfeatures','incallfilter');
INSERT INTO extenumbers VALUES (NULL,'_*735.','32e9b3597f8b9cd2661f0c3d3025168baafca7e6','','extenfeatures','phoneprogfunckey');
INSERT INTO extenumbers VALUES (NULL,'*10','eecefbd85899915e6fc2ff5a8ea44c2c83597cd6','','extenfeatures','phonestatus');
INSERT INTO extenumbers VALUES (NULL,'_*8.','b349d094036a97a7e0631ba60de759a9597c1c3a','','extenfeatures','pickup');
INSERT INTO extenumbers VALUES (NULL,'_*56.','95d84232b10af6f6905dcd22f4261a4550461c7d','','extenfeatures','queueaddmember');
INSERT INTO extenumbers VALUES (NULL,'_*57.','3ad1e945e85735f6417e5a0aba7fde3bc9d2ffec','','extenfeatures','queueremovemember');
INSERT INTO extenumbers VALUES (NULL,'_*55.','f8085e23f56e5433006483dee5fe3db8c94a0a06','','extenfeatures','queuetogglemember');
INSERT INTO extenumbers VALUES (NULL,'*9','e28d0f359da60dcf86340435478b19388b1b1d05','','extenfeatures','recsnd');
INSERT INTO extenumbers VALUES (NULL,'_*99.','6c92223f2ea0cfd9fad3db2f288ebdc9c64dc8f5','','extenfeatures','vmboxmsgslt');
INSERT INTO extenumbers VALUES (NULL,'_*93.','7d891f90799fd6cb5bc85c4bd227a3357096be8f','','extenfeatures','vmboxpurgeslt');
INSERT INTO extenumbers VALUES (NULL,'_*97.','8bdbf6703cf5225aad457422afdda738b9bd628c','','extenfeatures','vmboxslt');
INSERT INTO extenumbers VALUES (NULL,'*98','6fb653e9eaf6f4d9c8d2cb48d1a6e3f4d4085710','','extenfeatures','vmusermsg');
INSERT INTO extenumbers VALUES (NULL,'*92','97f991a4ffd7fa843bc0ca3bdc730851382c5cdf','','extenfeatures','vmuserpurge');
INSERT INTO extenumbers VALUES (NULL,'_*92.','36711086667cbfc27488236e0e0fdd2d7f896f6b','','extenfeatures','vmuserpurgeslt');
INSERT INTO extenumbers VALUES (NULL,'_*96.','ac6c7ac899867fe0120fe20120fae163012615f2','','extenfeatures','vmuserslt');
INSERT INTO extenumbers VALUES (NULL,'_*11.','0a038e5c4e6e33baee9f210b9a4f7e313f3e79fa','','extenfeatures','paging');
INSERT INTO extenumbers VALUES (NULL,'*14','7b32828c56cbc865729669a824d098c1e6584ae9','','extenfeatures','alarmclk-set');
INSERT INTO extenumbers VALUES (NULL,'*15','509d0dd56f5acd077613872f49e1dab759b1a435','','extenfeatures','alarmclk-clear');


DROP TABLE features;
CREATE TABLE features (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(255),
 PRIMARY KEY(id)
);

CREATE INDEX features__idx__commented ON features(commented);
CREATE INDEX features__idx__filename ON features(filename);
CREATE INDEX features__idx__category ON features(category);
CREATE INDEX features__idx__var_name ON features(var_name);

INSERT INTO features VALUES (NULL,0,0,0,'features.conf','general','parkext','700');
INSERT INTO features VALUES (NULL,0,0,0,'features.conf','general','parkpos','701-750');
INSERT INTO features VALUES (NULL,0,0,0,'features.conf','general','context','parkedcalls');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkinghints','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkingtime','45');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','comebacktoorigin','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','courtesytone',NULL);
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkedplay','caller');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkedcalltransfers','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkedcallreparking','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkedcallhangup','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkedcallrecording','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkeddynamic','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','adsipark','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','findslot','next');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','parkedmusicclass','default');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','transferdigittimeout','3');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','xfersound',NULL);
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','xferfailsound',NULL);
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','pickupexten','*8');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','pickupsound','');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','pickupfailsound','');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','featuredigittimeout','500');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','atxfernoanswertimeout','15');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','atxferdropcall','no');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','atxferloopdelay','10');
INSERT INTO features VALUES (NULL,0,0,1,'features.conf','general','atxfercallbackretries','2');
INSERT INTO features VALUES (NULL,1,0,0,'features.conf','featuremap','blindxfer','#1');
INSERT INTO features VALUES (NULL,1,0,0,'features.conf','featuremap','disconnect','*0');
INSERT INTO features VALUES (NULL,1,0,0,'features.conf','featuremap','automon','*1');
INSERT INTO features VALUES (NULL,1,0,0,'features.conf','featuremap','atxfer','*2');
INSERT INTO features VALUES (NULL,1,0,0,'features.conf','featuremap','parkcall','#72');
INSERT INTO features VALUES (NULL,1,0,0,'features.conf','featuremap','automixmon','*3');


DROP TABLE paging;
CREATE TABLE paging (
 id		 		INTEGER UNSIGNED,
 number 			VARCHAR(32),
 duplex 			INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 ignore 			INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 record 			INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 quiet 			INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 callnotbusy 		INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 timeout 			INTEGER NOT NULL,
 announcement_file VARCHAR(64),
 announcement_play INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 announcement_caller INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 commented 		INTEGER NOT NULL DEFAULT 0, -- BOOLEAN,
 description 		text,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX paging__uidx__number ON paging(number);

DROP TABLE paginguser;
CREATE TABLE paginguser (
 pagingid 		INTEGER NOT NULL,
 userfeaturesid 	INTEGER NOT NULL,
 caller 			INTEGER NOT NULL, -- BOOLEAN
 PRIMARY KEY(pagingid,userfeaturesid,caller)
);

CREATE INDEX paginguser__idx__pagingid ON paginguser(pagingid);
CREATE INDEX paginguser__idx__userfeaturesid ON paginguser(userfeaturesid);
CREATE INDEX paginguser__idx__caller ON paginguser(caller);


DROP TABLE parkinglot;
CREATE TABLE parkinglot (
 id            INTEGER UNSIGNED,
 name          VARCHAR(255) NOT NULL,
 context       VARCHAR(39) NOT NULL,       -- SHOULD BE A REF TO CONTEXT TABLE IN 2.0
 extension     VARCHAR(40) NOT NULL,
 positions     INTEGER NOT NULL,           -- NUMBER OF POSITIONS, (positions starts at extension + 1)
 next          INTEGER NOT NULL DEFAULT 1, -- BOOLEAN
 duration      INTEGER DEFAULT NULL,
 
 calltransfers VARCHAR(8) DEFAULT NULL,
 callreparking VARCHAR(8) DEFAULT NULL,
 callhangup    VARCHAR(8) DEFAULT NULL,
 callrecording VARCHAR(8) DEFAULT NULL,
 musicclass    VARCHAR(255) DEFAULT NULL,
 hints         INTEGER    NOT NULL DEFAULT 0, -- BOOLEAN

 commented     INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 description   TEXT NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX parkinglot__idx__name ON parkinglot(name);


DROP TABLE groupfeatures;
CREATE TABLE groupfeatures (
 id tinyint unsigned NOT NULL,
 name varchar(128) NOT NULL,
 number varchar(40) NOT NULL DEFAULT '',
 context varchar(39) NOT NULL,
 transfer_user tinyint(1) NOT NULL DEFAULT 0,
 transfer_call tinyint(1) NOT NULL DEFAULT 0,
 write_caller tinyint(1) NOT NULL DEFAULT 0,
 write_calling tinyint(1) NOT NULL DEFAULT 0,
 timeout tinyint unsigned NOT NULL DEFAULT 0,
 preprocess_subroutine varchar(39),
 deleted tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE INDEX groupfeatures__idx__name ON groupfeatures(name);
CREATE INDEX groupfeatures__idx__number ON groupfeatures(number);
CREATE INDEX groupfeatures__idx__context ON groupfeatures(context);
CREATE INDEX groupfeatures__idx__deleted ON groupfeatures(deleted);


DROP TABLE incall;
CREATE TABLE incall (
 id integer unsigned,
 exten varchar(40) NOT NULL,
 context varchar(39) NOT NULL,
 preprocess_subroutine varchar(39),
 faxdetectenable tinyint(1) NOT NULL DEFAULT 0,
 faxdetecttimeout tinyint unsigned NOT NULL DEFAULT 4,
 faxdetectemail varchar(255) NOT NULL DEFAULT '',
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX incall__idx__exten ON incall(exten);
CREATE INDEX incall__idx__context ON incall(context);
CREATE INDEX incall__idx__commented ON incall(commented);
CREATE UNIQUE INDEX incall__uidx__exten_context ON incall(exten,context);


DROP TABLE linefeatures;
CREATE TABLE linefeatures (
 id integer unsigned,
 protocol varchar(50) NOT NULL,
 protocolid integer unsigned NOT NULL,
 iduserfeatures integer unsigned DEFAULT 0,
 config varchar(128),
 device varchar(32),
 configregistrar varchar(128),
 name varchar(20) NOT NULL,
 number varchar(40),
 context varchar(39) NOT NULL,
 provisioningid char(6) NOT NULL,
 rules_type varchar(16),
 rules_time varchar(8),
 rules_order tinyint(3) DEFAULT 0,
 rules_group varchar(16),
 num INTEGER DEFAULT 0,
 line_num INTEGER DEFAULT 0,
 ipfrom varchar(15),
 internal tinyint(1) NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text,
 PRIMARY KEY(id)
);

CREATE INDEX linefeatures__idx__iduserfeatures ON linefeatures(iduserfeatures);
CREATE INDEX linefeatures__idx__line_num ON linefeatures(line_num);
CREATE INDEX linefeatures__idx__config ON linefeatures(config);
CREATE INDEX linefeatures__idx__device ON linefeatures(device);
CREATE INDEX linefeatures__idx__number ON linefeatures(number);
CREATE INDEX linefeatures__idx__context ON linefeatures(context);
CREATE INDEX linefeatures__idx__commented ON linefeatures(commented);
CREATE INDEX linefeatures__idx__internal ON linefeatures(internal);
CREATE UNIQUE INDEX linefeatures__uidx__provisioningid ON linefeatures(provisioningid);
CREATE UNIQUE INDEX linefeatures__uidx__name ON linefeatures(name);
CREATE UNIQUE INDEX linefeatures__uidx__protocol_protocolid ON linefeatures(protocol,protocolid);

INSERT INTO linefeatures VALUES (1,'sip',1,0,'','','','autoprov','','default',0,'','',0,'',0,0,'',1,0,'');


DROP TABLE ldapfilter;
CREATE TABLE ldapfilter (
 id integer unsigned,
 ldapserverid integer unsigned NOT NULL,
 name varchar(128) NOT NULL DEFAULT '',
 user varchar(255),
 passwd varchar(255),
 basedn varchar(255) NOT NULL DEFAULT '',
 filter varchar(255) NOT NULL DEFAULT '',
 attrdisplayname varchar(255) NOT NULL DEFAULT '',
 attrphonenumber varchar(255) NOT NULL DEFAULT '',
 additionaltype varchar(6) NOT NULL,
 additionaltext varchar(16) NOT NULL DEFAULT '',
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX ldapfilter__idx__ldapserverid ON ldapfilter(ldapserverid);
CREATE INDEX ldapfilter__idx__commented ON ldapfilter(commented);
CREATE UNIQUE INDEX ldapfilter__uidx__name ON ldapfilter(name);


DROP TABLE meetmefeatures;
CREATE TABLE meetmefeatures (
 id integer unsigned,
 meetmeid integer unsigned NOT NULL,
 name varchar(80) NOT NULL,
 confno varchar(40) NOT NULL,
 context varchar(39) NOT NULL,
 admin_typefrom varchar(9),
 admin_internalid integer unsigned,
 admin_externalid varchar(40),
 admin_identification varchar(11) NOT NULL,
 admin_mode varchar(6) NOT NULL,
 admin_announceusercount tinyint(1) NOT NULL DEFAULT 0,
 admin_announcejoinleave varchar(8) NOT NULL,
 admin_moderationmode tinyint(1) NOT NULL DEFAULT 0,
 admin_initiallymuted tinyint(1) NOT NULL DEFAULT 0,
 admin_musiconhold varchar(128),
 admin_poundexit tinyint(1) NOT NULL DEFAULT 0,
 admin_quiet tinyint(1) NOT NULL DEFAULT 0,
 admin_starmenu tinyint(1) NOT NULL DEFAULT 0,
 admin_closeconflastmarkedexit tinyint(1) NOT NULL DEFAULT 0,
 admin_enableexitcontext tinyint(1) NOT NULL DEFAULT 0,
 admin_exitcontext varchar(39),
 user_mode varchar(6) NOT NULL,
 user_announceusercount tinyint(1) NOT NULL DEFAULT 0,
 user_hiddencalls tinyint(1) NOT NULL DEFAULT 0,
 user_announcejoinleave varchar(8) NOT NULL,
 user_initiallymuted tinyint(1) NOT NULL DEFAULT 0,
 user_musiconhold varchar(128),
 user_poundexit tinyint(1) NOT NULL DEFAULT 0,
 user_quiet tinyint(1) NOT NULL DEFAULT 0,
 user_starmenu tinyint(1) NOT NULL DEFAULT 0,
 user_enableexitcontext tinyint(1) NOT NULL DEFAULT 0,
 user_exitcontext varchar(39),
 talkeroptimization tinyint(1) NOT NULL DEFAULT 0,
 record tinyint(1) NOT NULL DEFAULT 0,
 talkerdetection tinyint(1) NOT NULL DEFAULT 0,
 noplaymsgfirstenter tinyint(1) NOT NULL DEFAULT 0,
 durationm smallint unsigned,
 closeconfdurationexceeded tinyint(1) NOT NULL DEFAULT 0,
 nbuserstartdeductduration tinyint unsigned,
 timeannounceclose smallint unsigned,
 maxuser tinyint unsigned,
 startdate char(19),
 emailfrom varchar(255),
 emailfromname varchar(255),
 emailsubject varchar(255),
 emailbody text NOT NULL,
 preprocess_subroutine varchar(39),
 description text NOT NULL,
 commented INTEGER DEFAULT 0, -- BOOLEAN
 PRIMARY KEY(id)
);

CREATE INDEX meetmefeatures__idx__number ON meetmefeatures(confno);
CREATE INDEX meetmefeatures__idx__context ON meetmefeatures(context);
CREATE UNIQUE INDEX meetmefeatures__uidx__meetmeid ON meetmefeatures(meetmeid);
CREATE UNIQUE INDEX meetmefeatures__uidx__name ON meetmefeatures(name);


DROP TABLE meetmeguest;
CREATE TABLE meetmeguest (
 id integer unsigned,
 meetmefeaturesid integer unsigned NOT NULL,
 fullname varchar(255) NOT NULL,
 telephonenumber varchar(40),
 email varchar(320),
 PRIMARY KEY(id)
);

CREATE INDEX meetmeguest__idx__meetmefeaturesid ON meetmeguest(meetmefeaturesid);
CREATE INDEX meetmeguest__idx__fullname ON meetmeguest(fullname);
CREATE INDEX meetmeguest__idx__email ON meetmeguest(email);


DROP TABLE musiconhold;
CREATE TABLE musiconhold (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(128),
 PRIMARY KEY(id)
);

CREATE INDEX musiconhold__idx__commented ON musiconhold(commented);
CREATE UNIQUE INDEX musiconhold__uidx__filename_category_var_name ON musiconhold(filename,category,var_name);

INSERT INTO musiconhold VALUES (1,0,0,0,'musiconhold.conf','default','mode','custom');
INSERT INTO musiconhold VALUES (2,0,0,0,'musiconhold.conf','default','application','/usr/bin/madplay --mono -a -10 -R 8000 --output=raw:-');
INSERT INTO musiconhold VALUES (3,0,0,0,'musiconhold.conf','default','random','no');
INSERT INTO musiconhold VALUES (4,0,0,0,'musiconhold.conf','default','directory','/var/lib/pf-xivo/moh/default');


DROP TABLE operator;
CREATE TABLE operator (
 id SERIAL,
 name varchar(64) NOT NULL,
 default_price FLOAT,
 default_price_is varchar(16) DEFAULT minute NOT NULL,
 currency varchar(16) NOT NULL,
 disable integer DEFAULT 0 NOT NULL,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX operator__uidx__name ON operator(name);
CREATE INDEX operator__idx__disable ON operator(disable);


DROP TABLE operator_destination;
CREATE TABLE operator_destination (
 id SERIAL,
 operator_id integer NOT NULL,
 name varchar(64) NOT NULL,
 exten varchar(40) NOT NULL,
 price FLOAT,
 price_is varchar(16) DEFAULT minute NOT NULL,
 disable integer DEFAULT 0 NOT NULL,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX operator_destination__uidx__name ON operator_destination(name);
CREATE INDEX operator_destination__idx__disable ON operator_destination(disable);


DROP TABLE operator_trunk;
CREATE TABLE operator_trunk (
 operator_id integer NOT NULL,
 trunk_id integer NOT NULL,
 PRIMARY KEY(operator_id,trunk_id)
);


DROP TABLE outcall;
CREATE TABLE outcall (
 id integer unsigned,
 name varchar(128) NOT NULL,
 context varchar(39) NOT NULL,
 useenum tinyint(1) NOT NULL DEFAULT 0,
 internal tinyint(1) NOT NULL DEFAULT 0,
 preprocess_subroutine varchar(39),
 hangupringtime smallint unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX outcall__idx__commented ON outcall(commented);
CREATE UNIQUE INDEX outcall__uidx__name ON outcall(name);


DROP TABLE outcalltrunk;
CREATE TABLE outcalltrunk (
 outcallid integer unsigned NOT NULL DEFAULT 0,
 trunkfeaturesid integer unsigned NOT NULL DEFAULT 0,
 priority tinyint unsigned NOT NULL DEFAULT 0,
 PRIMARY KEY(outcallid,trunkfeaturesid)
);

CREATE INDEX outcalltrunk__idx__priority ON outcalltrunk(priority);


DROP TABLE outcalldundipeer;
CREATE TABLE outcalldundipeer (
 outcallid INTEGER NOT NULL DEFAULT 0,
 dundipeerid INTEGER NOT NULL DEFAULT 0,
 priority INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(outcallid,dundipeerid)
);

CREATE INDEX outcalldundipeer__idx__priority ON outcalldundipeer(priority);


DROP TABLE phonebook;
CREATE TABLE phonebook (
 id integer unsigned,
 title varchar(3) NOT NULL,
 firstname varchar(128) NOT NULL DEFAULT '',
 lastname varchar(128) NOT NULL DEFAULT '',
 displayname varchar(64) NOT NULL DEFAULT '',
 society varchar(128) NOT NULL DEFAULT '',
 email varchar(255) NOT NULL DEFAULT '',
 url varchar(255) NOT NULL DEFAULT '',
 image blob,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX phonebook__idx__title ON phonebook(title);
CREATE INDEX phonebook__idx__firstname ON phonebook(firstname);
CREATE INDEX phonebook__idx__lastname ON phonebook(lastname);
CREATE INDEX phonebook__idx__displayname ON phonebook(displayname);
CREATE INDEX phonebook__idx__society ON phonebook(society);
CREATE INDEX phonebook__idx__email ON phonebook(email);


DROP TABLE phonebookaddress;
CREATE TABLE phonebookaddress (
 id integer unsigned,
 phonebookid integer unsigned NOT NULL,
 address1 varchar(30) NOT NULL DEFAULT '',
 address2 varchar(30) NOT NULL DEFAULT '',
 city varchar(128) NOT NULL DEFAULT '',
 state varchar(128) NOT NULL DEFAULT '',
 zipcode varchar(16) NOT NULL DEFAULT '',
 country varchar(3) NOT NULL DEFAULT '',
 type varchar(6) NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX phonebookaddress__idx__address1 ON phonebookaddress(address1);
CREATE INDEX phonebookaddress__idx__address2 ON phonebookaddress(address2);
CREATE INDEX phonebookaddress__idx__city ON phonebookaddress(city);
CREATE INDEX phonebookaddress__idx__state ON phonebookaddress(state);
CREATE INDEX phonebookaddress__idx__zipcode ON phonebookaddress(zipcode);
CREATE INDEX phonebookaddress__idx__country ON phonebookaddress(country);
CREATE INDEX phonebookaddress__idx__type ON phonebookaddress(type);
CREATE UNIQUE INDEX phonebookaddress__uidx__phonebookid_type ON phonebookaddress(phonebookid,type);


DROP TABLE phonebooknumber;
CREATE TABLE phonebooknumber (
 id integer unsigned,
 phonebookid integer unsigned NOT NULL,
 number varchar(40) NOT NULL DEFAULT '',
 type varchar(6) NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX phonebooknumber__idx__number ON phonebooknumber(number);
CREATE INDEX phonebooknumber__idx__type ON phonebooknumber(type);
CREATE UNIQUE INDEX phonebooknumber__uidx__phonebookid_type ON phonebooknumber(phonebookid,type);


DROP TABLE phonefunckey;
CREATE TABLE phonefunckey (
 iduserfeatures integer unsigned NOT NULL,
 fknum smallint unsigned NOT NULL,
 exten varchar(40),
 typeextenumbers varchar(64),
 typevalextenumbers varchar(255),
 typeextenumbersright varchar(64),
 typevalextenumbersright varchar(255),
 label varchar(32),
 supervision tinyint(1) NOT NULL DEFAULT 0,
 progfunckey tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(iduserfeatures,fknum)
);

CREATE INDEX phonefunckey__idx__exten ON phonefunckey(exten);
CREATE INDEX phonefunckey__idx__progfunckey ON phonefunckey(progfunckey);
CREATE INDEX phonefunckey__idx__typeextenumbers_typevalextenumbers ON phonefunckey(typeextenumbers,typevalextenumbers);
CREATE INDEX phonefunckey__idx__typeextenumbersright_typevalextenumbersright ON phonefunckey(typeextenumbersright,typevalextenumbersright);


DROP TABLE queue;
CREATE TABLE queue (
 name varchar(128) NOT NULL,
 musiconhold varchar(128),
 announce varchar(128),
 context varchar(39),
 timeout tinyint unsigned DEFAULT 0,
 'monitor-type' varchar(10),
 'monitor-format' varchar(128),
 'queue-youarenext' varchar(128),
 'queue-thereare' varchar(128),
 'queue-callswaiting' varchar(128),
 'queue-holdtime' varchar(128),
 'queue-minutes' varchar(128),
 'queue-seconds' varchar(128),
 'queue-thankyou' varchar(128),
 'queue-reporthold' varchar(128),
 'periodic-announce' text,
 'announce-frequency' integer unsigned,
 'periodic-announce-frequency' integer unsigned,
 'announce-round-seconds' tinyint unsigned,
 'announce-holdtime' varchar(4),
 retry tinyint unsigned,
 wrapuptime tinyint unsigned,
 maxlen integer unsigned,
 servicelevel int(11),
 strategy varchar(11),
 joinempty varchar(6),
 leavewhenempty varchar(6),
 eventmemberstatus tinyint(1) NOT NULL DEFAULT 0,
 eventwhencalled tinyint(1) NOT NULL DEFAULT 0,
 ringinuse tinyint(1) NOT NULL DEFAULT 0,
 reportholdtime tinyint(1) NOT NULL DEFAULT 0,
 memberdelay integer unsigned,
 weight integer unsigned,
 timeoutrestart tinyint(1) NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 category char(5) NOT NULL,
 timeoutpriority varchar(10) NOT NULL DEFAULT 'app',
 autofill INTEGER NOT NULL DEFAULT 1, -- BOOLEAN
 autopause INTEGER NOT NULL DEFAULT 1, -- BOOLEAN
 setinterfacevar INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 setqueueentryvar INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 setqueuevar INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 membermacro varchar(1024),
 'min-announce-frequency' integer NOT NULL DEFAULT 60,
 'random-periodic-announce' INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 'announce-position' varchar(1024) NOT NULL DEFAULT 'yes',
 'announce-position-limit' integer NOT NULL DEFAULT 5,
 defaultrule varchar(1024) DEFAULT NULL,
 PRIMARY KEY(name)
);

CREATE INDEX queue__idx__commented ON queue(commented);
CREATE INDEX queue__idx__category ON queue(category);


DROP TABLE queue_info;
CREATE TABLE queue_info (
 id INTEGER UNSIGNED,
 call_time_t INTEGER,
 queue_name VARCHAR(128) NOT NULL DEFAULT '',
 caller VARCHAR(80) NOT NULL DEFAULT '',
 caller_uniqueid VARCHAR(32) NOT NULL DEFAULT '',
 call_picker VARCHAR(80),
 hold_time INTEGER,
 talk_time INTEGER,
 PRIMARY KEY(id)
);

CREATE INDEX queue_info_call_time_t_index ON queue_info (call_time_t);
CREATE INDEX queue_info_queue_name_index ON queue_info (queue_name);


DROP TABLE queuefeatures;
CREATE TABLE queuefeatures (
 id integer unsigned,
 name varchar(128) NOT NULL,
 displayname varchar(128) NOT NULL,
 number varchar(40) NOT NULL DEFAULT '',
 context varchar(39),
 data_quality INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 hitting_callee INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 hitting_caller INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 retries INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 ring INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 transfer_user INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 transfer_call INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 write_caller INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 write_calling INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 url varchar(255) NOT NULL DEFAULT '',
 announceoverride varchar(128) NOT NULL DEFAULT '',
 timeout INTEGER NOT NULL DEFAULT 0,
 preprocess_subroutine varchar(39),
 announce_holdtime INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 -- DIVERSIONS
 ctipresence VARCHAR(1024) DEFAULT NULL,
 nonctipresence VARCHAR(1024) DEFAULT NULL,
 waittime    INTEGER  DEFAULT NULL,
 waitratio   FLOAT DEFAULT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX queuefeatures__idx__number ON queuefeatures(number);
CREATE INDEX queuefeatures__idx__context ON queuefeatures(context);
CREATE UNIQUE INDEX queuefeatures__uidx__name ON queuefeatures(name);


DROP TABLE queuemember;
CREATE TABLE queuemember (
 queue_name varchar(128) NOT NULL,
 interface varchar(128) NOT NULL,
 penalty tinyint unsigned NOT NULL DEFAULT 0,
 'call-limit' tinyint unsigned NOT NULL DEFAULT 0,
 paused tinyint unsigned,
 commented tinyint(1) NOT NULL DEFAULT 0,
 usertype varchar(5) NOT NULL,
 userid integer unsigned NOT NULL,
 channel varchar(25) NOT NULL,
 category char(5) NOT NULL,
 skills char(64) NOT NULL DEFAULT '',
 state_interface varchar(128) NOT NULL DEFAULT '',
 PRIMARY KEY(queue_name,interface)
);

CREATE INDEX queuemember__idx__commented ON queuemember(commented);
CREATE INDEX queuemember__idx__usertype ON queuemember(usertype);
CREATE INDEX queuemember__idx__userid ON queuemember(userid);
CREATE INDEX queuemember__idx__channel ON queuemember(channel);
CREATE INDEX queuemember__idx__category ON queuemember(category);
CREATE UNIQUE INDEX queuemember__uidx__queue_name_channel_usertype_userid_category ON queuemember(queue_name,channel,usertype,userid,category);


DROP TABLE queuepenalty;
CREATE TABLE queuepenalty (
 id INTEGER UNSIGNED,
 name VARCHAR(255) NOT NULL UNIQUE,
 commented INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 description TEXT NOT NULL,
 PRIMARY KEY(id)
);


DROP TABLE queuepenaltychange;
CREATE TABLE queuepenaltychange (
 queuepenalty_id INTEGER NOT NULL,
 seconds    INTEGER NOT NULL DEFAULT 0,
 maxp_sign  VARCHAR(1) DEFAULT NULL,
 maxp_value INTEGER DEFAULT NULL,
 minp_sign  VARCHAR(1) DEFAULT NULL,
 minp_value INTEGER DEFAULT NULL,
 PRIMARY KEY(queuepenalty_id, seconds)
);


DROP TABLE rightcall;
CREATE TABLE rightcall (
 id integer unsigned,
 name varchar(128) NOT NULL DEFAULT '',
 context varchar(39) NOT NULL,
 passwd varchar(40) NOT NULL DEFAULT '',
 authorization tinyint(1) NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX rightcall__idx__context ON rightcall(context);
CREATE INDEX rightcall__idx__passwd ON rightcall(passwd);
CREATE INDEX rightcall__idx__authorization ON rightcall(authorization);
CREATE INDEX rightcall__idx__commented ON rightcall(commented);
CREATE UNIQUE INDEX rightcall__uidx__name ON rightcall(name);


DROP TABLE rightcallexten;
CREATE TABLE rightcallexten (
 id integer unsigned,
 rightcallid integer unsigned NOT NULL DEFAULT 0,
 exten varchar(40) NOT NULL DEFAULT '',
 extenhash char(40) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX rightcallexten__uidx__rightcallid_extenhash ON rightcallexten(rightcallid,extenhash);


DROP TABLE rightcallmember;
CREATE TABLE rightcallmember (
 id integer unsigned,
 rightcallid integer unsigned NOT NULL DEFAULT 0,
 type varchar(64) NOT NULL DEFAULT '',
 typeval varchar(128) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX rightcallmember__uidx__rightcallid_type_typeval ON rightcallmember(rightcallid,type,typeval);


DROP TABLE schedule;
CREATE TABLE schedule (
 id integer unsigned,
 name VARCHAR(255) NOT NULL DEFAULT '',
 timezone VARCHAR(128) DEFAULT NULL, 
 fallback_action     VARCHAR(64)  NOT NULL DEFAULT 'none',
 fallback_actionid   VARCHAR(255) DEFAULT NULL,
 fallback_actionargs VARCHAR(255) DEFAULT NULL,
 description TEXT DEFAULT NULL,
 commented tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE INDEX schedule__idx__commented ON schedule(commented);


DROP TABLE schedule_path;
CREATE TABLE schedule_path (
 schedule_id   INTEGER NOT NULL,

 path   VARCHAR(16) NOT NULL,
 pathid INTEGER DEFAULT NULL, 
 'order' INTEGER NOT NULL,
 PRIMARY KEY(schedule_id,path,pathid)
);

CREATE INDEX schedule_path_path ON schedule_path(path,pathid);


DROP TABLE schedule_time;
CREATE TABLE schedule_time (
 id SERIAL,
 schedule_id INTEGER,
 mode        VARCHAR(8) NOT NULL DEFAULT 'opened',
 hours       VARCHAR(512) DEFAULT NULL,
 weekdays    VARCHAR(512) DEFAULT NULL,
 monthdays   VARCHAR(512) DEFAULT NULL,
 months      VARCHAR(512) DEFAULT NULL,
 -- only when mode == 'closed'
 action      VARCHAR(64) DEFAULT NULL,
 actionid    VARCHAR(255) DEFAULT NULL,
 actionargs  VARCHAR(255) DEFAULT NULL,

 commented   INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 PRIMARY KEY(id)
);

--CREATE INDEX schedule__idx__commented ON schedule(commented);
CREATE INDEX schedule_time__idx__scheduleid_commented ON schedule_time(schedule_id,commented);


DROP TABLE serverfeatures;
CREATE TABLE serverfeatures (
 id integer unsigned,
 serverid integer unsigned NOT NULL,
 feature varchar(9) NOT NULL,
 type char(4) NOT NULL,
 commented tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE INDEX serverfeatures__idx__serverid ON serverfeatures(serverid);
CREATE INDEX serverfeatures__idx__feature ON serverfeatures(feature);
CREATE INDEX serverfeatures__idx__type ON serverfeatures(type);
CREATE INDEX serverfeatures__idx__commented ON serverfeatures(commented);
CREATE UNIQUE INDEX serverfeatures__uidx__serverid_feature_type ON serverfeatures(serverid,feature,type);



DROP TABLE servicesgroup;
CREATE TABLE servicesgroup (
 id integer unsigned,
 name varchar(64) NOT NULL,
 accountcode varchar(20),
 disable tinyint(1) NOT NULL DEFAULT 0,
 description text,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX servicesgroup__uidx__name ON servicesgroup(name);
CREATE UNIQUE INDEX servicesgroup__uidx__accountcode ON servicesgroup(accountcode);
CREATE INDEX servicesgroup__idx__disable ON servicesgroup(disable);


DROP TABLE servicesgroup_user;
CREATE TABLE servicesgroup_user (
 servicesgroup_id integer unsigned NOT NULL,
 userfeatures_id integer unsigned NOT NULL,
 PRIMARY KEY(servicesgroup_id,userfeatures_id)
);

CREATE UNIQUE INDEX servicesgroup_user__uidx__servicesgroupid_userfeaturesid ON servicesgroup_user(servicesgroup_id,userfeatures_id);

DROP TABLE staticagent;
CREATE TABLE staticagent (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(255),
 PRIMARY KEY(id)
);

CREATE INDEX staticagent__idx__cat_metric ON staticagent(cat_metric);
CREATE INDEX staticagent__idx__var_metric ON staticagent(var_metric);
CREATE INDEX staticagent__idx__commented ON staticagent(commented);
CREATE INDEX staticagent__idx__filename ON staticagent(filename);
CREATE INDEX staticagent__idx__category ON staticagent(category);
CREATE INDEX staticagent__idx__var_name ON staticagent(var_name);
CREATE INDEX staticagent__idx__var_val ON staticagent(var_val);

INSERT INTO staticagent VALUES (2,0,0,0,'agents.conf','general','multiplelogin','yes');
INSERT INTO staticagent VALUES (3,1,0,0,'agents.conf','agents','recordagentcalls','no');
INSERT INTO staticagent VALUES (4,1,0,0,'agents.conf','agents','recordformat','wav');
INSERT INTO staticagent VALUES (5,1,1000000,0,'agents.conf','agents','group',1);


DROP TABLE staticiax;
CREATE TABLE staticiax (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(255),
 PRIMARY KEY(id)
);

CREATE INDEX staticiax__idx__commented ON staticiax(commented);
CREATE INDEX staticiax__idx__filename ON staticiax(filename);
CREATE INDEX staticiax__idx__category ON staticiax(category);
CREATE INDEX staticiax__idx__var_name ON staticiax(var_name);

INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','bindport',4569);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','bindaddr','0.0.0.0');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','iaxthreadcount',10);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','iaxmaxthreadcount',100);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','iaxcompat','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','authdebug','yes');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','delayreject','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','trunkfreq',20);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','trunktimestamps','yes');
INSERT INTO staticiax VALUES (NULL,0,0,1,'iax.conf','general','regcontext',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','minregexpire',60);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','maxregexpire',60);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','bandwidth','high');
INSERT INTO staticiax VALUES (NULL,0,0,1,'iax.conf','general','tos',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','jitterbuffer','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','forcejitterbuffer','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','maxjitterbuffer',1000);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','maxjitterinterps',10);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','resyncthreshold',1000);
INSERT INTO staticiax VALUES (NULL,0,0,1,'iax.conf','general','accountcode',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','amaflags','default');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','adsi','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','transfer','yes');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','language','fr_FR');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','mohinterpret','default');
INSERT INTO staticiax VALUES (NULL,0,0,1,'iax.conf','general','mohsuggest',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','encryption','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','maxauthreq',3);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','codecpriority','host');
INSERT INTO staticiax VALUES (NULL,0,0,1,'iax.conf','general','disallow',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,1,'iax.conf','general','allow',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','rtcachefriends','yes');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','rtupdate','yes');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','rtignoreregexpire','yes');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','rtautoclear','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','pingtime',20);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','lagrqtime',10);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','nochecksums','no');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','autokill','yes');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','calltokenoptional','0.0.0.0');
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','srvlookup',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','jittertargetextra',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','forceencryption',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','trunkmaxsize',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','trunkmtu',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','cos',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','allowfwdownload',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','parkinglot',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','maxcallnumbers',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','maxcallnumbers_nonvalidated',NULL);
INSERT INTO staticiax VALUES (NULL,0,0,0,'iax.conf','general','shrinkcallerid',NULL);


DROP TABLE staticmeetme;
CREATE TABLE staticmeetme (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(128),
 PRIMARY KEY(id)
);

CREATE INDEX staticmeetme__idx__commented ON staticmeetme(commented);
CREATE INDEX staticmeetme__idx__filename ON staticmeetme(filename);
CREATE INDEX staticmeetme__idx__category ON staticmeetme(category);
CREATE INDEX staticmeetme__idx__var_name ON staticmeetme(var_name);

INSERT INTO staticmeetme VALUES (NULL,0,0,0,'meetme.conf','general','audiobuffers',32);
INSERT INTO staticmeetme VALUES (NULL,0,0,0,'meetme.conf','general','schedule','yes');
INSERT INTO staticmeetme VALUES (NULL,0,0,0,'meetme.conf','general','logmembercount','yes');
INSERT INTO staticmeetme VALUES (NULL,0,0,0,'meetme.conf','general','fuzzystart',300);
INSERT INTO staticmeetme VALUES (NULL,0,0,0,'meetme.conf','general','earlyalert',3600);
INSERT INTO staticmeetme VALUES (NULL,0,0,0,'meetme.conf','general','endalert',120);


DROP TABLE staticqueue;
CREATE TABLE staticqueue (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(128),
 PRIMARY KEY(id)
);

CREATE INDEX staticqueue__idx__commented ON staticqueue(commented);
CREATE INDEX staticqueue__idx__filename ON staticqueue(filename);
CREATE INDEX staticqueue__idx__category ON staticqueue(category);
CREATE INDEX staticqueue__idx__var_name ON staticqueue(var_name);

INSERT INTO staticqueue VALUES (NULL,0,0,0,'queues.conf','general','persistentmembers','yes');
INSERT INTO staticqueue VALUES (NULL,0,0,0,'queues.conf','general','autofill','no');
INSERT INTO staticqueue VALUES (NULL,0,0,0,'queues.conf','general','monitor-type','no');
INSERT INTO staticqueue VALUES (NULL,0,0,0,'queues.conf','general','updatecdr','no');
INSERT INTO staticqueue VALUES (NULL,0,0,0,'queues.conf','general','shared_lastcall','no');


DROP TABLE staticsip;
CREATE TABLE staticsip (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(255),
 PRIMARY KEY(id)
);

CREATE INDEX staticsip__idx__commented ON staticsip(commented);
CREATE INDEX staticsip__idx__filename ON staticsip(filename);
CREATE INDEX staticsip__idx__category ON staticsip(category);
CREATE INDEX staticsip__idx__var_name ON staticsip(var_name);

INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','bindport',5060);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','videosupport','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autocreatepeer','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autocreate_context','xivo-initconfig');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autocreate_maxexpiry','300');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autocreate_defaultexpiry','180');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autocreate_type','friend');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','allowautoprov','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','allowsubscribe','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','allowoverlap','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','promiscredir','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autodomain','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','domain',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','allowexternaldomains','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','usereqphone','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','realm','xivo');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','alwaysauthreject','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','useragent','XiVO PBX');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','buggymwi','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','regcontext',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','callerid','xivo');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','fromdomain',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','sipdebug','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','dumphistory','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','recordhistory','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','callevents','yes');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','tos_sip',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','tos_audio',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','tos_video',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','t38pt_udptl','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','t38pt_usertpsource','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','localnet',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','externip',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','externhost',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','externrefresh',10);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','matchexterniplocally','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','outboundproxy',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','g726nonstandard','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','disallow',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','allow',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','t1min',100);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','relaxdtmf','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rfc2833compensate','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','compactheaders','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtptimeout',0);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtpholdtimeout',0);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtpkeepalive',0);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','directrtpsetup','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','notifymimetype','application/simple-message-summary');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','srvlookup','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','pedantic','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','minexpiry',60);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','maxexpiry',3600);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','defaultexpiry',120);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','registertimeout',20);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','registerattempts',0);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','notifyringing','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','notifyhold','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','allowtransfer','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','maxcallbitrate',384);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','autoframing','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jbenable','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jbforce','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jbmaxsize',200);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jbresyncthreshold',1000);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jbimpl','fixed');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jblog','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','context',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','nat','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','dtmfmode','info');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','qualify','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','useclientcode','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','progressinband','never');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','language','fr_FR');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','mohinterpret','default');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','mohsuggest',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','vmexten','*98');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','trustrpid','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','sendrpid','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','insecure','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtcachefriends','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtupdate','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','ignoreregexpire','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtsavesysname','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','rtautoclear','no');
INSERT INTO staticsip VALUES (NULL,0,0,1,'sip.conf','general','subscribecontext',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','match_auth_username','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','udpbindaddr','0.0.0.0');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tcpenable','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tcpbindaddr',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlsenable','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlsbindaddr',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlscertfile',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlscafile',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlscadir','/var/lib/asterisk/certs/cadir');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlsdontverifyserver','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tlscipher',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','tos_text',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','cos_sip',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','cos_audio',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','cos_video',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','cos_text',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','mwiexpiry',3600);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','qualifyfreq',60);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','qualifygap',100);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','qualifypeers',1);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','parkinglot',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','permaturemedia',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','sdpsession',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','sdpowner',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','authfailureevents','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','dynamic_exclude_static','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','contactdeny',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','contactpermit',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','shrinkcallerid','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','regextenonqualify','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','timer1',500);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','timerb',32000);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','session-timers',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','session-expires',600);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','session-minse',90);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','session-refresher','uas');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','hash_users',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','hash_peers',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','hash_dialogs',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','notifycid','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','callcounter','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','faxdetect','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','stunaddr',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','directmedia','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','ignoresdpversion','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','jbtargetextra',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','srtp','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','externtcpport',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','externtlsport',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','media_address',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','use_q850_reason','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','snom_aoc_enabled','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','subscribe_network_change_event','yes');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','maxforwards',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','disallow_methods',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','domainsasrealm',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','textsupport',NULL);
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','auth_options_requests','no');
INSERT INTO staticsip VALUES (NULL,0,0,0,'sip.conf','general','transport','udp');


DROP TABLE staticvoicemail;
CREATE TABLE staticvoicemail (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val text,
 PRIMARY KEY(id)
);

CREATE INDEX staticvoicemail__idx__commented ON staticvoicemail(commented);
CREATE INDEX staticvoicemail__idx__filename ON staticvoicemail(filename);
CREATE INDEX staticvoicemail__idx__category ON staticvoicemail(category);
CREATE INDEX staticvoicemail__idx__var_name ON staticvoicemail(var_name);

INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','maxmsg',100);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','silencethreshold',256);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','minsecs',0);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','maxsecs',0);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','maxsilence',15);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','review','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','operator','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','format','wav');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','maxlogins',3);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','envelope','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','saycid','no');
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','cidinternalcontexts',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','sayduration','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','saydurationm',2);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','forcename','no');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','forcegreetings','no');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','tempgreetwarn','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','maxgreet',0);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','skipms',3000);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','sendvoicemail','no');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','usedirectory','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','nextaftercmd','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','dialout',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','callback',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','exitcontext',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','attach','yes');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','volgain',0);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','mailcmd','/usr/sbin/sendmail -t');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','serveremail','xivo');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','charset','UTF-8');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','fromstring','XiVO PBX');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','emaildateformat','%A %d %B %Y à %H:%M:%S %Z');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','pbxskip','no');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','emailsubject','Messagerie XiVO');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','emailbody','Bonjour ${VM_NAME} !

Vous avez reçu un message d''une durée de ${VM_DUR} minute(s), il vous reste actuellement ${VM_MSGNUM} message(s) non lu(s) sur votre messagerie vocale : ${VM_MAILBOX}.

Le dernier a été envoyé par ${VM_CALLERID}, le ${VM_DATE}. Si vous le souhaitez vous pouvez l''écouter ou le consulter en tapant le *98 sur votre téléphone.

Merci.

-- Messagerie XiVO --');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','pagerfromstring','XiVO PBX');
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','pagersubject',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','pagerbody',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','adsifdn','0000000F');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','adsisec','9BDBF7AC');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','adsiver',1);
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','searchcontexts','no');
INSERT INTO staticvoicemail VALUES (NULL,0,0,0,'voicemail.conf','general','externpass','/usr/share/asterisk/bin/change-pass-vm');
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','externnotify',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','smdiport',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','odbcstorage',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','odbctable',NULL);
INSERT INTO staticvoicemail VALUES (NULL,1,0,0,'voicemail.conf','zonemessages','eu-fr','Europe/Paris|''vm-received'' q ''digits/at'' kM');
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','moveheard',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','forward_urgent_auto',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','userscontext',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','smdienable',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','externpassnotify',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','externpasscheck',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','directoryinfo',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','pollmailboxes',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','pollfreq',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','imapgreetings',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','greetingsfolder',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','imapparentfolder',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','tz',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','hidefromdir',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','messagewrap',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','minpassword',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-password',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-newpassword',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-passchanged',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-reenterpassword',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-mismatch',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-invalid-password',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','vm-pls-try-again',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','listen-control-forward-key',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','listen-control-reverse-key',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','listen-control-pause-key',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','listen-control-restart-key',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','listen-control-stop-key',NULL);
INSERT INTO staticvoicemail VALUES (NULL,0,0,1,'voicemail.conf','general','backupdeleted',NULL);


DROP TABLE staticsccp;
CREATE TABLE staticsccp (
 id integer unsigned,
 cat_metric integer unsigned NOT NULL DEFAULT 0,
 var_metric integer unsigned NOT NULL DEFAULT 0,
 commented tinyint(1) NOT NULL DEFAULT 0,
 filename varchar(128) NOT NULL,
 category varchar(128) NOT NULL,
 var_name varchar(128) NOT NULL,
 var_val varchar(255),
 PRIMARY KEY(id)
);
CREATE INDEX staticsccp__idx__category ON staticsccp(category);
CREATE INDEX staticsccp__idx__commented ON staticsccp(commented);
CREATE INDEX staticsccp__idx__filename ON staticsccp(filename);
CREATE INDEX staticsccp__idx__var_name ON staticsccp(var_name);

INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','servername','Asterisk');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','keepalive',60);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','debug','');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','dateFormat','D.M.Y');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','port',2000);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','firstdigittimeout',16);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','digittimeout',8);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','autoanswer_ring_time',0);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','autoanswer_tone','0x32');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','remotehangup_tone','0x32');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','transfer_tone',0);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','callwaiting_tone','0x2d');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','musicclass','default');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','dnd','on');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','sccp_tos','0x68');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','sccp_cos',4);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','audio_tos','0xB8');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','audio_cos',6);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','video_tos','0x88');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','video_cos',5);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','echocancel','on');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','silencesuppression','off');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','trustphoneip','no');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','private','on');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','protocolversion',11);
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','disallow','all');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','language','fr_FR');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','hotline_enabled','yes');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','hotline_context','xivo-initconfig');
INSERT INTO staticsccp VALUES(NULL,0,0,0,'sccp.conf','general','hotline_extension','sccp');


DROP TABLE trunkfeatures;
CREATE TABLE trunkfeatures (
 id integer unsigned,
 protocol varchar(50) NOT NULL,
 protocolid integer unsigned NOT NULL,
 registerid integer unsigned NOT NULL DEFAULT 0,
 registercommented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX trunkfeatures__idx__registerid ON trunkfeatures(registerid);
CREATE INDEX trunkfeatures__idx__registercommented ON trunkfeatures(registercommented);
CREATE UNIQUE INDEX trunkfeatures__uidx__protocol_protocolid ON trunkfeatures(protocol,protocolid);


DROP TABLE usercustom;
CREATE TABLE usercustom (
 id integer unsigned,
 name varchar(40),
 context varchar(39),
 interface varchar(128) NOT NULL,
 intfsuffix varchar(32) NOT NULL DEFAULT '',
 commented tinyint(1) NOT NULL DEFAULT 0,
 protocol char(6) NOT NULL DEFAULT 'custom',
 category varchar(5) NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX usercustom__idx__name ON usercustom(name);
CREATE INDEX usercustom__idx__context ON usercustom(context);
CREATE INDEX usercustom__idx__commented ON usercustom(commented);
CREATE INDEX usercustom__idx__protocol ON usercustom(protocol);
CREATE INDEX usercustom__idx__category ON usercustom(category);
CREATE UNIQUE INDEX usercustom__uidx__interface_intfsuffix_category ON usercustom(interface,intfsuffix,category);


DROP TABLE userfeatures;
CREATE TABLE userfeatures (
 id integer unsigned,
 firstname varchar(128) NOT NULL DEFAULT '',
 lastname varchar(128) NOT NULL DEFAULT '',
 voicemailtype VARCHAR(8),
 voicemailid INTEGER,
 agentid INTEGER,
 pictureid INTEGER,
 entityid integer,
 callerid varchar(160),
 ringseconds INTEGER NOT NULL DEFAULT 30,
 simultcalls INTEGER NOT NULL DEFAULT 5,
 enableclient INTEGER NOT NULL DEFAULT 1, -- BOOLEAN
 loginclient varchar(64) NOT NULL DEFAULT '',
 passwdclient varchar(64) NOT NULL DEFAULT '',
 profileclient varchar(64) NOT NULL DEFAULT '',
 enablehint INTEGER NOT NULL DEFAULT 1, -- BOOLEAN
 enablevoicemail INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 enablexfer INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 enableautomon INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 callrecord INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 incallfilter INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 enablednd INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 enableunc INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 destunc varchar(128) NOT NULL DEFAULT '',
 enablerna INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 destrna varchar(128) NOT NULL DEFAULT '',
 enablebusy INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 destbusy varchar(128) NOT NULL DEFAULT '',
 musiconhold varchar(128) NOT NULL DEFAULT '',
 outcallerid varchar(80) NOT NULL DEFAULT '',
 mobilephonenumber varchar(128) NOT NULL DEFAULT '',
 bsfilter VARCHAR(16) NOT NULL DEFAULT 'no',
 preprocess_subroutine varchar(39),
 timezone varchar(128),
 language varchar(20),
 ringintern varchar(64),
 ringextern varchar(64),
 ringgroup varchar(64),
 ringforward varchar(64),
 rightcallcode varchar(16),
 alarmclock varchar(5) NOT NULL DEFAULT '',
 pitch varchar(16),
 pitchdirection varchar(16),
 commented INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX userfeatures__idx__firstname ON userfeatures(firstname);
CREATE INDEX userfeatures__idx__lastname ON userfeatures(lastname);
CREATE INDEX userfeatures__idx__voicemailid ON userfeatures(voicemailid);
CREATE INDEX userfeatures__idx__agentid ON userfeatures(agentid);
CREATE INDEX userfeatures__idx__loginclient ON userfeatures(loginclient);
CREATE INDEX userfeatures__idx__musiconhold ON userfeatures(musiconhold);
CREATE INDEX userfeatures__idx__commented ON userfeatures(commented);


DROP TABLE useriax;
CREATE TABLE useriax (
 id integer unsigned,
 name varchar(40) NOT NULL, -- user / peer --
 type VARCHAR(8) NOT NULL, -- user / peer --
 username varchar(80), -- peer --
 secret varchar(80) NOT NULL DEFAULT '', -- peer / user --
 dbsecret varchar(255) NOT NULL DEFAULT '', -- peer / user --
 context varchar(39), -- peer / user --
 language varchar(20), -- general / user --
 accountcode varchar(20), -- general / user --
 amaflags VARCHAR(16) DEFAULT 'default', -- general / user --
 mailbox varchar(80), -- peer --
 callerid varchar(160), -- user / peer --
 fullname varchar(80), -- user / peer --
 cid_number varchar(80), -- user / peer --
 trunk INTEGER NOT NULL DEFAULT 0, -- BOOLEAN -- user / peer --
 auth VARCHAR(32) NOT NULL DEFAULT 'plaintext,md5', -- user / peer --
 encryption VARCHAR(8) DEFAULT NULL, -- user / peer --
 forceencryption VARCHAR(8) DEFAULT NULL,
 maxauthreq INTEGER, -- general / user --
 inkeys varchar(80), -- user / peer --
 outkey varchar(80), -- peer --
 adsi INTEGER, -- BOOLEAN -- general / user / peer --
 transfer VARCHAR(16), -- general / user / peer --
 codecpriority VARCHAR(8), -- general / user --
 jitterbuffer INTEGER, -- BOOLEAN -- general / user / peer --
 forcejitterbuffer INTEGER, -- BOOLEAN -- general / user / peer --
 sendani INTEGER NOT NULL DEFAULT 0, -- BOOLEAN -- peer --
 qualify varchar(4) NOT NULL DEFAULT 'no', -- peer --
 qualifysmoothing INTEGER NOT NULL DEFAULT 0, -- BOOLEAN -- peer --
 qualifyfreqok INTEGER NOT NULL DEFAULT 60000, -- peer --
 qualifyfreqnotok INTEGER NOT NULL DEFAULT 10000, -- peer --
 timezone varchar(80), -- peer --
 disallow varchar(100), -- general / user / peer --
 allow varchar(100), -- general / user / peer --
 mohinterpret varchar(80), -- general / user / peer --
 mohsuggest varchar(80), -- general / user / peer --
 deny varchar(31), -- user / peer --
 permit varchar(31), -- user / peer --
 defaultip varchar(255), -- peer --
 sourceaddress varchar(255), -- peer --
 setvar varchar(100) NOT NULL DEFAULT '', -- user --
 host varchar(255) NOT NULL DEFAULT 'dynamic', -- peer --
 port INTEGER, -- peer --
 mask varchar(15), -- peer --
 regexten varchar(80), -- peer --
 peercontext varchar(80), -- peer --
 ipaddr varchar(255) NOT NULL DEFAULT '',
 regseconds INTEGER NOT NULL DEFAULT 0,
 immediate INTEGER DEFAULT NULL, -- BOOLEAN
 parkinglot INTEGER DEFAULT NULL,
 protocol varchar(15) NOT NULL DEFAULT 'iax' CHECK (protocol = 'iax'), -- ENUM
 category VARCHAR(8) NOT NULL,
 commented INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 requirecalltoken varchar(4) NOT NULL DEFAULT 'no', -- peer--
 PRIMARY KEY(id)
);

CREATE INDEX useriax__idx__mailbox ON useriax(mailbox);
CREATE INDEX useriax__idx__protocol ON useriax(protocol);
CREATE INDEX useriax__idx__category ON useriax(category);
CREATE INDEX useriax__idx__commented ON useriax(commented);
CREATE INDEX useriax__idx__name_host ON useriax(name,host);
CREATE INDEX useriax__idx__name_ipaddr_port ON useriax(name,ipaddr,port);
CREATE INDEX useriax__idx__ipaddr_port ON useriax(ipaddr,port);
CREATE INDEX useriax__idx__host_port ON useriax(host,port);
CREATE UNIQUE INDEX useriax__uidx__name ON useriax(name);


DROP TABLE usersip;
CREATE TABLE usersip (
 id integer unsigned,
 name varchar(40) NOT NULL, -- user / peer --
 type VARCHAR(8) NOT NULL, -- user / peer --
 username varchar(80), -- peer --
 secret varchar(80) NOT NULL DEFAULT '', -- user / peer --
 md5secret varchar(32) NOT NULL DEFAULT '', -- user / peer --
 context varchar(39), -- general / user / peer --
 language varchar(20), -- general / user / peer --
 accountcode varchar(20), -- user / peer --
 amaflags VARCHAR(16) NOT NULL DEFAULT 'default', -- user / peer --

 allowtransfer INTEGER, -- BOOLEAN -- general / user / peer --
 fromuser varchar(80), -- peer --
 fromdomain varchar(255), -- general / peer --
 mailbox varchar(80), -- peer --
 subscribemwi INTEGER NOT NULL DEFAULT 1, -- BOOLEAN -- peer --
 buggymwi INTEGER, -- BOOLEAN -- general / user / peer --
 'call-limit' INTEGER NOT NULL DEFAULT 0, -- user / peer --
 callerid varchar(160), -- general / user / peer --
 fullname varchar(80), -- user / peer --
 cid_number varchar(80), -- user / peer --
 maxcallbitrate INTEGER, -- general / user / peer --
 insecure VARCHAR(16), -- general / user / peer --
 nat VARCHAR(8), -- general / user / peer --
 promiscredir INTEGER, -- BOOLEAN -- general / user / peer --
 usereqphone INTEGER, -- BOOLEAN -- general / peer --
 videosupport VARCHAR(8) DEFAULT NULL, -- general / user / peer --
 trustrpid INTEGER, -- BOOLEAN -- general / user / peer --
 sendrpid INTEGER, -- BOOLEAN -- general / user / peer --

 allowsubscribe INTEGER, -- BOOLEAN -- general / user / peer --
 allowoverlap INTEGER, -- BOOLEAN -- general / user / peer --
 dtmfmode VARCHAR(8), -- general / user / peer --
 rfc2833compensate INTEGER, -- BOOLEAN -- general / user / peer --
 qualify varchar(4), -- general / peer --
 g726nonstandard INTEGER, -- BOOLEAN -- general / user / peer --
 disallow varchar(100), -- general / user / peer --
 allow varchar(100), -- general / user / peer --
 autoframing INTEGER, -- BOOLEAN -- general / user / peer --
 mohinterpret varchar(80), -- general / user / peer --
 mohsuggest varchar(80), -- general / user / peer --
 useclientcode INTEGER, -- BOOLEAN -- general / user / peer --
 progressinband VARCHAR(8), -- general / user / peer --

 t38pt_udptl INTEGER, -- BOOLEAN -- general / user / peer --
 t38pt_usertpsource INTEGER, -- BOOLEAN -- general / user / peer --
 rtptimeout INTEGER, -- general / peer --
 rtpholdtimeout INTEGER, -- general / peer --
 rtpkeepalive INTEGER, -- general / peer --
 deny varchar(31), -- user / peer --
 permit varchar(31), -- user / peer --
 defaultip varchar(255), -- peer --

 setvar varchar(100) NOT NULL DEFAULT '', -- user / peer --
 host varchar(255) NOT NULL DEFAULT 'dynamic', -- peer --
 port INTEGER, -- peer --
 regexten varchar(80), -- peer --
 subscribecontext varchar(80), -- general / user / peer --
 fullcontact varchar(255), -- peer --
 vmexten varchar(40), -- general / peer --
 callingpres INTEGER, -- BOOLEAN -- user / peer --
 ipaddr varchar(255) NOT NULL DEFAULT '',
 regseconds INTEGER NOT NULL DEFAULT 0,
 regserver varchar(20),
 lastms varchar(15) NOT NULL DEFAULT '',
 parkinglot INTEGER DEFAULT NULL,
 protocol varchar(15) NOT NULL DEFAULT 'sip' CHECK (protocol = 'sip'), -- ENUM
 category VARCHAR(8) NOT NULL,

 outboundproxy varchar(1024),
	-- asterisk 1.8 new values
 transport varchar(255) DEFAULT NULL,
 remotesecret varchar(255) DEFAULT NULL,
 directmedia VARCHAR(16) DEFAULT NULL,
 callcounter INTEGER DEFAULT NULL, -- BOOLEAN
 busylevel integer DEFAULT NULL,
 ignoresdpversion INTEGER DEFAULT NULL, -- BOOLEAN
 'session-timers' VARCHAR(16) DEFAULT NULL,
 'session-expires' integer DEFAULT NULL,
 'session-minse' integer DEFAULT NULL,
 'session-refresher' VARCHAR(8) DEFAULT NULL,
 callbackextension varchar(255) DEFAULT NULL,
 registertrying INTEGER DEFAULT NULL, -- BOOLEAN
 timert1 integer DEFAULT NULL,
 timerb integer DEFAULT NULL,
 
 qualifyfreq integer DEFAULT NULL,
 contactpermit varchar(1024) DEFAULT NULL,
 contactdeny varchar(1024) DEFAULT NULL,
 unsolicited_mailbox varchar(1024) DEFAULT NULL,
 use_q850_reason INTEGER DEFAULT NULL, -- BOOLEAN
 encryption INTEGER DEFAULT NULL, -- BOOLEAN
 snom_aoc_enabled INTEGER DEFAULT NULL, -- BOOLEAN
 maxforwards integer DEFAULT NULL,
 disallowed_methods varchar(1024) DEFAULT NULL,
 textsupport INTEGER DEFAULT NULL, -- BOOLEAN
 callgroup varchar(64) DEFAULT '', -- i.e: 3,4-9
 pickupgroup varchar(64) DEFAULT '',   -- i.e: 1,3-9
 commented INTEGER NOT NULL DEFAULT 2, -- BOOLEAN -- user / peer --
 PRIMARY KEY(id)
);

CREATE INDEX usersip__idx__mailbox ON usersip(mailbox);
CREATE INDEX usersip__idx__protocol ON usersip(protocol);
CREATE INDEX usersip__idx__category ON usersip(category);
CREATE INDEX usersip__idx__commented ON usersip(commented);
CREATE INDEX usersip__idx__host_port ON usersip(host,port);
CREATE INDEX usersip__idx__ipaddr_port ON usersip(ipaddr,port);
CREATE INDEX usersip__idx__lastms ON usersip(lastms);
CREATE UNIQUE INDEX usersip__uidx__name ON usersip(name);

INSERT INTO "usersip" VALUES (1, 'autoprov','friend','autoprov','autoprov','','xivo-initconfig',NULL,NULL,'default',
NULL,NULL,NULL,NULL,0,NULL,0,'Autoprov Mode',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,
NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,
'XIVO_USERID=1','dynamic',NULL,NULL,NULL,NULL,NULL,NULL,'',0,NULL,'',NULL,'sip','user',
NULL,'udp',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,
NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'','',0);


DROP TABLE voicemail;
CREATE TABLE voicemail (
 uniqueid integer unsigned,
 context varchar(39) NOT NULL,
 mailbox varchar(40) NOT NULL,
 password varchar(80) NOT NULL DEFAULT '',
 fullname varchar(80) NOT NULL DEFAULT '',
 email varchar(80),
 pager varchar(80),
 dialout varchar(39),
 callback varchar(39),
 exitcontext varchar(39),
 language varchar(20),
 tz varchar(80),
 attach INTEGER, -- BOOLEAN
 saycid INTEGER, -- BOOLEAN
 review INTEGER, -- BOOLEAN
 operator INTEGER, -- BOOLEAN
 envelope INTEGER, -- BOOLEAN
 sayduration INTEGER, -- BOOLEAN
 saydurationm INTEGER,
 sendvoicemail INTEGER, -- BOOLEAN
 deletevoicemail INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 forcename INTEGER, -- BOOLEAN
 forcegreetings INTEGER, -- BOOLEAN
 hidefromdir VARCHAR(8) NOT NULL DEFAULT 'no',
 maxmsg INTEGER,
 emailsubject varchar(1024),
 emailbody text,
 imapuser varchar(1024),
 imappassword varchar(1024),
 imapfolder varchar(1024),
 imapvmsharedid varchar(1024),
 attachfmt varchar(1024),
 serveremail varchar(1024),
 locale varchar(1024),
 tempgreetwarn INTEGER DEFAULT NULL, -- BOOLEAN
 messagewrap INTEGER DEFAULT NULL, -- BOOLEAN
 moveheard INTEGER DEFAULT NULL, -- BOOLEAN
 minsecs integer DEFAULT NULL,
 maxsecs integer DEFAULT NULL,
 nextaftercmd INTEGER DEFAULT NULL, -- BOOLEAN
 backupdeleted integer DEFAULT NULL,
 volgain float DEFAULT NULL,
 passwordlocation VARCHAR(16) DEFAULT NULL,
 commented INTEGER NOT NULL DEFAULT 0, -- BOOLEAN
 PRIMARY KEY(uniqueid)
);

CREATE INDEX voicemail__idx__context ON voicemail(context);
CREATE INDEX voicemail__idx__commented ON voicemail(commented);
CREATE UNIQUE INDEX voicemail__uidx__mailbox_context ON voicemail(mailbox,context);


DROP TABLE voicemailfeatures;
CREATE TABLE voicemailfeatures (
 id integer unsigned,
 voicemailid integer unsigned,
 skipcheckpass tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX voicemailfeatures__uidx__voicemailid ON voicemailfeatures(voicemailid);


DROP TABLE voicemenu;
CREATE TABLE voicemenu (
 id integer unsigned,
 name varchar(29) NOT NULL DEFAULT '',
 number varchar(40) NOT NULL,
 context varchar(39) NOT NULL,
 commented tinyint(1) NOT NULL DEFAULT 0,
 description text NOT NULL,
 PRIMARY KEY(id)
);

CREATE INDEX voicemenu__idx__number ON voicemenu(number);
CREATE INDEX voicemenu__idx__context ON voicemenu(context);
CREATE INDEX voicemenu__idx__commented ON voicemenu(commented);
CREATE UNIQUE INDEX voicemenu__uidx__name ON voicemenu(name);

-- queueskill categories
DROP TABLE queueskillcat;
CREATE TABLE queueskillcat (
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX queueskillcat__uidx__name ON queueskillcat(name);

-- queueskill values
DROP TABLE queueskill;
CREATE TABLE queueskill (
 id integer unsigned,
 catid integer unsigned NOT NULL DEFAULT 1,
 name varchar(64) NOT NULL DEFAULT '',
 description text,
 printscreen varchar(5),
 PRIMARY KEY(id)
);

CREATE INDEX queueskill__idx__catid ON queueskill(catid);
CREATE UNIQUE INDEX queueskill__uidx__name ON queueskill(name);

-- queueskill rules;
DROP TABLE queueskillrule;
CREATE TABLE queueskillrule
(
 id integer unsigned,
 name varchar(64) NOT NULL DEFAULT '',
 rule text,
 PRIMARY KEY(id)
);

-- user queueskills
DROP TABLE userqueueskill;
CREATE TABLE userqueueskill
(
 userid integer unsigned,
 skillid integer unsigned,
 weight integer unsigned NOT NULL DEFAULT 0,
 PRIMARY KEY(userid, skillid)
);

CREATE INDEX userqueueskill__idx__userid ON userqueueskill(userid);


-- http://chan-sccp-b.sourceforge.net/doc/structsccp__device.html
DROP TABLE usersccp;
CREATE TABLE usersccp
(
 id integer unsigned,
 name varchar(128),
 devicetype varchar(64),            -- phone model, ie 7960
 keepalive tinyint unsigned,        -- i.e 60
 tzoffset varchar(3),               -- ie: +1 == Europe/Paris
 dtmfmode varchar(16),               -- outofband, inband
 transfer varchar(3),                -- on, off, NULL
 park varchar(3),                    -- on, off, NULL
 cfwdall varchar(3),                 -- on, off, NULL
 cfwdbusy varchar(3),                -- on, off, NULL
 cfwdnoanswer varchar(3),            -- on, off, NULL
 mwilamp varchar(5),                 -- on, off, wink, flash, blink, NULL
 mwioncall varchar(3),               -- on, off, NULL
 dnd varchar(6),                     -- on, off, NULL
 pickupexten varchar(3),             -- on, off, NULL
 pickupcontext varchar(64),          -- pickup context name
 pickupmodeanswer varchar(3),        -- on, off, NULL
 permit varchar(31),                 -- 192.168.0.0/255.255.255.0
 deny varchar(31),                   -- 0.0.0.0/0.0.0.0
 addons varchar(24),                 -- comma separated addons list. i.e 7914,7914
 imageversion varchar(64),           -- i.e P00405000700
 trustphoneip varchar(3),            -- yes, no, NULL
 nat varchar(3),                     -- on, off, NULL
 directrtp varchar(3),               -- on, off, NULL
 earlyrtp varchar(7),                -- none, offhook, dial, ringout, on, off, NULL
 private varchar(3),                 -- on, off, NULL
 privacy varchar(4),                 -- on, off, full, NULL
 protocol varchar(4) NOT NULL DEFAULT 'sccp', -- required for join with userfeatures

 -- softkeys
 softkey_onhook      varchar(1024),
 softkey_connected   varchar(1024),
 softkey_onhold      varchar(1024),
 softkey_ringin      varchar(1024),
 softkey_offhook     varchar(1024),
 softkey_conntrans   varchar(1024),
 softkey_digitsfoll  varchar(1024),
 softkey_connconf    varchar(1024),
 softkey_ringout     varchar(1024),
 softkey_offhookfeat varchar(1024),
 softkey_onhint      varchar(1024),
           
 defaultline integer unsigned,
 commented tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX usersccp__uidx__name ON usersccp(name);
--INSERT INTO usersccp VALUES (NULL, 'SEP00164766A428', '7960', '2', 'inband', 'on', 'on', 'on', 'on', '', 0)

-- http://chan-sccp-b.sourceforge.net/doc/structsccp__line.html
DROP TABLE sccpline;
CREATE TABLE sccpline
(
 id integer unsigned,
 name varchar(80) NOT NULL,
 pin varchar(8) NOT NULL DEFAULT '',
 label varchar(128) NOT NULL DEFAULT '',
 description text,
 context varchar(64),
 incominglimit tinyint unsigned,
 transfer varchar(3) DEFAULT 'on',                    -- on, off, NULL
 mailbox varchar(64) DEFAULT NULL,
 vmnum varchar(64) DEFAULT NULL,
 meetmenum varchar(64) DEFAULT NULL,
 cid_name varchar(64) NOT NULL DEFAULT '',
 cid_num varchar(64) NOT NULL DEFAULT '',
 trnsfvm varchar(64),
 secondary_dialtone_digits varchar(10),
 secondary_dialtone_tone integer unsigned,
 musicclass varchar(32),
 language varchar(32),                                 -- en, fr, ...
 accountcode varchar(32),
 audio_tos varchar(8),
 audio_cos integer unsigned,
 video_tos varchar(8),
 video_cos integer unsigned,
 echocancel varchar(3) DEFAULT 'on',                   -- on, off, NULL
 silencesuppression varchar(3) DEFAULT 'on',           -- on, off, NULL
 callgroup varchar(64) DEFAULT '',                     -- i.e: 1,4-9
 pickupgroup varchar(64) DEFAULT '',                   -- i.e: 1,3-9
 amaflags varchar(16) DEFAULT '',                      -- default, omit, billing, documentation
 adhocnumber varchar(64),
 setvar varchar(512) DEFAULT '',
 commented tinyint(1) NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);

CREATE UNIQUE INDEX sccpline__uidx__name ON sccpline(name);

-- INSERT INTO sccpline (id, name, pin, label) VALUES (NULL, '160', '1234', 'ligne 160');


DROP TABLE general;
CREATE TABLE general
(
 id       integer unsigned,
 timezone varchar(128),
 exchange_trunkid INTEGER DEFAULT NULL,
 exchange_exten   varchar(128) DEFAULT NULL,
 dundi            INTEGER NOT NULL DEFAULT 0, -- boolean
 PRIMARY KEY(id)
);

INSERT INTO general VALUES (1, 'Europe/Paris', NULL, NULL, 0);


DROP TABLE sipauthentication;
CREATE TABLE sipauthentication
(
	id         integer unsigned,
	usersip_id integer,
	user       varchar(255) NOT NULL,
	secretmode varchar(5) NOT NULL, -- md5 or clear
	secret     varchar(255) NOT NULL,
	realm      varchar(1024) NOT NULL,
	PRIMARY KEY(id)
);
CREATE INDEX sipauthentication__idx__usersip_id ON sipauthentication(usersip_id);


DROP TABLE iaxcallnumberlimits;
CREATE TABLE iaxcallnumberlimits
(
 id          integer unsigned,
 destination varchar(39) NOT NULL,
 netmask     varchar(39) NOT NULL,
 calllimits  integer NOT NULL DEFAULT 0,
 PRIMARY KEY(id)
);


DROP TABLE queue_log;
CREATE TABLE queue_log (
  time char(30),
  callid char(50),
  queuename char(50),
  agent char(50),
  event char(20),
  data1 char(255),
  data2 char(255),
  data3 char(255),
  data4 char(255),
  data5 char(255)
);
CREATE INDEX queue_log__idx_time ON queue_log(time);
CREATE INDEX queue_log__idx_queuename ON queue_log(queuename);
CREATE INDEX queue_log__idx_agent ON queue_log(agent);
CREATE INDEX queue_log__idx_event ON queue_log(event);
CREATE INDEX queue_log__idx_data1 ON queue_log(data1);
CREATE INDEX queue_log__idx_data2 ON queue_log(data2);


DROP TABLE pickup;
CREATE TABLE pickup (
 -- id is not an autoincrement number, because pickups are between 0 and 63 only
 id INTEGER NOT NULL,
 name VARCHAR(128) UNIQUE NOT NULL,
 commented INTEGER NOT NULL DEFAULT 0,
 description TEXT NOT NULL DEFAULT '',
 PRIMARY KEY(id)
);


DROP TABLE  pickupmember;
CREATE TABLE pickupmember (
 pickupid INTEGER NOT NULL,
 category VARCHAR(8) NOT NULL,
 membertype VARCHAR(8) NOT NULL,
 memberid INTEGER NOT NULL,
 PRIMARY KEY(pickupid,category,membertype,memberid)
);


DROP TABLE  dundi;
CREATE TABLE dundi (
 id            INTEGER UNSIGNED,
 department    VARCHAR(255) DEFAULT NULL,
 organization  VARCHAR(255) DEFAULT NULL,
 locality      VARCHAR(255) DEFAULT NULL,
 stateprov     VARCHAR(255) DEFAULT NULL,
 country       VARCHAR(3)   DEFAULT NULL,
 email         VARCHAR(255) DEFAULT NULL,
 phone         VARCHAR(40)  DEFAULT NULL,

 bindaddr      VARCHAR(40)  DEFAULT '0.0.0.0',
 port          INTEGER      DEFAULT 4520,
 tos           VARCHAR(4)   DEFAULT NULL,
 entityid      VARCHAR(20)  DEFAULT NULL,
 cachetime     INTEGER      DEFAULT 5,
 ttl           INTEGER      DEFAULT 2,
 autokill      VARCHAR(16)  NOT NULL DEFAULT 'yes',
 secretpath    VARCHAR(64)  DEFAULT NULL,
 storehistory  INTEGER      DEFAULT 0, -- boolean
 PRIMARY KEY(id)
);

INSERT INTO dundi VALUES (1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '0.0.0.0', 4520, NULL, NULL, 5, 2, 'yes', NULL, 0);


DROP TABLE  dundi_mapping;
CREATE TABLE dundi_mapping (
 id              INTEGER UNSIGNED,
 name            VARCHAR(255) NOT NULL,
 context         VARCHAR(39)  NOT NULL,
 weight          VARCHAR(64)  NOT NULL DEFAULT '0',
 trunk           INTEGER      DEFAULT NULL, 
 number          VARCHAR(64)  DEFAULT NULL,

 -- options
 nounsolicited   INTEGER      NOT NULL DEFAULT 0, -- boolean
 nocomunsolicit  INTEGER      NOT NULL DEFAULT 0, -- boolean
 residential     INTEGER      NOT NULL DEFAULT 0, -- boolean
 commercial      INTEGER      NOT NULL DEFAULT 0, -- boolean
 mobile          INTEGER      NOT NULL DEFAULT 0, -- boolean
 nopartial       INTEGER      NOT NULL DEFAULT 0, -- boolean

 commented       INTEGER      NOT NULL DEFAULT 0, -- boolean
 description     TEXT         NOT NULL,
 PRIMARY KEY(id)
);


DROP TABLE  dundi_peer;
CREATE TABLE dundi_peer (
 id            INTEGER UNSIGNED,
 macaddr       VARCHAR(64)  NOT NULL,
 model         VARCHAR(16)  NOT NULL,
 host          VARCHAR(256) NOT NULL,
 inkey         VARCHAR(64)  DEFAULT NULL,
 outkey        VARCHAR(64)  DEFAULT NULL,
 include       VARCHAR(64)  DEFAULT NULL,
 noinclude     VARCHAR(64)  DEFAULT NULL,
 permit        VARCHAR(64)  DEFAULT NULL,
 deny          VARCHAR(64)  DEFAULT NULL,
 qualify       VARCHAR(16)  NOT NULL DEFAULT 'yes',
 'order'         VARCHAR(16)  DEFAULT NULL,
 precache      VARCHAR(16)  DEFAULT NULL,
 commented     INTEGER      NOT NULL DEFAULT 0, -- boolean
 description   TEXT         NOT NULL,
 PRIMARY KEY(id)
);

-- DAHDI
DROP TABLE  dahdi_general;
CREATE TABLE dahdi_general (
 id                  INTEGER UNSIGNED,
 context             VARCHAR(255) DEFAULT NULL,
 language            VARCHAR(16) DEFAULT NULL,
 usecallerid         INTEGER DEFAULT NULL, -- BOOLEAN
 hidecallerid        INTEGER DEFAULT NULL, -- BOOLEAN
 callerid            VARCHAR(64) DEFAULT NULL,
 restrictcid         INTEGER DEFAULT NULL, -- BOOLEAN
 usecallingpres      INTEGER DEFAULT NULL, -- BOOLEAN
 pridialplan         VARCHAR(64) DEFAULT NULL,
 prilocaldialplan    VARCHAR(64) DEFAULT NULL,
 priindication       VARCHAR(64) DEFAULT NULL,
 nationalprefix      VARCHAR(64) DEFAULT NULL,
 internationalprefix VARCHAR(64) DEFAULT NULL,
 threewaycalling     INTEGER DEFAULT NULL, -- BOOLEAN
 transfer            INTEGER DEFAULT NULL, -- BOOLEAN
 echocancel          INTEGER DEFAULT NULL, -- BOOLEAN
 echotraining        INTEGER DEFAULT NULL, -- BOOLEAN
 relaxdtmf           INTEGER DEFAULT NULL, -- BOOLEAN

 PRIMARY KEY (id)
);

INSERT INTO dahdi_general VALUES(1,'from-extern','fr_FR',1,0,'asreceived',0,1,'unknown','dynamic','outofband','0','00',1,1,1,NULL,1);


DROP TABLE  dahdi_group;
CREATE TABLE dahdi_group (
 groupno    INTEGER NOT NULL,
 context    VARCHAR(255),
 signalling VARCHAR(64),
 switchtype VARCHAR(64),

 mailbox    INTEGER,
 callerid   VARCHAR(255),

 channels   VARCHAR(255), -- comma separated channel numbers.ie: 64,65,68-70
 commented  INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY (groupno)
);

-- sample datas
-- INSERT INTO dahdi_group VALUES (1,'from-extern','pri_cpe','euroisdn',NULL,NULL,'1-15,17-31');
-- INSERT INTO dahdi_group VALUES (2,'from-extern','fxo_ks',NULL,'4032','bob sponge <4032>', '32');
-- INSERT INTO dahdi_group VALUES (3,'from-extern','fxs_ks',NULL,NULL,NULL, '33');


DROP TABLE callcenter_campaigns_general;
CREATE TABLE callcenter_campaigns_general (
	id                        INTEGER unsigned auto_increment,
	records_path              VARCHAR(2038) DEFAULT NULL,
	records_announce          VARCHAR(255) DEFAULT NULL,

	purge_syst_tagged_delay   INTEGER DEFAULT 15552000, -- 6 months
	purge_syst_tagged_at      TIME DEFAULT '00:00',
	purge_syst_untagged_delay INTEGER DEFAULT 2592000,  -- 30 days
	purge_syst_untagged_at    TIME DEFAULT '00:00',
	purge_punct_delay         INTEGER DEFAULT 15552000, -- 6 months
	purge_punct_at            TIME DEFAULT '00:00',

	-- SVI closed choices (press #1, #2, ...) VARIABLES
	-- i.e: "lang=XIVO_LANG;os=XIVO_OS"
	svichoices                TEXT,
	-- SVI open entries
	-- i.e: "creditcard=XIVO_CREDITCARDNO;password=XIVO_CREDITCARDPWD"
	svientries                TEXT,
	-- SVI extra defined variables (retrieved from ERP, ...)
	-- i.e: "customer=CUSTOMERNO"
	svivariables              TEXT,
	PRIMARY KEY (id)
);

INSERT INTO callcenter_campaigns_general VALUES(1,NULL,NULL,15552000,'00:00',2592000,'00:00',15552000,'00:00',NULL,NULL,NULL);


DROP TABLE callcenter_campaigns_campaign;
CREATE TABLE callcenter_campaigns_campaign (
	id               INTEGER unsigned auto_increment,
	name             VARCHAR(255) UNIQUE NOT NULL,
	start            DATETIME NOT NULL,
	end              DATETIME DEFAULT NULL,
	created_at       DATETIME,
	PRIMARY KEY (id)
);

DROP TABLE callcenter_campaigns_campaign_filter;
CREATE TABLE callcenter_campaigns_campaign_filter (
	campaign_id      INTEGER unsigned auto_increment,
	type             VARCHAR(8) NOT NULL,
	value            VARCHAR(255) NOT NULL,
	PRIMARY KEY (campaign_id,type,value)
);

DROP TABLE callcenter_campaigns_tag;
CREATE TABLE callcenter_campaigns_tag (
	name             VARCHAR(32),
	label            VARCHAR(255) NOT NULL,
	action           INTEGER NOT NULL,
	PRIMARY KEY (name)
);

INSERT INTO callcenter_campaigns_tag VALUES('notag', 'no tag', 'purge');

DROP TABLE callcenter_campaigns_records;
CREATE TABLE callcenter_campaigns_records (
	id                INTEGER unsigned auto_increment,
	uniqueid          VARCHAR(32) NOT NULL,
	channel           VARCHAR(32) NOT NULL,
	filename          VARCHAR(64) NOT NULL,
	campaignkind      VARCHAR(1) NOT NULL,

	direction         VARCHAR(1) NOT NULL,
	calleridnum       VARCHAR(32) NOT NULL,

	callstart         FLOAT NOT NULL,
	callstop          FLOAT NULL,
	callduration      INTEGER(11) NULL,
	callstatus        VARCHAR(16) NOT NULL,
	recordstatus      VARCHAR(16) NOT NULL,

	skillrules        VARCHAR(255) NOT NULL,
	queuenames        VARCHAR(255) NOT NULL,
	agentnames        VARCHAR(255) NOT NULL,
	agentnumbers      VARCHAR(255) NOT NULL,
	agentrights       VARCHAR(255) NOT NULL,

	callrecordtag     VARCHAR(16) NULL,
	callrecordcomment VARCHAR(255) NULL,

	svientries        VARCHAR(255) NULL,
	svichoices        VARCHAR(255) NULL,
	svivariables      VARCHAR(255) NULL,
	PRIMARY KEY (id)
);

COMMIT;
