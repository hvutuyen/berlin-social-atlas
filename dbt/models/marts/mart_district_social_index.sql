-- models/marts/mart_district_social_index.sql
-- Aggregiert LOR-Planungsräume auf Bezirksebene
-- → ein Row pro Bezirk mit Durchschnittswerten + sozialem Index

with stg as (
    select * from {{ ref('stg_berlin_mss') }}
),

district_agg as (
    select
        district,
        year,
        count(*)                                as lor_count,

        round(avg(unemployment_rate)::numeric, 4)       as avg_unemployment_rate,
        round(avg(child_poverty_rate)::numeric, 4)      as avg_child_poverty_rate,
        round(avg(transfer_rate)::numeric, 4)           as avg_transfer_rate,
        round(avg(youth_unemployment_rate)::numeric, 4) as avg_youth_unemployment_rate,

        -- Einfacher sozialer Belastungsindex: Mittelwert aller 4 Indikatoren
        round(
            (
                avg(unemployment_rate) +
                avg(child_poverty_rate) +
                avg(transfer_rate) +
                avg(youth_unemployment_rate)
            ) / 4.0, 4
        )                                               as social_burden_index

    from stg
    group by district, year
),

ranked as (
    select
        *,
        rank() over (
            partition by year
            order by social_burden_index desc
        )                                       as burden_rank  -- 1 = höchste Belastung
    from district_agg
)

select * from ranked
order by year, burden_rank
