-- Deploy userdb:update_user to pg
-- requires: user_table

BEGIN;

CREATE OR REPLACE FUNCTION users.update_user(
    user_id BIGINT,
    email TEXT,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    active BOOLEAN,
    confirmed_at TIMESTAMPTZ,
    roles VARCHAR
)
RETURNS users.user AS $$
DECLARE
    updated_user users.user;
BEGIN
    -- Validate user_id to ensure it exists.
    IF NOT EXISTS (SELECT 1 FROM users.user WHERE id = user_id) THEN
        RAISE EXCEPTION 'User with id % does not exist', user_id;
    END IF;

    UPDATE users.user
    SET 
        email = COALESCE(email, users.user.email),
        password = COALESCE(password, users.user.password),
        first_name = COALESCE(first_name, users.user.first_name),
        last_name = COALESCE(last_name, users.user.last_name),
        active = COALESCE(active, users.user.active),
        confirmed_at = COALESCE(confirmed_at, users.user.confirmed_at),
        roles = COALESCE(roles, users.user.roles),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = user_id
    RETURNING * INTO updated_user;

    COMMIT;

    RETURN updated_user;
END;
$$ LANGUAGE plpgsql;

COMMIT;
