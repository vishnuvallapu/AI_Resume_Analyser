import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_connection():
    """Create a MySQL connection using values from backend/.env."""
    host = os.getenv("DB_HOST", "localhost").strip()
    user = os.getenv("DB_USER", "root").strip()
    database = os.getenv("DB_NAME", "resume_analyzer").strip()

    if not host or not user or not database:
        raise RuntimeError(
            "DB_HOST, DB_USER, and DB_NAME must be set in backend/.env"
        )

    return mysql.connector.connect(
        host=host,
        port=int(os.getenv("DB_PORT", "3306")),
        user=user,
        password=os.getenv("DB_PASSWORD", ""),
        database=database,
        connection_timeout=10,
    )
