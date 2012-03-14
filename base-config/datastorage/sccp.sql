/*
 * SCCP - Skinny Client Control Protocol
 * 
 * Author: Nicolas Bouliane <nbouliane@avencall.com>
 */

\connect asterisk;
BEGIN;

/*
 * [name]
 * dateformat=D.M.Y
 */
DROP TABLE IF EXISTS "sccpgeneral";
CREATE TABLE "sccpgeneral" (
	"id"		SERIAL,
	"name"		varchar(80) NOT NULL,
	"option_name"	varchar(80) NOT NULL,
	"value"		varchar(80) NOT NULL,
	PRIMARY KEY("id")
);

/*
 * [100]
 * cid_name=John Smith
 * cid_num=100
 */
DROP TABLE IF EXISTS "sccpline";
CREATE TABLE "sccpline" (
	"id"		SERIAL,
	"name"		varchar(80) NOT NULL,
    "context"   varchar(80) NOT NULL,
	"cid_name"	varchar(80) NOT NULL,
	"cid_num"	varchar(80) NOT NULL,
	"commented" INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("id")
);

/*
 * [SEPACA016FDF235]
 * device=SEPACA016FDF235
 * line=100
 */
DROP TABLE IF EXISTS "sccpdevice";
CREATE TABLE "sccpdevice" (
	"id"		SERIAL,
	"name"		varchar(80) NOT NULL,
	"device"	varchar(80) NOT NULL,
	"line"		varchar(80) NOT NULL,
	PRIMARY KEY("id")
);

-- grant all rights to asterisk.* for asterisk user
CREATE OR REPLACE FUNCTION execute(text)
RETURNS VOID AS '
BEGIN
        execute $1;
END;
' LANGUAGE plpgsql;
SELECT execute('GRANT ALL ON '||schemaname||'.'||tablename||' TO asterisk;') FROM pg_tables WHERE schemaname = 'public';
SELECT execute('GRANT ALL ON SEQUENCE '||relname||' TO asterisk;') FROM pg_class WHERE relkind = 'S';

COMMIT;
