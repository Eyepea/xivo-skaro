
/*
 * XiVO Base-Config
 * Copyright (C) 2010  Proformatique <technique@proformatique.com>
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


DROP TABLE IF EXISTS "staticsip";
CREATE TABLE "staticsip" (
 "id" SERIAL,
 "cat_metric" int NOT NULL DEFAULT 0,
 "var_metric" int  NOT NULL DEFAULT 0,
 "commented" boolean NOT NULL DEFAULT FALSE,
 "filename" varchar(128) NOT NULL,
 "category" varchar(128) NOT NULL,
 "var_name" varchar(128) NOT NULL,
 "var_val" varchar(255),
 PRIMARY KEY("id")
);

CREATE INDEX "staticsip__idx__commented" ON "staticsip"("commented");
CREATE INDEX "staticsip__idx__filename" ON "staticsip"("filename");
CREATE INDEX "staticsip__idx__category" ON "staticsip"("category");
CREATE INDEX "staticsip__idx__var_name" ON "staticsip"("var_name");


INSERT INTO "staticsip" VALUES (nextval('staticsip_id_seq'),0,0,'f','sip.conf','general','bindport',5060);
