-- Revert userdb:create_user from pg

BEGIN;

DROP FUNCTION IF EXISTS users.create_user(
    VARCHAR(255),
    VARCHAR(255),
    VARCHAR(100),
    VARCHAR(100),
    VARCHAR(50),
    TEXT
);

COMMIT;
