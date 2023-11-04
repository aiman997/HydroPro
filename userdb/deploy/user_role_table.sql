-- Deploy userdb:user_role_table to pg
-- requires: user_table
-- requires: role_table

BEGIN;

CREATE TABLE users.user_role (
    user_id BIGINT,
    role_id INT,
    FOREIGN KEY (user_id) REFERENCES users.user(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES users.role(id) ON DELETE CASCADE
);

COMMIT;
