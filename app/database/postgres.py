from config.db_config import get_db_connection
from common_utils.loggers import logger
from database.base_db import BaseDB
from typing import List, Tuple, Any

class PostgresDB(BaseDB):
    """Handles PostgreSQL metadata fetching."""
    
    def fetch_metadata(self, schema_name: str, table_name: str) -> List[Tuple[Any, ...]]:
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:  # Using `with` ensures the cursor closes properly
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

                cursor.execute(query, (schema_name, table_name))
                rows = cursor.fetchall()

            return rows  # Ensures results are returned even if conn closes in `finally`

        except Exception as err:
            logger.error(f"Error fetching metadata for {table_name}: {err}", exc_info=True)
            return []

        finally:
            if conn:
                conn.close()  # Ensures connection is always closed, even if an error occurs
