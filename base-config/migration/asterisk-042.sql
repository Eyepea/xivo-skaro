
BEGIN;

DELETE FROM "dialaction" WHERE "event" = 'qctipresence';
DELETE FROM "dialaction" WHERE "event" = 'qnonctipresence';

ALTER TYPE "dialaction_event" RENAME TO "dialaction_event2";
CREATE TYPE "dialaction_event" AS ENUM ('answer',
 'noanswer',
 'congestion',
 'busy',
 'chanunavail',
 'inschedule',
 'outschedule',
 'qwaittime',
 'qwaitratio');

ALTER TABLE "dialaction" RENAME COLUMN "event" TO "_event";
ALTER TABLE "dialaction" ADD "event" "dialaction_event";
UPDATE "dialaction" SET "event" = "_event"::text::"dialaction_event";
ALTER TABLE "dialaction" DROP COLUMN "_event";
DROP TYPE "dialaction_event2";

COMMIT;
