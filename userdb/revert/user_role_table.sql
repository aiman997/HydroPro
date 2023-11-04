-- Revert userdb:user_role_table from pg

BEGIN;

DROP TABLE users.user_role;

COMMIT;
