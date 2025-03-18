from app.database.db_factory import get_db_instance
from app.common_utils.loggers import logger
from collections import defaultdict

def extract_table_metadata(conn, schema_name: str) -> dict:
    """
    Extracts metadata for all tables in a given schema.

    Args:
        conn: Database connection object.
        schema_name (str): The name of the schema to extract metadata from.

    Returns:
        dict: A dictionary where keys are table names and values are lists of metadata rows.
    """
    db_instance = get_db_instance()
    logger.info(f"Extracting metadata for {schema_name} using {db_instance.__class__.__name__}")
    
    rows = db_instance.fetch_metadata(conn, schema_name)

    metadata_by_table = defaultdict(list)
    for row in rows:
        table_name = row[0]
        metadata_by_table[table_name].append(row)

    return metadata_by_table
