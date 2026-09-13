def test_api_key(api_key):
    assert api_key == "MOCK_KEY1234"

def test_channel_handle(channel_handle):
    assert channel_handle == "MOCK_CHANNEL"

def test_postgres_connection(mock_postgres_connection):
    conn = mock_postgres_connection
    assert conn.login == "mock_user"
    assert conn.password == "mock_password"
    assert conn.host == "mock_host"
    assert conn.port == 5432
    assert conn.schema == "mock_db"

def test_dags_integrity(dag_bag):
    #1
    assert dag_bag.import_errors == {}, f"Import errors found: {dag_bag.import_errors}"

    #2
    expected_dags = ["produce_json", "update_db", "data_quality"]  # Replace with your actual expected DAG IDs
    loaded_dags = list(dag_bag.dags.keys())
    for dag_id in expected_dags:
        assert dag_id in loaded_dags, f"DAG '{dag_id}' is missing from the loaded DAGs"

    #3
    assert dag_bag.size() == 3, f"Expected 3 DAGs, but found {dag_bag.size()}"

    #4
    expected_task_counts = {
        "produce_json": 5, 
        "update_db": 3,
        "data_quality": 2
    }
    for dag_id, dag in dag_bag.dags.items():
        expected_count = expected_task_counts.get(dag_id)
        count = len(dag.tasks)
        assert count == expected_count, f"Expected {expected_count} tasks in DAG '{dag_id}', but found {count}"

