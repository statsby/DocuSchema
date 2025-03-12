import json
import os
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from src.metadata_extractor import extract_table_metadata
from config.config import Config
from common_utils.llm_selector import LLMSelector
from common_utils.loggers import logger

import json
import os
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from src.metadata_extractor import extract_table_metadata
from config.config import Config
from common_utils.llm_selector import LLMSelector
from common_utils.loggers import logger

def generate_column_description(metadata, table_name, model_name=None):
    """
    Generates a meaningful column-level description for each column in the table metadata.
    """
    metadata_str = str(metadata)
    domain_name = Config.DOMAIN_NAME

    column_description_prompt = PromptTemplate(
        input_variables=["metadata_str", "domain_name", "table_name"],
        template="""
        You are an expert database documenter. The database domain is {domain_name}.

        Below is metadata for the table "{table_name}":
        {metadata_str}

        First value is table_name, column name, datatype, length, is null, default, 
        primary key, foreign key, constraints, description.

        Update this list and add a meaningful, descriptive description (≤ 255 chars) 
        to each column. Do not modify existing descriptions.

        Return the response as a **valid JSON object** with this structure:
        {{
            "table_name": "{table_name}",
            "table_description": "<short_description>",
            "columns": [
                {{
                    "column_name": "<column_name>",
                    "datatype": "<datatype>",
                    "length": <length>,
                    "is_null": "<YES/NO>",
                    "default": <default_value>,
                    "primary_key": "<YES/NO>",
                    "foreign_key": "<YES/NO>",
                    "constraints": <constraints>,
                    "description": "<detailed column description>"
                }}
            ]
        }}
        """
    )

    try:
        llm_selector = LLMSelector()
        llm = llm_selector.get_llm_model()

        logger.info(f"Using LLM Model: {llm.__class__.__name__}")

        # ✅ Use new LangChain syntax (`RunnableLambda`)
        chain = column_description_prompt | llm | RunnableLambda(lambda x: x.content if hasattr(x, "content") else str(x))

        # ✅ Fix: Ensure correct input keys are passed
        response = chain.invoke({
            "metadata_str": metadata_str,
            "domain_name": domain_name,
            "table_name": table_name
        })

        if hasattr(response, "content"):  # ✅ Extract content safely
            response = response.content

        return response.strip()

    except Exception as e:
        logger.error(f"Error generating column description: {e}")
        raise e


def generate_data_dictionary(table_name, metadata, model_name=None):
    """
    Generates a data dictionary for a given table by fetching metadata and adding descriptions.
    """
    if not metadata:
        logger.warning(f"Warning: No metadata found for table {table_name}")
        return None

    logger.info(f"Generating data dictionary for table: {table_name}")

    llm_output = generate_column_description(metadata, table_name, model_name)

    if not llm_output or not llm_output.strip():
        logger.error(f"LLM output is empty for table: {table_name}")
        return None

    # ✅ Clean LLM output and validate JSON
    cleaned_output = llm_output.strip().strip("```json").strip("```")

    try:
        structured_data = json.loads(cleaned_output)

        # ✅ Fix: If the response is a list, wrap it in a dictionary
        if isinstance(structured_data, list):
            structured_data = {"table_name": table_name, "columns": structured_data}

        return json.dumps(structured_data)  # Return as JSON string

    except json.JSONDecodeError:
        logger.error(f"LLM output is not valid JSON for {table_name}: {cleaned_output}")
        return None
