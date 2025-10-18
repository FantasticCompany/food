# app.py
import streamlit as st
import sqlite3
from pathlib import Path
from datetime import date
import pandas as pd

# ========== CONFIG BÁSICA ==========
st.set_page_config(page_title="F&B Control", layout="wide")
DB_PATH = Path("fnb.sqlite")

# ========== ESQUEMA DE BASE ==========
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS unidades (unidad TEXT PRIMARY KEY, descripcion TEXT);
CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, categoria TEXT UNIQUE, descripcion TEXT);
CREATE TABLE IF NOT EXISTS insumos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT UNIQUE,
  categoria TEXT,
  unidad_base TEXT,
  stock_min REAL DEFAULT 0,
  stock_max REAL DEFAULT 0,
  activo INTEGER DEFAULT 1,
  sku TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS precios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  insumo_id INTEGER NOT NULL,
  fecha TEXT NOT NULL,
  proveedor TEXT,
  costo_unitario REAL NOT NULL,
  moneda TEXT DEFAULT 'COP',
  FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);
CREATE TABLE IF NOT EXISTS movimientos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT NOT NULL,
  tipo TEXT CHECK(tipo IN ('ENTRADA','SALIDA','AJUSTE')) NOT NULL,
  insumo_id INTEGER NOT NULL,
  cantidad REAL NOT NULL,
  unidad TEXT NOT NULL,
  costo_unitario REAL,
  documento TEXT,
  origen_destino TEXT,
  usuario TEXT,
  FOREIGN KEY (insumo_id) REFERENCES insumos(id)
);

-- MEAT TAG
CREATE TABLE IF NOT EXISTS meat_lote (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha TEXT NOT NULL,
  insumo_origen_id INTEGER NOT NULL,
  cantidad_origen REAL NOT NULL,
  unidad_origen TEXT NOT NULL,
  observacion TEXT,
  FOREIGN KEY (insumo_origen_id) REFERENCES insumos(id)
);
CREATE TABLE IF NOT EXISTS meat_salida (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lote_id INTEGER NOT NULL,
  insumo_destino_id INTEGER NOT NULL,
  cantidad REAL NOT NULL,
  unidad TEXT NOT NULL,
  FOREIGN KEY (lote_id) REFERENCES meat_lote(id),
  FOREIGN KEY (insumo_destino_id) REFERENCES insumos(id)
);

-- RECETAS
CREATE TABLE IF NOT EXISTS receta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL,        -- 'aux' | 'principal'
  nombre TEXT NOT NULL UNIQUE,
  rendimiento REAL NOT NULL,
  unidad TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS receta_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receta_id INTEGER NOT NULL,
  item_tipo TEXT NOT NULL,   -- 'insumo' | 'receta'
  item_id INTEGER NOT NULL,
  cantidad REAL NOT NULL,
  unidad TEXT NOT NULL,
  FOREIGN KEY (receta_id) REFERENCES receta(id)
);

