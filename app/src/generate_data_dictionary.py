import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from src.metadata_extractor import extract_table_metadata
from config.config import SCHEMA_NAME, DOMAIN_NAME
from common_utils.llm_selector import LLMSelector
from common_utils.loggers import logger

load_dotenv()

schema_name = SCHEMA_NAME

def generate_column_description(metadata, model_name=None):
    """
    Generates a meaningful column-level description for each column in the table metadata and also generates a table level description.

    Args:
        metadata (dict): The metadata of the table, including column names, data types, constraints, etc.
        model_name (str, optional): The name of the LLM model to be used for description generation.

    Returns:
        str: A JSON-formatted string containing the updated table metadata with meaningful descriptions.
        None: If an error occurs during processing.
    """
    metadata_str = str(metadata)
    domain_name= DOMAIN_NAME

    column_description_prompt = PromptTemplate(
        input_variables=["metadata_str","domain_name"],
        template="""
        {metadata_str}
        You are an expert database documenter. This metadata belongs to {domain_name}.
        First value is table_name, column name, datatype, length, is null, default, 
        primary key, foreign key, constraints, description.

        Update this list and add a meaningful, descriptive description (<= 255 chars) 
        to each column. Make sure there is a proper description for each column.
        Note, if description already exists, do not update it.
        Note - Do not add anything related to {domain_name} in column or table description.
        Return the output in the following sequence:
        table_name, column name, datatype, length, is null, default, primary key, 
        foreign key, constraints, description.
        Also generate a table-level description.

        Do not alter any other column except Description column.
        **IMPORTANT:** If a column name is "description", do not truncate output. 
        Treat it like any other column.
        For columns that have empty or none values, replace the value with NULL.
        Strictly return the final response in JSON format without extra text.
        """
    )

    try:
        llm_selector = LLMSelector()
        llm = llm_selector.get_llm_model()

        logger.info(f"Using LLM Model: {llm.__class__.__name__}")

        llm_chain = LLMChain(llm=llm, prompt=column_description_prompt)

        response = llm_chain.run({"metadata_str": metadata_str, "domain_name": domain_name})
        return response.strip()

    except Exception as e:
        logger.error(f"Error generating column description: {e}")
        raise e


def generate_data_dictionary(table_name, model_name=None):
    """
    Generates a data dictionary for a given table by fetching metadata and 
    adding meaningful descriptions to each column.

    Args:
        table_name (str): The name of the table for which the data dictionary is to be generated.
        model_name (str, optional): The name of the LLM model to be used for description generation.

    Returns:
        str: A JSON-formatted string containing the table metadata with updated descriptions.
        None: If no metadata is found or an error occurs.
    """
    metadata = extract_table_metadata(schema_name, table_name)

    if not metadata:
        logger.warning(f"Warning: No metadata found for table {table_name}")
        return None

    logger.info(f"Generating data dictionary for table: {table_name}")

    llm_output = generate_column_description(metadata, model_name)

    if llm_output:
        logger.info(f"Successfully generated data dictionary for {table_name}")
    else:
        logger.error(f"Failed to generate data dictionary for {table_name}")

    return llm_output
