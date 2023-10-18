-- Deploy userdb:create_user to pg
-- requires: user_table

BEGIN;

CREATE OR REPLACE FUNCTION users.create_user(
    email TEXT,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    active BOOLEAN,
    roles VARCHAR
)
RETURNS BIGINT AS $$
  DECLARE r_id BIGINT;
BEGIN
    INSERT INTO users.user( email, password, first_name, last_name, active, roles)
    VALUES (email, password, first_name, last_name, active, roles)
 RETURNING id INTO r_id;
    RETURN r_id;
END;
$$ LANGUAGE plpgsql;

COMMIT;
