"""
Database Connection & Query Manager for Muscle Monster Gym.
Supports MySQL with automatic table initialization and graceful SQLite fallback for seamless local testing.
"""

import os
import sqlite3
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "muscle_monster_db")
USE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "True").lower() == "true"

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "muscle_monster_local.db")
ACTIVE_DB_TYPE = "UNKNOWN"

def get_mysql_connection():
    """Attempt direct connection to MySQL database."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def get_sqlite_connection():
    """Fallback local SQLite connection for instant testing."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    """
    Returns an active database connection and its type ('MYSQL' or 'SQLITE').
    Tries MySQL first. If MySQL is offline and fallback is enabled, uses SQLite.
    """
    global ACTIVE_DB_TYPE
    try:
        conn = get_mysql_connection()
        ACTIVE_DB_TYPE = "MYSQL"
        return conn, "MYSQL"
    except Exception as e:
        if USE_FALLBACK:
            conn = get_sqlite_connection()
            ACTIVE_DB_TYPE = "SQLITE"
            return conn, "SQLITE"
        raise ConnectionError(f"Failed to connect to MySQL database: {e}")

def init_db():
    """Initializes tables in the active database engine."""
    conn, db_type = get_db()
    try:
        if db_type == "MYSQL":
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        full_name VARCHAR(150) NOT NULL,
                        email VARCHAR(191) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        membership_tier VARCHAR(50) DEFAULT 'Standard Athlete',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_user_email (email)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
            print("[DB] Connected to MySQL: Table 'users' verified.")
        else:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        membership_tier TEXT DEFAULT 'Standard Athlete',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            print(f"[DB] MySQL offline — using local SQLite fallback at {SQLITE_PATH}")
    finally:
        conn.close()

# -----------------------------------------------------------------------------
# User Repository Helper Functions
# -----------------------------------------------------------------------------

def find_user_by_email(email):
    """Fetch user by unique email address."""
    conn, db_type = get_db()
    try:
        clean_email = email.strip().lower()
        if db_type == "MYSQL":
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (clean_email,))
                return cursor.fetchone()
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (clean_email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def find_user_by_id(user_id):
    """Fetch user by primary key ID."""
    conn, db_type = get_db()
    try:
        if db_type == "MYSQL":
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, full_name, email, membership_tier, created_at FROM users WHERE id = %s LIMIT 1", (user_id,))
                return cursor.fetchone()
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id, full_name, email, membership_tier, created_at FROM users WHERE id = ? LIMIT 1", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def create_user(full_name, email, password_hash, membership_tier="Standard Athlete"):
    """Inserts a new user into database and returns the generated user id."""
    conn, db_type = get_db()
    try:
        clean_email = email.strip().lower()
        clean_name = full_name.strip()
        if db_type == "MYSQL":
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, membership_tier) VALUES (%s, %s, %s, %s)",
                    (clean_name, clean_email, password_hash, membership_tier)
                )
                return cursor.lastrowid
        else:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, membership_tier) VALUES (?, ?, ?, ?)",
                    (clean_name, clean_email, password_hash, membership_tier)
                )
                return cursor.lastrowid
    finally:
        conn.close()
