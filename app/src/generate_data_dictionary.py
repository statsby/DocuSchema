import os
import json
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.src.metadata_extractor import extract_table_metadata
from app.config.config import Config
from app.common_utils.llm_selector import LLMSelector
from app.common_utils.loggers import logger

# Load environment variables
load_dotenv()

schema_name = Config.SCHEMA_NAME
domain_name = Config.DOMAIN_NAME

# Initialize LLM model
llm_selector = LLMSelector()
llm = llm_selector.get_llm_model()
logger.info(f"Using LLM Model: {llm.__class__.__name__}")

# Prompt template
column_description_prompt = PromptTemplate(
    input_variables=["metadata_json", "domain_name"],
    template="""
    You are an expert database documenter. This metadata belongs to {domain_name}.
    First value is table_name, column name, datatype, length, is null, default,
    primary key, foreign key, constraints, description.

    Update this list and add a **meaningful, descriptive** description (≤ 255 chars)
    to each column. Make sure there is a proper description for each column.

    - **If a description already exists, do not update it.**
    - **Do not add anything related to {domain_name} in column or table descriptions.**
    - **Strictly return JSON format with no extra text, markdown, or formatting artifacts.**
    - Ensure the output maintains this exact sequence:
    `table_name, column name, datatype, length, is_null, default, primary_key, foreign_key, constraints, description.`

    Also, generate a **table-level description**.

    **Important Rules:**
    - Do **not** alter any column except `description`.
    - If a column name is `"description"`, do **not** truncate its value.
    - Replace any empty or `None` values with `"NULL"`.
    - Ensure that each column is listed only once, with no duplicate column entries.

    Strictly return **only** a valid JSON response.
    """
)

# Define the JSON parser
json_parser = JsonOutputParser()

def generate_column_description(metadata):
    """
    Generates meaningful column descriptions based on structured metadata.

    Args:
        metadata (dict): Table metadata containing column names, data types, and constraints.

    Returns:
        dict: JSON object with updated column descriptions.
    """
    try:
        metadata_json = json.dumps(metadata, indent=2)

        # Initialize LLM chain with prompt, model, and JSON parser
        llm_chain = LLMChain(llm=llm, prompt=column_description_prompt, output_parser=json_parser)

        # Use `.invoke()` instead of `.run()` to avoid deprecation warnings
        response = llm_chain.invoke({"metadata_json": metadata_json, "domain_name": domain_name})
        logger.info(f"Raw LLM response from LLM'{response}")


        # JsonOutputParser already returns a dictionary, so no need to call json.loads(response)
        return response  

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from LLM: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating column description: {e}")
        raise e

def generate_data_dictionary(table_name):
    """
    Generates a data dictionary for a given table by fetching metadata and 
    adding meaningful descriptions.

    Args:
        table_name (str): Name of the table to process.

    Returns:
        dict: JSON-formatted metadata with updated descriptions.
    """
    metadata = extract_table_metadata(schema_name, table_name)

    if not metadata:
        logger.warning(f"No metadata found for table: {table_name}")
        return None

    logger.info(f"Generating data dictionary for table: {table_name}")

    llm_output = generate_column_description(metadata)

    if llm_output:
        logger.info(f"Successfully generated data dictionary for {table_name}")
    else:
        logger.error(f"Failed to generate data dictionary for {table_name}")

    return llm_output
