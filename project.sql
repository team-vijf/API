-- Start the postgres uuid extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS buildings(
	id uuid DEFAULT uuid_generate_v4(),
	name varchar(20) NOT NULL,
	streetName varchar(30) NOT NULL,
	buildingNumber SMALLINT NOT NULL,
	CONSTRAINT buildings_pk PRIMARY KEY (id)
);

ALTER TABLE buildings OWNER TO postgres;


CREATE TABLE IF NOT EXISTS floors(
	id uuid DEFAULT uuid_generate_v4(),
	floorNumber varchar(255) NOT NULL,
	id_buildings uuid NOT NULL,
	CONSTRAINT floors_pk PRIMARY KEY (id)

);
-- ddl-end --
ALTER TABLE floors OWNER TO postgres;
-- ddl-end --

-- object: classrooms | type: TABLE --
-- DROP TABLE IF EXISTS classrooms CASCADE;
CREATE TABLE IF NOT EXISTS classrooms(
	classcode varchar(25) NOT NULL,
	id_floors uuid NOT NULL,
	CONSTRAINT classrooms_pk PRIMARY KEY (classcode)
);
-- ddl-end --
ALTER TABLE classrooms OWNER TO postgres;
-- ddl-end --

CREATE TABLE IF NOT EXISTS floorplans(
	floorplan xml NOT NULL,
	id_floors uuid NOT NULL,
	CONSTRAINT floorplan_pk PRIMARY KEY (id_floors)
);

-- ddl-end --
ALTER TABLE floorplans OWNER TO postgres;
-- ddl-end --


CREATE TABLE IF NOT EXISTS occupation(
	classcode varchar(25) NOT NULL,
	time TIMESTAMP NOT NULL,
	free boolean NOT NULL
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