import os
from dotenv import load_dotenv
import psycopg2
import mysql.connector
from common_utils.loggers import logger
from config.config import Config
load_dotenv()

def get_db_connection():
    """Returns a database connection based on the DBMS type (PostgreSQL or MySQL)."""
    try:
        if Config.DBMS == "mysql":
            connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
        )

            if connection.is_connected():
                print("Connected to MySQL")
                return connection

        elif Config.DBMS == "postgres" or Config.DBMS == "postgresql":
            connection = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            logger.info("Connected to PostgreSQL")
            return connection

        else:
            raise ValueError("Unsupported DBMS. Set DBMS to 'mysql' or 'postgres'.")

    except (psycopg2.Error, mysql.connector.Error) as err:
        logger.error(f"Database connection error: {err}")
        return None
