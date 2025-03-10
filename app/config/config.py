import os
from dotenv import load_dotenv

load_dotenv()

SCHEMA_NAME=os.getenv("SCHEMA_NAME")
API_KEY=os.getenv("API_KEY")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

DBMS = os.getenv("DBMS").lower()

LLM_MODEL_NAME=os.getenv("LLM_MODEL_NAME")

DOMAIN_NAME=os.getenv("DOMAIN_NAME")
