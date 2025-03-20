import json
import os
import pandas as pd
import re
from app.config.db_config import get_db_connection
from app.config.config import Config
from app.src.generate_data_dictionary import generate_data_dictionary
from app.src.metadata_extractor import extract_table_metadata
from app.common_utils.loggers import logger


def generate_data_dictionary_file(conn, schema_name: str) -> None:
    """Generates an Excel file containing the data dictionary."""
    try:
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(
            output_dir, f"{schema_name}_data_dictionary_({Config.DBMS}).xlsx")

        metadata_by_table = extract_table_metadata(conn, schema_name)

        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            for table, metadata in metadata_by_table.items():
                try:
                    logger.info(f"Processing table: {table}...")

                    result = generate_data_dictionary(table, metadata)

                    if not result:
                        logger.error(
                            f"Skipping {table} due to empty response.")
                        continue

                    if isinstance(result, str):
                        cleaned_result = re.sub(
                            r'```json|```|"Raw Result: ', '', result).strip()
                        structured_data = json.loads(cleaned_result)
                    elif isinstance(result, dict):
                        structured_data = result
                    else:
                        logger.error(
                            f"Unexpected response type: {type(result)}")
                        continue

                    tables_data = structured_data.get('text', {})

                    if not tables_data:
                        logger.warning(
                            f"No valid table metadata found in LLM response for table {table}")
                        continue

                    df = pd.json_normalize(tables_data, "columns", [
                                           "table_name", "table_description"])

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

                    df.drop(columns=["table"], inplace=True, errors='ignore')
                    # Fill empty constraint values
                    df["Valid Values/Constraints"] = df["Valid Values/Constraints"].fillna(
                        "")

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

                    # Truncate sheet name to 31 characters
                    sheet_name = table[:31]

                    # Get worksheet reference and add table metadata
                    df.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)
                    worksheet = writer.sheets[sheet_name]
                    table_description = tables_data.get(
                        'table_description', '')
                    worksheet.write(0, 0, f"Table Name: {table}")
                    worksheet.write(1, 0, f"Description: {table_description}")
                except Exception as table_err:
                    logger.error(
                        f"Error processing table {table}: {table_err}", exc_info=True)
                    continue

        logger.info(f"Data dictionary saved to {output_file}")

    except Exception as err:
        logger.exception(
            f"Critical error in generating data dictionary: {err}")


if __name__ == "__main__":
    try:
        logger.info("Starting data dictionary generation process.")
        conn = get_db_connection()

        if conn is None:
            logger.error("Failed to establish database connection. Exiting.")
        else:
            generate_data_dictionary_file(conn, Config.SCHEMA_NAME)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
