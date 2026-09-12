from airflow.providers.postgres.hooks.postgres import PostgresHook
from pycopg2.extras import RealDictCursor

table_name = "video_tbl"

def get_conn_cursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="elt_db")
    conn = hook.get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cursor

def close_conn_cursor(conn, cursor):
    cursor.close()
    conn.close()
    

def create_schema(schema_name):
    conn, cursor = get_conn_cursor()
    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    cursor.execute(schema_sql)
    conn.commit()
    close_conn_cursor(conn, cursor)

def create_table(schema_name):
    conn, cursor = get_conn_cursor()
    if schema_name == "staging":
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
            video_id VARCHAR(11) PRIMARY KEY,
            video_title TEXT NOT NULL,
            video_upload_date TIMESTAMP NOT NULL,
            video_duration VARCHAR(20) NOT NULL,
            video_views INT,
            video_likes_count INT,
            comments_count INT
        );
        """
    else:
        table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
            video_id VARCHAR(11) PRIMARY KEY,
            video_title TEXT NOT NULL,
            video_upload_date TIMESTAMP NOT NULL,
            video_duration TIME NOT NULL,
            video_type VARCHAR(100) NOT NULL,
            video_views INT,
            video_likes_count INT,
            comments_count INT
        );
        """
    cursor.execute(table_sql)

    conn.commit()

    close_conn_cursor(conn, cursor)

def get_video_ids(schema_name):
    conn, cursor = get_conn_cursor()
    query = f"SELECT video_id FROM {schema_name}.{table_name};"
    cursor.execute(query)
    ids = cursor.fetchall()
    video_ids = [row['video_id'] for row in ids]
    close_conn_cursor(conn, cursor)
    return video_ids