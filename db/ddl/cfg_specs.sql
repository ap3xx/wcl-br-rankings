-- public.cfg_specs definition

-- Drop table

-- DROP TABLE public.cfg_specs;

CREATE TABLE public.cfg_specs (
	"class" varchar NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT specs_pk PRIMARY KEY (name, class)
);
