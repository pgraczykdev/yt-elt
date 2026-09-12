from datawarehouse.data_utils import get_conn_cursor, close_conn_cursor, create_table, create_schema, get_video_ids
from datawarehouse.data_loading import load_data
from datawarehouse.data_transformation import transform_data
from datawarehouse.data_modification import insert_rows, update_rows, delete_rows

import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)
table_name = "video_tbl"


@task
def staging_table():
    schema_name = "staging"
    conn, cursor = None, None   
    try:
        conn, cursor = get_conn_cursor()
        raw_data = load_data()

        create_schema(schema_name)
        create_table(schema_name)

        table_video_ids = get_video_ids(cursor, schema_name)

        logger.info(f"Processing {len(raw_data)} rows of data")
        for row in raw_data:
            if len(table_video_ids) == 0:
                insert_rows(cursor, conn, schema_name, row)
            else:
                video_id = row['video_id']
                if video_id in table_video_ids:
                    update_rows(cursor, conn, schema_name, row)
                else:
                    insert_rows(cursor, conn, schema_name, row)

        ids_in_json = {row['video_id'] for row in raw_data}

        ids_to_delete = set(table_video_ids) - ids_in_json

        if ids_to_delete:
           delete_rows(cursor, conn, schema_name, ids_to_delete)

        logger.info(f"Finished processing data")
    except Exception as e:
        logger.error(f"Error in staging_table task: {e}")
        raise
    finally:
        if conn and cursor:
            close_conn_cursor(conn, cursor)

@task
def core_table():
    core_schema_name = "core"
    staging_schema_name = "staging"
    conn, cursor = None, None
    try:
        conn, cursor = get_conn_cursor()

        create_schema(core_schema_name)
        create_table(core_schema_name)

        table_ids = get_video_ids(cursor, core_schema_name)
        current_video_ids = set()

        cursor.execute(f"""
                        SELECT 
                            video_id, 
                            video_title, 
                            video_upload_date, 
                            video_duration, 
                            video_views, 
                            video_likes_count, 
                            comments_count 
                        FROM {staging_schema_name}.{table_name}""")
        
        rows = cursor.fetchall()

        logger.info(f"Fetched {len(rows)} rows from {staging_schema_name}.{table_name}")
        for row in rows:
            logger.info(f"Current row data: {row}")
            current_video_ids.add(row['video_id'])

            if len(table_ids) == 0:
                logger.info(f"No existing rows in core table. Transforming row with video_id: {row['video_id']}")
                transformed_row = transform_data(row)
                insert_rows(cursor, conn, core_schema_name, transformed_row)

            else:
                logger.info(f"Existing rows found in core table. Transforming row with video_id: {row['video_id']}")
                transformed_row = transform_data(row)
                if transformed_row['video_id'] in table_ids:
                    update_rows(cursor, conn, core_schema_name, transformed_row)
                else:
                    insert_rows(cursor, conn, core_schema_name, transformed_row)

        ids_to_delete = set(table_ids) - current_video_ids

        if ids_to_delete:
            delete_rows(cursor, conn, core_schema_name, list(ids_to_delete))

        logger.info(f"Finished processing core table data")

    except Exception as e:
        logger.error(f"Error in core_table task: {e}")
        raise
    finally:
        if conn and cursor:
            close_conn_cursor(conn, cursor)
