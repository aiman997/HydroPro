-- Verify userdb:role_table on pg

BEGIN;

SELECT table_name
  FROM information_schema.tables
 WHERE table_schema = 'users' AND table_name = 'role';

ROLLBACK;
