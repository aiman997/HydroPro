-- Deploy userdb:create_user to pg
-- requires: user_table

BEGIN;

CREATE OR REPLACE FUNCTION users.create_user(
    p_username VARCHAR(255),
    p_email VARCHAR(255),
    p_first_name VARCHAR(100),
    p_last_name VARCHAR(100),
    p_role_name VARCHAR(50),
    p_password_hash TEXT
)
RETURNS users.user
AS $$
DECLARE
    v_role_id INT;
    v_new_user users.user;
BEGIN
    -- Check if the role exists
    SELECT INTO v_role_id r.id
      FROM users.role r
     WHERE r.name = p_role_name;

    IF v_role_id IS NULL THEN
        RAISE EXCEPTION 'Role not found: %', p_role_name;
    END IF;

    -- Create a new user
    INSERT INTO users.user (username, email, password, first_name, last_name)
    VALUES (p_username, p_email, p_password_hash, p_first_name, p_last_name)
    RETURNING * INTO v_new_user;

    RETURN v_new_user;
END;
$$ LANGUAGE plpgsql;

COMMIT;
