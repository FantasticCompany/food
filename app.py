import streamlit as st

# --- NAV ---
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

page_key, crumbs = render_menu(NAV)

# Router mínimo (conserva tu page_stock existente)
PAGES = {}

def page_placeholder(title):
    st.title(title)
    st.info("Vista en construcción. Aquí irá la funcionalidad.")

PAGES["page_stock"] = lambda: None  # tu consulta actual
# Placeholders para que el esqueleto funcione
for key in [
    "page_unidades","page_categorias","page_insumos",
    "page_mov_entradas","page_mov_salidas","page_mov_ajustes",
    "page_rep_kardex","page_rep_valorizado",
    "page_meat_lotes","page_meat_rend","page_meat_rep",
    "page_rec_aux","page_rec_aux_items",
    "page_rec_pri","page_rec_pri_items","page_rec_pri_costeo",
    "page_carta_items","page_carta_margenes",
    "page_admin_init","page_admin_seed","page_admin_backup"
]:
    if key not in PAGES:
        PAGES[key] = (lambda t=key: page_placeholder(t))

# Render
if page_key in PAGES and page_key != "page_stock":
    PAGES[page_key]()
