"""Funciones sencillas para guardar la tienda en una base SQLite."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

RUTA_BASE_DATOS = Path(__file__).with_name("tienda.db")


@contextmanager
def conectar():
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        with conexion:
            yield conexion
    finally:
        conexion.close()


def inicializar_base_datos():
    """Crea las tablas y carga el inventario inicial solo la primera vez."""
    with conectar() as conexion:
        conexion.executescript("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL COLLATE NOCASE UNIQUE,
                precio REAL NOT NULL CHECK (precio >= 0),
                stock REAL NOT NULL DEFAULT 0 CHECK (stock >= 0),
                unidad TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                subtotal REAL NOT NULL,
                descuento REAL NOT NULL,
                total REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL REFERENCES ventas(id),
                producto_id INTEGER REFERENCES productos(id),
                nombre_producto TEXT NOT NULL,
                cantidad REAL NOT NULL,
                unidad TEXT NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                producto_id INTEGER REFERENCES productos(id),
                nombre_producto TEXT NOT NULL,
                tipo TEXT NOT NULL,
                cantidad REAL NOT NULL,
                nota TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS cierres_semanales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio_semana TEXT NOT NULL UNIQUE,
                fin_semana TEXT NOT NULL,
                fecha_cierre TEXT NOT NULL,
                numero_ventas INTEGER NOT NULL,
                ingresos REAL NOT NULL
            );
        """)
        cantidad = conexion.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
        if cantidad == 0:
            iniciales = [
                ("Leche", 28.0, 12, "pieza"), ("Huevo", 48.0, 8, "docena"),
                ("Arroz", 32.0, 15, "kg"), ("Frijol", 38.0, 10, "kg"),
                ("Aceite", 45.0, 9, "litro"), ("Azucar", 29.0, 20, "kg"),
                ("Galletas", 18.0, 14, "paquete"), ("Refresco", 35.0, 10, "pieza"),
            ]
            conexion.executemany(
                "INSERT INTO productos (nombre, precio, stock, unidad) VALUES (?, ?, ?, ?)",
                iniciales,
            )

