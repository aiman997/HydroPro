SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;
CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';
SET search_path = public, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;
SET timezone = +8;

-- Users Microservice

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
RETURNS VOID AS $$
BEGIN
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
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION users.delete_user(
    user_id BIGINT
)
RETURNS VOID AS $$
BEGIN
    DELETE FROM users.user
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION users.get_user(
    v_email TEXT
)
RETURNS TABLE(
    id BIGINT,
    email TEXT,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    active BOOLEAN,
    roles VARCHAR,
    confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
    users.user.id,
    users.user.email,
    users.user.password,
    users.user.first_name,
    users.user.last_name,
    users.user.active,
    users.user.roles,
    users.user.confirmed_at,
    users.user.created_at,
    users.user.updated_at
    FROM
    users.user
    WHERE
    users.user.email = v_email;
END;
$$ LANGUAGE plpgsql;

-- Plants Microservice

CREATE SCHEMA plants;

CREATE TABLE plants.plant (
    id BIGSERIAL PRIMARY KEY,
    raspberry_pi_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE plants.grow_stage (
    id BIGSERIAL PRIMARY KEY,
    plant_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    duration INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plant_id) REFERENCES plants.plant(id)
);

CREATE TABLE plants.optimal_parameters (
    id BIGSERIAL PRIMARY KEY,
    grow_stage_id INT NOT NULL,
    parameter_name VARCHAR(50) NOT NULL,
    parameter_value VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grow_stage_id) REFERENCES plants.grow_stage(id)
);


