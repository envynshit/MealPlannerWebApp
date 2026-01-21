import os
from sqlalchemy import create_engine, text
import pandas as pd

DB_HOST = "localhost"
DB_PORT = 5000
DB_NAME = "meal_planner"
DB_USER = "postgres"
DB_PASSWORD = "database1"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

def get_connection():
    conn = engine.connect()
    conn.execution_options(isolation_level="AUTOCOMMIT")
    return conn
