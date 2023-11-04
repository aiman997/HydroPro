-- Verify userdb:update_user on pg

BEGIN;

SELECT proname
  FROM pg_proc
 WHERE proname = 'update_user'
   AND pronamespace = (
        SELECT oid
          FROM pg_namespace
         WHERE nspname = 'users'
       );

ROLLBACK;
