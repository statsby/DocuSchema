import json
import os
import pandas as pd
import re
from app.config.db_config import get_db_connection
from app.config.config import Config
from app.src.generate_data_dictionary import generate_data_dictionary
from app.common_utils.loggers import logger
from typing import List


def get_table_names(schema_name: str) -> List[str]:
    """
    Fetches the names of all tables within a given database schema.
    """
    conn = get_db_connection()
    if conn is None:
        logger.error("Database connection failed.")
        return []

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name = %s;
            """, (schema_name,))

            if not cursor.fetchone():
                logger.warning(f"Schema '{schema_name}' does not exist in the database.")
                return []

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_type = 'BASE TABLE';
            """, (schema_name,))

            table_names = [row[0] for row in cursor.fetchall()]
            logger.info(f"Table names fetched: {table_names}")
            return table_names

    except Exception as err:
        logger.exception(f"Error fetching table names: {err}")
        return []

    finally:
        if conn:
            conn.close()


def generate_data_dictionary_file(schema_name: str, table_names: List[str]) -> None:
    """
    Generates an Excel file containing the data dictionary for the specified schema.
    """
    try:
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{schema_name}_data_dictionary_({Config.DBMS}).xlsx")

        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            for table in table_names:
                logger.info(f"Processing table: {table}...")
                result = generate_data_dictionary(table)
                logger.info(f"Raw LLM response for table '{table}': {result}")

                if not result:
                    logger.warning(f"No valid data dictionary found for table: {table}")
                    continue

                if isinstance(result, str):  
                    cleaned_result = re.sub(r'```json|```|"Raw Result: ', '', result).strip()
                    structured_data = json.loads(cleaned_result)
                elif isinstance(result, dict):  
                    structured_data = result
                else:  
                    logger.error(f"Unexpected response type: {type(result)}")  
                    continue  

                tables_data = structured_data.get('text', {}).get('tables', [])
                if not tables_data:
                    logger.warning(f"No valid table metadata found in LLM response for table {table}")
                    continue  

                df = pd.json_normalize(tables_data, "columns", ["table_name", "table_description"])
                logger.info(f"Data Frames for table '{table}': {df}")

                if df.empty:
                    logger.warning(f"Skipping empty table: {table}")
                    continue

                df.rename(columns={
                    "column_name": "Field Name",
                    "datatype": "Data Type",
                    "length": "Length",
                    "is_null": "Allow Null?",
                    "foreign_key": "Foreign Key?",
                    "primary_key": "Primary Key?",
                    "default": "Default",
                    "description": "Description",
                    "constraints": "Valid Values/Constraints"
                }, inplace=True)

                df.drop(columns=["table_name"], inplace=True, errors='ignore')
                df["Valid Values/Constraints"] = df["Valid Values/Constraints"].fillna("")

                # Define expected columns
                expected_columns = [
                    "Field Name", "Data Type", "Length", "Allow Null?", "Foreign Key?",
                    "Primary Key?", "Default", "Description", "Valid Values/Constraints"
                ]

                # Add extra columns dynamically
                if Config.ADD_EXTRA_COLUMNS and Config.EXTRA_COLUMNS:
                    for col_name, col_value in Config.EXTRA_COLUMNS.items():
                        df[col_name] = col_value
                    expected_columns.extend(Config.EXTRA_COLUMNS.keys())

                df = df[expected_columns]

                sheet_name = table[:31]
                df.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)
                worksheet = writer.sheets[sheet_name]
                table_description = tables_data[0].get('table_description', '')
                worksheet.write(0, 0, f"Table Name: {table}")
                worksheet.write(1, 0, f"Description: {table_description}")

        logger.info(f"Data dictionary saved to {output_file}")

    except Exception as err:
        logger.exception(f"Failed to generate data dictionary: {err}")


if __name__ == "__main__":
    try:
        logger.info("Starting data dictionary generation process.")
        schema_name = Config.SCHEMA_NAME
        table_names = get_table_names(schema_name)

        if not table_names:
            logger.warning(f"No tables found in schema '{schema_name}'. Exiting process.")
        else:
            generate_data_dictionary_file(schema_name, table_names)

    except Exception as e:
        logger.exception(f"Unexpected error in script execution: {e}")
