-- Deploy userdb:role_table to pg
-- requires: user_schema

BEGIN;

CREATE TABLE users.role(
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

COMMIT;
