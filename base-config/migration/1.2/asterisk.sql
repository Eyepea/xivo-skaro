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

-- alter type "useriax_type" add new value 'user' in enum ('friend', 'peer');
BEGIN;

ALTER TYPE "useriax_type" RENAME TO "useriax_type2";
CREATE TYPE "useriax_type" AS ENUM ('friend', 'peer', 'user');

ALTER TABLE "useriax" RENAME COLUMN "type" TO "_type";
ALTER TABLE "usersip" RENAME COLUMN "type" TO "_type";

ALTER TABLE "useriax" ADD type "useriax_type";
ALTER TABLE "usersip" ADD type "useriax_type";

UPDATE "useriax" SET "type" = "_type"::text::"useriax_type";
UPDATE "usersip" SET "type" = "_type"::text::"useriax_type";

ALTER TABLE "useriax" DROP COLUMN "_type";
ALTER TABLE "usersip" DROP COLUMN "_type";

DROP TYPE "useriax_type2";

COMMIT;


-- remove faxdetect for incall
BEGIN;

ALTER TABLE "incall" DROP COLUMN faxdetectenable;
ALTER TABLE "incall" DROP COLUMN faxdetecttimeout;
ALTER TABLE "incall" DROP COLUMN faxdetectemail;

COMMIT;


-- fix trunk management iax form
BEGIN;

ALTER TABLE "useriax" ADD COLUMN keyrotate INTEGER DEFAULT NULL;
ALTER TABLE "useriax" ALTER allow TYPE text USING NOT NULL;

COMMIT;


-- fix trunk management sip form
BEGIN;

ALTER TABLE "usersip" ALTER allow TYPE text USING NOT NULL;

COMMIT;
