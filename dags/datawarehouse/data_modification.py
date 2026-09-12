import logging

logger = logging.getLogger(__name__)

TABLE_NAME = "video_tbl"

TABLE_JSON_STAGING_MAPPING = {
    "video_id": "%(video_id)s",
    "video_title": "%(title)s",
    "video_upload_date": "%(published_at)s",
    "video_duration": "%(duration)s",
    "video_views": "%(view_count)s",
    "video_likes_count": "%(like_count)s",
    "comments_count": "%(comment_count)s",
}

def insert_rows(cur, con, schema_name, row):

    logger.info(f"Inserting rows into table: {TABLE_NAME}")
    try:
        if schema_name == "staging":
        
            insert_query = f"""
            INSERT INTO {schema_name}.{TABLE_NAME} (
                video_id, 
                video_title, 
                video_upload_date, 
                video_duration,
                video_views, 
                video_likes_count, 
                comments_count
            ) VALUES (
                {TABLE_JSON_STAGING_MAPPING['video_id']}, 
                {TABLE_JSON_STAGING_MAPPING['video_title']}, 
                {TABLE_JSON_STAGING_MAPPING['video_upload_date']}, 
                {TABLE_JSON_STAGING_MAPPING['video_duration']},
                {TABLE_JSON_STAGING_MAPPING['video_views']}, 
                {TABLE_JSON_STAGING_MAPPING['video_likes_count']},
                {TABLE_JSON_STAGING_MAPPING['comments_count']}
            );
            """
        else:
            insert_query = f"""
            INSERT INTO {schema_name}.{TABLE_NAME} (
                video_id, 
                video_title, 
                video_upload_date, 
                video_duration, 
                video_type,
                video_views, 
                video_likes_count, 
                comments_count
            ) VALUES (
                %(video_id)s, 
                %(video_title)s, 
                %(video_upload_date)s, 
                %(video_duration)s, 
                %(video_type)s,
                %(video_views)s, 
                %(video_likes_count)s, 
                %(comments_count)s
            );
            """
        cur.execute(insert_query, row)
        con.commit()

        logger.info(f"Successfully inserted row into table: {TABLE_NAME}")

    except Exception as e:
        logger.error(f"Error inserting rows into table: {TABLE_NAME} with video_id: {row.get('video_id')}. Error: {e}")
        con.rollback()
        raise

def update_rows(cur, con, schema_name, row):
    logger.info(f"Updating rows in table: {TABLE_NAME}")
    try:
        if schema_name == "staging":
            update_query = f"""
            UPDATE {schema_name}.{TABLE_NAME}
            SET 
                video_title = COALESCE({TABLE_JSON_STAGING_MAPPING['video_title']}, video_title),
                video_duration = COALESCE({TABLE_JSON_STAGING_MAPPING['video_duration']}, video_duration),
                video_views = COALESCE({TABLE_JSON_STAGING_MAPPING['video_views']}, video_views),
                video_likes_count = COALESCE({TABLE_JSON_STAGING_MAPPING['video_likes_count']}, video_likes_count),
                comments_count = COALESCE({TABLE_JSON_STAGING_MAPPING['comments_count']}, comments_count)
            WHERE video_id = {TABLE_JSON_STAGING_MAPPING['video_id']}
              AND video_upload_date = {TABLE_JSON_STAGING_MAPPING['video_upload_date']};
            """
        else:
            update_query = f"""
            UPDATE {schema_name}.{TABLE_NAME}
            SET 
                video_title = COALESCE(%(video_title)s, video_title),
                video_duration = COALESCE(%(video_duration)s, video_duration),
                video_type = COALESCE(%(video_type)s, video_type),
                video_views = COALESCE(%(video_views)s, video_views),
                video_likes_count = COALESCE(%(video_likes_count)s, video_likes_count),
                comments_count = COALESCE(%(comments_count)s, comments_count)
            WHERE video_id = %(video_id)s 
              AND video_upload_date = %(video_upload_date)s;
            """

        cur.execute(update_query, row)
        con.commit()

        logger.info(f"Successfully updated row in table: {TABLE_NAME} with video_id: {row.get('video_id')}")
    except Exception as e:
        logger.error(f"Error updating rows in table: {TABLE_NAME} with video_id: {row.get('video_id')}. Error: {e}")
        con.rollback()
        raise

def delete_rows(cur, con, schema_name, video_ids:list):

    try: 
    
        ids_to_delete = f"""({', '.join(f"'{video_id}'" for video_id in video_ids)})"""
        logger.info(f"Deleting rows from table: {TABLE_NAME} for video_ids: {video_ids}")

        delete_query = f"""
        DELETE FROM {schema_name}.{TABLE_NAME}
        WHERE video_id IN {ids_to_delete};
        """
        cur.execute(delete_query)
        con.commit()
    except Exception as e:
        logger.error(f"Error deleting rows from table: {TABLE_NAME} for video_ids: {video_ids}. Error: {e}")
        con.rollback()
        raise
