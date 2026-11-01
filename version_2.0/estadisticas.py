"""Consultas de resumen para el menú de estadísticas."""
from base_datos import conectar


def obtener_estadisticas():
    with conectar() as conexion:
        ventas = conexion.execute(
            "SELECT COUNT(*) AS cantidad, COALESCE(SUM(total), 0) AS ingresos FROM ventas"
        ).fetchone()
        productos = conexion.execute(
            "SELECT COUNT(*) AS cantidad, COALESCE(SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END), 0) AS agotados FROM productos WHERE activo = 1"
        ).fetchone()
        mas_caro = conexion.execute(
            "SELECT nombre, precio FROM productos WHERE activo = 1 ORDER BY precio DESC, nombre LIMIT 1"
        ).fetchone()
        return {
            "ventas": ventas["cantidad"], "ingresos": ventas["ingresos"],
            "promedio": ventas["ingresos"] / ventas["cantidad"] if ventas["cantidad"] else 0,
            "productos": productos["cantidad"], "agotados": productos["agotados"],
            "mas_caro": mas_caro,
        }


def mostrar_estadisticas():
    datos = obtener_estadisticas()
    print("\n--- ESTADÍSTICAS ---")
    print("Productos activos:", datos["productos"])
    print("Ventas realizadas:", datos["ventas"])
    print(f"Ingresos acumulados: ${datos['ingresos']:.2f}")
    print(f"Promedio por venta: ${datos['promedio']:.2f}")
    print("Productos agotados:", datos["agotados"])
    if datos["mas_caro"]:
        print(f"Producto más caro: {datos['mas_caro']['nombre']} (${datos['mas_caro']['precio']:.2f})")

