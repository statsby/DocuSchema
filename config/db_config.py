import os
from dotenv import load_dotenv
import psycopg2
import mysql.connector
from common_utils.loggers import logger
from config.config import (DB_HOST,
                               DB_NAME,
                               DB_PASSWORD,
                               DB_PORT,
                               DB_USER,
                               MYSQL_DATABASE,
                               MYSQL_HOST,
                               MYSQL_PASSWORD,
                               MYSQL_USER,
                               DBMS)
load_dotenv()

def get_db_connection():
    """Returns a database connection based on the DBMS type (PostgreSQL or MySQL)."""
    try:
        if DBMS == "mysql":
            connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )

            if connection.is_connected():
                print("Connected to MySQL")
                return connection

        elif DBMS == "postgres" or DBMS == "postgresql":
            connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            logger.info("Connected to PostgreSQL")
            return connection

        else:
            raise ValueError("Unsupported DBMS. Set DBMS to 'mysql' or 'postgres'.")

    except (psycopg2.Error, mysql.connector.Error) as err:
        logger.error(f"Database connection error: {err}")
        return None
