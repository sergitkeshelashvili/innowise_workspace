from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime

default_args = {
    'owner': 'sergi',
    'start_date': datetime(2026, 1, 1),
}

with DAG(
        'snowflake_airline_pipeline',
        default_args=default_args,
        schedule_interval='@daily',
        catchup=False
) as dag:

   
    load_to_bronze = SnowflakeOperator(
        task_id='load_stage_to_bronze',
        snowflake_conn_id='snowflake_conn',
        sql="""
            COPY INTO AIRLINE_DWH.BRONZE.FLIGHTS_RAW
            FROM @AIRLINE_DWH.BRONZE.AIRLINE_STAGE
            FILE_FORMAT = (
                TYPE = 'CSV' 
                FIELD_OPTIONALLY_ENCLOSED_BY = '"' 
                SKIP_HEADER = 1
                ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            )
            ON_ERROR = 'CONTINUE';
        """
    )

    transform_to_silver = SnowflakeOperator(
        task_id='transform_bronze_to_silver',
        snowflake_conn_id='snowflake_conn',
        sql="CALL AIRLINE_DWH.SILVER.PROCESS_RAW_TO_SILVER();"
    )

    load_to_gold = SnowflakeOperator(
        task_id='load_to_gold',
        snowflake_conn_id='snowflake_conn',
        sql="""
            INSERT INTO AIRLINE_DWH.GOLD.FACT_FLIGHTS (FLIGHT_ID, ORIGIN_AIRPORT, STATUS)
            SELECT FLIGHT_ID, ORIGIN_AIRPORT, STATUS 
            FROM AIRLINE_DWH.SILVER.FLIGHTS_TRANSFORMED;
        """
    )

    load_to_bronze >> transform_to_silver >> load_to_gold
