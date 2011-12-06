/*
 * XiVO Base-Config
 * Copyright (C) 2011  Avencall
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

\connect asterisk;

BEGIN;

-- alter type "useriax_type" add new value 'user' in enum ('friend', 'peer');
ALTER TYPE "useriax_type" RENAME TO "useriax_type2";
CREATE TYPE "useriax_type" AS ENUM ('friend', 'peer', 'user');

ALTER TABLE "useriax" RENAME COLUMN "type" TO "_type";
ALTER TABLE "usersip" RENAME COLUMN "type" TO "_type";

ALTER TABLE "useriax" ADD "type" "useriax_type";
ALTER TABLE "usersip" ADD "type" "useriax_type";

UPDATE "useriax" SET "type" = "_type"::text::"useriax_type";
UPDATE "usersip" SET "type" = "_type"::text::"useriax_type";

ALTER TABLE "useriax" DROP COLUMN "_type";
ALTER TABLE "usersip" DROP COLUMN "_type";

DROP TYPE "useriax_type2";


-- remove faxdetect for incall
ALTER TABLE "incall" DROP COLUMN IF EXISTS faxdetectenable;
ALTER TABLE "incall" DROP COLUMN IF EXISTS faxdetecttimeout;
ALTER TABLE "incall" DROP COLUMN IF EXISTS faxdetectemail;


-- fix trunk management iax form
ALTER TABLE "useriax" ADD COLUMN IF NOT EXISTS keyrotate INTEGER DEFAULT NULL;
ALTER TABLE "useriax" ALTER allow TYPE text USING NOT NULL;


-- fix trunk management sip form
ALTER TABLE "usersip" ALTER allow TYPE text USING NOT NULL;


-- alter type "phonefunckey_typeextenumbersright add new value 'paging' in enum ('agent', 'group', 'meetme', 'queue', 'user');

ALTER TYPE "phonefunckey_typeextenumbersright" RENAME TO "phonefunckey_typeextenumbersright2";
CREATE TYPE "phonefunckey_typeextenumbersright" AS ENUM ('agent', 'group', 'meetme', 'queue', 'user','paging');
ALTER TABLE "phonefunckey" RENAME COLUMN "typeextenumbersright" TO "_typeextenumbersright";
ALTER TABLE "phonefunckey" ADD "typeextenumbersright" "phonefunckey_typeextenumbersright";
UPDATE "phonefunckey" SET "typeextenumbersright" = "_typeextenumbersright"::text::"phonefunckey_typeextenumbersright";
ALTER TABLE "phonefunckey" DROP COLUMN "_typeextenumbersright";
DROP TYPE "phonefunckey_typeextenumbersright2";


-- remove all occurences of chan_sccp-b

DROP TABLE IF EXISTS "sccpline";
DROP TABLE IF EXISTS "usersccp";
DROP TABLE IF EXISTS "staticsccp";


-- add libsccp schema
DROP TABLE IF EXISTS "sccpgeneral";
CREATE TABLE "sccpgeneral" (
	"id"		SERIAL,
	"name"		varchar(80) NOT NULL,
	"option_name"	varchar(80) NOT NULL,
	"value"		varchar(80) NOT NULL,
	PRIMARY KEY("id")
);

DROP TABLE IF EXISTS "sccpline";
CREATE TABLE "sccpline" (
	"id"		SERIAL,
	"name"		varchar(80) NOT NULL,
	"cid_name"	varchar(80) NOT NULL,
	"cid_num"	varchar(80) NOT NULL,
	PRIMARY KEY("id")
);

DROP TABLE IF EXISTS "sccpdevice";
CREATE TABLE "sccpdevice" (
	"id"		SERIAL,
	"name"		varchar(80) NOT NULL,
	"device"	varchar(80) NOT NULL,
	"line"		varchar(80) NOT NULL,
	PRIMARY KEY("id")
);


-- grant all rights to asterisk.* for asterisk user
SELECT execute('GRANT ALL ON '||schemaname||'.'||tablename||' TO asterisk;') FROM pg_tables WHERE schemaname = 'public';
SELECT execute('GRANT ALL ON SEQUENCE '||relname||' TO asterisk;') FROM pg_class WHERE relkind = 'S';

COMMIT;
