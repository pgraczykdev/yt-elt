import logging
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "pg_datasource"

def yt_elt_data_quality(schema_name: str):
    try:
        bash_command = f"soda scan -d {DATASOURCE} -c {SODA_PATH}/configuration.yml -v SCHEMA={schema_name} {SODA_PATH}/checks.yml"
        return BashOperator(
            task_id=f"soda_test_{schema_name}",
            bash_command=bash_command
        )
    except Exception as e:
        logger.error(f"Error creating data quality task: {e}")
        raise e