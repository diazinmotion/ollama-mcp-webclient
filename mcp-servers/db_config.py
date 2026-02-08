import sqlite3
import json

DB_PATH = "mcp_config.db"

def get_config(key, default=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM configs WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except sqlite3.OperationalError:
        return default

def get_db_tools():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, description, input_schema FROM tools")
        rows = cursor.fetchall()
        conn.close()
        return [{"name": r[0], "description": r[1], "inputSchema": json.loads(r[2])} for r in rows]
    except sqlite3.OperationalError:
        return []

def get_all_configs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM configs")
        rows = cursor.fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}
    except sqlite3.OperationalError:
        return {}
