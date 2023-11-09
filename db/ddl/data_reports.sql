-- public.data_reports definition

-- Drop table

-- DROP TABLE public.data_reports;

CREATE TABLE public.data_reports (
	id varchar NOT NULL,
	guild varchar NOT NULL,
	title varchar NOT NULL,
	"date" timestamp NOT NULL,
	realm varchar NOT NULL,
	region varchar NOT NULL,
	faction varchar NOT NULL,
	CONSTRAINT reports_pk PRIMARY KEY (id)
);
