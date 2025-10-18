-- Tablas base (ya existentes en tu prototipo; deja solo si faltan)
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

-- Extensiones para MEAT TAG
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

-- Recetas (auxiliares y principales)
CREATE TABLE IF NOT EXISTS receta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL,        -- 'aux' | 'principal'
  nombre TEXT NOT NULL UNIQUE,
  rendimiento REAL NOT NULL, -- cantidad final
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

-- Carta
CREATE TABLE IF NOT EXISTS carta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  receta_principal_id INTEGER NOT NULL,
  sku TEXT UNIQUE,
  precio_venta REAL NOT NULL,
  iva REAL DEFAULT 0,
  activo INTEGER DEFAULT 1,
  FOREIGN KEY (receta_principal_id) REFERENCES receta(id)
);
