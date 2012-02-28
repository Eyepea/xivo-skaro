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

BEGIN;

-- Create new type

DROP TYPE IF EXISTS "trunk_protocol";
CREATE TYPE "trunk_protocol" AS ENUM ('sip', 'iax', 'custom');

-- Update trunkfeatures.protocol to use trunk_protocol

ALTER TABLE "trunkfeatures" RENAME COLUMN "protocol" TO "_protocol";
ALTER TABLE "trunkfeatures" ADD "protocol" "trunk_protocol";

UPDATE "trunkfeatures" SET "protocol" = 'sip' where "_protocol" = 'sip';
UPDATE "trunkfeatures" SET "protocol" = 'iax' where "_protocol" = 'iax';
UPDATE "trunkfeatures" SET "protocol" = 'custom' where "_protocol" = 'custom';

ALTER TABLE "trunkfeatures" DROP COLUMN "_protocol";

COMMIT;
