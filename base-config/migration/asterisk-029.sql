BEGIN;

CREATE TABLE "agentglobalparams" (
 "id" SERIAL,
 "category" varchar(128) NOT NULL,
 "option_name" varchar(255) NOT NULL,
 "option_value" varchar(255),
 PRIMARY KEY("id")
);
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'general','multiplelogin','yes');
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'general','persistentagents','yes');
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'agents','urlprefix','');
INSERT INTO "agentglobalparams" VALUES (DEFAULT,'agents','savecallsin','');

insert into "agentglobalparams" ("option_name","option_value","category")
select distinct(var_name),var_val,category from staticagent  where category = 'agents' and var_name not in ('deleted','agent','group') and var_val != '';

COMMIT;

-- grant all rights to asterisk.* for asterisk user
BEGIN;

SELECT execute('GRANT ALL ON '||schemaname||'.'||tablename||' TO asterisk;') FROM pg_tables WHERE schemaname = 'public';
SELECT execute('GRANT ALL ON SEQUENCE '||relname||' TO asterisk;') FROM pg_class WHERE relkind = 'S';

COMMIT;
