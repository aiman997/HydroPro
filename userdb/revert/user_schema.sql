-- Revert userdb:user_schema from pg

BEGIN;

DROP SCHEMA users;

COMMIT;
