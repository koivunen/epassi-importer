--TODO


create table site_diner_counts (
	id serial not null,
	siteid int2 not null default -1, 
	"date" date not null,
	count int2 not null,
	created_at timestamptz default now() not null,
	constraint site_diner_counts_pkey primary key (id),
	constraint unique_site_date unique (siteid,
date)
);

comment on
column public.site_diner_counts.siteid is '1=asd 2=qwe';

create table site_diners_5m_buckets (
    bucket_time timestamptz(0) primary key,
    count int2,
	siteid int2 not null default -1,
    updated_at timestamptz(0) default CURRENT_TIMESTAMP not null
);

create index idx_site_diners_5m_buckets_bucket_time on
	site_diners_5m_buckets (bucket_time);

CREATE OR REPLACE FUNCTION func_update_site_diners_5m_buckets_timestamp() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_site_diners_5m_buckets_timestamp
BEFORE UPDATE ON site_diners_5m_buckets
FOR EACH ROW
EXECUTE FUNCTION func_update_site_diners_5m_buckets_timestamp();


create user site_diners_5m_buckets with password 'password';

grant connect on
database diningflow to site_diners_5m_buckets;

grant ipaccess to site_diners_5m_buckets;

GRANT USAGE ON SCHEMA public TO site_diners_5m_buckets;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.site_diners_5m_buckets TO site_diners_5m_buckets;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.site_diner_counts TO site_diners_5m_buckets;
