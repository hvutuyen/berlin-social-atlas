"""
ingestion/fetch_berlin_mss.py

Lädt Berliner MSS-Sozialdaten (Monitoring Soziale Stadtentwicklung)
vom Berlin Open Data WFS-Endpoint und schreibt sie in PostgreSQL raw schema.
"""

import requests
import json
import logging
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import execute_values

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# WFS Endpoint – MSS 2025 (Berlin Open Data)
WFS_BASE = "https://gdi.berlin.de/services/wfs/mss_2025"
WFS_PARAMS = {
    "SERVICE": "WFS",
    "VERSION": "2.0.0",
    "REQUEST": "GetFeature",
    "TYPENAMES": "mss_2025:mss2025_indexind_542",
    "OUTPUTFORMAT": "application/json",
    "SRSNAME": "EPSG:4326",
}

DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "airflow",
    "user": "airflow",
    "password": "airflow",
}

# Feldmapping WFS → DB (anpassen nach echtem GetCapabilities-Response)
FIELD_MAP = {
    "bezirk":             "bez_id",
    "lor_name":           "plr_name",
    "lor_key":            "plr_id",
    "unemployment_rate":  "s1",    # Arbeitslosigkeit
    "child_poverty_rate": "s2",    # Kinderarmut  
    "transfer_rate":      "s3",    # Transferbezug
    "youth_unemployment": "s4",    # Kinder in Alleinerziehenden-HH
}

YEAR = 2025


def fetch_wfs(url: str, params: dict) -> Optional[dict]:
    """WFS GetFeature Request → GeoJSON dict."""
    log.info(f"Fetching WFS: {url}")
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        log.error(f"WFS fetch failed: {e}")
        raise


def parse_features(geojson: dict) -> list[dict]:
    """Extrahiert relevante Felder aus GeoJSON FeatureCollection."""
    records = []
    features = geojson.get("features", [])
    log.info(f"Parsing {len(features)} features")

    for feat in features:
        props = feat.get("properties", {})
        geom = feat.get("geometry")

        record = {
            "bezirk":            props.get(FIELD_MAP["bezirk"]),
            "lor_name":          props.get(FIELD_MAP["lor_name"]),
            "lor_key":           props.get(FIELD_MAP["lor_key"]),
            "year":              YEAR,
            "unemployment_rate": _safe_float(props.get(FIELD_MAP["unemployment_rate"])),
            "child_poverty_rate": _safe_float(props.get(FIELD_MAP["child_poverty_rate"])),
            "transfer_rate":     _safe_float(props.get(FIELD_MAP["transfer_rate"])),
            "youth_unemployment": _safe_float(props.get(FIELD_MAP["youth_unemployment"])),
            "geometry":          json.dumps(geom) if geom else None,
            "source_url":        WFS_BASE,
        }
        records.append(record)

    return records


def _safe_float(val) -> Optional[float]:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def load_to_postgres(records: list[dict]) -> None:
    """Schreibt Records in raw.berlin_mss (upsert auf lor_key + year)."""
    if not records:
        log.warning("No records to load.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Löscht bestehende Daten für dieses Jahr (idempotent)
            cur.execute(
                "DELETE FROM raw.berlin_mss WHERE year = %s", (YEAR,)
            )
            log.info(f"Cleared existing year={YEAR} records")

            rows = [
                (
                    r["bezirk"], r["lor_name"], r["lor_key"], r["year"],
                    r["unemployment_rate"], r["child_poverty_rate"],
                    r["transfer_rate"], r["youth_unemployment"],
                    f"ST_SetSRID(ST_GeomFromGeoJSON('{r['geometry']}'), 4326)"
                    if r["geometry"] else None,
                    r["source_url"],
                )
                for r in records
            ]

            # Geometrie-Insert via ST_GeomFromGeoJSON
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


def run():
    geojson = fetch_wfs(WFS_BASE, WFS_PARAMS)
    records = parse_features(geojson)
    load_to_postgres(records)
    log.info("Ingestion complete.")


if __name__ == "__main__":
    run()
