FROM apache/airflow:2.7.1


USER airflow

RUN pip install --no-cache-dir \
    snowflake-connector-python==3.10.0 \
    snowflake-sqlalchemy \
    apache-airflow-providers-snowflake
