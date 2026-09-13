import os
import pytest   
from unittest import mock
from airflow.models import Variable, Connection, DagBag


@pytest.fixture
def api_key():
    with mock.patch.dict("os.environ", AIRFLOW_VAR_API_KEY="MOCK_KEY1234"):
        yield Variable.get("API_KEY")


@pytest.fixture
def channel_handle():
    with mock.patch.dict("os.environ", AIRFLOW_VAR_CHANNEL_HANDLE="MOCK_CHANNEL"):
        yield Variable.get("CHANNEL_HANDLE")


@pytest.fixture
def mock_postgres_connection():
    conn = Connection(
        login="mock_user",
        password="mock_password",
        host="mock_host",
        port=5432,
        schema="mock_db"
    )
    conn_uri = conn.get_uri()
    with mock.patch.dict("os.environ", AIRFLOW_CONN_POSTGRES_DB_YT_ELT=conn_uri):
        yield Connection.get_connection_from_secrets("POSTGRES_DB_YT_ELT")
   

@pytest.fixture
def dag_bag():
    yield DagBag()
