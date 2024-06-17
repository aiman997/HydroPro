-- Revert userdb:user_table from pg

BEGIN;

DROP TABLE users.user;

COMMIT;
