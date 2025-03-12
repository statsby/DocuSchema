from database.db_factory import get_db_instance
from common_utils.loggers import logger
from typing import List, Tuple, Any
from collections import defaultdict

def extract_table_metadata(conn, schema_name: str) -> dict:
    """Fetches metadata dynamically using an existing connection."""
    db_instance = get_db_instance()
    logger.info(f"Extracting metadata for {schema_name} using {db_instance.__class__.__name__}")
    
    rows = db_instance.fetch_metadata(conn, schema_name)

    metadata_by_table = defaultdict(list)
    for row in rows:
        table_name = row[0]  # Assuming table_name is the first column
        metadata_by_table[table_name].append(row)

    return metadata_by_table

