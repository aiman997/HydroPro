-- Revert userdb:role_table from pg

BEGIN;

DROP TABLE users.role;

COMMIT;
