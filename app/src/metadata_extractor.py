from database.db_factory import get_db_instance
from common_utils.loggers import logger

def extract_table_metadata(schema_name, table_name):
    """
    Fetches metadata dynamically using the appropriate DB class.

    Args:
        schema_name (str): The schema name.
        table_name (str): The table name.

    Returns:
        list: Table metadata.
    """
    db_instance = get_db_instance()
    logger.info(f"Extracting metadata for {table_name} using {db_instance.__class__.__name__}")
    return db_instance.fetch_metadata(schema_name, table_name)
