-- public.data_characters definition

-- Drop table

-- DROP TABLE public.data_characters;

CREATE TABLE public.data_characters (
	id int4 NOT NULL,
	"name" varchar NOT NULL,
	guild varchar NOT NULL,
	realm varchar NOT NULL,
	region varchar NOT NULL,
	faction varchar NOT NULL,
	is_blacklisted bool NOT NULL,
	"class" varchar NOT NULL,
	CONSTRAINT newtable_pk PRIMARY KEY (id)
);
