#connection_pool.py

from dbutils.pooled_db import PooledDB
import sqlite3


def create_connection_pool():
    return PooledDB(
        creator=sqlite3,
        database='ntsoekhe.db',
        maxconnections=10,
        blocking=True,
    )
