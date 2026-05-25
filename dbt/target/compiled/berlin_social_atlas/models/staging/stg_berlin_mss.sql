-- models/staging/stg_berlin_mss.sql
-- Bereinigt und typisiert die raw-Daten

with source as (
    select * from raw.berlin_mss
),

cleaned as (
    select
        lor_key                                     as lor_key,
        lor_name                                    as lor_name,
        bezirk                                      as district,
        year,

        -- Raten als Dezimal normalisieren (falls > 1 = Prozentwert)
        case
            when unemployment_rate > 1
            then unemployment_rate / 100.0
            else unemployment_rate
        end                                         as unemployment_rate,

        case
            when child_poverty_rate > 1
            then child_poverty_rate / 100.0
            else child_poverty_rate
        end                                         as child_poverty_rate,

        case
            when transfer_rate > 1
            then transfer_rate / 100.0
            else transfer_rate
        end                                         as transfer_rate,

        case
            when youth_unemployment > 1
            then youth_unemployment / 100.0
            else youth_unemployment
        end                                         as youth_unemployment_rate,

        geometry,
        ingested_at,
        source_url

    from source
    where lor_key is not null
)

select * from cleaned