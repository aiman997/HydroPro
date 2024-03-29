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
-- SET timezone = 'Asia/Singapore Singapore';
-- AT TIME ZONE '-03:30',
CREATE SCHEMA IF NOT EXISTS project;
CREATE SCHEMA IF NOT EXISTS hydro;

CREATE TABLE project.visitors(
    site_id integer,
    site_name text,
    visitor_count integer
);

CREATE TABLE hydro.usrs(
	id serial PRIMARY KEY,
	fullname VARCHAR ( 100 ) NOT NULL,
	username VARCHAR ( 50 ) NOT NULL,
	password VARCHAR ( 255 ) NOT NULL,
	email VARCHAR ( 50 ) NOT NULL
);



CREATE TABLE hydro.stage(
	ID BIGSERIAL PRIMARY KEY,
	PLANTID INT REFERENCES hydro.plant (ID),
	PERIOD INT NOT NULL,
	INTRVL_WATER INT NOT NULL,
	RANGE_EC  INT NOT NULL,
	RANGE_PH INT NOT NULL,
);

CREATE TABLE hydro.role(
	id INT PRIMARY KEY,
	name TEXT UNIQUE,
	description TEXT
);
CREATE TABLE hydro.hydrotable(
        ID BIGSERIAL PRIMARY KEY,
        TIMEZ TIMESTAMPTZ,
        STATUS_PH TEXT NOT NULL,
        READING_PH FLOAT NOT NULL,
        STATUS_EC TEXT NOT NULL,
        READING_EC FLOAT NOT NULL,
        STATUS_TEMP TEXT NOT NULL,
        READING_TEMP FLOAT NOT NULL,
        STATUS_MPUMP TEXT NOT NULL,
        STATUS_ECUP TEXT  NOT NULL,
        STATUS_PHUP TEXT NOT NULL,
        STATUS_PHDOWN TEXT NOT NULL,
        READING_WLEVEL FLOAT NOT NULL,
        STATUS_WLEVEL TEXT NOT NULL,
	STAGEID INT REFERENCES hydro.stage (ID),
	PLANTID INT REFERENCES hydro.plant (ID)
);

CREATE TABLE hydro.users(
	id TEXT PRIMARY KEY,
	PLANTID INT REFERENCE hydro.plant (ID),
	USERNAME TEXT NOT NULL,
	PASSWORD TEXT NOT NULL,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT UNIQUE NOT NULL,
	active BOOLEAN,
	confirmed_at TIMESTAMPTZ,
	roles VARCHAR,
	FOREIGN KEY roles REFERENCES hydro.role (id) ON DELETE CASCADE
);

CREATE TABLE hydro.plant(
	ID BIGSERIAL PRIMARY KEY,
	USERID INT REFERENCES hydro.users (ID),
	PLANT_NAME TEXT NOT NULL,
	INTRVL_WATER INT NOT NULL,
	STAGEID INT REFERENCES hydro.stage (ID),
);


}
ALTER TABLE project.visitors OWNER TO postgres;
ALTER TABLE hydro.hydrotable OWNER TO postgres;
ALTER TABLE hydro.plant OWNER TO postgres;
ALTER TABLE hydro.users OWNER TO postgres;
ALTER TABLE hydro.stage OWNER TO postgres;
ALTER TABLE hydro.usrs OWNER TO postrgres;
-- ALTER TABLE hydro.hydrotable ALTER COLUMN value NUMERIC(22,6)
