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

ALTER TYPE "usersip_nat" RENAME TO "usersip_nat2";
CREATE TYPE "usersip_nat" AS ENUM ('no','yes','force_rport','comedia');

ALTER TABLE "usersip" RENAME COLUMN "nat" TO "_nat";

ALTER TABLE "usersip" ADD "nat" "usersip_nat";

UPDATE "usersip" SET "nat" = "_nat"::text::"usersip_nat";

ALTER TABLE "usersip" DROP COLUMN "_nat";

DROP TYPE "usersip_nat2";

COMMIT;
