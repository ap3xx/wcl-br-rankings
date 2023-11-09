-- public.cfg_guilds definition

-- Drop table

-- DROP TABLE public.cfg_guilds;

CREATE TABLE public.cfg_guilds (
	"name" varchar NOT NULL,
	realm varchar NOT NULL,
	region varchar NOT NULL,
	faction varchar NOT NULL,
	fetch_enabled bool NOT NULL DEFAULT true,
	id int4 NOT NULL,
	CONSTRAINT cfg_guilds_pk PRIMARY KEY (id, name)
);
