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

BEGIN;

DROP TABLE IF EXISTS "stats_conf_xivouser";
CREATE TABLE "stats_conf_xivouser" (
    "stats_conf_id" integer NOT NULL,
    "user_id" integer NOT NULL
);
CREATE UNIQUE INDEX "stats_conf_xivouser_index" ON "stats_conf_xivouser" USING btree ("stats_conf_id","user_id");

GRANT ALL ON "stats_conf_xivouser" TO xivo;

COMMIT;
