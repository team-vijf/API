-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.1
-- PostgreSQL version: 10.0
-- Project Site: pgmodeler.io
-- Model Author: ---


-- Database creation must be done outside a multicommand file.
-- These commands were put in this file only as a convenience.
-- -- object: new_database | type: DATABASE --
-- -- DROP DATABASE IF EXISTS new_database;
-- CREATE DATABASE new_database;
-- -- ddl-end --
-- 

-- object: buildings | type: TABLE --
-- DROP TABLE IF EXISTS buildings CASCADE;
CREATE TABLE IF NOT EXISTS buildings(
	id varchar(255) NOT NULL UNIQUE,
	name varchar(255) NOT NULL,
	streetName varchar(255) NOT NULL,
	buildingNumber varchar(255) NOT NULL,
	CONSTRAINT buildings_pk PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE buildings OWNER TO postgres;
-- ddl-end --

-- object: floors | type: TABLE --
-- DROP TABLE IF EXISTS floors CASCADE;
CREATE TABLE IF NOT EXISTS floors(
	id varchar(255) NOT NULL UNIQUE,
	floorNumber varchar(255) NOT NULL,
	id_buildings varchar(255) NOT NULL,
	CONSTRAINT floors_pk PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE floors OWNER TO postgres;
-- ddl-end --

-- object: classrooms | type: TABLE --
-- DROP TABLE IF EXISTS classrooms CASCADE;
CREATE TABLE IF NOT EXISTS classrooms(
	classcode varchar(255) NOT NULL,
	id_floors varchar(255) NOT NULL,
	CONSTRAINT classrooms_pk PRIMARY KEY (classcode)
);
-- ddl-end --
ALTER TABLE classrooms OWNER TO postgres;
-- ddl-end --

CREATE TABLE IF NOT EXISTS occupation(
	time TIMESTAMP NOT NULL,
	classcode varchar(255) NOT NULL,
	free varchar(255) NOT NULL
);

ALTER TABLE occupation OWNER TO postgres;

-- object: buildings_fk | type: CONSTRAINT --
-- ALTER TABLE floors DROP CONSTRAINT IF EXISTS buildings_fk CASCADE;
ALTER TABLE floors ADD CONSTRAINT buildings_fk FOREIGN KEY (id_buildings)
REFERENCES buildings(id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: floors_fk | type: CONSTRAINT --
-- ALTER TABLE classrooms DROP CONSTRAINT IF EXISTS floors_fk CASCADE;
ALTER TABLE classrooms ADD CONSTRAINT floors_fk FOREIGN KEY (id_floors)
REFERENCES floors(id) MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

COMMIT;

SELECT create_hypertable('occupation'::regclass, 'time'::name);