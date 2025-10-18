PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS unidades (unidad TEXT PRIMARY KEY, descripcion TEXT);
CREATE TABLE IF NOT EXISTS categorias (categoria TEXT PRIMARY KEY, descripcion TEXT);
CREATE TABLE IF NOT EXISTS insumos (
  insumo_id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL UNIQUE,
  categoria TEXT REFERENCES categorias(categoria) ON UPDATE CASCADE,
  unidad_base TEXT REFERENCES unidades(unidad) ON UPDATE CASCADE,
  stock_min REAL DEFAULT 0, stock_max REAL DEFAULT 0,
  activo INTEGER DEFAULT 1, sku TEXT, notas TEXT);
CREATE TABLE IF NOT EXISTS precios (
  precio_id INTEGER PRIMARY KEY AUTOINCREMENT,
  insumo_id INTEGER NOT NULL REFERENCES insumos(insumo_id) ON DELETE CASCADE,
  fecha TEXT NOT NULL, proveedor TEXT, costo_unitario REAL NOT NULL, moneda TEXT DEFAULT 'COP', observaciones TEXT);
CREATE INDEX IF NOT EXISTS idx_precios_insumo_fecha ON precios(insumo_id, fecha);
CREATE TABLE IF NOT EXISTS movinv (
  mov_id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, tipo TEXT NOT NULL,
  insumo_id INTEGER NOT NULL REFERENCES insumos(insumo_id) ON DELETE RESTRICT,
  cantidad REAL NOT NULL, unidad TEXT NOT NULL, costo_unitario REAL,
  documento TEXT, origen_destino TEXT, lote TEXT, vencimiento TEXT, usuario TEXT, notas TEXT);
CREATE TABLE IF NOT EXISTS meattag_lotes (
  batch_id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL,
  insumo_origen_id INTEGER NOT NULL REFERENCES insumos(insumo_id),
  peso_bruto REAL NOT NULL, peso_limpio REAL, merma REAL, rendimiento_pct REAL,
  responsable TEXT, notas TEXT);
CREATE TABLE IF NOT EXISTS meattag_detalle (
  detalle_id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id INTEGER NOT NULL REFERENCES meattag_lotes(batch_id) ON DELETE CASCADE,
  insumo_derivado_id INTEGER NOT NULL REFERENCES insumos(insumo_id), cantidad REAL NOT NULL, unidad TEXT NOT NULL, observaciones TEXT);
CREATE TABLE IF NOT EXISTS receta_aux (
  receta_aux_id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE,
  rendimiento_cantidad REAL NOT NULL, unidad_salida TEXT NOT NULL, version TEXT DEFAULT '1.0', activa INTEGER DEFAULT 1, notas TEXT);
CREATE TABLE IF NOT EXISTS receta_aux_det (
  receta_aux_det_id INTEGER PRIMARY KEY AUTOINCREMENT, receta_aux_id INTEGER NOT NULL REFERENCES receta_aux(receta_aux_id) ON DELETE CASCADE,
  tipo TEXT NOT NULL, componente_id INTEGER NOT NULL, cantidad REAL NOT NULL, unidad TEXT NOT NULL, merma_prep_pct REAL DEFAULT 0, notas TEXT);
CREATE TABLE IF NOT EXISTS receta_ppal (
  receta_id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE,
  porcion_estandar REAL NOT NULL, unidad_porcion TEXT NOT NULL, version TEXT DEFAULT '1.0', activa INTEGER DEFAULT 1, costo_objetivo REAL, notas TEXT);
CREATE TABLE IF NOT EXISTS receta_ppal_det (
  receta_ppal_det_id INTEGER PRIMARY KEY AUTOINCREMENT, receta_id INTEGER NOT NULL REFERENCES receta_ppal(receta_id) ON DELETE CASCADE,
  tipo TEXT NOT NULL, componente_id INTEGER NOT NULL, cantidad REAL NOT NULL, unidad TEXT NOT NULL, merma_prep_pct REAL DEFAULT 0, notas TEXT);
CREATE TABLE IF NOT EXISTS carta (
  item_id INTEGER PRIMARY KEY AUTOINCREMENT, plu TEXT UNIQUE, nombre TEXT NOT NULL, categoria_venta TEXT,
  receta_id INTEGER REFERENCES receta_ppal(receta_id) ON DELETE SET NULL, precio_venta REAL NOT NULL, impuesto_pct REAL DEFAULT 0, activo INTEGER DEFAULT 1, notas TEXT);
