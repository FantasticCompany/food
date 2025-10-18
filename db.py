
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("fnb.sqlite")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    schema_file = Path(__file__).with_name("schema.sql")
    with get_conn() as con, open(schema_file, "r", encoding="utf-8") as f:
        con.executescript(f.read())

def load_sample_data():
    import pandas as pd
    with get_conn() as con:
        for name in ["unidades","categorias"]:
            df = pd.read_csv(Path(__file__).with_name("sample_data")/f"{name}.csv")
            df.to_sql(name, con, if_exists="append", index=False)
        ins = pd.read_csv(Path(__file__).with_name("sample_data")/"insumos.csv")
        ins.to_sql("insumos", con, if_exists="append", index=False)
        id_map = {row[1]:row[0] for row in con.execute("SELECT insumo_id,nombre FROM insumos").fetchall()}
        pre = pd.read_csv(Path(__file__).with_name("sample_data")/"precios.csv")
        pre["insumo_id"] = pre["insumo_nombre"].map(id_map)
        pre.drop(columns=["insumo_nombre"], inplace=True)
        pre.to_sql("precios", con, if_exists="append", index=False)
        mov = pd.read_csv(Path(__file__).with_name("sample_data")/"movinv.csv")
        mov["insumo_id"] = mov["insumo_nombre"].map(id_map)
        mov.drop(columns=["insumo_nombre"], inplace=True)
        mov.to_sql("movinv", con, if_exists="append", index=False)
