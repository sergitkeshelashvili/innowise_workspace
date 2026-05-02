from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'sergi',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG for Airline ETL Pipeline
with DAG(
    'snowflake_airline_pipeline',
    default_args=default_args,
    description='End-to-End Airline ETL Pipeline using Snowflake and Airflow',
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Task 1: Load raw CSV data from Snowflake Stage to Bronze Layer
    load_bronze = SnowflakeOperator(
        task_id='load_stage_to_bronze',
        snowflake_conn_id='snowflake_conn',
        sql="CALL AIRLINE_DWH.BRONZE.LOAD_FROM_STAGE();"
    )

    # Task 2: Clean and transform data into Silver Layer
    transform_silver = SnowflakeOperator(
        task_id='transform_bronze_to_silver',
        snowflake_conn_id='snowflake_conn',
        sql="CALL AIRLINE_DWH.SILVER.PROCESS_RAW_TO_SILVER();"
    )

    # Task 3: Populate final Gold Layer Fact Table
    load_gold = SnowflakeOperator(
        task_id='load_to_gold',
        snowflake_conn_id='snowflake_conn',
        sql="CALL AIRLINE_DWH.GOLD.LOAD_TO_GOLD_PROC();"
    )

    # Define execution order
    load_bronze >> transform_silver >> load_gold
