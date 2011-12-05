/*
 * SCCP - Skinny Client Control Protocol
 * 
 * Author: Nicolas Bouliane <nbouliane@avencall.com>
 */

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
	"cid_name"	varchar(80) NOT NULL,
	"cid_num"	varchar(80) NOT NULL,
	PRIMARY KEY("id")
);

/*
 * [cisco7940desk]
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

END;
COMMIT;
