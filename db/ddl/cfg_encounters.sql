-- public.cfg_encounters definition

-- Drop table

-- DROP TABLE public.cfg_encounters;

CREATE TABLE public.cfg_encounters (
	zone_id int4 NOT NULL,
	zone_name varchar NOT NULL,
	id int4 NOT NULL,
	"name" varchar NOT NULL,
	difficulty int4 NOT NULL,
	CONSTRAINT encounters_pk PRIMARY KEY (id)
);
