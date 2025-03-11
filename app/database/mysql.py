import os
from app.config.db_config import get_db_connection
from app.database.base_db import BaseDB
from typing import List, Tuple, Any

class MySQLDB(BaseDB):
    """Handles MySQL metadata fetching."""
    
    def fetch_metadata(self, schema_name: str, table_name: str) -> List[Tuple[Any, ...]]:
        conn = get_db_connection()
        cursor = conn.cursor()

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

        cursor.execute(query, (schema_name, table_name))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()
        return rows
