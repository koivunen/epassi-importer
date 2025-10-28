--TODO


CREATE TABLE site_diner_counts (
	id serial NOT NULL,
	siteid int2 NOT NULL DEFAULT -1, 
	"date" date NOT NULL,
	count int2 NOT NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT site_diner_counts_pkey PRIMARY KEY (id),
	CONSTRAINT unique_site_date UNIQUE (siteid, date)
);


COMMENT ON COLUMN public.site_diner_counts.siteid IS '1=asd 2=qwe';


CREATE TABLE site_diners_5m_buckets (
    bucket_time TIMESTAMP PRIMARY KEY,
    entry_count INT,
	siteid int2 NOT NULL DEFAULT -1
);

CREATE INDEX idx_site_diners_5m_buckets_bucket_time ON site_diners_5m_buckets (bucket_time);


CREATE USER site_diners_5m_buckets WITH PASSWORD 'password';

GRANT CONNECT ON DATABASE diningflow TO site_diners_5m_buckets;
grant ipaccess to site_diners_5m_buckets;

GRANT USAGE ON SCHEMA public TO site_diners_5m_buckets;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.site_diners_5m_buckets TO site_diners_5m_buckets;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.site_diner_counts TO site_diners_5m_buckets;
