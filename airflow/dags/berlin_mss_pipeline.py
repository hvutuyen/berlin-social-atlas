"""
airflow/dags/berlin_mss_pipeline.py

DAG: Berlin Social Atlas Pipeline
Schedule: jährlich (MSS wird ~1x pro Jahr veröffentlicht)
Tasks: ingest → dbt_run → dbt_test
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="berlin_social_atlas",
    description="Ingest Berlin MSS Geodaten → Postgres → dbt transform",
    schedule_interval="0 6 1 1 *",  # jährlich, 1. Januar 6 Uhr
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["gis", "berlin", "social", "geodata"],
) as dag:

    def ingest_mss():
        import sys
        sys.path.insert(0, "/opt/airflow/ingestion")
        from fetch_berlin_mss import run
        run()

    task_ingest = PythonOperator(
        task_id="ingest_berlin_mss",
        python_callable=ingest_mss,
    )

    task_dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt deps --profiles-dir . && dbt run --profiles-dir .",
    )
    
    task_dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir .",
    )

    task_ingest >> task_dbt_run >> task_dbt_test