-- CARTA
CREATE TABLE IF NOT EXISTS carta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receta_principal_id INTEGER NOT NULL,
  sku TEXT UNIQUE,
  precio_venta REAL NOT NULL,
  iva REAL DEFAULT 0,
  activo INTEGER DEFAULT 1,
  FOREIGN KEY (receta_principal_id) REFERENCES receta(id)
);
"""

# ========== DB HELPERS ==========
def get_conn():
    # check_same_thread=False para permitir múltiples llamadas en Streamlit
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    if not DB_PATH.exists():
        DB_PATH.touch()
    with get_conn() as con:
        con.executescript(SCHEMA_SQL)

def seed_from_csv_folder(folder="sample_data"):
    """
    Si existen CSV en sample_data/ los carga.
    Archivos esperados (opcionales):
      unidades.csv (unidad,descripcion)
      categorias.csv (categoria,descripcion)
      insumos.csv (nombre,categoria,unidad_base,sku,stock_min,stock_max,activo)
      movimientos.csv (fecha,tipo,insumo, cantidad, unidad, costo_unitario, documento, origen_destino, usuario)
    """
    import os
    from csv import DictReader

    path = Path(folder)
    if not path.exists():
        return "No se encontró la carpeta sample_data/"

    with get_conn() as con:
        cur = con.cursor()

        # Unidades
        f = path / "unidades.csv"
        if f.exists():
            with f.open(encoding="utf-8") as fd:
                dr = DictReader(fd)
                for r in dr:
                    cur.execute("INSERT OR IGNORE INTO unidades(unidad, descripcion) VALUES(?,?)",
                                (r["unidad"], r.get("descripcion","")))
        # Categorías
        f = path / "categorias.csv"
        if f.exists():
            with f.open(encoding="utf-8") as fd:
                dr = DictReader(fd)
                for r in dr:
                    cur.execute("INSERT OR IGNORE INTO categorias(categoria, descripcion) VALUES(?,?)",
                                (r["categoria"], r.get("descripcion","")))
        # Insumos
        f = path / "insumos.csv"
        if f.exists():
            with f.open(encoding="utf-8") as fd:
                dr = DictReader(fd)
                for r in dr:
                    cur.execute("""
                        INSERT OR IGNORE INTO insumos(nombre,categoria,unidad_base,sku,stock_min,stock_max,activo)
                        VALUES(?,?,?,?,?,?,?)
                    """, (r["nombre"], r.get("categoria"), r.get("unidad_base"), r.get("sku"),
                          float(r.get("stock_min",0) or 0), float(r.get("stock_max",0) or 0),
                          int(r.get("activo",1) or 1)))
        # Movimientos
        f = path / "movimientos.csv"
        if f.exists():
            with f.open(encoding="utf-8") as fd:
                dr = DictReader(fd)
                for r in dr:
                    # Mapear nombre de insumo -> id
                    insumo_id = cur.execute("SELECT id FROM insumos WHERE nombre=?",
                                            (r["insumo"],)).fetchone()
                    if not insumo_id: 
                        continue
                    insumo_id = insumo_id[0]
                    cur.execute("""
                        INSERT INTO movimientos(fecha,tipo,insumo_id,cantidad,unidad,costo_unitario,documento,origen_destino,usuario)
                        VALUES(?,?,?,?,?,?,?,?,?)
                    """, (r["fecha"], r["tipo"], insumo_id, float(r["cantidad"]),
                          r["unidad"], float(r["costo_unitario"]) if r.get("costo_unitario") else None,
                          r.get("documento"), r.get("origen_destino"), r.get("usuario")))
        con.commit()
    return "Datos de ejemplo cargados."

def seed_minimal_demo():
    """Carga unos pocos registros si no hay CSV, solo para ver la app viva."""
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("INSERT OR IGNORE INTO unidades(unidad,descripcion) VALUES('kg','kilogramo'),('und','unidad')")
        cur.execute("INSERT OR IGNORE INTO categorias(categoria,descripcion) VALUES('Granos','Granos y legumbres')")
        cur.execute("""INSERT OR IGNORE INTO insumos(nombre,categoria,unidad_base,sku,stock_min,stock_max,activo)
                       VALUES('FRIJOL SABANERO','Granos','kg','GR-001',0,0,1)""")
        insumo_id = cur.execute("SELECT id FROM insumos WHERE nombre='FRIJOL SABANERO'").fetchone()[0]
        # Entrada y salida para mostrar existencia
        cur.execute("""INSERT INTO movimientos(fecha,tipo,insumo_id,cantidad,unidad,costo_unitario,documento,origen_destino,usuario)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (str(date.today()), 'ENTRADA', insumo_id, 25, 'kg', 6500, 'OC-1001', 'Proveedor B', 'None'))
        cur.execute("""INSERT INTO movimientos(fecha,tipo,insumo_id,cantidad,unidad,costo_unitario,documento,origen_destino,usuario)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (str(date.today()), 'SALIDA', insumo_id, 5, 'kg', None, 'PRD-0001', 'Cocina Caliente', 'None'))
        con.commit()

# ========== UI: MENÚ ==========
NAV = {
    "Insumos": {
        "Consulta de existencias": "page_stock",
        "Maestros": {
            "Unidades": "page_unidades",
            "Categorías": "page_categorias",
            "Insumos": "page_insumos",
        },
        "Movimientos": {
            "Entradas": "page_mov_entradas",
            "Salidas": "page_mov_salidas",
            "Ajustes": "page_mov_ajustes",
        },
        "Reportes": {
            "Kardex": "page_rep_kardex",
            "Valorizado": "page_rep_valorizado",
        }
    },
    "Meat Tag": {
        "Lotes de desposte": "page_meat_lotes",
        "Rendimientos": "page_meat_rend",
        "Reporte por lote": "page_meat_rep",
    },
    "Receta auxiliar": {
        "Catálogo": "page_rec_aux",
        "Componentes": "page_rec_aux_items",
    },
    "Receta principal": {
        "Platos": "page_rec_pri",
        "Componentes": "page_rec_pri_items",
        "Costeo": "page_rec_pri_costeo",
    },
    "Carta": {
        "Items facturables": "page_carta_items",
        "Márgenes": "page_carta_margenes",
    },
    "Administración": {
        "Inicializar base de datos": "page_admin_init",
        "Cargar datos de ejemplo": "page_admin_seed",
        "Respaldos": "page_admin_backup",
    }
}

def render_menu(nav_map):
    st.sidebar.header("F&B Control")
    nivel1 = st.sidebar.selectbox("Módulo", list(nav_map.keys()))
    submap = nav_map[nivel1]
    if isinstance(submap, dict):
        nivel2 = st.sidebar.selectbox("Sección", list(submap.keys()))
        sub2 = submap[nivel2]
        if isinstance(sub2, dict):
            nivel3 = st.sidebar.selectbox("Vista", list(sub2.keys()))
            return sub2[nivel3], (nivel1, nivel2, nivel3)
        else:
            return sub2, (nivel1, nivel2)
    else:
        return submap, (nivel1,)

# ========== PÁGINAS ==========
def page_placeholder(title):
    st.title(title)
    st.info("Vista en construcción.")

def page_stock():
    st.title("Consulta de existencias")
    init_db()

    with get_conn() as con:
        insumos = [r[0] for r in con.execute(
            "SELECT nombre FROM insumos WHERE activo=1 ORDER BY nombre"
        ).fetchall()]

    if not insumos:
        st.info("No hay insumos. Ve a **Administración → Inicializar base de datos** y (opcional) **Cargar datos de ejemplo**.")
        return

    prod = st.selectbox("Producto", insumos)

    with get_conn() as con:
        # Ficha
        row = con.execute("""
            SELECT i.id, i.unidad_base, i.categoria, IFNULL(i.sku,'')
            FROM insumos i WHERE i.nombre=?""", (prod,)).fetchone()
        insumo_id, unidad_base, categoria, sku = row

        existencia = con.execute("""
            SELECT IFNULL(SUM(
                CASE tipo WHEN 'ENTRADA' THEN cantidad
                          WHEN 'SALIDA'  THEN -cantidad
                          WHEN 'AJUSTE'  THEN cantidad END
            ),0) FROM movimientos WHERE insumo_id=?""", (insumo_id,)).fetchone()[0] or 0

        precio = con.execute("""
            SELECT ROUND(AVG(costo_unitario),0)
            FROM movimientos
            WHERE insumo_id=? AND tipo='ENTRADA' AND costo_unitario IS NOT NULL
        """, (insumo_id,)).fetchone()[0]

        df = pd.read_sql_query("""
            SELECT fecha, tipo, cantidad, unidad, costo_unitario, documento, origen_destino
            FROM movimientos
            WHERE insumo_id=?
            ORDER BY fecha DESC, id DESC
            LIMIT 30
        """, con, params=(insumo_id,))

    # UI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cod sistema", f"{insumo_id}")
    c2.metric("Unidad base", unidad_base)
    c3.metric("Categoría", categoria)
    c4.metric("SKU", sku if sku else "—")
    st.metric("Existencia actual", f"{existencia:.2f} {unidad_base}")
    if precio:
        st.metric("Precio promedio (entradas)", f"{int(precio):,} COP".replace(",", "."))

    st.subheader("Movimientos recientes")
    st.dataframe(df, use_container_width=True, height=420)

def page_admin_init():
    st.title("Administración · Inicializar base de datos")
    if st.button("Inicializar base"):
        init_db()
        st.success("Base inicializada / verificada.")
        st.info("Si quieres ver datos de pruebas, usa **Cargar datos de ejemplo**.")

def page_admin_seed():
    st.title("Administración · Cargar datos de ejemplo")
    init_db()
    if st.button("Cargar desde sample_data/ (si existe)"):
        msg = seed_from_csv_folder("sample_data")
        st.success(msg)
    if st.button("Cargar demo mínima (FRIJOL SABANERO)"):
        seed_minimal_demo()
        st.success("Demo mínima cargada.")
    st.info("Luego ve a **Insumos → Consulta de existencias** para visualizar.")

def page_admin_backup():
    st.title("Administración · Respaldos")
    if DB_PATH.exists():
        with open(DB_PATH, "rb") as f:
            st.download_button("Descargar fnb.sqlite", f, file_name="fnb.sqlite")
    else:
        st.warning("No hay base de datos aún.")

# Mapear páginas
PAGES = {"page_stock": page_stock,
         "page_admin_init": page_admin_init,
         "page_admin_seed": page_admin_seed,
         "page_admin_backup": page_admin_backup}

# Placeholders para las demás vistas
for key in [
    "page_unidades","page_categorias","page_insumos",
    "page_mov_entradas","page_mov_salidas","page_mov_ajustes",
    "page_rep_kardex","page_rep_valorizado",
    "page_meat_lotes","page_meat_rend","page_meat_rep",
    "page_rec_aux","page_rec_aux_items",
    "page_rec_pri","page_rec_pri_items","page_rec_pri_costeo",
    "page_carta_items","page_carta_margenes",
]:
    if key not in PAGES:
        PAGES[key] = (lambda t=key: page_placeholder(t))

# ========== RENDER ==========
page_key, _crumbs = render_menu(NAV)
PAGES[page_key]()
