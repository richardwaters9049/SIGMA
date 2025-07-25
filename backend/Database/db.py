# File: /SIGMA/backend/Database/db.py

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Retrieve DB settings
DB_HOST = os.getenv("PGHOST")
DB_NAME = os.getenv("PGDATABASE")
DB_USER = os.getenv("PGUSER")
DB_PASS = os.getenv("PGPASSWORD")
DB_PORT = os.getenv("PGPORT")


def get_connection():
    """
    Creates and returns a connection object to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        print("[✅] Database connection successful.")
        return conn
    except Exception as e:
        print(f"[❌] Database connection failed: {e}")
        raise
