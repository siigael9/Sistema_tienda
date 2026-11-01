"""Altas, cambios, bajas lógicas y consultas de productos."""
from base_datos import conectar


def listar_productos(solo_activos=True):
    with conectar() as conexion:
        consulta = "SELECT * FROM productos"
        if solo_activos:
            consulta += " WHERE activo = 1"
        return conexion.execute(consulta + " ORDER BY nombre").fetchall()


def buscar_producto(texto):
    with conectar() as conexion:
        return conexion.execute(
            "SELECT * FROM productos WHERE activo = 1 AND nombre LIKE ? ORDER BY nombre",
            (f"%{texto.strip()}%",),
        ).fetchall()


def agregar_producto(nombre, precio, stock, unidad):
    nombre = nombre.strip()
    if not nombre or precio < 0 or stock < 0 or not unidad.strip():
        raise ValueError("Revisa el nombre, el precio, las existencias y la unidad.")
    with conectar() as conexion:
        conexion.execute(
            "INSERT INTO productos (nombre, precio, stock, unidad) VALUES (?, ?, ?, ?)",
            (nombre, precio, stock, unidad.strip()),
        )


def editar_producto(producto_id, nombre, precio, unidad):
    if not nombre.strip() or precio < 0 or not unidad.strip():
        raise ValueError("El nombre y la unidad son obligatorios; el precio no puede ser negativo.")
    with conectar() as conexion:
        resultado = conexion.execute(
            "UPDATE productos SET nombre = ?, precio = ?, unidad = ? WHERE id = ? AND activo = 1",
            (nombre.strip(), precio, unidad.strip(), producto_id),
        )
        if resultado.rowcount == 0:
            raise ValueError("No se encontró ese producto activo.")


def retirar_producto(producto_id):
    """Lo oculta de ventas sin borrar ventas ni movimientos anteriores."""
    with conectar() as conexion:
        resultado = conexion.execute(
            "UPDATE productos SET activo = 0 WHERE id = ? AND activo = 1", (producto_id,)
        )
        if resultado.rowcount == 0:
            raise ValueError("No se encontró ese producto activo.")

