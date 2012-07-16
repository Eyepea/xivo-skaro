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

CREATE TABLE "agentglobalparams" (
 "id" SERIAL,
 "category" VARCHAR(128) NOT NULL,
 "option_name" VARCHAR(255) NOT NULL,
 "option_value" VARCHAR(255),
 PRIMARY KEY("id")
);
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'general','multiplelogin','yes');
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'general','persistentagents','yes');
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'agents','urlprefix','');
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'agents','savecallsin','');

INSERT INTO "agentglobalparams" ("option_name","option_value","category")
SELECT DISTINCT(var_name),var_val,category FROM staticagent  WHERE category = 'agents' AND var_name NOT IN ('deleted','agent','group') AND var_val != '';

GRANT ALL ON ALL TABLES IN SCHEMA public TO asterisk;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public to asterisk;

COMMIT;
