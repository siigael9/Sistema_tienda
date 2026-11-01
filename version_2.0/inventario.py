"""Consulta y reposición de existencias con registro de movimientos."""
from datetime import datetime
from base_datos import conectar
from productos import listar_productos


def registrar_reposicion(producto_id, cantidad, nota="Reposición"):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")
    ahora = datetime.now().isoformat(timespec="seconds")
    with conectar() as conexion:
        producto = conexion.execute(
            "SELECT * FROM productos WHERE id = ? AND activo = 1", (producto_id,)
        ).fetchone()
        if producto is None:
            raise ValueError("No se encontró ese producto activo.")
        conexion.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id))
        conexion.execute(
            "INSERT INTO movimientos_inventario (fecha, producto_id, nombre_producto, tipo, cantidad, nota) VALUES (?, ?, ?, 'reposicion', ?, ?)",
            (ahora, producto_id, producto["nombre"], cantidad, nota.strip()),
        )


def registrar_salida(conexion, producto, cantidad, fecha):
    """Se usa dentro de la misma transacción que guarda una venta."""
    conexion.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, producto["id"]))
    conexion.execute(
        "INSERT INTO movimientos_inventario (fecha, producto_id, nombre_producto, tipo, cantidad, nota) VALUES (?, ?, ?, 'venta', ?, ?)",
        (fecha, producto["id"], producto["nombre"], -cantidad, "Venta"),
    )


def mostrar_inventario():
    print("\n--- INVENTARIO ---")
    productos = listar_productos()
    if not productos:
        print("No hay productos activos.")
    for numero, producto in enumerate(productos, start=1):
        print(f"{numero}. {producto['nombre']} | ${producto['precio']:.2f} | "
              f"Existencias: {producto['stock']:g} {producto['unidad']}")
    print("Productos activos:", len(productos))

