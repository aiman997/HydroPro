-- Verify userdb:user_role_table on pg

BEGIN;

SELECT table_name
  FROM information_schema.tables
 WHERE table_schema = 'users' AND table_name = 'user_role';

ROLLBACK;
