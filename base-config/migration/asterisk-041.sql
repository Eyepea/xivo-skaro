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

ALTER TABLE "ctireversedirectories" DROP "context";
ALTER TABLE "ctireversedirectories" DROP "extensions";
ALTER TABLE "ctireversedirectories" DROP "description";
ALTER TABLE "ctireversedirectories" DROP "deletable";


CREATE FUNCTION asterisk_041()
  RETURNS void AS
$$
DECLARE
    first_directories text;
BEGIN
    SELECT "directories" INTO first_directories FROM "ctireversedirectories" ORDER BY "id" LIMIT 1;
    IF NOT FOUND THEN
        first_directories := '[]';
    END IF;

    DELETE FROM "ctireversedirectories";
    INSERT INTO "ctireversedirectories" VALUES(1,first_directories);
END;
$$
LANGUAGE 'plpgsql';

SELECT asterisk_041();

DROP FUNCTION asterisk_041();

COMMIT;
