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

CREATE SCHEMA users;

CREATE TABLE users.user(
	id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	plant_id INT,
	email TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	active BOOLEAN,
	confirmed_at TIMESTAMPTZ,
	roles VARCHAR
);

CREATE TABLE users.role(
	id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	name TEXT UNIQUE,
	description TEXT
);

CREATE OR REPLACE FUNCTION users.insert_user(
	plant_id INT,
	email TEXT,
	password TEXT,
	first_name TEXT,
	last_name TEXT,
	active BOOLEAN,
	confirmed_at TIMESTAMPTZ,
	roles VARCHAR
)
RETURNS BIGINT AS $$
BEGIN
	INSERT INTO users.user(plant_id, email, password, first_name, last_name, active, confirmed_at, roles)
	VALUES (plant_id, email, password, first_name, last_name, active, confirmed_at, roles) RETURNING id;
END;
$$ LANGUAGE plpgsql;

CREATE SCHEMA plants;

CREATE TABLE plants.plant(
	id BIGSERIAL PRIMARY KEY,
	user_id INT,
	name TEXT NOT NULL,
	stage INT
);

CREATE SCHEMA stages;

CREATE TABLE stages.stage(
	id BIGSERIAL PRIMARY KEY,
	plant_id INT,
	period INT NOT NULL,
	intrvl_water INT NOT NULL,
	range_ec  INT NOT NULL,
	range_ph INT NOT NULL
);

CREATE SCHEMA rpi;

CREATE TABLE rpi.reading(
	id BIGSERIAL PRIMARY KEY,
	timez TIMESTAMPTZ,
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
	stage_id INT,
	plant_id INT 
);


ALTER TABLE hydro.reading OWNER TO postgres;
ALTER TABLE hydro.plant OWNER TO postgres;
ALTER TABLE hydro.user OWNER TO postgres;
ALTER TABLE hydro.stage OWNER TO postgres;
ALTER TABLE hydro.role OWNER TO postgres;
