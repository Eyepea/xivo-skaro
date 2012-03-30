/*
 * XiVO Base-Config
 * Copyright (C) 2012  Avencall
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

-- alter type "trunk_protocol" add new value 'sccp'
BEGIN;

ALTER TYPE "trunk_protocol" RENAME TO "trunk_protocol2";
CREATE TYPE "trunk_protocol" AS ENUM ('sip', 'iax', 'sccp', 'custom');

ALTER TABLE "linefeatures" DROP COLUMN IF EXISTS "_protocol";
ALTER TABLE "linefeatures" RENAME COLUMN "protocol" TO "_protocol";
ALTER TABLE "linefeatures" ADD "protocol" "trunk_protocol";
UPDATE "linefeatures" SET "protocol" = "_protocol"::text::"trunk_protocol";
ALTER TABLE "linefeatures" DROP COLUMN "_protocol";

ALTER TABLE "trunkfeatures" DROP COLUMN IF EXISTS "_protocol";
ALTER TABLE "trunkfeatures" RENAME COLUMN "protocol" TO "_protocol";
ALTER TABLE "trunkfeatures" ADD "protocol" "trunk_protocol";
UPDATE "trunkfeatures" SET "protocol" = "_protocol"::text::"trunk_protocol";
ALTER TABLE "trunkfeatures" DROP COLUMN "_protocol";

ALTER TABLE "usercustom" DROP COLUMN IF EXISTS "_protocol";
ALTER TABLE "usercustom" RENAME COLUMN "protocol" TO "_protocol";
ALTER TABLE "usercustom" ADD "protocol" "trunk_protocol";
UPDATE "usercustom" SET "protocol" = "_protocol"::text::"trunk_protocol";
ALTER TABLE "usercustom" DROP COLUMN "_protocol";

ALTER TABLE "useriax" DROP COLUMN IF EXISTS "_protocol";
ALTER TABLE "useriax" RENAME COLUMN "protocol" TO "_protocol";
ALTER TABLE "useriax" ADD "protocol" "trunk_protocol";
UPDATE "useriax" SET "protocol" = "_protocol"::text::"trunk_protocol";
ALTER TABLE "useriax" DROP COLUMN "_protocol";

ALTER TABLE "usersip" DROP COLUMN IF EXISTS "_protocol";
ALTER TABLE "usersip" RENAME COLUMN "protocol" TO "_protocol";
ALTER TABLE "usersip" ADD "protocol" "trunk_protocol";
UPDATE "usersip" SET "protocol" = "_protocol"::text::"trunk_protocol";
ALTER TABLE "usersip" DROP COLUMN "_protocol";

DROP TYPE "trunk_protocol2";

COMMIT;


BEGIN;

ALTER TABLE "sccpline" ADD "context" varchar(80) NOT NULL;
ALTER TABLE "sccpline" ADD "commented" INTEGER NOT NULL DEFAULT 0;

COMMIT;
