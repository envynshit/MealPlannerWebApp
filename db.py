
import sqlite3
import os

def get_connection():
    db_path = os.path.join("data", "meal_planner.db")
    os.makedirs("data", exist_ok=True)  # Create folder if it doesn't exist
    conn = sqlite3.connect(db_path)
    return conn

