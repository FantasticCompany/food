import streamlit as st
import pandas as pd
import db

def page_stock():
    st.title("Consulta de existencias")

    # Asegura que la BD y tablas existan
    try:
        db.init_db()
    except Exception:
        pass

    # Cargar lista de insumos
    with db.get_conn() as con:
        insumos = [r[0] for r in con.execute(
            "SELECT nombre FROM insumos WHERE activo=1 ORDER BY nombre"
        ).fetchall()]

    if not insumos:
        st.info("No hay insumos aún. Ve a **Administración → Inicializar base de datos** y (opcional) **Cargar datos de ejemplo**.")
        return

    prod = st.selectbox("Producto", insumos)

    with db.get_conn() as con:
        # Ficha básica
        ficha = con.execute("""
            SELECT i.id, i.unidad_base, i.categoria, IFNULL(i.sku,'')
            FROM insumos i
            WHERE i.nombre=?""", (prod,)).fetchone()
        insumo_id, unidad_base, categoria, sku = ficha

        # Existencia = entradas - salidas (ajuste suma signo que corresponda)
        existencia = con.execute("""
            SELECT IFNULL(SUM(
                CASE m.tipo WHEN 'ENTRADA' THEN m.cantidad
                            WHEN 'SALIDA'  THEN -m.cantidad
                            WHEN 'AJUSTE'  THEN m.cantidad
                END
            ),0)
            FROM movimientos m
            WHERE m.insumo_id=?""", (insumo_id,)).fetchone()[0] or 0

        # Precio promedio (de entradas)
        precio = con.execute("""
            SELECT ROUND(AVG(costo_unitario),0)
            FROM movimientos
            WHERE insumo_id=? AND tipo='ENTRADA' AND costo_unitario IS NOT NULL
        """, (insumo_id,)).fetchone()[0]

        # Movimientos recientes
        df = pd.read_sql_query("""
            SELECT fecha, tipo, cantidad, unidad, costo_unitario, documento, origen_destino
            FROM movimientos
            WHERE insumo_id=?
            ORDER BY fecha DESC, id DESC
            LIMIT 20
        """, con, params=(insumo_id,))

    # Render
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cod sistema", f"{insumo_id}")
    c2.metric("Unidad base", unidad_base)
    c3.metric("Categoría", categoria)
    c4.metric("SKU", sku if sku else "—")

    st.metric("Existencia actual", f"{existencia:.2f} {unidad_base}")
    st.metric("Precio promedio (entradas)", f"{int(precio):,} COP".replace(",", ".")) if precio else st.write("")

    st.subheader("Movimientos recientes")
    st.dataframe(df, use_container_width=True)
