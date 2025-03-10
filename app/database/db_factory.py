import os
from database.postgres import PostgresDB
from database.mysql import MySQLDB

def get_db_instance():
    """Returns an instance of the appropriate database class based on the DBMS."""
    dbms = os.getenv("DBMS", "postgres").lower()

    if dbms == "postgres":
        return PostgresDB()
    elif dbms == "mysql":
        return MySQLDB()
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}. Please implement a class for it.")
