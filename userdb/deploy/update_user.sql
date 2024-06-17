-- Deploy userdb:update_user to pg
-- requires: user_table

BEGIN;

CREATE OR REPLACE FUNCTION users.update_user(
    p_user_id BIGINT,
    p_user_name TEXT,
    p_email TEXT,
    p_password TEXT,
    p_first_name TEXT,
    p_last_name TEXT,
    p_active BOOLEAN,
    p_confirmed_at TIMESTAMPTZ,
    p_roles VARCHAR
)
RETURNS users.user AS $$
DECLARE
    v_updated_user users.user;
BEGIN

    IF NOT EXISTS (
        SELECT 1 
          FROM users.user 
         WHERE id = p_user_id
        ) THEN
        RAISE EXCEPTION 'User with id % does not exist', p_user_id;
    END IF;

    UPDATE users.user
    SET 
        email = COALESCE(p_email, users.user.email),
        password = COALESCE(p_password, users.user.password),
        first_name = COALESCE(p_first_name, users.user.first_name),
        last_name = COALESCE(p_last_name, users.user.last_name),
        active = COALESCE(p_active, users.user.active),
        confirmed_at = COALESCE(p_confirmed_at, users.user.confirmed_at),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = p_user_id
    RETURNING * INTO v_updated_user;

    RETURN v_updated_user;
END;
$$ LANGUAGE plpgsql;

COMMIT;
