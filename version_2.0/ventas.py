"""Carrito de compra y registro persistente de ventas."""
from datetime import datetime
from base_datos import conectar
from inventario import registrar_salida


def registrar_venta(carrito, fecha=None):
    """carrito: lista de (id_producto, cantidad). Valida y guarda todo junto."""
    if not carrito:
        raise ValueError("El carrito está vacío.")
    fecha = fecha or datetime.now().isoformat(timespec="seconds")
    dia = datetime.fromisoformat(fecha).date()
    inicio_semana = dia.fromordinal(dia.toordinal() - dia.weekday()).isoformat()
    with conectar() as conexion:
        if conexion.execute(
            "SELECT 1 FROM cierres_semanales WHERE inicio_semana = ?", (inicio_semana,)
        ).fetchone():
            raise ValueError("La semana de esta venta ya está cerrada.")
        cantidades = {}
        for producto_id, cantidad in carrito:
            if cantidad <= 0:
                raise ValueError("Todas las cantidades deben ser mayores que cero.")
            cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad
        lineas = []
        for producto_id, cantidad in cantidades.items():
            producto = conexion.execute(
                "SELECT * FROM productos WHERE id = ? AND activo = 1", (producto_id,)
            ).fetchone()
            if producto is None:
                raise ValueError("Uno de los productos ya no está disponible.")
            if producto["unidad"] in ("pieza", "paquete", "docena") and not float(cantidad).is_integer():
                raise ValueError(f"{producto['nombre']} requiere una cantidad entera.")
            if cantidad > producto["stock"]:
                raise ValueError(f"No hay suficientes existencias de {producto['nombre']}.")
            lineas.append((producto, cantidad, round(producto["precio"] * cantidad, 2)))
        subtotal = round(sum(linea[2] for linea in lineas), 2)
        descuento = round(subtotal * 0.10, 2) if subtotal > 500 else 0.0
        total = round(subtotal - descuento, 2)
        venta_id = conexion.execute(
            "INSERT INTO ventas (fecha, subtotal, descuento, total) VALUES (?, ?, ?, ?)",
            (fecha, subtotal, descuento, total),
        ).lastrowid
        for producto, cantidad, importe in lineas:
            conexion.execute(
                "INSERT INTO detalle_ventas (venta_id, producto_id, nombre_producto, cantidad, unidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (venta_id, producto["id"], producto["nombre"], cantidad, producto["unidad"], producto["precio"], importe),
            )
            registrar_salida(conexion, producto, cantidad, fecha)
        return {"id": venta_id, "subtotal": subtotal, "descuento": descuento, "total": total}


def obtener_ventas():
    with conectar() as conexion:
        return conexion.execute("SELECT * FROM ventas ORDER BY id").fetchall()


def obtener_detalle_venta(venta_id):
    with conectar() as conexion:
        return conexion.execute(
            "SELECT * FROM detalle_ventas WHERE venta_id = ? ORDER BY id", (venta_id,)
        ).fetchall()

