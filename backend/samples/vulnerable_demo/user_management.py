"""
DEMO SCENARIO — deliberately vulnerable sample module.

This file exists ONLY to demonstrate the SENTINEL-AI pipeline. It is
never executed by the platform — it is analyzed statically, exactly
like an uploaded project would be.
"""

import sqlite3
import hashlib

DB_PASSWORD = "sup3rSecretDbPass!"
API_KEY = "sk_live_9f8a7b6c5d4e3f2a1b0c"


def get_user_by_name(conn: sqlite3.Connection, username: str):
    cursor = conn.cursor()
    # Vulnerable: SQL query built via f-string interpolation of user input.
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    return cursor.fetchone()


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
