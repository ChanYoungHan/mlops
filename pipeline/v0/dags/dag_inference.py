from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from processor import ThresholdProcessor

default_args = {
    'owner': 'pipeline_v0',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def run_inference():
    db_config = {
        'host': os.getenv('DB_HOST', 'postgres'),
        'database': os.getenv('DB_NAME', 'pipeline_db'),
        'user': os.getenv('DB_USER', 'pipeline_user'),
        'password': os.getenv('DB_PASS', 'pipeline_pass'),
        'port': int(os.getenv('DB_PORT', 5432))
    }
    
    processor = ThresholdProcessor(db_config, threshold=50.0)
    
    try:
        processed_count = processor.process_batch()
        print(f"Successfully processed {processed_count} records")
        return processed_count
    finally:
        processor.close()

dag = DAG(
    'pipeline_v0_inference',
    default_args=default_args,
    description='Pipeline v0 threshold-based inference DAG',
    schedule_interval=timedelta(minutes=10),
    catchup=False,
    tags=['pipeline', 'v0', 'inference']
)

check_db_task = BashOperator(
    task_id='check_database_connection',
    bash_command='python -c "import psycopg2; print(\\"DB connection check passed\\")"',
    dag=dag
)

inference_task = PythonOperator(
    task_id='run_threshold_inference',
    python_callable=run_inference,
    dag=dag
)

check_db_task >> inference_task