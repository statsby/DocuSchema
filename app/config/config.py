import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class to load environment variables."""

    SCHEMA_NAME = os.getenv("SCHEMA_NAME")
    API_KEY = os.getenv("API_KEY")
    DBMS = os.getenv("DBMS", "").lower()

    # PostgreSQL Configuration
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

    # LLM Configuration
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

    # Domain Name
    DOMAIN_NAME = os.getenv("DOMAIN_NAME", "Clinical Trials")

    # Data Dictionary Configuration for extra columns
    ADD_EXTRA_COLUMNS = os.getenv(
        "ADD_EXTRA_COLUMNS", "False").lower() == "true"

    # Read dynamic extra columns
    EXTRA_COLUMNS = {}
    extra_col_names = os.getenv("EXTRA_COLUMNS", "").split(",")
    extra_col_values = os.getenv("EXTRA_COLUMN_VALUES", "").split(",")

    # Ensure valid key-value pairs
    if len(extra_col_names) == len(extra_col_values) and extra_col_names[0]:
        EXTRA_COLUMNS = {col.strip(): val.strip()
                         for col, val in zip(extra_col_names, extra_col_values)}
