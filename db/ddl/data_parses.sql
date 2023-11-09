-- public.data_parses definition

-- Drop table

-- DROP TABLE public.data_parses;

CREATE TABLE public.data_parses (
	"name" varchar NOT NULL,
	"class" varchar NOT NULL,
	spec varchar NOT NULL,
	realm varchar NOT NULL,
	region varchar NOT NULL,
	guild varchar NOT NULL,
	faction varchar NOT NULL,
	"zone" varchar NOT NULL,
	encounter varchar NOT NULL,
	duration float4 NOT NULL,
	percentile float4 NOT NULL,
	dps float4 NOT NULL,
	ilvl int4 NOT NULL,
	encounter_id int4 NOT NULL,
	character_id int4 NOT NULL,
	"date" timestamp NOT NULL,
	zone_id int4 NOT NULL,
	report_id varchar NOT NULL,
	report_fight_id int4 NOT NULL,
	guild_id int4 NULL,
	CONSTRAINT data_parses_pk PRIMARY KEY (encounter_id, character_id, spec)
);
CREATE INDEX data_parses_class_idx ON public.data_parses USING btree (class);
CREATE INDEX data_parses_encounter_id_idx ON public.data_parses USING btree (encounter_id);
