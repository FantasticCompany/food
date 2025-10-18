from pathlib import Path
import sqlite3

DB_PATH = Path("fnb.sqlite")  # en Railway vive en /app

def get_conn():
    return sqlite3.connect(DB_PATH)

def run_sql_script(path: str):
    with get_conn() as con:
        with open(path, "r", encoding="utf-8") as f:
            con.executescript(f.read())

def init_db():
    # Crea DB y tablas si no existen
    if not DB_PATH.exists():
        DB_PATH.touch()
    run_sql_script("schema.sql")
