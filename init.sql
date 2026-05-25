-- Raw schema für ingestion layer
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Raw MSS table (Monitoring Soziale Stadtentwicklung)
CREATE TABLE IF NOT EXISTS raw.berlin_mss (
    id                  SERIAL PRIMARY KEY,
    bezirk              TEXT,
    lor_name            TEXT,
    lor_key             TEXT,
    year                INTEGER,
    unemployment_rate   NUMERIC,
    child_poverty_rate  NUMERIC,
    transfer_rate       NUMERIC,
    youth_unemployment  NUMERIC,
    geometry            GEOMETRY(MULTIPOLYGON, 4326),
    ingested_at         TIMESTAMP DEFAULT NOW(),
    source_url          TEXT
);

-- Index auf geometry für räumliche Queries
CREATE INDEX IF NOT EXISTS idx_berlin_mss_geom
    ON raw.berlin_mss USING GIST(geometry);
