import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dags.stock_api_script import create_table_if_not_exists, fetch_and_store_stock_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'stock_data_pipeline',
    default_args=default_args,
    description='A simple data pipeline to fetch and store stock data.',
    schedule_interval=timedelta(hours=1),
    start_date=days_ago(1),
    tags=['stock', 'api', 'data-pipeline'],
    catchup=False,
) as dag:
    create_table_task = PythonOperator(
        task_id='create_stock_table',
        python_callable=create_table_if_not_exists,
        dag=dag,
    )
    fetch_data_task = PythonOperator(
        task_id='fetch_and_store_data',
        python_callable=fetch_and_store_stock_data,
        dag=dag,
    )

    create_table_task >> fetch_data_task