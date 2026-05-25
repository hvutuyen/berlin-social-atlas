# Berlin Social Atlas Pipeline

End-to-end Data Engineering Pipeline für Berliner Sozialdaten (MSS).

## Stack
| Layer | Tool |
|---|---|
| Orchestration | Apache Airflow 2.9 |
| Ingestion | Python + requests |
| Storage (raw) | PostgreSQL + PostGIS |
| Transformation | dbt Core |
| Production | Azure Blob Storage |

## Datenquelle
[Monitoring Soziale Stadtentwicklung (MSS)](https://daten.berlin.de) – Senatsverwaltung Berlin  
Indikatoren: Arbeitslosigkeit, Kinderarmut, Transferbezug, Jugendarbeitslosigkeit auf LOR-Planungsraum-Ebene.

## Pipeline-Flow
```
Berlin Open Data WFS
        │
        ▼
  fetch_berlin_mss.py   ← Python Ingestion
        │
        ▼
  raw.berlin_mss        ← PostgreSQL Raw Layer
        │
        ▼
  stg_berlin_mss        ← dbt Staging (View)
        │
        ▼
  mart_district_social_index  ← dbt Mart (Table)
        │
        ▼
  Azure Blob Storage    ← Production Export (CSV/Parquet)
```

## Setup (lokal)

### 1. Docker starten
```bash
docker-compose up -d
```

Airflow UI: http://localhost:8080 (admin / admin)

### 2. Python dependencies
```bash
pip install -r requirements.txt
```

### 3. dbt setup
```bash
cd dbt
pip install dbt-postgres dbt-utils
dbt deps
dbt debug   # Verbindung testen
```

### 4. Manuelle Ingestion testen
```bash
python ingestion/fetch_berlin_mss.py
```

### 5. dbt ausführen
```bash
cd dbt
dbt run
dbt test
```

## Projektstruktur
```
berlin-social-atlas/
├── airflow/
│   └── dags/
│       └── berlin_mss_pipeline.py   # Airflow DAG
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_berlin_mss.sql
│   │   └── marts/
│   │       └── mart_district_social_index.sql
│   ├── dbt_project.yml
│   └── profiles.yml
├── ingestion/
│   └── fetch_berlin_mss.py
├── docker-compose.yml
├── init.sql
└── requirements.txt
```

## Nächste Schritte
- [ ] Azure Blob Storage Export-Task in Airflow
- [ ] dbt-utils installieren für range-Tests
- [ ] Visualization (optional: Streamlit oder Metabase)
- [ ] CI/CD via GitHub Actions
