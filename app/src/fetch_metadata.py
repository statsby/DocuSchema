import os
from config.db_config import get_db_connection
from dotenv import load_dotenv
from config.config import SCHEMA_NAME
from common_utils.loggers import logger

# Load environment variables from .env file
load_dotenv()

# Retrieve database management system type from environment variables
DBMS = os.getenv("DBMS", "postgres").lower()
schema_name = SCHEMA_NAME

def fetch_table_metadata(schema_name, table_name):
    """
    Fetches metadata for a given table from the selected database.

    This function dynamically selects the SQL query based on the configured DBMS (PostgreSQL or MySQL).
    It retrieves metadata such as column names, data types, lengths, nullability, default values, 
    primary/foreign key constraints, and descriptions of foreign keys.

    Args:
        schema_name (str): The name of the schema containing the table.
        table_name (str): The name of the table for which metadata is to be fetched.

    Returns:
        list: A list of tuples where each tuple represents metadata for a column.
    
    Notes:
        - If `DBMS` is "postgres", it executes a PostgreSQL-specific query.
        - If `DBMS` is "mysql", it executes a MySQL-specific query.
        - If the `DBMS` is neither "postgres" nor "mysql", it raises a ValueError
        - We can similary add support for other database management systems by adding additional queries.
    """

    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Choose query based on the configured DBMS
    if DBMS == "postgres":
        # PostgreSQL query to fetch column metadata
        query = """
        SELECT 
            c.table_name,  
            c.column_name,  
            c.data_type,  
            COALESCE(c.character_maximum_length, c.numeric_precision) AS length,  
            c.is_nullable,  
            c.column_default,  
            CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN 'Yes' ELSE 'No' END AS primary_key,  
            CASE WHEN tc.constraint_type = 'FOREIGN KEY' THEN 'Yes' ELSE 'No' END AS foreign_key,  
            pg_get_expr(pgc.conbin, pgc.conrelid) AS constraints,  
            CASE 
                WHEN tc.constraint_type = 'FOREIGN KEY' THEN 
                     'Foreign key for ' || pgc.confrelid::regclass::text  
                ELSE 
                     ''
            END AS description
        FROM information_schema.columns c
        LEFT JOIN information_schema.key_column_usage kcu
               ON c.table_schema = kcu.table_schema
              AND c.table_name   = kcu.table_name
              AND c.column_name  = kcu.column_name
        LEFT JOIN information_schema.table_constraints tc
               ON kcu.constraint_name = tc.constraint_name
              AND tc.table_schema     = c.table_schema
        LEFT JOIN pg_constraint pgc
               ON tc.constraint_name  = pgc.conname
              AND pgc.connamespace    = (
                    SELECT oid 
                      FROM pg_namespace 
                     WHERE nspname = c.table_schema
                  )
        WHERE c.table_schema = %s
          AND c.table_name   = %s
        ORDER BY c.ordinal_position;
        """
        db_type = "PostgreSQL"

    elif DBMS == "mysql":
        # MySQL query to fetch column metadata
        query = """
        SELECT 
            c.TABLE_NAME AS table_name,  
            c.COLUMN_NAME AS column_name,  
            c.DATA_TYPE AS data_type,  
            COALESCE(c.CHARACTER_MAXIMUM_LENGTH, c.NUMERIC_PRECISION) AS length,  
            c.IS_NULLABLE AS is_nullable,  
            c.COLUMN_DEFAULT AS column_default,  
            CASE WHEN tc.CONSTRAINT_TYPE = 'PRIMARY KEY' THEN 'Yes' ELSE 'No' END AS primary_key,  
            CASE WHEN tc.CONSTRAINT_TYPE = 'FOREIGN KEY' THEN 'Yes' ELSE 'No' END AS foreign_key,  
            '' AS constraints,  
            CASE 
                WHEN tc.CONSTRAINT_TYPE = 'FOREIGN KEY' THEN 
                     CONCAT('Foreign key for ', kcu.REFERENCED_TABLE_NAME)  
                ELSE 
                     ''
            END AS description
        FROM information_schema.COLUMNS c
        LEFT JOIN information_schema.KEY_COLUMN_USAGE kcu
               ON c.TABLE_SCHEMA = kcu.TABLE_SCHEMA
              AND c.TABLE_NAME   = kcu.TABLE_NAME
              AND c.COLUMN_NAME  = kcu.COLUMN_NAME
        LEFT JOIN information_schema.TABLE_CONSTRAINTS tc
               ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
              AND tc.TABLE_SCHEMA     = c.TABLE_SCHEMA
        WHERE c.TABLE_SCHEMA = %s
          AND c.TABLE_NAME   = %s
        ORDER BY c.ORDINAL_POSITION;
        """
        db_type = "MySQL"

    else:
        raise ValueError(f"Unsupported DBMS: {DBMS}. Please use 'postgres' or 'mysql'.")

    # Log which database query is being used
    logger.info(f"Fetching metadata from {db_type} for table '{table_name}' in schema '{schema_name}'.")

    # Execute the query with schema and table name as parameters
    cursor.execute(query, (schema_name, table_name))

    # Fetch all resulting rows from the query
    rows = cursor.fetchall()

    # Close cursor and database connection to free resources
    cursor.close()
    conn.close()

    return rows
