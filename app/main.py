import json
import os
import pandas as pd
from config.db_config import get_db_connection
from config.config import Config
from src.metadata_extractor import extract_table_metadata
from src.generate_data_dictionary import generate_data_dictionary
from common_utils.loggers import logger
from typing import List

def generate_data_dictionary_file(conn, schema_name: str) -> None:
    """Generates an Excel file containing the data dictionary."""
    try:
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{schema_name}_data_dictionary_({Config.DBMS}).xlsx")

        # Pass the connection instead of opening a new one
        metadata_by_table = extract_table_metadata(conn, schema_name)

        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            for table_name, metadata in metadata_by_table.items():
                try:
                    logger.info(f"Processing table: {table_name}...")

                    # Generate dictionary using LLM
                    result = generate_data_dictionary(table_name, metadata)

                    if not result:
                        logger.error(f"Skipping {table_name} due to empty response.")
                        continue

                    structured_data = json.loads(result.strip().strip("```json").strip("```"))
                    df = pd.DataFrame(structured_data.get("columns", []))

                    if df.empty:
                        logger.warning(f"Skipping empty table: {table_name}")
                        continue

                    df.to_excel(writer, sheet_name=table_name[:31], startrow=2, index=False)
                    worksheet = writer.sheets[table_name[:31]]
                    worksheet.write(0, 0, f"Table Name: {table_name}")
                    worksheet.write(1, 0, f"Description: {structured_data.get('table_description', '')}")

                except Exception as table_err:
                    logger.error(f"Error processing table {table_name}: {table_err}", exc_info=True)
                    continue

        logger.info(f"Data dictionary saved to {output_file}")

    except Exception as err:
        logger.exception(f"Critical error in generating data dictionary: {err}")



if __name__ == "__main__":
    try:
        logger.info("Starting data dictionary generation process.")
        conn = get_db_connection()

        if conn is None:
            logger.error("Failed to establish database connection. Exiting.")
        else:
            generate_data_dictionary_file(conn, Config.SCHEMA_NAME)
            conn.close()

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

