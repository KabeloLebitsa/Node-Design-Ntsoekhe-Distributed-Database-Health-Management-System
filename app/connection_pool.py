#connection_pool.py

from sqlalchemy.pool import QueuePool
import sqlite3
import os
import re

def create_connection_pool(DATABASE_URL):
    try:
        if not re.match(r'^sqlite:///.*\.db$', DATABASE_URL):
            raise ValueError("Invalid DATABASE_URL. It must be a valid SQLite connection string.")
        DATABASE_URL_ = DATABASE_URL.replace("sqlite:///","")
        # Check if database file exists
        if not os.path.exists(DATABASE_URL_):
            # Ensure the directory exists
            os.makedirs(os.path.dirname(DATABASE_URL_), exist_ok=True)
            # Create an empty file to trigger database creation on connection
            open(DATABASE_URL_, 'w').close()
        return QueuePool(
            creator=lambda: sqlite3.connect(DATABASE_URL_),
            pool_size=10,
            max_overflow=0,
        )
    except sqlite3.Error as e:
        print(f"Error connecting to database: {str(e)}")
        raise e