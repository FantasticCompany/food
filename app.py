
import streamlit as st
import pandas as pd
from db import get_conn, init_db, load_sample_data, DB_PATH

st.set_page_config(page_title="F&B Control Hotel", layout="wide")

def costo_promedio_actual(con, insumo_id):
    q = """
    SELECT SUM(cantidad*costo_unitario) / NULLIF(SUM(cantidad),0)
    FROM movinv
    WHERE insumo_id=? AND tipo='ENTRADA' AND costo_unitario IS NOT NULL
    """
    val = con.execute(q, (insumo_id,)).fetchone()[0]
    return float(val) if val is not None else None

def existencia_actual(con, insumo_id):
    q = """
    SELECT COALESCE(SUM(CASE WHEN tipo IN ('ENTRADA','PRODUCCION') THEN cantidad
                             WHEN tipo IN ('SALIDA','AJUSTE') THEN -cantidad
                             ELSE 0 END),0)
    FROM movinv WHERE insumo_id=?
    """
    val = con.execute(q, (insumo_id,)).fetchone()[0]
    return float(val or 0)

def page_consulta():
    st.header("Consulta de existencias")
    with get_conn() as con:
        ins_df = pd.read_sql_query("SELECT insumo_id, nombre, sku, unidad_base, categoria FROM insumos WHERE activo=1 ORDER BY nombre", con)
    col1, col2 = st.columns([2,1])
    with col1:
        sel = st.selectbox("Producto", ins_df["nombre"].tolist())
    row = ins_df[ins_df["nombre"]==sel].iloc[0]
    with get_conn() as con:
        costo = costo_promedio_actual(con, int(row["insumo_id"]))
        exist = existencia_actual(con, int(row["insumo_id"]))

    st.subheader("Ficha")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cod sistema", int(row["insumo_id"]))
    c2.metric("Unidad base", row["unidad_base"])
    c3.metric("Categoría", row["categoria"])
    c4.metric("SKU", row["sku"] if row["sku"] else "-")

    c1, c2 = st.columns(2)
    c1.metric("Precio promedio (Entradas)", f"{costo:,.0f} COP" if costo else "s/datos")
    c2.metric("Existencia actual", f"{exist:,.2f} {row['unidad_base']}")

    st.divider()
    st.caption("Movimientos recientes")
    with get_conn() as con:
        mov = pd.read_sql_query(
            "SELECT fecha, tipo, cantidad, unidad, costo_unitario, documento, origen_destino, usuario "
            "FROM movinv WHERE insumo_id=? ORDER BY fecha DESC, mov_id DESC LIMIT 50",
            con, params=(int(row["insumo_id"]),)
        )
    st.dataframe(mov, use_container_width=True)

def page_insumos():
    st.header("Maestro de Insumos")
    with get_conn() as con:
        df = pd.read_sql_query("SELECT * FROM insumos", con)
    st.dataframe(df, use_container_width=True)
    with st.expander("Agregar insumo"):
        with get_conn() as con:
            cats = [r[0] for r in con.execute("SELECT categoria FROM categorias").fetchall()]
            uns = [r[0] for r in con.execute("SELECT unidad FROM unidades").fetchall()]
        nombre = st.text_input("Nombre")
        categoria = st.selectbox("Categoría", cats)
        unidad = st.selectbox("Unidad base", uns)
        sku = st.text_input("SKU", "")
        stock_min = st.number_input("Stock mínimo", 0.0, step=1.0)
        stock_max = st.number_input("Stock máximo", 0.0, step=1.0)
        if st.button("Guardar insumo"):
            with get_conn() as con:
                con.execute(
                    "INSERT INTO insumos(nombre,categoria,unidad_base,stock_min,stock_max,sku,activo) VALUES (?,?,?,?,?,?,1)",
                    (nombre,categoria,unidad,stock_min,stock_max,sku)
                )
                con.commit()
            st.success("Guardado")

def page_movimientos():
    st.header("Movimientos de Inventario")
    with get_conn() as con:
        ins = pd.read_sql_query("SELECT insumo_id, nombre, unidad_base FROM insumos WHERE activo=1 ORDER BY nombre", con)
    nombre = st.selectbox("Producto", ins["nombre"])
    tipo = st.selectbox("Tipo", ["ENTRADA","SALIDA","AJUSTE","PRODUCCION"])
    cantidad = st.number_input("Cantidad", 0.0, step=0.1)
    unidad = st.text_input("Unidad", ins[ins["nombre"]==nombre]["unidad_base"].iloc[0])
    costo = st.number_input("Costo unitario (solo ENTRADA)", 0.0, step=100.0)
    documento = st.text_input("Documento", "")
    origen = st.text_input("Centro/Origen-Destino", "")
    usuario = st.text_input("Usuario", "")
    if st.button("Registrar movimiento"):
        with get_conn() as con:
            insumo_id = int(ins[ins["nombre"]==nombre]["insumo_id"].iloc[0])
            con.execute(
                "INSERT INTO movinv(fecha,tipo,insumo_id,cantidad,unidad,costo_unitario,documento,origen_destino,usuario) "
                "VALUES (date('now'),?,?,?,?,?,?,?,?)",
                (tipo,insumo_id,cantidad,unidad,(costo if tipo=='ENTRADA' else None),documento,origen,usuario)
            )
            con.commit()
        st.success("Movimiento registrado")

    with get_conn() as con:
        mov = pd.read_sql_query(
            "SELECT m.fecha, i.nombre as producto, m.tipo, m.cantidad, m.unidad, m.costo_unitario, m.documento, m.origen_destino, m.usuario "
            "FROM movinv m JOIN insumos i USING(insumo_id) "
            "ORDER BY m.fecha DESC, m.mov_id DESC LIMIT 200",
            con
        )
    st.dataframe(mov, use_container_width=True)

def page_admin():
    st.header("Administración")
    if st.button("Inicializar base de datos"):
        init_db()
        st.success("Esquema creado")
    if st.button("Cargar datos de ejemplo"):
        load_sample_data()
        st.success("Ejemplo cargado")
    st.caption(f"Ruta DB: {DB_PATH}")

PAGES = {
    "Consulta de existencias": page_consulta,
    "Insumos": page_insumos,
    "Movimientos": page_movimientos,
    "Administración": page_admin,
}

st.sidebar.title("F&B Control")
choice = st.sidebar.radio("Navegación", list(PAGES.keys()))
PAGES[choice]()
