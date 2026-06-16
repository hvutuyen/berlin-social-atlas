"""
ingestion/fetch_berlin_mss.py

Lädt Berliner MSS-Sozialdaten (Monitoring Soziale Stadtentwicklung)
vom Berlin Open Data WFS-Endpoint und schreibt sie in PostgreSQL raw schema.
Unterstützt historische Jahrgänge: 2021, 2023, 2025
"""

import requests
import json
import logging
from typing import Optional
import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
}

AVAILABLE_YEARS = [2021, 2023, 2025]
FEATURE_COUNT = 542


def wfs_url(year: int) -> str:
    return f"https://gdi.berlin.de/services/wfs/mss_{year}"


def wfs_typename(year: int) -> str:
    return f"mss_{year}:mss{year}_indexind_{FEATURE_COUNT}"


def normalize_props(props: dict) -> dict:
    """Normalisiert Feldnamen über Jahrgänge hinweg.
    2021 hat d2_x/s2_x statt d2/s2."""
    return {
        k.replace("_x", ""): v
        for k, v in props.items()
    }


def fetch_wfs(year: int) -> Optional[dict]:
    url = wfs_url(year)
    params = {
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAMES": wfs_typename(year),
        "OUTPUTFORMAT": "application/json",
        "SRSNAME": "EPSG:4326",
    }
    log.info(f"Fetching WFS {year}: {url}")
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        log.error(f"WFS fetch failed ({year}): {e}")
        raise


def parse_features(geojson: dict, year: int) -> list[dict]:
    features = geojson.get("features", [])
    log.info(f"Parsing {len(features)} features for {year}")
    records = []

    for feat in features:
        props = normalize_props(feat.get("properties", {}))
        geom = feat.get("geometry")

        records.append({
            "bezirk":             props.get("bez_id"),
            "lor_name":           props.get("plr_name"),
            "lor_key":            props.get("plr_id"),
            "year":               year,
            "unemployment_rate":  _safe_float(props.get("s1")),
            "child_poverty_rate": _safe_float(props.get("s2")),
            "transfer_rate":      _safe_float(props.get("s3")),
            "youth_unemployment": _safe_float(props.get("s4")),
            "geometry":           json.dumps(geom) if geom else None,
            "source_url":         wfs_url(year),
        })

    return records


def _safe_float(val) -> Optional[float]:
    try:
        f = float(val) if val is not None else None
        return None if f is not None and f < -999 else f
    except (TypeError, ValueError):
        return None


def load_to_postgres(records: list[dict], year: int) -> None:
    if not records:
        log.warning(f"No records to load for {year}.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM raw.berlin_mss WHERE year = %s", (year,))
            log.info(f"Cleared existing year={year} records")

            for r in records:
                cur.execute(
                    """
                    INSERT INTO raw.berlin_mss
                        (bezirk, lor_name, lor_key, year,
                         unemployment_rate, child_poverty_rate,
                         transfer_rate, youth_unemployment,
                         geometry, source_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                            ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326),
                            %s)
                    """,
                    (
                        r["bezirk"], r["lor_name"], r["lor_key"], r["year"],
                        r["unemployment_rate"], r["child_poverty_rate"],
                        r["transfer_rate"], r["youth_unemployment"],
                        r["geometry"], r["source_url"],
                    ),
                )

        conn.commit()
        log.info(f"Loaded {len(records)} records into raw.berlin_mss")
    finally:
        conn.close()


def run(years: list[int] = None) -> None:
    years = years or AVAILABLE_YEARS
    for year in years:
        log.info(f"--- Processing year {year} ---")
        geojson = fetch_wfs(year)
        records = parse_features(geojson, year)
        load_to_postgres(records, year)
    log.info("Ingestion complete.")


if __name__ == "__main__":
    run()