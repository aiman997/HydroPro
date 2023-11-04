-- Revert userdb:update_user from pg

BEGIN;

DROP FUNCTION users.update_user( BIGINT, TEXT, TEXT, TEXT, TEXT, TEXT, BOOLEAN, TIMESTAMPTZ, VARCHAR );

COMMIT;
