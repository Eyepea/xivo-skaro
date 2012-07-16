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

DROP TABLE IF EXISTS "stat_queue_periodic";
DROP TABLE IF EXISTS "stat_call_on_queue";
DROP TYPE IF EXISTS "call_exit_type";
DROP TABLE IF EXISTS "stat_queue";


CREATE TABLE "stat_queue" (
 "id" SERIAL PRIMARY KEY,
 "name" VARCHAR(128) NOT NULL
);

CREATE TYPE "call_exit_type" AS ENUM (
  'full',
  'closed',
  'joinempty',
  'leaveempty',
  'reroutedguide',
  'reroutednumber',
  'answered',
  'abandoned',
  'timeout'
);

CREATE TABLE "stat_queue_periodic" (
 "id" SERIAL PRIMARY KEY,
 "time" timestamp NOT NULL,
 "answered" INTEGER NOT NULL DEFAULT 0,
 "abandoned" INTEGER NOT NULL DEFAULT 0,
 "total" INTEGER NOT NULL DEFAULT 0,
 "full" INTEGER NOT NULL DEFAULT 0,
 "closed" INTEGER NOT NULL DEFAULT 0,
 "joinempty" INTEGER NOT NULL DEFAULT 0,
 "leaveempty" INTEGER NOT NULL DEFAULT 0,
 "reroutedguide" INTEGER NOT NULL DEFAULT 0,
 "reroutednumber" INTEGER NOT NULL DEFAULT 0,
 "timeout" INTEGER NOT NULL DEFAULT 0,
 "queue_id" INTEGER REFERENCES stat_queue (id)
);

CREATE TABLE "stat_call_on_queue" (
 "callid" VARCHAR(32) NOT NULL,
 "time" timestamp NOT NULL,
 "ringtime" INTEGER,
 "talktime" INTEGER,
 "status" call_exit_type NOT NULL,
 "queue_id" INTEGER REFERENCES stat_queue (id),
 PRIMARY KEY("callid")
);

GRANT ALL ON ALL TABLES IN SCHEMA public TO asterisk;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public to asterisk;

COMMIT;
