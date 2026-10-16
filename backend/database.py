import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_connection():
    """Create a secure MySQL connection."""

    options = {
        "host": os.getenv("DB_HOST", "localhost").strip(),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root").strip(),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "resume_analyzer").strip(),
        "connection_timeout": 10,
    }

    # Use the CA certificate when configured on Render.
    ssl_ca = os.getenv("DB_SSL_CA", "").strip()

    if ssl_ca:
        options["ssl_ca"] = ssl_ca
        options["ssl_verify_cert"] = True
        options["ssl_verify_identity"] = True

    return mysql.connector.connect(**options)