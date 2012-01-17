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

-- alter type "netiface_method" add new value 'manual' in enum ('static','dhcp');
BEGIN;

ALTER TYPE "netiface_method" RENAME TO "netiface_method2";
CREATE TYPE "netiface_method" AS ENUM ('static','dhcp','manual');
ALTER TABLE "netiface" RENAME COLUMN "method" TO "_method";
ALTER TABLE "netiface" ADD "method" "netiface_method";
UPDATE "netiface" SET "method" = "_method"::text::"netiface_method";
ALTER TABLE "netiface" DROP COLUMN "_method";
DROP TYPE "netiface_method2";

COMMIT;