-- models/staging/stg_berlin_mss.sql
-- Bereinigt und typisiert die raw-Daten

with source as (
    select * from raw.berlin_mss
),

cleaned as (
    select
        lor_key,
        lor_name,
        bezirk                  as district,
        year,

        unemployment_rate,      -- bereits in %, kein / 100 nötig
        child_poverty_rate,
        transfer_rate,
        youth_unemployment      as youth_unemployment_rate,

        geometry,
        ingested_at,
        source_url

    from source
    where lor_key is not null
      and unemployment_rate is not null
      and unemployment_rate >= 0   -- filtert Sentinel-Werte raus
)

select * from cleaned