-- Insert a new plant
CREATE OR REPLACE PROCEDURE plants.insert_plant(
    IN p_raspberry_pi_id INT,
    IN p_name VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO plants.plant (raspberry_pi_id, name)
    VALUES (p_raspberry_pi_id, p_name) RETURNING id;
END;
$$;

-- Insert a new grow stage for a plant
CREATE OR REPLACE PROCEDURE plants.insert_grow_stage(
    IN p_plant_id INT,
    IN p_name VARCHAR(50),
    IN p_duration INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO plants.grow_stage (plant_id, name, duration)
    VALUES (p_plant_id, p_name, p_duration);
END;
$$;

-- Insert a new optimal parameter for a grow stage
CREATE OR REPLACE PROCEDURE plants.insert_optimal_parameter(
    IN p_grow_stage_id INT,
    IN p_parameter_name VARCHAR(50),
    IN p_parameter_value VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO plants.optimal_parameters (grow_stage_id, parameter_name, parameter_value)
    VALUES (p_grow_stage_id, p_parameter_name, p_parameter_value);
END;
$$;

-- Update a plant's name
CREATE OR REPLACE PROCEDURE plants.update_plant_name(
    IN p_plant_id INT,
    IN p_name VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE plants.plant
    SET name = p_name,
    updated_at = NOW()
    WHERE id = p_plant_id;
END;
$$;

-- Update a grow stage's name or duration
CREATE OR REPLACE PROCEDURE plants.update_grow_stage(
    IN p_grow_stage_id INT,
    IN p_name VARCHAR(50),
    IN p_duration INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE plants.grow_stage
    SET name = p_name,
    duration = p_duration,
    updated_at = NOW()
    WHERE id = p_grow_stage_id;
END;
$$;

-- Update an optimal parameter's name or value
CREATE OR REPLACE PROCEDURE plants.update_optimal_parameter(
    IN p_optimal_parameter_id INT,
    IN p_parameter_name VARCHAR(50),
    IN p_parameter_value VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE plants.optimal_parameters
    SET parameter_name = p_parameter_name,
    parameter_value = p_parameter_value,
    updated_at = NOW()
    WHERE id = p_optimal_parameter_id;
END;
$$;

-- Delete a plant
CREATE OR REPLACE PROCEDURE plants.delete_plant(
    IN p_plant_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM plants.plant WHERE id = p_plant_id;
END;
$$;

-- Delete a grow stage
CREATE OR REPLACE PROCEDURE plants.delete_grow_stage(
    IN p_grow_stage_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM plants.grow_stage WHERE id = p_grow_stage_id;
END;
$$;

-- Delete an optimal parameter
CREATE OR REPLACE PROCEDURE plants.delete_optimal_parameter(
    IN p_optimal_parameter_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM plants.optimal_parameters WHERE id = p_optimal_parameter_id;
END;
$$;

-- RPI Microservice

CREATE SCHEMA rpi;

CREATE TABLE rpi.rpi(
    id BIGSERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE PROCEDURE rpi.insert_rpi(
    IN p_user_id INT,
    IN p_name VARCHAR(50),
    IN p_ip_address VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO rpi.rpi (user_id, name, ip_address)
    VALUES (p_user_id, p_name, p_ip_address);
END;
$$;

CREATE OR REPLACE PROCEDURE rpi.update_rpi(
    IN p_id BIGINT,
    IN p_user_id INT,
    IN p_name VARCHAR(50),
    IN p_ip_address VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE rpi.rpi SET
    user_id = p_user_id,
    name = p_name,
    ip_address = p_ip_address,
    updated_at = CURRENT_TIMESTAMP
    WHERE id = p_id;
END;
$$;

-- Reporting Microservice

CREATE SCHEMA reporting;

CREATE TABLE reporting.reading(
    id BIGSERIAL PRIMARY KEY,
    raspberry_pi_id TEXT NOT NULL,
    plant_id TEXT NOT NULL,
    status_ph TEXT NOT NULL,
    reading_ph FLOAT NOT NULL,
    status_ec TEXT NOT NULL,
    reading_ec FLOAT NOT NULL,
    status_temp TEXT NOT NULL,
    reading_temp FLOAT NOT NULL,
    status_mpump TEXT NOT NULL,
    status_ecup TEXT  NOT NULL,
    status_phup TEXT NOT NULL,
    status_phdown TEXT NOT NULL,
    reading_wlevel FLOAT NOT NULL,
    status_wlevel TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reporting.report (
    id BIGSERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE reporting.report_data (
    id BIGSERIAL PRIMARY KEY,
    report_id INT NOT NULL,
    data TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reporting.report(id)
);

CREATE OR REPLACE FUNCTION reporting.insert_reading(
    raspberry_pi_id TEXT,
    plant_id TEXT,
    status_ph TEXT,
    reading_ph FLOAT,
    status_ec TEXT,
    reading_ec FLOAT,
    status_temp TEXT,
    reading_temp FLOAT,
    status_mpump TEXT,
    status_ecup TEXT,
    status_phup TEXT,
    status_phdown TEXT,
    reading_wlevel FLOAT,
    status_wlevel TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO reporting.reading(
        raspberry_pi_id,
        plant_id,
        status_ph,
        reading_ph,
        status_ec,
        reading_ec,
        status_temp,
        reading_temp,
        status_mpump,
        status_ecup,
        status_phup,
        status_phdown,
        reading_wlevel,
        status_wlevel
        ) VALUES (
        raspberry_pi_id,
        plant_id,
        status_ph,
        reading_ph,
        status_ec,
        reading_ec,
        status_temp,
        reading_temp,
        status_mpump,
        status_ecup,
        status_phup,
        status_phdown,
        reading_wlevel,
        status_wlevel
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION reporting.generate_report(
    report_type VARCHAR(50),
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ
) RETURNS VOID AS $$
DECLARE
report_id INT;
BEGIN
    INSERT INTO reporting.report(
        type
        ) VALUES (
        report_type
    ) RETURNING id INTO report_id;

    INSERT INTO reporting.report_data(
        report_id,
        data
    ) SELECT
    report_id,
    json_build_object(
        'raspberry_pi_id', raspberry_pi_id,
        'plant_id', plant_id,
        'status_ph', status_ph,
        'reading_ph', reading_ph,
        'status_ec', status_ec,
        'reading_ec', reading_ec,
        'status_temp', status_temp,
        'reading_temp', reading_temp,
        'status_mpump', status_mpump,
        'status_ecup', status_ecup,
        'status_phup', status_phup,
        'status_phdown', status_phdown,
        'reading_wlevel', reading_wlevel,
        'status_wlevel', status_wlevel
    ) FROM reporting.reading
    WHERE created_at >= start_date AND created_at <= end_date;

END;
$$ LANGUAGE plpgsql;
